#!/usr/bin/env python3
import os, sys, requests

BASE = "http://localhost:8000"


def generate_token():
    email = "marioh90@gmail.com" # os.getenv("MAPBIOMIAS_EMAIL")
    pwd = "xZyn$3*6Hh" #os.getenv("MAPBIOMIAS_PASSWORD")
    if not email or not pwd:
        print("Defina MAPBIOMIAS_EMAIL e MAPBIOMIAS_PASSWORD", file=sys.stderr)
        sys.exit(1)
    r = requests.post(f"{BASE}/token",
                      json={"email": email, "password": pwd})
    r.raise_for_status()
    return r.json()["token"]


def list_territories(token):
    h = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/territories/options", headers=h)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    token = generate_token()
    opts = list_territories(token)
    for cat in opts:
        print(f"{cat['categoryName']}:")
        for t in cat["territories"]:
            print(f"  {t['code']}  {t['name']}")
