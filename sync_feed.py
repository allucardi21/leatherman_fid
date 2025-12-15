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
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return f"{h}{pick_ext(url)}"

def download_image(url: str, path: str):
    r = requests.get(url, timeout=60, headers=HEADERS, allow_redirects=True)
    r.raise_for_status()
    ct = (r.headers.get("Content-Type") or "").lower()
    if "image" not in ct:
        raise RuntimeError(f"Not an image response. Content-Type={ct} url={url}")
    with open(path, "wb") as f:
        f.write(r.content)

# 1) качаємо XML
resp = requests.get(FEED_URL, timeout=60, headers=HEADERS)
resp.raise_for_status()
root = etree.fromstring(resp.content)

# 2) беремо item'и і обрізаємо до LIMIT_ITEMS
all_items = root.xpath("//*[local-name()='item']")
items = all_items[:LIMIT_ITEMS]
for extra in all_items[LIMIT_ITEMS:]:
    parent = extra.getparent()
    if parent is not None:
        parent.remove(extra)

# 3) для кожного item переписуємо image_link (+ additional_image_link) і качаємо фото
def iter_image_nodes(item):
    for tag in ["image_link", "additional_image_link"]:
        for node in item.xpath(f".//*[local-name()='{tag}']"):
            yield node

downloaded = 0
for item in items:
    for node in iter_image_nodes(item):
        url = (node.text or "").strip()
        if not url:
            continue

        filename = stable_name(url)
        local_path = os.path.join(IMG_DIR, filename)

        if not os.path.exists(local_path):
            download_image(url, local_path)
            downloaded += 1

        node.text = f"{PAGES_BASE}/{IMG_DIR}/{filename}"

# 4) записуємо новий фід
out = etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
with open(OUT_FEED, "wb") as f:
    f.write(out)

print(f"OK: kept={len(items)} downloaded_new_images={downloaded} wrote={OUT_FEED}")
