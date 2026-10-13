import os
import re
import time
import random
import socket
import urllib.parse
import urllib.request
import urllib.error
import gzip
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import socks
except ImportError:
    socks = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from colorama import Fore, Style, Back, init
    init()
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = RESET = ''
    class Style:
        BRIGHT = RESET_ALL = ''
    class Back:
        RED = YELLOW = RESET = ''

PROXY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "free-proxy-list.txt")

DORK_SEARCH_ENGINES = {
    "duck": {
        "url": "https://lite.duckduckgo.com/lite/?q={query}&kl=wt-wt",
        "patterns": [
            r'href="((?:https?:)?//[^"]+)"',
            r'href="(https?://[^"]+)"',
        ],
        "decoder": None,
        "skip": ["duckduckgo.com", "lite.duckduckgo.com", "youtube.com", "facebook.com", "w3.org", "w3schools.com", "duck.co"],
    },
    "bing": {
        "url": "https://www.bing.com/search?q={query}&first=0&count=25",
        "patterns": [
            r'<cite[^>]*>(https?://[^<›\s]+)',
            r'<a\s+class="tilk"[^>]*href="([^"]+)"',
            r'<h2><a[^>]+href="([^"]+)"[^>]*>',
            r'<a\s+class="b_algo"[^>]*><h2><a[^>]+href="([^"]+)"',
        ],
        "decoder": "bing",
        "skip": ["bing.com", "microsoft.com", "go.microsoft.com", "w3.org"],
    },
    "brave": {
        "url": "https://search.brave.com/search?q={query}&source=web",
        "patterns": [
            r'<a\s+href="([^"]+)"[^>]*class="(?:h|result-header|snippet-title)"',
            r'<a class="(?:h|result-header|snippet-title)"\s+href="([^"]+)"',
            r'<a\s+href="(https?://[^"]+)"\s+rel="noopener"',
        ],
        "decoder": None,
        "skip": ["brave.com", "search.brave.com"],
    },
    "yahoo": {
        "url": "https://search.yahoo.com/search?p={query}&fr=yscf3&b=1",
        "patterns": [
            r'<a class="d-ib[^"]*"\s+href="([^"]+)"',
            r'<h3 class="title"[^>]*>\s*<a\s+href="([^"]+)"',
            r'<a\s+href="(https?://[^"]+RU=[^"]+)"',
        ],
        "decoder": "yahoo",
        "skip": ["yahoo.com", "yahooapis.com", "search.yahoo.com"],
    },
    "mojeek": {
        "url": "https://www.mojeek.com/search?q={query}",
        "patterns": [
            r'<a class="ob"\s+href="([^"]+)"',
            r'<a class="title"\s+href="([^"]+)"',
            r'<a\s+href="(https?://[^"]+)"[^>]*class="title"',
        ],
        "decoder": None,
        "skip": ["mojeek.com", "mojeek.co.uk"],
    },
    "ecosia": {
        "url": "https://www.ecosia.org/search?q={query}",
        "patterns": [
            r'<a class="result-title"\s+href="([^"]+)"',
            r'<a\s+href="([^"]+)"[^>]*class="result__title"',
            r'<a\s+data-test-id="result-link"\s+href="([^"]+)"',
        ],
        "decoder": None,
        "skip": ["ecosia.org"],
    },
    "startpage": {
        "url": "https://www.startpage.com/do/search?query={query}",
        "patterns": [
            r'<a class="w-gl__result-title result-link"\s+href="([^"]+)"',
            r'<a class="result-link"\s+href="([^"]+)"',
            r'<a\s+href="([^"]+)"\s+class="result-link"',
        ],
        "decoder": None,
        "skip": ["startpage.com", "startpage.nl"],
    },
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

PROXY_LIST = []
_proxy_lock = __import__("threading").Lock()


def _read_response(resp):
    data = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        data = gzip.decompress(data)
    return data.decode("utf-8", errors="ignore")


def _load_proxies(path=None):
    proxy_file = path or PROXY_FILE
    proxies = []
    try:
        if os.path.exists(proxy_file):
            with open(proxy_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("*"):
                        continue
                    if ":" not in line:
                        continue
                    if not line.startswith("socks") and not line.startswith("http"):
                        if line.endswith(":80") or line.endswith(":8080") or line.endswith(":3128"):
                            line = "http://" + line
                        else:
                            line = "socks4://" + line
                    proxies.append(line)
    except Exception:
        pass
    return proxies


def _get_proxy_rotator():
    global PROXY_LIST
    if not PROXY_LIST:
        with _proxy_lock:
            if not PROXY_LIST:
                PROXY_LIST = _load_proxies()
    if not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)


def _proxy_url_to_parts(proxy_url):
    clean = proxy_url.replace("socks4://", "").replace("socks5://", "").replace("http://", "")
    host, port = clean.rsplit(":", 1)
    return host, int(port)


def _get_proxy_socket(proxy_url=None):
    if not proxy_url or not socks:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        host, port = _proxy_url_to_parts(proxy_url)
        if proxy_url.startswith("socks5"):
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            sock.set_proxy(socks.PROXY_TYPE_SOCKS5, host, port)
            return sock
        else:
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            sock.set_proxy(socks.PROXY_TYPE_SOCKS4, host, port)
            return sock
    except Exception:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def _make_urllib_opener(proxy_url=None):
    if not proxy_url:
        return urllib.request.build_opener()
    if proxy_url.startswith("socks"):
        orig_socket = socket.socket
        try:
            sock = _get_proxy_socket(proxy_url)
            opener = urllib.request.build_opener()
            opener.addheaders = []
            return opener, orig_socket
        except Exception:
            return urllib.request.build_opener(), orig_socket
    else:
        proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
        return urllib.request.build_opener(proxy_handler), None


def load_dorks(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    except Exception:
        return []


def _clean_url(url):
    url = urllib.parse.unquote(url)
    parsed = urllib.parse.urlparse(url)
    if parsed.query:
        params = urllib.parse.parse_qs(parsed.query)
        for key in ("uddg", "url", "q", "target", "redirect"):
            if key in params:
                inner = params[key][0]
                if inner.startswith("http://") or inner.startswith("https://"):
                    return inner.rstrip("/")
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    if parsed.netloc:
        return url.rstrip("/")
    for sep in ["/", "&"]:
        if sep in url:
            url = url.rsplit(sep, 1)[0] + sep
    return url.rstrip("/")


def _bing_decode(raw):
    raw = raw.replace('&amp;', '&')
    m = re.search(r'[?&]u=a1([^&]+)', raw)
    if not m:
        return raw
    token = m.group(1)
    try:
        import base64 as b64
        padding = len(token) % 4
        if padding == 1:
            return raw
        elif padding == 2:
            token += '=='
        elif padding == 3:
            token += '='
        return b64.urlsafe_b64decode(token).decode('utf-8', errors='replace')
    except Exception:
        return raw


def _yahoo_decode(raw):
    if 'RU=' in raw:
        piece = raw.rsplit('RU=', 1)[1]
        piece = piece.split('/RK=', 1)[0]
        return urllib.parse.unquote(piece)
    return raw


def _decode_url(url, decoder_name):
    if decoder_name == 'bing':
        return _bing_decode(url)
    elif decoder_name == 'yahoo':
        return _yahoo_decode(url)
    return url


def _search_engine(dork, engine_name, max_results=15, use_proxies=False):
    engine = DORK_SEARCH_ENGINES.get(engine_name)
    if not engine:
        return []

    query = urllib.parse.quote(dork)
    url = engine["url"].format(query=query)
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    headers.update(DEFAULT_HEADERS)

    results = []
    patterns = engine.get("patterns", [engine.get("pattern", r'href="(https?://[^"]+)"')])
    decoder = engine.get("decoder")

    def _do_request(use_proxy, timeout=15):
        req = urllib.request.Request(url, headers=headers)
        if use_proxy:
            proxy_url = _get_proxy_rotator()
            if proxy_url:
                if proxy_url.startswith("socks"):
                    orig_socket = socket.socket
                    socket.socket = lambda *args, **kwargs: _get_proxy_socket(proxy_url)
                    try:
                        with urllib.request.urlopen(req, timeout=timeout) as resp:
                            return _read_response(resp)
                    finally:
                        socket.socket = orig_socket
                else:
                    proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
                    opener = urllib.request.build_opener(proxy_handler)
                    opener.addheaders = [(k, v) for k, v in headers.items()]
                    with opener.open(req, timeout=timeout) as resp:
                        return _read_response(resp)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return _read_response(resp)

    html = ""
    if use_proxies:
        for attempt in range(5):
            try:
                html = _do_request(True, timeout=15)
                if html:
                    break
            except Exception:
                continue
    if not html:
        try:
            html = _do_request(False, timeout=15)
        except Exception:
            return results

    try:
        raw_links = []
        for pat in patterns:
            raw_links = re.findall(pat, html)
            if raw_links:
                break
        for href in raw_links:
            href = _clean_url(href)
            if decoder:
                href = _decode_url(href, decoder)
            href = _clean_url(href)
            if not any(skip in href.lower() for skip in engine["skip"]):
                results.append(href)
                if len(results) >= max_results:
                    break
    except Exception:
        pass

    return results


def search_zombies(dork, engines, max_results_per_engine=15, use_proxies=False):
    found = []
    with ThreadPoolExecutor(max_workers=min(len(engines), len(engines))) as executor:
        futures = {
            executor.submit(_search_engine, dork, engine, max_results_per_engine, use_proxies): engine
            for engine in engines
        }
        for future in as_completed(futures):
            try:
                found.extend(future.result())
            except Exception:
                pass
    return found


def _is_alive(url, timeout=5, use_proxies=False):
    proxy_url = _get_proxy_rotator() if use_proxies else None
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    headers.update(DEFAULT_HEADERS)
    try:
        req = urllib.request.Request(url, method="HEAD", headers=headers)
        if proxy_url:
            if proxy_url.startswith("socks"):
                orig_socket = socket.socket
                socket.socket = lambda *args, **kwargs: _get_proxy_socket(proxy_url)
                try:
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        return resp.status in (200, 301, 302, 403, 401, 404)
                finally:
                    socket.socket = orig_socket
            else:
                proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
                opener = urllib.request.build_opener(proxy_handler)
                opener.addheaders = [(k, v) for k, v in headers.items()]
                with opener.open(req, timeout=timeout) as resp:
                    return resp.status in (200, 301, 302, 403, 401, 404)
        else:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status in (200, 301, 302, 403, 401, 404)
    except Exception:
        pass
    try:
        req = urllib.request.Request(url, method="GET", headers=headers)
        if proxy_url:
            if proxy_url.startswith("socks"):
                orig_socket = socket.socket
                socket.socket = lambda *args, **kwargs: _get_proxy_socket(proxy_url)
                try:
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        return True
                finally:
                    socket.socket = orig_socket
            else:
                proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
                opener = urllib.request.build_opener(proxy_handler)
                opener.addheaders = [(k, v) for k, v in headers.items()]
                with opener.open(req, timeout=timeout) as resp:
                    return True
        else:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return True
    except Exception:
        return False


def validate_zombie(url, use_proxies=False):
    try:
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        if not _is_alive(url, use_proxies=use_proxies):
            return False

        if 80 <= parsed.port <= 65535 or parsed.port is None:
            if parsed.port in (23, 2323, 22, 2222, 7547, 5555, 443):
                return True
            if parsed.port is None or parsed.port == 80 or parsed.port == 443 or parsed.port == 8080:
                return True

        ssrf_vulnerable = False
        test_url = url.rstrip("/") + "/"
        req = urllib.request.Request(test_url, method="GET")
        req.add_header("User-Agent", random.choice(USER_AGENTS))

        proxy_url = _get_proxy_rotator() if use_proxies else None
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        headers.update(DEFAULT_HEADERS)
        if proxy_url:
            if proxy_url.startswith("socks"):
                orig_socket = socket.socket
                socket.socket = lambda *args, **kwargs: _get_proxy_socket(proxy_url)
                try:
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        body = resp.read(1024).decode("utf-8", errors="ignore")
                        if any(sig in body.lower() for sig in ["login", "password", "admin", "username"]):
                            ssrf_vulnerable = True
                except Exception:
                    pass
                finally:
                    socket.socket = orig_socket
            else:
                proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
                opener = urllib.request.build_opener(proxy_handler)
                opener.addheaders = [(k, v) for k, v in headers.items()]
                try:
                    with opener.open(req, timeout=5) as resp:
                        body = resp.read(1024).decode("utf-8", errors="ignore")
                        if any(sig in body.lower() for sig in ["login", "password", "admin", "username"]):
                            ssrf_vulnerable = True
                except Exception:
                    pass
        else:
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    body = resp.read(1024).decode("utf-8", errors="ignore")
                    if any(sig in body.lower() for sig in ["login", "password", "admin", "username"]):
                        ssrf_vulnerable = True
            except Exception:
                pass

        return True
    except Exception:
        return False


def gather_zombies(dorks_file, zombies_file, max_zombies=50, engines=None, use_proxies=False):
    if engines is None:
        engines = list(DORK_SEARCH_ENGINES.keys())

    dorks = load_dorks(dorks_file)
    if not dorks:
        print(f"{Fore.RED}[!] No dorks found in {dorks_file}{Fore.RESET}")
        return []

    existing = set()
    if os.path.exists(zombies_file):
        with open(zombies_file, "r", encoding="utf-8", errors="ignore") as f:
            existing = {line.strip() for line in f if line.strip()}

    candidates = []
    seen = set()
    print(f"{Fore.CYAN}[*] Searching {len(dorks)} dorks across {len(engines)} engines" + (" via proxies" if use_proxies else "") + "...{Fore.RESET}")

    for dork in dorks:
        if len(candidates) >= max_zombies:
            break
        print(f"{Fore.YELLOW}[+] Dork: {dork}{Fore.RESET}")
        urls = search_zombies(dork, engines, use_proxies=use_proxies)
        for url in urls:
            if url in seen:
                continue
            seen.add(url)
            candidates.append(url)
            if len(candidates) % 5 == 0:
                try:
                    with open(zombies_file, "a", encoding="utf-8") as f:
                        for u in candidates[-5:]:
                            f.write(u + "\n")
                    print(f"{Fore.CYAN}[*] Auto-saved {len(candidates)} candidates so far.{Fore.RESET}")
                except Exception:
                    pass
            if len(candidates) >= max_zombies:
                break
        time.sleep(random.uniform(0.1, 0.5))

    print(f"\n{Fore.CYAN}[*] Validating {len(candidates)} candidates..." + (" via proxies" if use_proxies else "") + f"{Fore.RESET}")
    valid = []
    save_counter = 0
    max_workers = min(len(candidates), 50) if candidates else 50
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(validate_zombie, url, use_proxies=use_proxies): url for url in candidates}
        for future in as_completed(future_map):
            url = future_map[future]
            try:
                if future.result():
                    print(f"    {Fore.GREEN}[OK] {url}{Fore.RESET}")
                    if url not in existing:
                        valid.append(url)
                        existing.add(url)
                        save_counter += 1
                        if save_counter % 5 == 0:
                            try:
                                with open(zombies_file, "a", encoding="utf-8") as f:
                                    for u in valid[-5:]:
                                        f.write(u + "\n")
                                print(f"{Fore.CYAN}[*] Auto-saved {save_counter} verified zombies so far.{Fore.RESET}")
                            except Exception:
                                pass
                else:
                    print(f"    {Fore.RED}[FAIL] {url}{Fore.RESET}")
            except Exception:
                pass

    if valid:
        try:
            with open(zombies_file, "a", encoding="utf-8") as f:
                for url in valid:
                    f.write(url + "\n")
            print(f"\n{Fore.GREEN}[+] Saved {len(valid)} new zombies to {zombies_file}{Fore.RESET}")
        except Exception as e:
            print(f"\n{Fore.RED}[!] Failed to save zombies: {e}{Fore.RESET}")
    else:
        print(f"\n{Fore.YELLOW}[!] No new valid zombies found.{Fore.RESET}")

    return valid
