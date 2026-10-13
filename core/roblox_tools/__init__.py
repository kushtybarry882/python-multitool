import os
import re
import json
import time
import random
import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from core.ui.console import Colors
except ImportError:
    class Colors:
        RED = '\033[91m'
        GREEN = '\033[92m'
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'

_BASE = "https://www.roblox.com"
_ROBLOX_API = "https://api.roblox.com"
_ROBLOX_USERS = "https://users.roblox.com/v1/users"
_ROBLOX_FRIENDS = "https://friends.roblox.com/v1/users"
_ROBLOX_GROUPS = "https://groups.roblox.com/v1"
_ROBLOX_GAMES = "https://games.roblox.com/v1"
_ROBLOX_THUMBS = "https://thumbnails.roblox.com/v1"
_ECON = "https://economy.roblox.com/v1/users"
_PRESENCE = "https://presence.roblox.com/v1/presence/users"
_ACCOUNT_SETTINGS = "https://accountsettings.roblox.com/v1"
_AUTH = "https://auth.roblox.com/v1"
_APIS = "https://apis.roblox.com/universes/v1"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def _get_user(user_id):
    try:
        r = requests.get(f"{_ROBLOX_USERS}/{user_id}", headers=_HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def _get_friends_count(user_id):
    try:
        r = requests.get(f"{_ROBLOX_FRIENDS}/{user_id}/friends/count", headers=_HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json().get("count", "None")
    except Exception:
        pass
    return "None"


def _get_follow_counts(user_id):
    followers = "None"
    following = "None"
    try:
        r = requests.get(f"{_ROBLOX_FRIENDS}/{user_id}/followers/count", headers=_HEADERS, timeout=10)
        if r.status_code == 200:
            followers = r.json().get("count", "None")
    except Exception:
        pass
    try:
        r = requests.get(f"{_ROBLOX_FRIENDS}/{user_id}/followings/count", headers=_HEADERS, timeout=10)
        if r.status_code == 200:
            following = r.json().get("count", "None")
    except Exception:
        pass
    return followers, following


def _get_groups_count(user_id):
    try:
        r = requests.get(f"{_ROBLOX_GROUPS}/users/{user_id}/groups/roles", headers=_HEADERS, timeout=10)
        if r.status_code == 200:
            return len(r.json().get("data", []))
    except Exception:
        pass
    return "None"


def _get_avatar(user_id):
    try:
        r = requests.get(
            f"{_ROBLOX_THUMBS}/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false",
            headers=_HEADERS,
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json().get("data", [{}])
            if data:
                return data[0].get("imageUrl", "None")
    except Exception:
        pass
    return "None"


def _get_presence(user_id):
    try:
        r = requests.post(
            f"{_PRESENCE}/users",
            json={"userIds": [user_id]},
            headers=_HEADERS,
            timeout=10,
        )
        if r.status_code == 200:
            presences = r.json().get("userPresences", [{}])
            if presences:
                pd = presences[0]
                types = {0: "Offline", 1: "Online", 2: "In-Game", 3: "In Studio"}
                presence = types.get(pd.get("userPresenceType", 0), "None")
                loc = pd.get("lastLocation", "")
                if loc:
                    presence += f" ({loc})"
                return presence
    except Exception:
        pass
    return "None"


def _get_username_history(user_id):
    names = []
    try:
        r = requests.get(
            f"{_ROBLOX_USERS}/{user_id}/username-history?limit=10&sortOrder=Desc",
            headers=_HEADERS,
            timeout=10,
        )
        if r.status_code == 200:
            names = [n.get("name", "") for n in r.json().get("data", []) if n.get("name")]
    except Exception:
        pass
    return names


def _format_date(created):
    if not created or created == "None":
        return "None"
    try:
        dt = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return created[:10] if created else "None"


def get_cookie_info(cookie):
    session = requests.Session()
    session.cookies[".ROBLOSECURITY"] = cookie
    session.headers.update(_HEADERS)

    try:
        r = session.get(f"{_ROBLOX_USERS}/authenticated", timeout=10)
    except Exception:
        return {"error": "Could not connect!"}
    if r.status_code != 200:
        return {"error": "Invalid or expired cookie!"}

    auth = r.json()
    user_id = auth.get("id")
    username = auth.get("name", "None")

    user = _get_user(user_id)
    robux = "None"
    try:
        eco = session.get(f"{_ECON}/{user_id}/currency", timeout=10).json()
        robux = eco.get("robux", "None")
    except Exception:
        pass

    friends_count = _get_friends_count(user_id)
    followers_count, following_count = _get_follow_counts(user_id)
    groups_count = _get_groups_count(user_id)
    avatar_url = _get_avatar(user_id)

    email_status = "None"
    try:
        settings = session.get(f"{_ACCOUNT_SETTINGS}/email", timeout=10).json()
        email_verified = settings.get("verified", False)
        email_addr = settings.get("emailAddress", "None")
        email_status = f"{email_addr} (Verified: {email_verified})"
    except Exception:
        pass

    pin_status = "None"
    try:
        pin = session.get(f"{_AUTH}/account/pin", timeout=10).json()
        pin_status = "Enabled" if pin.get("isEnabled", False) else "Disabled"
    except Exception:
        pass

    presence = _get_presence(user_id)
    prev_names = _get_username_history(user_id)
    created = _format_date(user.get("created"))

    return {
        "status": "Valid",
        "cookie": cookie[:30] + "..",
        "user_id": user_id,
        "username": username,
        "display_name": user.get("displayName", "None"),
        "bio": (user.get("description") or "None")[:100],
        "created": created,
        "banned": user.get("isBanned", False),
        "verified_badge": user.get("hasVerifiedBadge", False),
        "email": email_status,
        "pin": pin_status,
        "presence": presence,
        "robux": robux,
        "friends": friends_count,
        "followers": followers_count,
        "following": following_count,
        "groups": groups_count,
        "previous_usernames": ", ".join(prev_names) if prev_names else "None",
        "avatar": avatar_url,
        "profile": f"https://www.roblox.com/users/{user_id}/profile",
    }


def get_id_info(user_id):
    if not user_id or not str(user_id).isdigit():
        return {"error": "Invalid user ID."}

    try:
        r = requests.get(f"{_ROBLOX_USERS}/{user_id}", headers=_HEADERS, timeout=10)
    except Exception:
        return {"error": "Could not connect!"}
    if r.status_code != 200:
        return {"error": "User not found!"}

    data = r.json()
    username = data.get("name", "None")
    display_name = data.get("displayName", "None")
    description = (data.get("description") or "None")[:150]
    is_banned = data.get("isBanned", False)
    has_badge = data.get("hasVerifiedBadge", False)
    created = _format_date(data.get("created"))

    friends = _get_friends_count(user_id)
    followers, following = _get_follow_counts(user_id)
    groups_count = _get_groups_count(user_id)
    avatar_url = _get_avatar(user_id)
    prev_names = _get_username_history(user_id)

    return {
        "user_id": user_id,
        "username": username,
        "display_name": display_name,
        "bio": description,
        "created": created,
        "banned": is_banned,
        "verified_badge": has_badge,
        "friends": friends,
        "followers": followers,
        "following": following,
        "groups": groups_count,
        "previous_usernames": ", ".join(prev_names) if prev_names else "None",
        "avatar": avatar_url,
        "profile": f"https://www.roblox.com/users/{user_id}/profile",
    }


def get_username_info(username):
    if not username:
        return {"error": "Username required."}

    try:
        r = requests.post(
            f"{_ROBLOX_USERS}/users",
            json={"usernames": [username], "excludeBannedUsers": False},
            headers=_HEADERS,
            timeout=10,
        )
    except Exception:
        return {"error": "Could not connect!"}
    if r.status_code != 200:
        return {"error": "Could not fetch user!"}

    users = r.json().get("data", [])
    if not users:
        return {"error": "Username not found!"}

    user_id = users[0].get("id")
    user = _get_user(user_id)
    display_name = user.get("displayName", "None")
    description = (user.get("description") or "None")[:150]
    is_banned = user.get("isBanned", False)
    has_badge = user.get("hasVerifiedBadge", False)
    created = _format_date(user.get("created"))

    friends = _get_friends_count(user_id)
    followers, following = _get_follow_counts(user_id)
    groups_count = _get_groups_count(user_id)
    avatar_url = _get_avatar(user_id)
    presence = _get_presence(user_id)
    prev_names = _get_username_history(user_id)

    return {
        "user_id": user_id,
        "username": user.get("name", username),
        "display_name": display_name,
        "bio": description,
        "created": created,
        "banned": is_banned,
        "verified_badge": has_badge,
        "presence": presence,
        "friends": friends,
        "followers": followers,
        "following": following,
        "groups": groups_count,
        "previous_usernames": ", ".join(prev_names) if prev_names else "None",
        "avatar": avatar_url,
        "profile": f"https://www.roblox.com/users/{user_id}/profile",
    }


def get_group_info(group_id):
    if not group_id or not str(group_id).isdigit():
        return {"error": "Invalid group ID."}

    try:
        r = requests.get(f"{_ROBLOX_GROUPS}/groups/{group_id}", headers=_HEADERS, timeout=10)
    except Exception:
        return {"error": "Could not connect!"}
    if r.status_code != 200:
        return {"error": "Group not found!"}

    data = r.json()
    name = data.get("name", "None")
    description = (data.get("description") or "None")[:200]
    member_count = data.get("memberCount", "None")
    is_public = data.get("publicEntryAllowed", "None")
    is_locked = data.get("isLocked", False)
    is_verified = data.get("hasVerifiedBadge", False)
    shout = data.get("shout", {})
    owner = data.get("owner", {})
    owner_name = owner.get("username", "None") if owner else "No Owner"
    owner_display = owner.get("displayName", "None") if owner else "None"
    created = _format_date(data.get("created"))
    updated = _format_date(data.get("updated"))

    icon_url = "None"
    try:
        th = requests.get(
            f"{_ROBLOX_THUMBS}/groups/icons?groupIds={group_id}&size=420x420&format=Png&isCircular=false",
            headers=_HEADERS,
            timeout=10,
        ).json()
        icon_url = th.get("data", [{}])[0].get("imageUrl", "None")
    except Exception:
        pass

    roles = []
    try:
        rl = requests.get(f"{_ROBLOX_GROUPS}/groups/{group_id}/roles", headers=_HEADERS, timeout=10).json()
        roles = [(r.get("name", "None"), r.get("memberCount", 0), r.get("rank", 0)) for r in rl.get("roles", [])]
        roles.sort(key=lambda x: x[2], reverse=True)
    except Exception:
        pass

    result = {
        "group_id": group_id,
        "name": name,
        "description": description,
        "members": member_count,
        "public_entry": is_public,
        "locked": is_locked,
        "verified_badge": is_verified,
        "created": created,
        "updated": updated,
        "owner": f"{owner_name} ({owner_display})",
        "icon": icon_url,
        "group_url": f"https://www.roblox.com/groups/{group_id}",
        "shout": shout,
        "roles": roles,
    }
    return result


def get_game_info(universe_id=None, place_id=None):
    if not universe_id and not place_id:
        return {"error": "Universe ID or Place ID required."}

    if place_id and not universe_id:
        try:
            r = requests.get(f"{_APIS}/places/{place_id}/universe", headers=_HEADERS, timeout=10)
        except Exception:
            return {"error": "Could not connect!"}
        if r.status_code != 200:
            return {"error": "Could not resolve place id!"}
        universe_id = str(r.json().get("universeId", ""))
        if not universe_id:
            return {"error": "Could not resolve universe id!"}

    try:
        r = requests.get(f"{_ROBLOX_GAMES}/games?universeIds={universe_id}", headers=_HEADERS, timeout=10)
    except Exception:
        return {"error": "Could not connect!"}
    if r.status_code != 200:
        return {"error": "Game not found!"}

    games = r.json().get("data", [])
    if not games:
        return {"error": "No game data found!"}

    game = games[0]
    name = game.get("name", "None")
    description = (game.get("description") or "None")[:200]
    creator_name = game.get("creator", {}).get("name", "None")
    creator_type = game.get("creator", {}).get("type", "None")
    playing = game.get("playing", "None")
    visits = game.get("visits", "None")
    max_players = game.get("maxPlayers", "None")
    created = game.get("created", "None")
    updated = game.get("updated", "None")
    favorited = game.get("favoritedCount", "None")
    genre = game.get("genre", "None")
    price = game.get("price")
    root_place_id = game.get("rootPlaceId", "None")
    if created and created != "None":
        created = created[:10]
    if updated and updated != "None":
        updated = updated[:10]

    votes_up = "None"
    votes_down = "None"
    try:
        votes = requests.get(f"{_ROBLOX_GAMES}/votes?universeIds={universe_id}", headers=_HEADERS, timeout=10).json()
        vote_data = votes.get("data", [{}])[0]
        votes_up = vote_data.get("upVotes", "None")
        votes_down = vote_data.get("downVotes", "None")
    except Exception:
        pass

    thumb_url = "None"
    try:
        th = requests.get(
            f"{_ROBLOX_THUMBS}/games/icons?universeIds={universe_id}&size=512x512&format=Png&isCircular=false",
            headers=_HEADERS,
            timeout=10,
        ).json()
        thumb_url = th.get("data", [{}])[0].get("imageUrl", "None")
    except Exception:
        pass

    return {
        "universe_id": universe_id,
        "root_place_id": root_place_id,
        "name": name,
        "description": description,
        "creator": f"{creator_name} ({creator_type})",
        "genre": genre,
        "price": price if price else "Free",
        "created": created,
        "updated": updated,
        "playing": playing,
        "visits": visits,
        "max_players": max_players,
        "favorites": favorited,
        "upvotes": votes_up,
        "downvotes": votes_down,
        "thumbnail": thumb_url,
        "game_url": f"https://www.roblox.com/games/{root_place_id}",
    }
