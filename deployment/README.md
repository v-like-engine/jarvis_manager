# Gerald Desktop Manager - Deployment Package

This directory contains deployment-related files and scripts for Gerald Desktop Manager.

## Directory Structure

```
deployment/
├── README.md                    # This file
├── RELEASE_CHECKLIST.md         # Pre-release checklist
├── scripts/                     # Deployment scripts
│   ├── create_release.ps1      # Create release archive (Windows)
│   ├── install_service.py      # Install as Windows service
│   └── verify_installation.py  # Verify installation integrity
├── configs/                     # Production configurations
│   ├── production.yaml         # Production config example
│   └── .env.example           # Environment variables template
├── docs/                       # Deployment documentation
│   └── (symlinks to main docs/)
└── installers/                 # Installer packages (when created)
    └── (future: .msi, .exe installers)
```

## Files

### RELEASE_CHECKLIST.md

Comprehensive checklist for preparing and releasing new versions of Gerald.
Use this before every release to ensure nothing is missed.

**Key Sections**:
- Pre-Release Checklist (code quality, docs, features)
- Release Preparation (versioning, changelog, build)
- Publication (GitHub, announcements)
- Post-Release (monitoring, support)

### Scripts (Future)

#### create_release.ps1
PowerShell script to create release archives automatically.

#### install_service.py
Python script to install Gerald as a Windows service.

#### verify_installation.py
Script to verify installation integrity and configuration.

## Usage

### Preparing a Release

1. **Complete Development**:
   ```bash
   # Ensure all features complete
   # Run full test suite
   pytest tests/ -v
   ```

2. **Update Version**:
   - Edit `config/main_config.yaml`
   - Edit `README.md`
   - Edit `docs/CHANGELOG.md`

3. **Follow Release Checklist**:
   ```bash
   # Open and follow
   cat deployment/RELEASE_CHECKLIST.md
   ```

4. **Create Release Archive**:
   ```powershell
   # Manual method
   Compress-Archive -Path .\jarvis_manager\* -DestinationPath gerald-v1.0.0.zip
   ```

5. **Publish Release**:
   - Create GitHub release
   - Upload archive
   - Publish documentation

### Deploying to Production

See [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md) for complete deployment guide.

**Quick Steps**:
1. Download release archive
2. Extract to installation directory
3. Install dependencies: `pip install -r requirements.txt`
4. Download models: `python setup_models.py`
5. Configure: Edit `config/main_config.yaml`
6. Launch: `python start_gerald.py`

### Installing as Service

See [docs/WINDOWS_SERVICE.md](../docs/WINDOWS_SERVICE.md) for detailed instructions.

**Quick Method (NSSM)**:
```powershell
# Install NSSM
# Download from https://nssm.cc/

# Install service
nssm install GeraldManager "C:\Python310\python.exe" "C:\Gerald\jarvis_manager\run_gerald.py"

# Start service
nssm start GeraldManager
```

## Deployment Environments

### Development

**Purpose**: Active development and testing

**Configuration**:
- Debug logging enabled
- All services in development mode
- Test data and fixtures available

**Commands**:
```bash
python run_gerald.py --debug
```

### Staging

**Purpose**: Pre-production validation

**Configuration**:
- Production-like settings
- INFO level logging
- Real-world data

**Commands**:
```bash
python run_gerald.py --config config/staging.yaml
```

### Production

**Purpose**: End-user deployment

**Configuration**:
- Optimized settings
- WARNING level logging
- Error reporting enabled

**Commands**:
```bash
python start_gerald.py
# Or as service
nssm start GeraldManager
```

## Version Management

### Versioning Scheme

Gerald uses [Semantic Versioning](https://semver.org/):
- **Major** (X.0.0): Breaking changes
- **Minor** (1.X.0): New features, backwards compatible
- **Patch** (1.0.X): Bug fixes, backwards compatible

### Release Types

**Major Release** (v2.0.0):
- Significant architectural changes
- Breaking API changes
- Major new features

**Minor Release** (v1.1.0):
- New features
- Improvements
- Backwards compatible

**Patch Release** (v1.0.1):
- Bug fixes
- Security patches
- Minor improvements

**Hotfix Release** (v1.0.0-hotfix.1):
- Critical bug fixes
- Released between regular releases
- Merged to next regular release

## Support

### Documentation

- [Deployment Guide](../docs/DEPLOYMENT.md)
- [Windows Service Guide](../docs/WINDOWS_SERVICE.md)
- [System Requirements](../docs/SYSTEM_REQUIREMENTS.md)
- [Quick Start Guide](../docs/QUICK_START.md)
- [Troubleshooting](../docs/TROUBLESHOOTING.md)

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Check `docs/` directory
- **Logs**: Review `logs/` directory for errors

## Best Practices

### Before Release

- ✅ Run full test suite
- ✅ Update all documentation
- ✅ Test on clean Windows installation
- ✅ Verify all download links
- ✅ Check performance metrics
- ✅ Review security

### During Deployment

- ✅ Back up existing installation
- ✅ Test in staging first
- ✅ Monitor initial deployments
- ✅ Have rollback plan ready
- ✅ Communicate with users

### After Release

- ✅ Monitor for issues
- ✅ Respond to bug reports quickly
- ✅ Collect user feedback
- ✅ Plan next release
- ✅ Update documentation as needed

## Security

### Pre-Release Security Checks

- [ ] No hardcoded credentials
- [ ] No API keys in code
- [ ] Dependencies up to date
- [ ] No known vulnerabilities (bandit scan)
- [ ] Audit logs enabled
- [ ] Safe defaults in config

### Deployment Security

- [ ] Use service account (not admin)
- [ ] Enable logging
- [ ] Secure config files
- [ ] Review firewall rules
- [ ] Monitor logs for suspicious activity

## Troubleshooting Deployment

### Common Issues

**Issue**: Models fail to download

**Solution**:
```bash
# Manual download
python setup_models.py --force
```

**Issue**: Service won't start

**Solution**:
```powershell
# Check logs
Get-Content logs\asr_service.log -Tail 50

# Check ports
netstat -ano | findstr "8001 8002 8003"
```

**Issue**: Python not found

**Solution**:
```powershell
# Verify Python installation
python --version

# Add to PATH if needed
$env:Path += ";C:\Python310"
```

## Contact

For deployment issues or questions:

1. Check [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
2. Review logs in `logs/` directory
3. Create GitHub issue with:
   - System information
   - Error logs
   - Steps to reproduce

---

**Deployment Package Version**: 1.0.0
**Last Updated**: 2025-11-22
**Maintained By**: Agent 4 (Testing & Documentation)
