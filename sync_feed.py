import os
import requests
from lxml import etree

FEED_URL = os.environ["FEED_URL"]
LIMIT_ITEMS = int(os.environ.get("LIMIT_ITEMS", "20"))
OUT_FEED = os.environ.get("OUT_FEED", "feed.xml")

headers = {"User-Agent": "Mozilla/5.0"}

# 1) качаємо фід
resp = requests.get(FEED_URL, timeout=60, headers=headers)
resp.raise_for_status()
xml = resp.content

# 2) парсимо
root = etree.fromstring(xml)

all_items = root.xpath("//*[local-name()='item']")
keep = all_items[:LIMIT_ITEMS]
remove = all_items[LIMIT_ITEMS:]

# 3) вирізаємо зайві item з XML
for extra in remove:
    parent = extra.getparent()
    if parent is not None:
        parent.remove(extra)

# 4) записуємо результат
out = etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
with open(OUT_FEED, "wb") as f:
    f.write(out)

print(f"OK: kept {len(keep)} items, removed {len(remove)} items, wrote {OUT_FEED}")
