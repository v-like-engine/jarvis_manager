# Gerald Desktop Manager - Troubleshooting Guide

Common issues and solutions for Gerald Desktop Manager v1.0.0

## Table of Contents
1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Service Startup Issues](#service-startup-issues)
4. [Voice Recognition Problems](#voice-recognition-problems)
5. [Performance Issues](#performance-issues)
6. [Application Control Issues](#application-control-issues)
7. [Language Issues](#language-issues)
8. [Windows-Specific Issues](#windows-specific-issues)
9. [Error Messages](#error-messages)
10. [Getting Help](#getting-help)

---

## Quick Diagnostics

Before detailed troubleshooting, run these quick checks:

### Check Service Status

```bash
# Check if all services are running
curl http://localhost:8001/health  # ASR Service
curl http://localhost:8002/health  # LLM Service
curl http://localhost:8003/health  # Command Service
```

All should return `{"status": "healthy"}`

### Check Logs

```bash
# View recent errors
tail -n 50 logs/asr_service.log
tail -n 50 logs/llm_service.log
tail -n 50 logs/command_service.log
```

### Check System Resources

```bash
# Check Python processes
tasklist | findstr python

# Check CPU and memory
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"
```

---

## Installation Issues

### Issue: `pip install` fails with "error: Microsoft Visual C++ 14.0 is required"

**Symptoms**:
```
error: Microsoft Visual C++ 14.0 or greater is required.
Get it with "Microsoft C++ Build Tools"
```

**Solution 1** (Recommended):
1. Download Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Run installer
3. Restart terminal
4. Retry `pip install`

**Solution 2** (Use precompiled wheels):
```bash
pip install pipwin
pipwin install pyaudio
pipwin install dlib
```

---

### Issue: `pyaudio` installation fails

**Symptoms**:
```
ERROR: Could not build wheels for pyaudio
```

**Solution 1** (Pipwin):
```bash
pip install pipwin
pipwin install pyaudio
```

**Solution 2** (Download wheel):
1. Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Install: `pip install PyAudio‑0.2.13‑cp311‑cp311‑win_amd64.whl`

**Solution 3** (Use sounddevice instead):
Edit `services/asr_service/requirements.txt`:
```
# pyaudio>=0.2.13  # Comment out
sounddevice>=0.4.6  # Already present
```

---

### Issue: `dlib` installation fails

**Symptoms**:
```
ERROR: Could not build wheels for dlib
CMake must be installed
```

**Solution**:
```bash
pip install cmake
pip install dlib
```

If still fails, download precompiled wheel:
```bash
# Find matching wheel for your Python version
pip install dlib-19.24.0-cp311-cp311-win_amd64.whl
```

---

### Issue: Models fail to download

**Symptoms**:
```
Error: Connection timeout while downloading models
```

**Solutions**:

1. **Check internet connection**
2. **Disable VPN/proxy temporarily**
3. **Manual download**: See [INSTALLATION.md](INSTALLATION.md#manual-download-if-automated-fails)
4. **Increase timeout**:
   ```bash
   python setup_models.py --timeout 600  # 10 minutes
   ```
5. **Resume interrupted download**:
   ```bash
   python setup_models.py --resume
   ```

---

### Issue: "Python not found" error

**Symptoms**:
```
'python' is not recognized as an internal or external command
```

**Solution**:
1. Add Python to PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Edit "Path" under User variables
   - Add: `C:\Python311\` and `C:\Python311\Scripts\`
2. Or use `py` instead of `python`:
   ```bash
   py -m pip install -r requirements.txt
   ```

---

## Service Startup Issues

### Issue: "Port already in use" error

**Symptoms**:
```
ERROR: Port 8001 is already in use
```

**Solution 1** (Find and kill process):
```bash
# Find process using port
netstat -ano | findstr :8001

# Kill process (replace PID with actual number)
taskkill /PID 12345 /F
```

**Solution 2** (Change port):
Edit `config/main_config.yaml`:
```yaml
services:
  asr:
    port: 8011  # Changed from 8001
```

---

### Issue: Service crashes on startup

**Symptoms**:
```
Service crashed: [Errno 2] No such file or directory
```

**Solutions**:

1. **Check models are downloaded**:
   ```bash
   ls shared/models/asr/
   ls shared/models/llm/
   ls shared/models/face/
   ```
   If empty, run: `python setup_models.py`

2. **Check permissions**:
   ```bash
   # Run as administrator
   python run_gerald.py
   ```

3. **Check logs**:
   ```bash
   cat logs/asr_service.log | grep ERROR
   ```

4. **Verify Python version**:
   ```bash
   python --version  # Should be 3.10+
   ```

---

### Issue: LLM Service takes forever to start

**Symptoms**:
```
LLM Service starting... (hangs for 5+ minutes)
```

**Explanation**: Loading large LLM model (2-5GB) into memory takes time.

**Solutions**:

1. **Be patient**: First load can take 2-5 minutes
2. **Use smaller model**: Edit `config/main_config.yaml`:
   ```yaml
   llm:
     model: "gemma-2-2b"  # Smaller, faster
   ```
3. **Check disk space**: Ensure 10GB+ free
4. **Close other apps**: Free up memory

---

## Voice Recognition Problems

### Issue: Gerald doesn't hear me

**Symptoms**:
- No response when speaking
- No "beep" sound after wake word

**Solutions**:

1. **Check microphone is enabled**:
   - Settings → Privacy → Microphone
   - Enable "Allow apps to access microphone"
   - Enable for Python

2. **Check microphone volume**:
   - Right-click volume icon → Sounds → Recording
   - Check mic is not muted
   - Speak and verify levels move

3. **Test microphone**:
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```
   Your mic should be listed

4. **Increase VAD sensitivity**:
   Edit `config/main_config.yaml`:
   ```yaml
   asr:
     vad:
       threshold: 0.3  # Lower = more sensitive (default: 0.5)
   ```

5. **Reduce background noise**:
   - Turn off fans, music, TV
   - Position mic 6-12 inches from mouth

---

### Issue: Gerald misunderstands commands

**Symptoms**:
- Recognizes wrong words
- Gets app names wrong

**Solutions**:

1. **Speak more clearly**:
   - Enunciate words
   - Speak at normal pace (not too fast)
   - Avoid mumbling

2. **Check language detection**:
   ```bash
   # Manually set language
   curl -X POST http://localhost:8001/recognize \
     -d '{"audio_data":"...","language":"en"}'  # Force English
   ```

3. **Update ASR models**:
   ```bash
   python setup_models.py --update-asr
   ```

4. **Use exact app names**:
   - Instead of: "Open browser"
   - Say: "Open Chrome" or "Open Yandex Browser"

5. **Check logs for recognized text**:
   ```bash
   tail -f logs/asr_service.log | grep "Recognized:"
   ```

---

### Issue: TTS (Gerald's voice) not working

**Symptoms**:
- No sound from Gerald
- Errors in log: "TTS engine failed"

**Solutions**:

1. **Check speakers/headphones**:
   - Ensure not muted
   - Test with other audio

2. **Install Windows Media Feature Pack** (Windows N/KN only):
   - Settings → Apps → Optional features → Add "Media Feature Pack"

3. **Check TTS engine**:
   ```python
   import pyttsx3
   engine = pyttsx3.init()
   engine.say("Testing")
   engine.runAndWait()
   ```

4. **Change TTS engine**:
   Edit `config/main_config.yaml`:
   ```yaml
   asr:
     tts:
       engine: "silero"  # Instead of pyttsx3
   ```

---

## Performance Issues

### Issue: High CPU usage (>20% when idle)

**Symptoms**:
- Laptop fan spinning
- System sluggish
- Task Manager shows high Python CPU usage

**Solutions**:

1. **Reduce VAD processing frequency**:
   Edit `config/main_config.yaml`:
   ```yaml
   asr:
     vad:
       processing_interval_ms: 200  # Increase from 100ms
   ```

2. **Use smaller LLM model**:
   ```yaml
   llm:
     model: "gemma-2-2b"  # Instead of phi-3-mini
   ```

3. **Disable face recognition** (if not using):
   ```yaml
   asr:
     face_recognition:
       enabled: false
   ```

4. **Close other applications**

5. **Check for infinite loops**:
   ```bash
   tail -f logs/*.log
   ```
   Look for repeating error messages

---

### Issue: High memory usage (>4GB)

**Symptoms**:
- RAM usage keeps increasing
- "Out of memory" errors

**Solutions**:

1. **Restart Gerald** (clears memory leaks):
   ```bash
   # Say "Exit Gerald" then restart
   python run_gerald.py
   ```

2. **Use smaller models**:
   - Switch to gemma-2-2b LLM
   - Disable face/voice recognition if unused

3. **Limit conversation context**:
   Edit `config/main_config.yaml`:
   ```yaml
   llm:
     context:
       max_history: 3  # Reduce from 5
   ```

4. **Check for memory leaks**:
   ```bash
   python -m memory_profiler services/asr_service/src/main.py
   ```

---

### Issue: Slow response time (>5 seconds)

**Symptoms**:
- Long delay between command and execution
- Gerald takes forever to respond

**Solutions**:

1. **Check CPU usage**: Close other heavy apps

2. **Reduce LLM token limit**:
   ```yaml
   llm:
     inference:
       max_tokens: 50  # Reduce from 100
   ```

3. **Optimize LLM temperature**:
   ```yaml
   llm:
     inference:
       temperature: 0.5  # Lower = faster
   ```

4. **Use SSD instead of HDD** (for model storage)

5. **Upgrade hardware**:
   - Add more RAM (16GB recommended)
   - Better CPU (6+ cores)

---

## Application Control Issues

### Issue: "Application not found" error

**Symptoms**:
```
Gerald: "I can't find that application"
```

**Solutions**:

1. **Use exact app name**:
   ```bash
   # Check installed apps
   wmic product get name
   ```

2. **Enable fuzzy matching**:
   Edit `config/main_config.yaml`:
   ```yaml
   commands:
     apps:
       fuzzy_match_threshold: 60  # Lower = more lenient (default: 70)
   ```

3. **Check app is installed**:
   - Start menu → Search for app
   - If not found, install it first

4. **Add app to database manually**:
   ```python
   # Coming in v1.1: Custom app registry
   ```

---

### Issue: App launches but Gerald says it failed

**Symptoms**:
- App actually opens
- Gerald reports: "Failed to launch"

**Solution**:
This is a logging issue. The app launched successfully despite the message.

**Workaround**: Ignore error message if app actually opened.

**Fix**: Coming in v1.0.1

---

### Issue: Can't close running apps

**Symptoms**:
```
Gerald: "Application is not running"
(But it is running!)
```

**Solutions**:

1. **Use exact app name**:
   - "Close Chrome" (not "Close browser")

2. **Try force close**:
   ```bash
   curl -X POST http://localhost:8003/app/close \
     -d '{"app_name":"chrome","force_close":true}'
   ```

3. **Check running processes**:
   ```bash
   curl http://localhost:8003/app/list
   ```

---

## Language Issues

### Issue: Gerald speaks wrong language

**Symptoms**:
- I speak English, Gerald responds in Russian
- Or vice versa

**Solutions**:

1. **Manually set language**:
   - "Change language to English"
   - Or edit `config/main_config.yaml`:
     ```yaml
     app:
       default_language: "en"  # or "ru"
     ```

2. **Disable auto-detection**:
   ```yaml
   asr:
     language_detection:
       auto_detect: false
   ```

3. **Speak more clearly**: Auto-detection may misidentify accent

---

### Issue: Russian commands not recognized

**Symptoms**:
- Russian voice commands don't work
- English commands work fine

**Solutions**:

1. **Check Russian model is downloaded**:
   ```bash
   ls shared/models/asr/vosk-model-small-ru-0.22/
   ```
   If empty: `python setup_models.py`

2. **Force Russian language**:
   ```yaml
   asr:
     default_language: "ru"
   ```

3. **Test Russian model**:
   ```bash
   curl -X POST http://localhost:8001/recognize \
     -d '{"audio_data":"BASE64","language":"ru"}'
   ```

---

## Windows-Specific Issues

### Issue: "Access denied" errors

**Symptoms**:
```
ERROR: PermissionError: [WinError 5] Access is denied
```

**Solutions**:

1. **Run as Administrator**:
   - Right-click `run_gerald.bat` → Run as administrator

2. **Disable antivirus temporarily**: Some AVs block microphone access

3. **Check folder permissions**:
   - Right-click Gerald folder → Properties → Security
   - Ensure your user has "Full control"

---

### Issue: Windows Defender blocks Gerald

**Symptoms**:
- Windows Defender quarantines Python files
- "This app has been blocked" message

**Solutions**:

1. **Add exclusion**:
   - Windows Security → Virus & threat protection
   - Manage settings → Exclusions → Add folder
   - Add Gerald installation folder

2. **Allow through firewall**:
   - Windows Defender Firewall → Allow app
   - Add Python

---

### Issue: Gerald doesn't start with Windows

**Symptoms**:
- Auto-start enabled but doesn't work

**Solutions**:

1. **Check startup folder**:
   ```bash
   dir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
   ```
   `run_gerald.bat` should be there

2. **Manually add to startup**:
   - Press `Win+R` → `shell:startup`
   - Create shortcut to `run_gerald.bat`

3. **Check Task Scheduler**:
   - Task Scheduler → Task Scheduler Library
   - Look for "Gerald Desktop Manager"
   - Enable if disabled

---

## Error Messages

### "Model not found" error

**Cause**: AI models not downloaded

**Solution**:
```bash
python setup_models.py
```

---

### "Microphone access denied"

**Cause**: Windows privacy settings block mic

**Solution**:
1. Settings → Privacy → Microphone
2. Enable for Python/Terminal

---

### "Service crashed: [Errno 10048] Address already in use"

**Cause**: Port already in use by another service

**Solution**:
```bash
# Find and kill process on port 8001
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

---

### "CUDA out of memory"

**Cause**: GPU memory exhausted (shouldn't happen, Gerald uses CPU)

**Solution**:
```yaml
llm:
  device: "cpu"  # Force CPU
```

---

### "Cannot import name 'xyz'"

**Cause**: Missing dependency

**Solution**:
```bash
pip install -r services/asr_service/requirements.txt --upgrade
pip install -r services/llm_service/requirements.txt --upgrade
pip install -r services/command_service/requirements.txt --upgrade
```

---

## Performance Benchmarks

### Expected Performance

| Metric | Target | Acceptable |
|--------|--------|------------|
| CPU (idle) | <3% | <5% |
| CPU (active) | <30% | <50% |
| Memory | <2GB | <4GB |
| Response time | <1.5s | <2s |
| Startup time | <30s | <60s |

### Measuring Performance

```bash
# CPU and memory
python -c "import psutil; p = psutil.Process(); print(f'CPU: {p.cpu_percent()}%, Memory: {p.memory_info().rss/1024/1024:.0f}MB')"

# Response time
time curl -X POST http://localhost:8001/recognize -d '{"audio_data":"...","language":"en"}'
```

---

## Diagnostic Commands

### Collect System Info

```bash
# Create diagnostic report
python -m gerald_diagnostics > diagnostic_report.txt
```

This includes:
- System information
- Python version and packages
- Service status
- Recent logs
- Configuration
- Performance metrics

**Send this report when asking for help!**

---

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Search GitHub issues: `github.com/yourusername/gerald/issues`
3. Check logs: `logs/*.log`
4. Generate diagnostic report

### Where to Get Help

1. **GitHub Issues**: Report bugs and request features
   - https://github.com/yourusername/gerald-desktop-manager/issues

2. **Community Discord**: Ask questions and get support
   - discord.gg/gerald (link TBD)

3. **Documentation**: Read all docs
   - `docs/` folder

### Creating a Good Bug Report

Include:
1. **Gerald version**: `v1.0.0`
2. **OS**: Windows 10/11, build number
3. **Python version**: `python --version`
4. **What you tried**: Exact command or voice command
5. **What happened**: Error message or unexpected behavior
6. **What you expected**: Intended result
7. **Logs**: Relevant lines from `logs/*.log`
8. **Diagnostic report**: Output of `python -m gerald_diagnostics`

**Example**:
```
Title: Gerald doesn't recognize "Open Chrome" command

Environment:
- Gerald v1.0.0
- Windows 11 22H2
- Python 3.11.4

Steps to reproduce:
1. Say "Hey Gerald"
2. Say "Open Chrome"

Expected: Chrome launches
Actual: Gerald says "I don't understand"

Logs:
[ASR Service] Recognized: "open crone" (confidence: 0.6)

Diagnostic report attached.
```

---

## Known Issues

### v1.0.0 Known Limitations

1. **Windows Only**: No macOS/Linux support yet (planned v2.0)
2. **No GPU Acceleration**: LLM runs on CPU only (planned v1.2)
3. **Limited Languages**: Only English and Russian (planned: more languages v1.3)
4. **No Custom Commands**: Can't add custom voice commands (planned v1.1)
5. **Basic Music Control**: Only play/pause/next/previous (planned: advanced controls v1.2)

### Workarounds

See [CHANGELOG.md](CHANGELOG.md) for fixes in upcoming releases.

---

## FAQ

### Q: Can I use Gerald offline?
**A**: Yes! After initial setup, Gerald works 100% offline.

### Q: Does Gerald send my voice to the cloud?
**A**: No. All processing happens locally.

### Q: Why is Gerald using so much CPU?
**A**: See [High CPU usage](#issue-high-cpu-usage-20-when-idle)

### Q: Can I change Gerald's voice?
**A**: Currently only pitch/rate/volume. Custom voices planned for v1.1.

### Q: Does Gerald work on laptops?
**A**: Yes, but performance may be limited. 16GB RAM recommended.

---

## Still Need Help?

If your issue isn't covered here:

1. Create GitHub issue with diagnostic report
2. Join community Discord
3. Check for updates: `git pull origin main`

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0
