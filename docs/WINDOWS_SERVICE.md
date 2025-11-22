# Gerald Desktop Manager - Windows Service Guide

Complete guide for running Gerald Desktop Manager as a Windows Service.

## Table of Contents

1. [Overview](#overview)
2. [Why Run as a Service](#why-run-as-a-service)
3. [Installation Methods](#installation-methods)
4. [Service Configuration](#service-configuration)
5. [Service Management](#service-management)
6. [Troubleshooting](#troubleshooting)
7. [Uninstallation](#uninstallation)

---

## Overview

Running Gerald as a Windows Service allows it to:
- Start automatically when Windows boots
- Run in the background without user login
- Restart automatically if it crashes
- Be managed through Windows Service Manager

**Note**: This requires **Administrator privileges**.

---

## Why Run as a Service

### Advantages

✅ **Auto-Start**: Launches automatically on Windows boot
✅ **Background Operation**: Runs without keeping a console window open
✅ **Reliability**: Automatic restart on failure
✅ **Professional Deployment**: Managed through Windows Services
✅ **Security**: Runs with configured service account

### Disadvantages

⚠️ **No Console Output**: Cannot see logs in terminal (must use log files)
⚠️ **Debugging Harder**: More difficult to debug than console mode
⚠️ **Requires Admin**: Installation and configuration need admin rights

### When to Use

- **Production Deployment**: Running on a dedicated machine
- **Always-On Requirement**: Need Gerald available 24/7
- **Server Environment**: Running on Windows Server
- **Kiosk Mode**: Dedicated workstation for voice control

### When NOT to Use

- **Development**: Use console mode for easier debugging
- **Testing**: Console mode shows immediate feedback
- **Personal Use**: Simple auto-start with Task Scheduler may be easier

---

## Installation Methods

### Method 1: Using NSSM (Recommended)

**NSSM** (Non-Sucking Service Manager) is the easiest way to create Windows services.

#### Step 1: Download NSSM

```powershell
# Download NSSM
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "nssm.zip"

# Extract
Expand-Archive -Path nssm.zip -DestinationPath C:\Tools\

# Add to PATH (or use full path)
$env:Path += ";C:\Tools\nssm-2.24\win64"
```

#### Step 2: Install Service

```powershell
# Navigate to Gerald directory
cd C:\Gerald\jarvis_manager

# Install service with NSSM
nssm install GeraldManager "C:\Python310\python.exe" "C:\Gerald\jarvis_manager\run_gerald.py"

# Set service description
nssm set GeraldManager Description "Gerald Desktop Manager - Voice-controlled desktop manager"

# Set startup directory
nssm set GeraldManager AppDirectory "C:\Gerald\jarvis_manager"

# Set to start automatically
nssm set GeraldManager Start SERVICE_AUTO_START

# Configure logging
nssm set GeraldManager AppStdout "C:\Gerald\jarvis_manager\logs\service_stdout.log"
nssm set GeraldManager AppStderr "C:\Gerald\jarvis_manager\logs\service_stderr.log"

# Set log rotation
nssm set GeraldManager AppRotateFiles 1
nssm set GeraldManager AppRotateBytes 10485760  # 10MB
```

#### Step 3: Start Service

```powershell
# Start service
nssm start GeraldManager

# Or use Windows service commands
sc start GeraldManager
```

#### Verify Service

```powershell
# Check service status
nssm status GeraldManager

# Or
sc query GeraldManager
```

---

### Method 2: Using pywin32

Create service using Python's pywin32 package.

#### Step 1: Install pywin32

```powershell
pip install pywin32
```

#### Step 2: Create Service Script

Create `install_service.py`:

```python
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import subprocess
from pathlib import Path


class GeraldService(win32serviceutil.ServiceFramework):
    """Gerald Desktop Manager Windows Service"""

    _svc_name_ = "GeraldManager"
    _svc_display_name_ = "Gerald Desktop Manager"
    _svc_description_ = "Voice-controlled desktop manager for Windows"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        self.gerald_process = None

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

        # Stop Gerald
        if self.gerald_process:
            self.gerald_process.terminate()

    def SvcDoRun(self):
        """Run the service"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )

        self.main()

    def main(self):
        """Main service loop"""
        # Get Gerald directory
        gerald_dir = Path(__file__).parent

        # Start Gerald
        run_gerald = gerald_dir / "run_gerald.py"

        try:
            self.gerald_process = subprocess.Popen(
                [sys.executable, str(run_gerald)],
                cwd=str(gerald_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for stop signal
            while self.is_running:
                rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                if rc == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            servicemanager.LogErrorMsg(f"Gerald service error: {e}")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(GeraldService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(GeraldService)
```

#### Step 3: Install Service

```powershell
# Install service
python install_service.py install

# Set to auto-start
python install_service.py --startup auto install

# Start service
python install_service.py start
```

---

### Method 3: Using Task Scheduler (Simple Alternative)

Task Scheduler is simpler than a full service, but provides similar auto-start functionality.

```powershell
# Create startup task
$Action = New-ScheduledTaskAction -Execute "pythonw.exe" -Argument "C:\Gerald\jarvis_manager\run_gerald.py" -WorkingDirectory "C:\Gerald\jarvis_manager"

$Trigger = New-ScheduledTaskTrigger -AtLogon

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName "Gerald Desktop Manager" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Gerald voice-controlled desktop manager"
```

**Advantages over Service**:
- Easier to set up
- No additional tools needed
- Good for single-user machines

**Disadvantages**:
- Only starts at user login (not at boot)
- Tied to specific user account

---

## Service Configuration

### Configure Automatic Recovery

Set service to restart on failure:

```powershell
# Using NSSM
nssm set GeraldManager AppExit Default Restart
nssm set GeraldManager AppRestartDelay 5000  # Wait 5 seconds before restart

# Using sc.exe
sc failure GeraldManager reset= 0 actions= restart/5000/restart/5000/restart/5000
```

### Configure Service Account

By default, services run as `Local System`. To run as specific user:

```powershell
# Using NSSM
nssm set GeraldManager ObjectName ".\YourUsername" "YourPassword"

# Or use Windows Service Manager GUI
services.msc
# Right-click service → Properties → Log On tab
```

### Configure Dependencies

If Gerald depends on other services:

```powershell
# Set dependencies
nssm set GeraldManager DependOnService AudioSrv Audiosrv
```

### Configure Environment Variables

```powershell
# Set environment variables for service
nssm set GeraldManager AppEnvironmentExtra "GERALD_ENV=production" "LOG_LEVEL=INFO"
```

---

## Service Management

### Start Service

```powershell
# Using NSSM
nssm start GeraldManager

# Using sc
sc start GeraldManager

# Using PowerShell
Start-Service -Name GeraldManager

# Using Services GUI
services.msc  # Then right-click → Start
```

### Stop Service

```powershell
# Using NSSM
nssm stop GeraldManager

# Using sc
sc stop GeraldManager

# Using PowerShell
Stop-Service -Name GeraldManager
```

### Restart Service

```powershell
# Using NSSM
nssm restart GeraldManager

# Using PowerShell
Restart-Service -Name GeraldManager
```

### Check Service Status

```powershell
# Using NSSM
nssm status GeraldManager

# Using sc
sc query GeraldManager

# Using PowerShell
Get-Service -Name GeraldManager
```

### View Service Logs

```powershell
# Service stdout/stderr logs (NSSM)
Get-Content C:\Gerald\jarvis_manager\logs\service_stdout.log -Wait

# Gerald application logs
Get-Content C:\Gerald\jarvis_manager\logs\asr_service.log -Wait
Get-Content C:\Gerald\jarvis_manager\logs\llm_service.log -Wait
Get-Content C:\Gerald\jarvis_manager\logs\command_service.log -Wait

# Windows Event Log
Get-EventLog -LogName Application -Source GeraldManager -Newest 50
```

---

## Troubleshooting

### Service Won't Start

#### Check Service Status

```powershell
sc query GeraldManager
```

#### Check Service Configuration

```powershell
# Using NSSM
nssm dump GeraldManager

# Using sc
sc qc GeraldManager
```

#### Check Logs

```powershell
# Service logs
Get-Content C:\Gerald\jarvis_manager\logs\service_stderr.log

# Application logs
Get-Content C:\Gerald\jarvis_manager\logs\asr_service.log -Tail 50
```

#### Common Issues

**Issue**: "Service did not respond in a timely fashion"

**Solution**: Increase service timeout
```powershell
# Increase startup timeout to 2 minutes
nssm set GeraldManager AppStopMethodConsole 120000
```

**Issue**: "Access denied"

**Solution**: Run as Administrator
```powershell
# Run PowerShell as Administrator
Start-Process powershell -Verb RunAs
```

**Issue**: "Python not found"

**Solution**: Use full path to Python
```powershell
# Find Python path
Get-Command python | Select-Object -ExpandProperty Source

# Update service
nssm set GeraldManager Application "C:\Python310\python.exe"
```

### Service Runs But Doesn't Work

#### Check if Python Process is Running

```powershell
Get-Process python
```

#### Check Service Ports

```powershell
netstat -ano | findstr "8001 8002 8003"
```

#### Test Services Manually

```powershell
# Stop service
nssm stop GeraldManager

# Run manually
cd C:\Gerald\jarvis_manager
python run_gerald.py

# Check for errors in console output
```

#### Check Permissions

Service account needs access to:
- Gerald installation directory
- Microphone device
- User profile directories (for file operations)

### Service Crashes Repeatedly

#### Check Crash Logs

```powershell
Get-Content logs\service_stderr.log | Select-String "error" -Context 5
```

#### Disable Auto-Restart for Debugging

```powershell
# Disable restart on failure
nssm set GeraldManager AppExit Default Exit
sc failure GeraldManager reset= 0 actions= ""
```

#### Run in Console Mode

```powershell
# Stop service
nssm stop GeraldManager

# Run in console
python run_gerald.py --debug
```

---

## Uninstallation

### Remove Service (NSSM)

```powershell
# Stop service
nssm stop GeraldManager

# Remove service
nssm remove GeraldManager confirm

# Verify removal
sc query GeraldManager
```

### Remove Service (pywin32)

```powershell
# Stop and remove
python install_service.py stop
python install_service.py remove
```

### Remove Task Scheduler Task

```powershell
Unregister-ScheduledTask -TaskName "Gerald Desktop Manager" -Confirm:$false
```

### Cleanup

```powershell
# Remove logs
Remove-Item C:\Gerald\jarvis_manager\logs\service_*.log -Force

# Remove NSSM (optional)
Remove-Item C:\Tools\nssm-2.24 -Recurse -Force
```

---

## Best Practices

### Production Deployment

1. **Use NSSM**: Easiest and most reliable
2. **Enable Logging**: Configure stdout/stderr logging
3. **Set Auto-Restart**: Configure failure recovery
4. **Monitor Logs**: Regularly check service logs
5. **Use Service Account**: Don't run as Local System in production
6. **Test Restart**: Ensure service recovers from crashes
7. **Document Configuration**: Keep service config documented

### Development

1. **Use Console Mode**: Easier to see output and debug
2. **Use Task Scheduler**: For simple auto-start during development
3. **Keep Service for Testing**: Test as service before production deployment

### Security

1. **Least Privilege**: Run service with minimum required permissions
2. **Secure Credentials**: Use Windows Credential Manager for service account
3. **Audit Logs**: Enable logging and review regularly
4. **Update Regularly**: Keep Gerald and dependencies updated

---

## Quick Reference

### Service Commands Cheat Sheet

```powershell
# NSSM Commands
nssm install ServiceName Program Arguments
nssm start ServiceName
nssm stop ServiceName
nssm restart ServiceName
nssm remove ServiceName
nssm status ServiceName
nssm edit ServiceName       # GUI editor

# Windows SC Commands
sc create ServiceName binPath= "Path"
sc start ServiceName
sc stop ServiceName
sc delete ServiceName
sc query ServiceName
sc config ServiceName start= auto

# PowerShell Commands
Get-Service ServiceName
Start-Service ServiceName
Stop-Service ServiceName
Restart-Service ServiceName
Set-Service ServiceName -StartupType Automatic
```

---

## Additional Resources

- **NSSM Documentation**: https://nssm.cc/usage
- **Windows Services**: https://docs.microsoft.com/en-us/windows/win32/services
- **pywin32**: https://github.com/mhammond/pywin32

---

**Windows Service Guide Version**: 1.0.0
**Last Updated**: 2025-11-22
**Tested On**: Windows 10 (21H2), Windows 11 (22H2)
