# Scrape — Ajio + Myntra Scrapy Spiders

Production-grade Scrapy project for scraping product listings and PDP data from Ajio and Myntra.

---

## Setup

```bash
git clone https://github.com/13-Joban/scrape.git
cd scrape
pip install -r requirements.txt
```

---

## Project Structure

```
scrape/
├── scraper/
│   ├── spiders/
│   │   ├── ajio/
│   │   │   ├── base.py
│   │   │   ├── products.py       # ajio_products spider
│   │   │   └── pdp.py            # ajio_pdp spider
│   │   └── myntra/
│   │       ├── base.py
│   │       ├── products.py       # myntra_products spider
│   │       └── pdp.py            # pdp spider
│   ├── items.py
│   ├── pipelines.py
│   └── settings.py
├── data/                         # output lives here (gitignored)
├── all_values.json               # Ajio category filters (343 entries)
├── men_filters.json              # Ajio men gender filters
├── women_filters.json            # Ajio women gender filters
├── requirements.txt
└── README.md
```

---

## Data Flow

```
Step 1: Run products spider  →  data/<retailer>/<date>/products/results.jsonl
Step 2: Run pdp spider       →  data/<retailer>/<date>/pdp/results.jsonl
```

Always run products first. PDP spider reads from products output.

---

## Ajio

### Step 1 — Scrape Product Listings

Categories come from `all_values.json` (343 entries). Each entry has:
```json
{
  "code": "men-kurtas",
  "name": "Men - Kurtas",
  "query": { "url": "/men-kurtas/c/830216001?q=..." },
  "count": 1200
}
```

**Run all categories:**
```bash
scrapy crawl ajio_products
```

**Run a specific category by name:**
```bash
scrapy crawl ajio_products -a category_name="Men - Kurtas"
scrapy crawl ajio_products -a category_name="Boys - Backpacks"
scrapy crawl ajio_products -a category_name="Men - 2P-Suit Sets"
```

> Category names must exactly match the `name` field in `all_values.json`.
> To see all available names: `cat all_values.json | python3 -c "import json,sys; [print(e['name']) for e in json.load(sys.stdin)]"`

**Output:** `data/ajio/<today>/products/results.jsonl`

Each line:
```json
{
  "product_id": "469461600_ivory",
  "pdp_url": "https://www.ajio.com/p/469461600_ivory",
  "category": "men-kurtas",
  "page": 0,
  "position": 1,
  "category_url": "https://www.ajio.com/api/category/830216001"
}
```

---

### Step 2 — Scrape PDPs

Reads from products output automatically.

**Run all PDPs:**
```bash
scrapy crawl ajio_pdp
```

**Run PDPs for a specific category:**
```bash
scrapy crawl ajio_pdp -a path="men-kurtas"
```

> `path` here is the `category` field (code) from products output, not the display name.

**Output:** `data/ajio/<today>/pdp/results.jsonl`

Each line includes:
```json
{
  "product_id": "469461600_ivory",
  "name": "Libas Men Kurta",
  "brand": "Libas",
  "mrp": 1999.0,
  "selling_price": 999.0,
  "color": "Ivory",
  "style_attrs": { "Fabric": "Cotton", "Fit": "Regular" },
  "sizes": [...],
  "all_images": [...],
  "breadcrumbs": ["Men", "Western Wear", "Kurtas"],
  "description": "..."
}
```

---

## Myntra

### Step 1 — Scrape Product Listings

Categories come from `categories.jsonl` (set in `CATEGORIES_FILE` in settings).

Each line in categories file:
```json
{ "path": ["Men", "Topwear", "Tshirts"], "url": "https://www.myntra.com/tshirts" }
```

**Run all categories:**
```bash
scrapy crawl myntra_products
```

**Run a specific category by path:**
```bash
scrapy crawl myntra_products -a path='["Men", "Topwear", "Tshirts"]'
scrapy crawl myntra_products -a path='["Women", "Western Wear", "Tops"]'
scrapy crawl myntra_products -a path='["Women", "Western Wear", "Dresses"]'
```

> Path must be a valid JSON array matching the `path` field in categories file exactly.

**Output:** `data/myntra/<today>/products/results.jsonl`

Each line:
```json
{
  "product_id": "12345678",
  "pdp_url": "https://www.myntra.com/tshirts/h&m/...",
  "category": ["Men", "Topwear", "Tshirts"],
  "page": 1,
  "position": 1,
  "category_url": "https://www.myntra.com/tshirts"
}
```

---

### Step 2 — Scrape PDPs

Reads from products output automatically.

**Run all PDPs:**
```bash
scrapy crawl pdp
```

**Run PDPs for a specific category path:**
```bash
scrapy crawl pdp -a path='["Men", "Topwear", "Tshirts"]'
scrapy crawl pdp -a path='["Women", "Western Wear", "Tops"]'
```

> `path` must exactly match the `category` field in products output.

**Run PDPs for a specific date's products:**
```bash
scrapy crawl pdp -a date=2025-04-10
```

**Output:** `data/myntra/<today>/pdp/results.jsonl`

Each line includes:
```json
{
  "product_id": "12345678",
  "name": "H&M Regular Fit T-Shirt",
  "brand": "H&M",
  "mrp": 799.0,
  "selling_price": 599.0,
  "color": "White",
  "features": ["100% Cotton", "Regular Fit", "Crew Neck"],
  "style_attrs": { "Sleeve Length": "Short Sleeves", "Pattern": "Solid" },
  "all_images": [...],
  "videos": [...],
  "breadcrumbs": [
    { "name": "Clothing", "url": "https://www.myntra.com/clothing", "position": 1 },
    { "name": "Men", "url": "https://www.myntra.com/men-clothing", "position": 2 },
    { "name": "Tshirts", "url": "https://www.myntra.com/tshirts", "position": 3 }
  ],
  "description": "..."
}
```

---

## Full Run — Both Retailers

```bash
# Day 1 — collect all listings
scrapy crawl ajio_products
scrapy crawl myntra_products

# Day 1 — collect all PDPs
scrapy crawl ajio_pdp
scrapy crawl pdp
```

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `File not found: data/.../products/results.jsonl` | Products spider not run yet | Run products spider first |
| `No entry found for category_name='...'` | Name doesn't match `all_values.json` | Check exact name spelling |
| `Found 0 products matching path` | Path doesn't match products output | Ensure path format matches exactly |
| `JSON parse failed` | Site blocked request | Check headers in base spider |
| `window.__myx not found` | Myntra returned error page | Rotate proxy or slow down requests |

---

## Requirements

```
Scrapy==2.11.2
requests==2.32.5
curl_cffi==0.15.0
redis==7.3.0
parsel==1.8.1
itemadapter==0.8.0
lxml==4.9.3
```

Install:
```bash
pip install -r requirements.txt
```