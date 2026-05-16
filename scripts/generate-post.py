#!/usr/bin/env python3
"""
Tech Compare Pro - AI Content Generator v2
Generates tech product comparison articles using DeepSeek API,
with topic dedup, SEO optimization, and anti-AI-ism processing.

Usage:
    export DEEPSEEK_API_KEY='sk-your-key-here'
    export DEEPSEEK_BASE_URL='https://api.deepseek.com'  (optional)
    python3 scripts/generate-post.py

Dependencies: Python 3 stdlib only (os, sys, json, random, subprocess, urllib.request)
"""

import os
import sys
import json
import random
import subprocess
import urllib.request
import urllib.error
from datetime import date

# ---- Configuration ----
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(PROJECT_ROOT, "content", "posts")
USED_TOPICS_FILE = os.path.join(PROJECT_ROOT, "scripts", "used_topics.json")

API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-v4-flash"
MAX_TOKENS = 4000  # increased for longer, more detailed articles
RETRY_COUNT = 2
TEMPERATURE = 0.5   # lower = more consistent, less hallucination

# Topic pool: (title, category, tags[], keywords/description)
# WARNING: Used topics are tracked in used_topics.json. 
# If you add a new topic here, delete used_topics.json to reset tracking.
TOPIC_POOL = [
    # SSDs (P0 - our existing articles, write more variations)
    ("Samsung 990 Pro vs WD Black SN850X", "ssds",
     ["samsung", "wd", "ssd", "nvme", "storage", "comparison"],
     "NVMe SSD comparison: Samsung 990 Pro vs WD Black SN850X - speed, price, durability"),
    ("Crucial T705 vs Seagate FireCuda 540", "ssds",
     ["crucial", "seagate", "ssd", "nvme", "pcie-5", "storage"],
     "PCIe 5.0 SSD comparison: Crucial T705 vs Seagate FireCuda 540"),
    ("Samsung 870 EVO vs Crucial MX500", "ssds",
     ["samsung", "crucial", "ssd", "sata", "storage", "comparison"],
     "SATA SSD comparison: Samsung 870 EVO vs Crucial MX500 for budget builds"),
    ("WD Black SN850X vs Samsung 990 Pro for PS5", "ssds",
     ["wd", "samsung", "ssd", "nvme", "ps5", "gaming", "storage"],
     "PS5 SSD comparison: WD Black SN850X vs Samsung 990 Pro for gaming"),
    ("Sabrent Rocket 4 Plus vs Corsair MP600 Pro", "ssds",
     ["sabrent", "corsair", "ssd", "nvme", "storage", "comparison"],
     "PCIe 4.0 SSD comparison: Sabrent Rocket vs Corsair MP600 Pro"),
    # Laptops (P0)
    ("MacBook Air M4 vs MacBook Pro M4", "laptops",
     ["apple", "macbook", "air", "pro", "m4", "laptop", "comparison"],
     "MacBook comparison: MacBook Air M4 vs MacBook Pro M4 - which Apple Silicon laptop fits you"),
    ("Dell XPS 16 vs MacBook Pro M4", "laptops",
     ["dell", "apple", "xps", "macbook", "laptop", "comparison"],
     "Premium laptop comparison: Dell XPS 16 vs MacBook Pro M4"),
    ("ThinkPad X1 Carbon Gen 13 vs MacBook Air M4", "laptops",
     ["lenovo", "apple", "thinkpad", "macbook", "business", "laptop"],
     "Business ultrabook vs MacBook Air: ThinkPad X1 Carbon Gen 13 vs MacBook Air M4"),
    ("ASUS ROG Zephyrus G16 vs Razer Blade 16", "laptops",
     ["asus", "razer", "gaming", "laptop", "g16", "blade"],
     "Gaming laptop showdown: ASUS ROG Zephyrus G16 vs Razer Blade 16"),
    ("HP Spectre x360 vs Dell XPS 16", "laptops",
     ["hp", "dell", "spectre", "xps", "2-in-1", "laptop"],
     "Convertible laptop comparison: HP Spectre x360 vs Dell XPS 16"),
    ("Acer Swift Go 14 vs Lenovo Yoga 9i", "laptops",
     ["acer", "lenovo", "swift", "yoga", "ultrabook", "laptop"],
     "Mid-range ultrabook comparison: Acer Swift Go 14 vs Lenovo Yoga 9i"),
    # Smartphones
    ("iPhone 16 Pro Max vs Samsung Galaxy S25 Ultra", "smartphones",
     ["apple", "samsung", "iphone", "galaxy", "flagship", "smartphone"],
     "Flagship smartphone comparison: iPhone 16 Pro Max vs Samsung Galaxy S25 Ultra"),
    ("Google Pixel 10 Pro vs iPhone 16 Pro", "smartphones",
     ["google", "apple", "pixel", "iphone", "smartphone", "comparison"],
     "Pixel vs iPhone: Google Pixel 10 Pro vs iPhone 16 Pro camera and software"),
    ("OnePlus 13 vs Samsung Galaxy S25 Plus", "smartphones",
     ["oneplus", "samsung", "flagship", "smartphone", "comparison"],
     "Android flagship comparison: OnePlus 13 vs Samsung Galaxy S25 Plus"),
    ("Nothing Phone 3 vs Google Pixel 10", "smartphones",
     ["nothing", "google", "pixel", "smartphone", "comparison"],
     "Mid-range smartphone comparison: Nothing Phone 3 vs Google Pixel 10"),
    # Headphones (P1)
    ("Sony WH-1000XM6 vs Bose QuietComfort Ultra", "headphones",
     ["sony", "bose", "headphones", "noise-cancelling", "wireless"],
     "Premium ANC headphones comparison: Sony WH-1000XM6 vs Bose QuietComfort Ultra"),
    ("AirPods Max 2 vs Sony WH-1000XM6", "headphones",
     ["apple", "sony", "airpods", "headphones", "over-ear"],
     "Over-ear headphones comparison: AirPods Max 2 vs Sony WH-1000XM6"),
    ("Sennheiser Momentum 4 vs Sony WH-1000XM6", "headphones",
     ["sennheiser", "sony", "headphones", "premium", "wireless"],
     "Premium wireless headphones: Sennheiser Momentum 4 vs Sony WH-1000XM6"),
    # Earbuds (P1)
    ("AirPods Pro 3 vs Samsung Galaxy Buds 4 Pro", "earbuds",
     ["apple", "samsung", "airpods", "galaxy-buds", "earbuds", "tws"],
     "Premium TWS earbuds comparison: AirPods Pro 3 vs Samsung Galaxy Buds 4 Pro"),
    ("Sony WF-1000XM6 vs AirPods Pro 3", "earbuds",
     ["sony", "apple", "earbuds", "noise-cancelling", "tws"],
     "Noise-cancelling earbuds comparison: Sony WF-1000XM6 vs AirPods Pro 3"),
    ("Nothing Ear 3 vs OnePlus Buds Pro 3", "earbuds",
     ["nothing", "oneplus", "earbuds", "tws", "comparison"],
     "Mid-range TWS earbuds comparison: Nothing Ear 3 vs OnePlus Buds Pro 3"),
    # Tablets (P1)
    ("iPad Pro M4 vs Samsung Galaxy Tab S10 Ultra", "tablets",
     ["apple", "samsung", "ipad", "galaxy-tab", "tablet", "comparison"],
     "Premium tablet comparison: iPad Pro M4 vs Samsung Galaxy Tab S10 Ultra"),
    ("iPad Air M3 vs iPad Pro M4", "tablets",
     ["apple", "ipad", "air", "pro", "tablet"],
     "iPad comparison: iPad Air M3 vs iPad Pro M4 - which Apple tablet to buy"),
    ("Microsoft Surface Pro 11 vs iPad Pro M4", "tablets",
     ["microsoft", "apple", "surface", "ipad", "tablet", "comparison"],
     "Professional tablet comparison: Surface Pro 11 vs iPad Pro M4"),
    # Smartwatches (P1)
    ("Apple Watch Ultra 3 vs Samsung Galaxy Watch 8 Pro", "smartwatches",
     ["apple", "samsung", "watch", "smartwatch", "ultra", "galaxy"],
     "Premium smartwatch comparison: Apple Watch Ultra 3 vs Samsung Galaxy Watch 8 Pro"),
    ("Garmin Fenix 8 vs Apple Watch Ultra 3", "smartwatches",
     ["garmin", "apple", "fenix", "watch", "outdoor", "smartwatch"],
     "Outdoor smartwatch comparison: Garmin Fenix 8 vs Apple Watch Ultra 3"),
    ("Apple Watch Series 11 vs Samsung Galaxy Watch 8", "smartwatches",
     ["apple", "samsung", "watch", "smartwatch", "comparison"],
     "Everyday smartwatch comparison: Apple Watch Series 11 vs Samsung Galaxy Watch 8"),
    # Monitors (P1)
    ("LG UltraGear 32GS95UE vs Samsung Odyssey OLED G8", "monitors",
     ["lg", "samsung", "monitor", "gaming", "oled"],
     "Gaming monitor comparison: LG UltraGear vs Samsung Odyssey OLED G8"),
    ("Apple Studio Display 2 vs Dell UltraSharp U3224KB", "monitors",
     ["apple", "dell", "monitor", "display", "studio", "ultrasharp"],
     "Premium monitor comparison: Apple Studio Display 2 vs Dell UltraSharp"),
    ("Dell S2722QC vs LG 27UP850N", "monitors",
     ["dell", "lg", "monitor", "4k", "usb-c", "comparison"],
     "Budget 4K monitor comparison: Dell S2722QC vs LG 27UP850N for work and creative use"),
    # Gaming Consoles (P2)
    ("PlayStation 6 vs Xbox Series Y", "gaming-consoles",
     ["sony", "microsoft", "playstation", "xbox", "gaming", "console"],
     "Next-gen gaming console comparison: PS6 vs Xbox Series Y specs and games"),
    ("Nintendo Switch 2 vs Steam Deck 2", "gaming-consoles",
     ["nintendo", "valve", "switch", "steam-deck", "handheld", "gaming"],
     "Handheld gaming comparison: Nintendo Switch 2 vs Steam Deck 2"),
    ("ASUS ROG Ally 2 vs Steam Deck 2", "gaming-consoles",
     ["asus", "valve", "ally", "steam-deck", "handheld", "gaming"],
     "PC gaming handheld comparison: ASUS ROG Ally 2 vs Steam Deck 2"),
    # Cameras (P2)
    ("Sony A7 V vs Canon EOS R6 Mark III", "cameras",
     ["sony", "canon", "mirrorless", "camera", "full-frame"],
     "Full-frame mirrorless camera comparison: Sony A7 V vs Canon EOS R6 Mark III"),
    ("Fujifilm X-T6 vs Sony A6700", "cameras",
     ["fujifilm", "sony", "aps-c", "mirrorless", "camera"],
     "APS-C mirrorless camera comparison: Fujifilm X-T6 vs Sony A6700"),
    ("Nikon Z6 III vs Sony A7 V", "cameras",
     ["nikon", "sony", "mirrorless", "camera", "full-frame", "comparison"],
     "Full-frame mirrorless comparison: Nikon Z6 III vs Sony A7 V"),
    # Keyboards / Mice (P2)
    ("Logitech MX Mechanical Mini vs Keychron Q1 Pro", "keyboards",
     ["logitech", "keychron", "keyboard", "mechanical", "wireless"],
     "Mechanical keyboard comparison: Logitech MX Mechanical Mini vs Keychron Q1 Pro"),
    ("Logitech MX Master 3S vs Razer Basilisk V3 Pro", "mice",
     ["logitech", "razer", "mouse", "productivity", "gaming", "comparison"],
     "Premium mouse comparison: Logitech MX Master 3S vs Razer Basilisk V3 Pro"),
    # Chargers / Accessories (P2)
    ("Anker Prime GaN 100W vs Ugreen Nexode 100W", "chargers",
     ["anker", "ugreen", "charger", "gan", "usb-c", "comparison"],
     "GaN charger comparison: Anker Prime vs Ugreen Nexode 100W"),
    # Smart Home (NEW)
    ("Amazon Echo Show 10 vs Google Nest Hub Max", "smart-home",
     ["amazon", "google", "echo", "nest", "smart-display", "comparison"],
     "Smart display comparison: Amazon Echo Show 10 vs Google Nest Hub Max"),
    ("Ring Video Doorbell Pro 2 vs Google Nest Doorbell", "smart-home",
     ["ring", "google", "doorbell", "security", "smart-home", "comparison"],
     "Smart doorbell comparison: Ring Pro 2 vs Google Nest Doorbell"),
    ("Philips Hue vs LIFX Smart Bulbs", "smart-home",
     ["philips", "lifx", "smart-bulb", "lighting", "smart-home", "comparison"],
     "Smart lighting comparison: Philips Hue vs LIFX bulbs ecosystem"),
    ("Ecobee Premium vs Google Nest Learning Thermostat 4th Gen", "smart-home",
     ["ecobee", "google", "nest", "thermostat", "smart-home", "comparison"],
     "Smart thermostat comparison: Ecobee Premium vs Nest Learning Thermostat"),
    # Routers & WiFi (NEW)
    ("ASUS RT-BE96U vs TP-Link Archer BE800", "routers",
     ["asus", "tp-link", "router", "wifi-7", "mesh", "comparison"],
     "WiFi 7 router comparison: ASUS RT-BE96U vs TP-Link Archer BE800"),
    ("Netgear Orbi RBKE963 vs ASUS ZenWiFi BQ16 Pro", "routers",
     ["netgear", "asus", "mesh", "wifi", "router", "comparison"],
     "Mesh WiFi system comparison: Netgear Orbi vs ASUS ZenWiFi"),
    ("Eero Max 7 vs Google Nest WiFi Pro", "routers",
     ["eero", "google", "mesh", "wifi-7", "router", "comparison"],
     "Mesh router comparison: Eero Max 7 vs Google Nest WiFi Pro"),
    # Webcams (NEW)
    ("Logitech Brio 4K vs Insta360 Link 2", "webcams",
     ["logitech", "insta360", "webcam", "4k", "streaming", "comparison"],
     "4K webcam comparison: Logitech Brio vs Insta360 Link 2"),
    ("Obsbot Tiny 2 vs Opal C1", "webcams",
     ["obsbot", "opal", "webcam", "ai-tracking", "comparison"],
     "AI webcam comparison: Obsbot Tiny 2 vs Opal C1"),
    # Microphones (NEW)
    ("Shure MV7 Plus vs Rode PodMic USB", "microphones",
     ["shure", "rode", "microphone", "usb", "podcast", "comparison"],
     "USB podcast microphone comparison: Shure MV7 Plus vs Rode PodMic USB"),
    ("Blue Yeti X vs HyperX QuadCast S", "microphones",
     ["blue", "hyperx", "yeti", "quadcast", "microphone", "comparison"],
     "Streaming microphone comparison: Blue Yeti X vs HyperX QuadCast S"),
    # Streaming Devices (NEW)
    ("Apple TV 4K vs Nvidia Shield TV Pro", "streaming",
     ["apple", "nvidia", "streaming", "tv-box", "4k", "comparison"],
     "Streaming box comparison: Apple TV 4K vs Nvidia Shield TV Pro"),
    ("Roku Ultra vs Amazon Fire TV Cube", "streaming",
     ["roku", "amazon", "fire-tv", "streaming", "tv-box", "comparison"],
     "Streaming device comparison: Roku Ultra vs Amazon Fire TV Cube"),
    # Electric Scooters (NEW)
    ("Segway Ninebot Max G3 vs Niu KQi3 Pro", "escooters",
     ["segway", "niu", "escooter", "electric", "commute", "comparison"],
     "Electric scooter comparison: Segway Max G3 vs Niu KQi3 Pro for commuting"),
    ("Xiaomi Electric Scooter 5 Pro vs Segway F3 Pro", "escooters",
     ["xiaomi", "segway", "escooter", "budget", "comparison"],
     "Budget electric scooter comparison: Xiaomi 5 Pro vs Segway F3 Pro"),
    # More Keyboards (NEW)
    ("NuPhy Air75 V2 vs Lofree Flow", "keyboards",
     ["nuphy", "lofree", "keyboard", "low-profile", "mechanical", "comparison"],
     "Low-profile mechanical keyboard comparison: NuPhy Air75 V2 vs Lofree Flow"),
    ("Wooting 80HE vs Razer Huntsman V3 Pro", "keyboards",
     ["wooting", "razer", "keyboard", "hall-effect", "gaming", "comparison"],
     "Hall-effect gaming keyboard comparison: Wooting 80HE vs Razer Huntsman V3 Pro"),
    # More Mice (NEW)
    ("Lamzu Atlantis Mini vs Endgame Gear XM2we", "mice",
     ["lamzu", "endgame-gear", "mouse", "gaming", "ultralight", "comparison"],
     "Ultralight gaming mouse comparison: Lamzu Atlantis Mini vs EGG XM2we"),
    # Portable Power Stations (NEW)
    ("Anker Solix F2000 vs EcoFlow Delta 2 Max", "power-stations",
     ["anker", "ecoflow", "power-station", "portable", "outdoor", "comparison"],
     "Portable power station comparison: Anker Solix F2000 vs EcoFlow Delta 2 Max"),
    ("Jackery Explorer 2000 Pro vs Bluetti AC200L", "power-stations",
     ["jackery", "bluetti", "power-station", "solar", "comparison"],
     "Solar power station comparison: Jackery Explorer 2000 Pro vs Bluetti AC200L"),
]


def load_used_topics():
    """Load the set of already-used topic titles."""
    try:
        with open(USED_TOPICS_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("used", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_used_topics(used):
    """Save the set of used topic titles to file."""
    os.makedirs(os.path.dirname(USED_TOPICS_FILE), exist_ok=True)
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump({"used": sorted(used)}, f, indent=2)


def get_available_topics():
    """Return topics that haven't been written yet."""
    used = load_used_topics()
    available = [t for t in TOPIC_POOL if t[0] not in used]
    return available, used


def pick_topic():
    """Pick a random unused topic. If all used, reset tracking and start over."""
    available, used = get_available_topics()

    if not available:
        print("⚠️  All topics have been used. Resetting topic tracking for round 2.")
        save_used_topics(set())
        available = list(TOPIC_POOL)
        used = set()

    random.shuffle(available)
    chosen = available[0]
    return chosen, used


def get_env_or_exit(var_name):
    """Read a required environment variable or exit."""
    value = os.environ.get(var_name)
    if not value:
        print(f"ERROR: Environment variable {var_name} is not set.", file=sys.stderr)
        sys.exit(1)
    return value.strip()


def call_deepseek(prompt):
    """Call the DeepSeek API with the given prompt. Returns the response text."""
    api_key = os.environ["DEEPSEEK_API_KEY"]
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    url = f"{base_url}/v1/chat/completions"

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    last_error = None
    for attempt in range(1 + RETRY_COUNT):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            choices = result.get("choices", [])
            if not choices:
                raise RuntimeError(f"No choices in API response: {result}")
            content = choices[0].get("message", {}).get("content", "").strip()
            if not content:
                raise RuntimeError("Empty content in API response")
            return content
        except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError, RuntimeError) as e:
            last_error = e
            print(f"  API call attempt {attempt + 1} failed: {e}", file=sys.stderr)
            if attempt < RETRY_COUNT:
                print("  Retrying...", file=sys.stderr)

    print(f"ERROR: All API attempts failed. Last error: {last_error}", file=sys.stderr)
    sys.exit(1)


def slugify(title):
    """Convert a title to a URL-friendly slug."""
    s = title.lower().strip()
    s = s.replace(" vs ", "-vs-")
    s = s.replace("'", "")
    s = s.replace(":", "")
    s = s.replace("/", "-")
    result = []
    for ch in s:
        if ch.isalnum() or ch == "-":
            result.append(ch)
        else:
            result.append("-")
    s = "".join(result)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def build_prompt(title_text, category, tags, description_text, today):
    """Build a detailed generation prompt optimized for SEO and quality."""

    tags_str = ", ".join(tags)

    prompt = f"""You are a professional tech reviewer writing for a product comparison website. Write a comprehensive, factual comparison article.

Title: {title_text}
Category: {category}
Tags: {tags_str}

## Writing Guidelines

### Format
- Write 1000-1800 words in English
- Use proper markdown with ## headings for each section and ### for sub-sections
- Start immediately with value — no fluff introductions

### SEO Requirements
- Naturally include these keywords throughout: {description_text}
- Use the primary keyword phrase in the first paragraph
- Write a compelling meta description (under 160 chars) in the frontmatter
- Use descriptive H2 and H3 subheadings that include relevant keywords
- Write a minimum 400-character introductory section

### Structure Requirements
1. **Comparison Table**: A markdown table with 10-15 rows covering: price, specs, key features
2. **Design & Build Quality** section
3. **Performance** section with benchmarks where applicable
4. **Key Features** comparison
5. **Price & Value** analysis
6. **Verdict**: Bullet-point pros/cons for each product, then a clear recommendation
7. **FAQ**: 4-6 Q&A pairs in a natural Q&A format

### Anti-AI Guidelines (IMPORTANT)
- NEVER use phrases like: "as an AI", "as a language model", "I hope this helps", "feel free to", "in today's digital age", "let's dive in", "I've analyzed", "whether you're a..."
- Write in a direct, journalistic tone — like a tech magazine
- Use concrete numbers, specific model names, and real-world usage examples
- Include specific pricing (use current USD estimates)
- Vary sentence structure — avoid repetitive patterns
- Use contractions (it's, don't, can't, won't) for a natural, human voice
- Start paragraphs with specific claims, not generic phrases

### YAML Frontmatter
Include a proper YAML frontmatter with:
- title: "{title_text}"
- date: {today}
- draft: false
- tags: [{', '.join(f'"{t}"' for t in tags)}]
- categories: ["{category}"]
- description: "{description_text}"
- summary: "{description_text}"

Write the complete article now, delimited by --- for frontmatter."""

    return prompt


def call_deepseek_and_write(topic_entry, used_set):
    """Generate an article from a topic, write it to disk, return the file path."""
    title_text, category, tags, description_text = topic_entry
    today = date.today()
    slug = slugify(title_text)
    filename = f"{slug}.md"
    filepath = os.path.join(POSTS_DIR, filename)

    print(f"\n{'='*60}")
    print(f"Generating post: {title_text}")
    print(f"  Slug: {slug}")
    print(f"  Category: {category}")
    print(f"  File: {filepath}")
    print(f"{'='*60}")

    # Build prompt
    prompt = build_prompt(title_text, category, tags, description_text, today)

    # Call API
    article = call_deepseek(prompt)

    # Ensure the article has frontmatter
    tags_yaml = ", ".join(f'"{t}"' for t in tags)
    if not article.startswith("---"):
        article = f"""---
title: "{title_text}"
date: {today}
draft: false
tags: [{tags_yaml}]
categories: ["{category}"]
description: "{description_text}"
summary: "{description_text}"
---

{article}"""

    # Write the file
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(article)
        f.write("\n")

    print(f"  ✓ Article saved ({len(article)} chars)")

    # Mark topic as used
    used_set.add(title_text)
    save_used_topics(used_set)
    print(f"  ✓ Topic marked as used ({len(used_set)}/{len(TOPIC_POOL)} total)")

    return filepath


def git_commit_and_push(filepath):
    """Git add, commit, and push the new post."""
    print("\n--- Git operations ---")

    # git add
    rel_path = os.path.relpath(filepath, PROJECT_ROOT)
    result = subprocess.run(
        ["git", "add", rel_path],
        cwd=PROJECT_ROOT,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR: git add failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    print(f"  ✓ git add {rel_path}")

    # git commit
    title = os.path.basename(filepath).replace(".md", "").replace("-", " ").title()
    commit_msg = f"Add post: {title}"
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=PROJECT_ROOT,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        if "nothing to commit" in result.stderr or "nothing to commit" in result.stdout:
            print("  - Nothing to commit (already up to date)")
            return
        print(f"  ERROR: git commit failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    print(f"  ✓ git commit: {commit_msg}")

    # git push
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=PROJECT_ROOT,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR: git push failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    print(f"  ✓ git push to origin/main")

    print(f"\n  ✅ Published: {rel_path}")


def main():
    # Validate environment
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY environment variable is required.", file=sys.stderr)
        print("Usage: export DEEPSEEK_API_KEY='sk-your-key'", file=sys.stderr)
        print("       export DEEPSEEK_BASE_URL='https://api.deepseek.com' (optional)", file=sys.stderr)
        sys.exit(1)

    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    print(f"DeepSeek API endpoint: {base_url}/v1/chat/completions")
    print(f"Model: {MODEL}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Posts directory: {POSTS_DIR}")

    # Check topic availability
    available, used = get_available_topics()
    print(f"\nTopics: {len(available)} remaining / {len(TOPIC_POOL)} total")

    # Pick a topic
    topic, used_set = pick_topic()
    print(f"Selected topic: {topic[0]} [{topic[1]}]")

    # Generate the article
    filepath = call_deepseek_and_write(topic, used_set)

    # Git operations
    git_commit_and_push(filepath)

    # Summary
    remaining = len(TOPIC_POOL) - len(used_set) - 1  # -1 because we just added one
    print(f"\n{'='*60}")
    print(f"✅ DONE - Published: {os.path.basename(filepath)}")
    print(f"📊 Progress: {len(used_set)}/{len(TOPIC_POOL)} topics used ({remaining} remaining)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
