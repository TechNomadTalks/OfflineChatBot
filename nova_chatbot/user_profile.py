"""
User profile management for personalization.
"""

import os
import json
from .config import config


def get_profile_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "user_profile.json")


def load_profile():
    path = get_profile_path()
    if not os.path.exists(path):
        return {
            "username": None,
            "first_interaction": None,
            "preferences": {},
            "learned_info": {}
        }
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"username": None, "first_interaction": None, "preferences": {}, "learned_info": {}}


def save_profile(profile):
    path = get_profile_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)


def get_username():
    profile = load_profile()
    if profile.get("username"):
        return profile["username"]
    return config.get_visualizer_username()


def set_username(username):
    profile = load_profile()
    profile["username"] = username
    save_profile(profile)
    return username


def ask_for_username():
    print("\n[Nova] What's your name?")
    try:
        name = input("You: ").strip()
        if name:
            set_username(name)
            return name
    except:
        pass
    return get_username()


def update_preference(key, value):
    profile = load_profile()
    if "preferences" not in profile:
        profile["preferences"] = {}
    profile["preferences"][key] = value
    save_profile(profile)


def learn_info(key, value):
    profile = load_profile()
    if "learned_info" not in profile:
        profile["learned_info"] = {}
    profile["learned_info"][key] = value
    save_profile(profile)


def get_learned_info(key, default=None):
    profile = load_profile()
    return profile.get("learned_info", {}).get(key, default)


def get_user_context():
    profile = load_profile()
    username = profile.get("username")
    learned = profile.get("learned_info", {})
    return {
        "username": username,
        "preferences": profile.get("preferences", {}),
        "learned": learned
    }


def format_user_context():
    ctx = get_user_context()
    parts = []
    if ctx["username"]:
        parts.append(f"User's name is {ctx['username']}")
    for key, value in ctx["learned"].items():
        parts.append(f"{key}: {value}")
    if not parts:
        return ""
    return "User context: " + ". ".join(parts) + "."


def clear_profile():
    path = get_profile_path()
    if os.path.exists(path):
        os.remove(path)