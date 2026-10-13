import json
import os

_PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'profiles')
os.makedirs(_PROFILES_DIR, exist_ok=True)


def _profile_path(name):
    return os.path.join(_PROFILES_DIR, f"{name}.json")


def list_profiles():
    profiles = []
    if os.path.isdir(_PROFILES_DIR):
        for f in os.listdir(_PROFILES_DIR):
            if f.endswith('.json'):
                profiles.append(f[:-5])
    return profiles


def save_profile(name, data):
    try:
        path = _profile_path(name)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def load_profile(name):
    try:
        path = _profile_path(name)
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def delete_profile(name):
    try:
        path = _profile_path(name)
        if os.path.exists(path):
            os.remove(path)
        return True
    except Exception:
        return False
