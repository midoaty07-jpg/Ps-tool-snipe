from flask import Flask, jsonify, request, send_from_directory
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(**name**, static_folder=‘public’)

REGIONS = {
“مصر”:      {“code”: “en-eg”, “flag”: “🇪🇬”, “currency”: “EGP”},
“السعودية”: {“code”: “en-sa”, “flag”: “🇸🇦”, “currency”: “SAR”},
“الإمارات”: {“code”: “en-ae”, “flag”: “🇦🇪”, “currency”: “AED”},
“تركيا”:    {“code”: “tr-tr”, “flag”: “🇹🇷”, “currency”: “TRY”},
“أمريكا”:   {“code”: “en-us”, “flag”: “🇺🇸”, “currency”: “USD”},
“أرجنتين”:  {“code”: “es-ar”, “flag”: “🇦🇷”, “currency”: “ARS”},
“البرازيل”: {“code”: “pt-br”, “flag”: “🇧🇷”, “currency”: “BRL”},
}

HEADERS = {
“User-Agent”: “Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36”,
“Accept-Language”: “en-US,en;q=0.9”,
}

def search_game(game_name, region_code):
try:
search_url = f”https://store.playstation.com/en-us/search/{requests.utils.quote(game_name)}”
r = requests.get(search_url, headers=HEADERS, timeout=8)
soup = BeautifulSoup(r.text, “html.parser”)

```
    # Try to get first result concept ID
    links = soup.find_all("a", href=re.compile(r"/product/"))
    if not links:
        return None

    product_path = links[0]["href"]
    product_id = product_path.split("/product/")[-1].split("/")[0]
    return product_id
except:
    return None
```

def get_price_for_region(product_id, region_code):
try:
url = f”https://store.playstation.com/{region_code}/product/{product_id}”
r = requests.get(url, headers=HEADERS, timeout=8)
soup = BeautifulSoup(r.text, “html.parser”)

```
    # Look for price in meta or page
    price_tag = soup.find("span", {"data-qa": re.compile(r"price")})
    if price_tag:
        return price_tag.get_text(strip=True)

    # Fallback: search for price pattern in page text
    matches = re.findall(r'[\$£€]?\s*\d+[\.,]\d+\s*(?:EGP|SAR|AED|TRY|USD|ARS|BRL|EUR)?', r.text)
    if matches:
        return matches[0].strip()

    return None
except:
    return None
```

@app.route(”/api/prices”)
def prices():
game = request.args.get(“game”, “”).strip()
if not game:
return jsonify({“error”: “ادخل اسم اللعبة”}), 400

```
# Find product ID from US store
product_id = search_game(game, "en-us")
if not product_id:
    return jsonify({"error": f"مش لاقي لعبة بالاسم ده: {game}"}), 404

results = []
for country, info in REGIONS.items():
    price = get_price_for_region(product_id, info["code"])
    results.append({
        "country": country,
        "flag": info["flag"],
        "currency": info["currency"],
        "price": price or "غير متاح",
        "available": price is not None,
        "storeUrl": f"https://store.playstation.com/{info['code']}/product/{product_id}"
    })

available = [r for r in results if r["available"]]
return jsonify({
    "game": game,
    "productId": product_id,
    "prices": results,
    "cheapestCount": len(available)
})
```

@app.route(”/”, defaults={“path”: “”})
@app.route(”/<path:path>”)
def serve(path):
if path and os.path.exists(os.path.join(app.static_folder, path)):
return send_from_directory(app.static_folder, path)
return send_from_directory(app.static_folder, “index.html”)

if **name** == “**main**”:
port = int(os.environ.get(“PORT”, 3000))
app.run(host=“0.0.0.0”, port=port)
