# Multi-Toolkit Setup Guide

This guide covers setup instructions for the Python Multi-Utility Toolkit.

## Quick Setup

### Windows (Recommended)

Run `setup.bat` as Administrator:

```bash
setup\setup.bat
```

### Manual Setup

```bash
# Install Python dependencies
pip install -r setup\requirements.txt

# Run the toolkit
python mainframe.py
```

## What setup.bat Installs

- All Python dependencies from `requirements.txt`
- Impacket (`psexec.py`, `wmiexec.py`)
- Chocolatey package manager
- Nmap, Hashcat, Metasploit via Chocolatey
- Checks for Node.js/Vercel CLI (for tracker page)
- Checks for Go (Sherlock, PhoneInfoga)

## External Tools

| Tool | Purpose | Install Method |
|------|---------|----------------|
| Nmap | Port scanning | `choco install nmap` |
| Hashcat | Password auditing | `choco install hashcat` |
| Metasploit | Testing framework | `choco install metasploit` |
| Sherlock | Username lookup | `go install github.com/sherlock-project/sherlock@latest` |
| PhoneInfoga | Telecom lookup | `go install github.com/sundowndev/phoneinfoga@latest` |
| Vercel CLI | Tracker page deployment | `npm install -g vercel` |

## Troubleshooting

- **Python not found**: Download from https://python.org/downloads/
- **pip not found**: Run `python -m ensurepip --default-pip`
- **Module import errors**: Run `pip install -r setup\requirements.txt`
- **Nmap not found**: Install via `choco install nmap` or download from https://nmap.org/
- **Metasploit not found**: Install from https://www.metasploit.com/download

## Support

If you find this project useful, consider supporting development:

### Bitcoin
```
bc1quaqzqt8g6xv7r854wqm5wsn4z3mwu9arnece6q
```

## Tutorial

Setup and usage tutorials:
https://www.youtube.com/@kydn-iu5kd