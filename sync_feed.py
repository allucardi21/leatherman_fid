import os
import hashlib
import requests
from lxml import etree

FEED_URL = os.environ["FEED_URL"]
LIMIT_ITEMS = int(os.environ.get("LIMIT_ITEMS", "20"))
OUT_FEED = os.environ.get("OUT_FEED", "feed.xml")
PAGES_BASE = os.environ["PAGES_BASE"].rstrip("/")  # https://allucardi21.github.io/leatherman_fid

IMG_DIR = "images"
os.makedirs(IMG_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0"}

def pick_ext(url: str) -> str:
    u = url.split("?")[0].lower()
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        if u.endswith(ext):
            return ext
    return ".jpg"

def stable_name(url: str) -> str:
    # стабільна назва по хешу (щоб не було дублів і проблем зі символами)
    h = hashlib.s
