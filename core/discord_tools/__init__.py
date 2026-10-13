
import os
import time
import json
import random
import string
import urllib.request
import urllib.error
import urllib.parse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

_DISCORD_API = "https://discord.com/api/v10"
_LITELLINK = "https://discord.com/api/v10/entitlements/gift-codes/{code}/redeemable"
_NITRO_CHARS = string.ascii_uppercase + string.digits
_NITRO_LENGTH = 16
_NITRO_PROMO_LENGTH = 24
_NITRO_WEBHOOK_URL = None
_NITRO_STOP = False
_NITOS_COUNT = 0
_NITOS_VALID = 0


def _api_request(token, endpoint, method="GET", body=None):
    req = urllib.request.Request(
        f"{_DISCORD_API}{endpoint}",
        data=json.dumps(body or {}).encode("utf-8") if body else None,
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
            data = resp.read().decode("utf-8", errors="ignore")
            return status, json.loads(data) if data else {}
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="ignore")
            return e.code, json.loads(body) if body else {}
        except Exception:
            return e.code, {}
    except Exception:
        return None, None


def get_token_info(token):
    status, data = _api_request(token, "/users/@me")
    if status == 200 and data:
        return {
            "id": data.get("id"),
            "username": data.get("username"),
            "discriminator": data.get("discriminator"),
            "avatar": data.get("avatar"),
            "banner": data.get("banner"),
            "accent_color": data.get("accent_color"),
            "locale": data.get("locale"),
            "email": data.get("email"),
            "verified": data.get("verified"),
            "flags": data.get("flags"),
            "premium_type": data.get("premium_type"),
            "mfa_enabled": data.get("mfa_enabled"),
            "phone": data.get("phone"),
        }
    return None


def check_token(token):
    info = get_token_info(token)
    if info:
        return True, info
    return False, None


def get_guild_info(invite_code):
    status, data = _api_request("", f"/invites/{invite_code}?with_counts=true")
    if status == 200 and data:
        guild = data.get("guild", {})
        return {
            "id": guild.get("id"),
            "name": guild.get("name"),
            "members": data.get("approximate_member_count"),
            "presence": data.get("approximate_presence_count"),
            "verification_level": guild.get("verification_level"),
            "nsfw": guild.get("nsfw"),
            "features": guild.get("features", []),
        }
    return None


def send_webhook(webhook_url, content=None, username=None, avatar_url=None):
    payload = {"content": content or ""}
    if username:
        payload["username"] = username
    if avatar_url:
        payload["avatar_url"] = avatar_url
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode()
    except Exception:
        return None


def delete_webhook(webhook_url):
    req = urllib.request.Request(
        webhook_url,
        headers={"User-Agent": "Mozilla/5.0"},
        method="DELETE",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode()
    except Exception:
        return None


def _check_nitro_code(code):
    global _NITOS_COUNT, _NITOS_VALID, _NITRO_STOP
    if _NITRO_STOP:
        return None
    url = _LITELLINK.format(code=code)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            status = resp.getcode()
            _NITOS_COUNT += 1
            if status == 200:
                _NITOS_VALID += 1
                return code, True
            return code, False
    except urllib.error.HTTPError as e:
        _NITOS_COUNT += 1
        if e.code == 200:
            _NITOS_VALID += 1
            return code, True
        return code, False
    except Exception:
        return None


def generate_nitro_code(promo=False):
    if promo:
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choice(chars) for _ in range(_NITRO_PROMO_LENGTH))
    return "".join(random.choice(_NITRO_CHARS) for _ in range(_NITRO_LENGTH))


def start_nitro_checker(threads=10, count=100, webhook_url=None, on_result=None):
    global _NITOS_COUNT, _NITOS_VALID, _NITRO_STOP, _NITRO_WEBHOOK_URL
    _NITOS_COUNT = 0
    _NITOS_VALID = 0
    _NITRO_STOP = False
    _NITRO_WEBHOOK_URL = webhook_url

    codes = [generate_nitro_code() for _ in range(count)]
    valid = []

    def worker(code):
        global _NITOS_COUNT, _NITOS_VALID
        if _NITRO_STOP:
            return None
        result = _check_nitro_code(code)
        if result and result[1]:
            valid.append(result[0])
            if on_result:
                on_result(result[0])
        return result

    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(worker, c): c for c in codes}
            for future in as_completed(futures):
                if _NITRO_STOP:
                    break
                try:
                    future.result()
                except Exception:
                    pass
    except KeyboardInterrupt:
        _NITRO_STOP = True

    return valid


def send_discord_log(webhook_url, content):
    if not webhook_url:
        return
    try:
        payload = json.dumps({"content": content}).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def create_channel(token, guild_id, name, type=0):
    body = {"name": name, "type": type}
    status, data = _api_request(token, f"/guilds/{guild_id}/channels", method="POST", body=body)
    return status == 200, data


def create_role(token, guild_id, name):
    body = {"name": name}
    status, data = _api_request(token, f"/guilds/{guild_id}/roles", method="POST", body=body)
    return status == 200, data


def get_guild_channels(token, guild_id):
    status, data = _api_request(token, f"/guilds/{guild_id}/channels")
    if status == 200 and data:
        return [c for c in data if c.get("type") == 0]
    return []


def get_guild_roles(token, guild_id):
    status, data = _api_request(token, f"/guilds/{guild_id}/roles")
    if status == 200 and data:
        return data
    return []


def clone_server(token, source_invite, dest_guild_id):
    source_info = get_guild_info(source_invite)
    if not source_info:
        print("[-] Could not fetch source server info.")
        return False
    source_guild_id = source_info.get("id")
    if not source_guild_id:
        print("[-] Invalid invite.")
        return False
    channels = get_guild_channels(token, source_guild_id)
    roles = get_guild_roles(token, source_guild_id)
    created_channels = []
    for ch in channels:
        name = ch.get("name", "channel")
        ok, data = create_channel(token, dest_guild_id, name, type=ch.get("type", 0))
        if ok:
            created_channels.append(data)
            print(f"[+] Created channel: {name}")
        else:
            print(f"[-] Failed to create channel: {name}")
    created_roles = []
    for role in roles:
        if role.get("managed") or role.get("default"):
            continue
        name = role.get("name", "role")
        ok, data = create_role(token, dest_guild_id, name)
        if ok:
            created_roles.append(data)
            print(f"[+] Created role: {name}")
        else:
            print(f"[-] Failed to create role: {name}")
    return True


def create_dm_channel(token, user_id):
    body = {"recipient_id": user_id}
    status, data = _api_request(token, "/users/@me/channels", method="POST", body=body)
    if status == 200 and data:
        return data.get("id")
    return None


def send_dm(token, channel_id, content):
    body = {"content": content}
    status, data = _api_request(token, f"/channels/{channel_id}/messages", method="POST", body=body)
    return status == 200


def mass_dm(token, user_ids, message):
    success = 0
    fail = 0
    for uid in user_ids:
        try:
            channel_id = create_dm_channel(token, uid)
            if channel_id:
                if send_dm(token, channel_id, message):
                    success += 1
                else:
                    fail += 1
            else:
                fail += 1
        except Exception:
            fail += 1
    print(f"\n[+] Mass DM complete. Success: {success}, Failed: {fail}")
    return success, fail
