import requests
import os
import configparser
import argparse
from pathlib import Path
import json
from codecs import BOM_UTF8

SETTINGS_FILE = os.path.join(os.path.expanduser('~'), ".ctfd_settings")

config = configparser.ConfigParser()
session = requests.Session()

def lstrip_bom(val, bom=BOM_UTF8):
    if val.startswith(bom):
        return val[len(bom):]
    else:
        return val

def ensure_config_exists():
    if not os.path.exists(SETTINGS_FILE):
        config["integration"] = {"url": "", "admin_token": "" }
        store_config()

def store_config():
    with open(SETTINGS_FILE, "w+") as f:
        config.write(f)

def parse_arguments():
    stored_url = config.get("integration", "url")
    stored_token = config.get("integration", "admin_token")

    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, help="the access token for the API access, e.g. d41d8cd98f00b204e9800998ecf8427e", default=stored_token)
    parser.add_argument("--url", type=str, help="url to the instance, e.g. https://demo.ctfd.io. Without trailing slash", default=stored_url)
    parser.add_argument("path", type=str, help="directory to traverse for challenges")

    parsed = parser.parse_args()

    if parsed.token != stored_token or parsed.url != stored_url:
        config["integration"]["admin_token"] = parsed.token
        config["integration"]["url"] = parsed.url
        store_config()

    return parsed


def validate_challenge_info(challenge):
    valid = True
    keys = ["title","description","flag"]

    for key in keys:
        value = challenge.get(key)
        if value is None:
            print(f"Missing property '{key}'")
            valid = False
        elif not isinstance(value, str) or len(value) == 0:
            print(f"Invalid property '{key}', must be a string with some content")
            valid = False

    # Optional
    keys_arrays = ['downloadable_files', 'tags']
    for key in keys_arrays:
        value = challenge.get(key)
        if value is not None and not isinstance(value, list):
            print(f"Invalid property '{key}', must be an array!")
            valid = False
            
    # File paths
    if challenge.get("downloadable_files"):
        for f in challenge["downloadable_files"]:
            file_path = Path(challenge["directory"], f)
            if not file_path.exists():
                print(f"File {file_path} was not found")
                valid = False

    return valid

def get_local_challenges(directory):
    dirs = next(os.walk(directory))[1]
    ignore = [".git"]
    challenges = []

    for category in dirs:
        if category in ignore:
            continue

        challenge_dirs = next(os.walk(Path(directory, category)))[1]

        for dir in challenge_dirs:
            filename = Path(directory, category, dir, "ctfd.json")
            if not filename.exists():
                print(f"File "+ str(filename) + " does not exist. Ignoring for now!")
                continue
                
            with open(filename, "rb") as f:
                info = json.loads(lstrip_bom(f.read()))
                info["category"] = category
                info["directory"] = Path(directory, category, dir)
                challenges.append(info)

    return challenges

def get_ctfd_challenges(url, access_token):
    auth_headers = {"Authorization": f"Token {access_token}"}
    return requests.get(url + "/api/v1/challenges?view=admin", json=True, headers=auth_headers).json()["data"]

def create_challenge(challenge, directory, url, access_token):
    auth_headers = {"Authorization": f"Token {access_token}"}

    data = {
        "name": challenge["title"],
        "category": challenge["category"],
        "description": challenge["description"],
        "type": challenge.get("type", "dynamic"),
        "state": "hidden",
        "initial": 500,
        "decay": 15,
        "minimum": 100,
    }

    if challenge.get("connection_info"):
        data["connection_info"] = challenge.get("connection_info")

    r = session.post(url + "/api/v1/challenges", json=data, headers=auth_headers)
    r.raise_for_status()

    challenge_data = r.json()
    challenge_id = challenge_data["data"]["id"]

    # Create flags
    data = {"content": challenge["flag"], "type": "static", "challenge_id": challenge_id}
    r = session.post(url + f"/api/v1/flags", json=data, headers=auth_headers)
    r.raise_for_status()

    # Create tags
    if challenge.get("tags"):
        for tag in challenge["tags"]:
            r = session.post(
                url + f"/api/v1/tags", json={"challenge_id": challenge_id, "value": tag},
                headers=auth_headers
            )
            r.raise_for_status()

    # Upload files
    if challenge.get("downloadable_files") and challenge.get("directory"):
        files = []
        for f in challenge["downloadable_files"]:
            file_path = Path(challenge["directory"], f)
            if file_path.exists():
                file_object = ("file", file_path.open(mode="rb"))
                files.append(file_object)
            else:
                print(f"File {file_path} was not found", fg="red")
                raise Exception(f"File {file_path} was not found")

        data = {"challenge_id": challenge_id, "type": "challenge"}
        
        r = session.post(url + f"/api/v1/files", files=files, data=data, headers=auth_headers)
        r.raise_for_status()

    # Set challenge state
    #if challenge.get("state"):
    #    data = {"state": "hidden"}
    #    if challenge["state"] in ["hidden", "visible"]:
    #        data["state"] = challenge["state"]
    #
    #    r = session.patch(f"/api/v1/challenges/{challenge_id}", json=data)
    #    r.raise_for_status()

if __name__ == "__main__":
    ensure_config_exists()
    config.read(SETTINGS_FILE)

    settings = parse_arguments()

    if settings.url.endswith("/"):
        print("Instance url must not include a trailing slash!")
        exit(1)

    is_fully_configured = len(settings.token) > 0 and len(settings.url) > 0
    if is_fully_configured:
        existing_challenges = get_ctfd_challenges(settings.url, settings.token)
        existing_challenge_names = [c["name"] for c in existing_challenges]

        print("[+] Existing challenges:")
        [print(" - " + name) for name in existing_challenge_names]

    print("[+] Local challenges")
    challenges = get_local_challenges(settings.path)

    print("[+] Validating challenges")
    for chal in challenges:
        validate_challenge_info(chal)

    if not is_fully_configured:
        print("System is not configured with url and access_token. Skipping creation")
        exit(1)

    print("[+] New challenges")
    for chal in challenges:
        if chal["title"] not in existing_challenge_names:
            print("-", chal["title"])

    choice = input("Do you want to import the new challenges? (y/N) ").lower().strip()
    if choice == "y":
        print("[+] Creating challenges")
        for chal in challenges:
            if chal["title"] not in existing_challenge_names:
                create_challenge(chal, None, settings.url, settings.token)
