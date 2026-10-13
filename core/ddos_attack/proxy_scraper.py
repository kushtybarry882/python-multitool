import os
import re
import time
import threading
import urllib.request
import urllib.error
import json

try:
    import socks
except ImportError:
    socks = None

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "free-proxy-list.txt")

SCRAPE_SOURCES = {
    "socks_proxy_net": {
        "url": "https://www.socks-proxy.net/",
        "format": "table",
        "proxy_type": "socks4",
    },
    "free_proxy_list_http": {
        "url": "https://www.free-proxy-list.net/",
        "format": "table",
        "proxy_type": "http",
    },
    "us_proxy": {
        "url": "https://www.us-proxy.org/",
        "format": "table",
        "proxy_type": "http",
    },
    "ssl_proxies": {
        "url": "https://www.sslproxies.org/",
        "format": "table",
        "proxy_type": "http",
    },
    "free-proxy-list_socks": {
        "url": "https://free-proxy-list.net/socks-proxy.html",
        "format": "table",
        "proxy_type": "socks4",
    },
    "proxyscrape_socks4_jsdelivr": {
        "url": "https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/socks4/data.txt",
        "format": "plain",
        "proxy_type": "socks4",
    },
    "proxyscrape_socks5_jsdelivr": {
        "url": "https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/socks5/data.txt",
        "format": "plain",
        "proxy_type": "socks5",
    },
    "proxifly_socks4_jsdelivr": {
        "url": "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt",
        "format": "plain",
        "proxy_type": "socks4",
    },
    "proxifly_socks5_jsdelivr": {
        "url": "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt",
        "format": "plain",
        "proxy_type": "socks5",
    },
    "syscallh00k_socks4": {
        "url": "https://raw.githubusercontent.com/Syscallh00k/proxy-list/main/socks4.txt",
        "format": "plain",
        "proxy_type": "socks4",
    },
    "syscallh00k_socks5": {
        "url": "https://raw.githubusercontent.com/Syscallh00k/proxy-list/main/socks5.txt",
        "format": "plain",
        "proxy_type": "socks5",
    },
    "syscallh00k_http": {
        "url": "https://raw.githubusercontent.com/Syscallh00k/proxy-list/main/http.txt",
        "format": "plain",
        "proxy_type": "http",
    },
    "thespeedx_socks4": {
        "url": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
        "format": "plain",
        "proxy_type": "socks4",
    },
    "thespeedx_socks5": {
        "url": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        "format": "plain",
        "proxy_type": "socks5",
    },
    "solispirit_socks4": {
        "url": "https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks4.txt",
        "format": "plain",
        "proxy_type": "socks4",
    },
    "solispirit_socks5": {
        "url": "https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks5.txt",
        "format": "plain",
        "proxy_type": "socks5",
    },
    "hproxy_socks4": {
        "url": "https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/socks4.txt",
        "format": "plain",
        "proxy_type": "socks4",
    },
    "hproxy_socks5": {
        "url": "https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/socks5.txt",
        "format": "plain",
        "proxy_type": "socks5",
    },
    "hproxy_http": {
        "url": "https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/http.txt",
        "format": "plain",
        "proxy_type": "http",
    },
    "hproxy_https": {
        "url": "https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/https.txt",
        "format": "plain",
        "proxy_type": "http",
    },
    "clarketm_readme": {
        "url": "https://raw.githubusercontent.com/clarketm/proxy-list/master/README.md",
        "format": "plain",
        "proxy_type": "http",
    },
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

lock = threading.Lock()
new_proxies = []


def _clean_entry(proxy_url, proxy_type):
    if not proxy_url or not proxy_type:
        return None
    ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', proxy_url)
    if not ip_match:
        return None
    ip = ip_match.group(1)
    port_match = re.search(r'(\d{2,5})', proxy_url.replace(ip, "", 1))
    if not port_match:
        return None
    port = port_match.group(1)
    return f"{ip}:{port}"


def _parse_json_source(data, proxy_type, json_ip_key="IP", json_port_key="PORT"):
    results = []
    try:
        if isinstance(data, str):
            parsed = json.loads(data)
        else:
            parsed = data
        if isinstance(parsed, dict):
            if "data" in parsed or "result" in parsed:
                items = parsed.get("data") or parsed.get("result", [])
            else:
                items = [parsed]
        else:
            items = parsed
        for item in items:
            if isinstance(item, str):
                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', item)
                port_match = re.search(r':(\d{2,5})', item)
                if ip_match and port_match:
                    results.append(f"{ip_match.group(1)}:{port_match.group(1)}")
            elif isinstance(item, dict):
                ip = item.get(json_ip_key, "")
                port = item.get(json_port_key, "")
                if ip and port:
                    results.append(f"{ip}:{port}")
    except Exception:
        pass
    return results


def _parse_table_source(html, proxy_type):
    results = []
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    for row in rows[1:]:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) >= 2:
            ip = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', cells[0])
            port = cells[1].strip()
            if ip and port:
                results.append(f"{ip.group(1)}:{port}")
    return results


def _download_source(name, config):
    url = config["url"]
    fmt = config.get("format", "plain")
    proxy_type = config.get("proxy_type", "socks4")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ProxyScraper/1.0)"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        if fmt == "json":
            proxies = _parse_json_source(raw, proxy_type,
                                        config.get("json_ip_key", "IP"),
                                        config.get("json_port_key", "PORT"))
        elif fmt == "table":
            proxies = _parse_table_source(raw, proxy_type)
        else:
            proxies = [l.strip() for l in raw.split("\n") if l.strip() and ":" in l]
        with lock:
            new_proxies.extend(proxies)
        print(f"  [{proxy_type}] {name}: scraped {len(proxies)} proxies")
    except urllib.error.HTTPError as e:
        print(f"  [{proxy_type}] {name}: HTTP error {e.code}")
    except Exception as e:
        print(f"  [{proxy_type}] {name}: {e}")


def scrape_proxies(output_file=None):
    outfile = output_file or OUTPUT_FILE
    existing = set()
    if os.path.exists(outfile):
        with open(outfile, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    existing.add(line)

    global new_proxies
    new_proxies = []

    threads = []
    for name, config in SCRAPE_SOURCES.items():
        t = threading.Thread(target=_download_source, args=(name, config), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join(timeout=45)

    all_proxies = list(existing | set(new_proxies))
    with open(outfile, "w", encoding="utf-8") as f:
        for proxy in sorted(all_proxies):
            f.write(proxy + "\n")
    print(f"\n[*] Proxy file written: {outfile}")
    print(f"[*] Total proxies: {len(all_proxies)} (was {len(existing)}, added {len(new_proxies)})")
    print(f"[*] New proxies: {len(new_proxies)}")
    return all_proxies


if __name__ == "__main__":
    scrape_proxies()
