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

    # === EXPANDED 2026-05-22: Batch-generated topics ===
    ("Canon EOS R5 Mark II vs Sony A1 II: The Ultimate High-Resolution Showdown", "cameras",
     ["mirrorless", "professional", "high-resolution", "8K video", "flagship"],
     "Compare the latest flagship mirrorless cameras from Canon and Sony for professional photographers and videographers."),
    ("Nikon Z8 vs Sony A7R V: Best for Landscape Photography", "cameras",
     ["landscape", "high-megapixel", "mirrorless", "Nikon", "Sony"],
     "A detailed comparison of the Nikon Z8 and Sony A7R V for landscape photographers seeking maximum detail and dynamic range."),
    ("Fujifilm GFX 100S II vs Hasselblad X2D 100C: Medium Format Battle", "cameras",
     ["medium-format", "high-resolution", "professional", "studio", "Fujifilm"],
     "Which medium format camera offers the best value and image quality for studio and commercial work."),
    ("Panasonic Lumix S5 IIX vs Sony A7 IV: Best Hybrid Camera Under $2500", "cameras",
     ["hybrid", "video", "photo", "under-2500", "full-frame"],
     "A head-to-head comparison of two popular full-frame hybrid cameras for content creators on a budget."),
    ("OM System OM-1 Mark II vs Fujifilm X-H2S: Best for Wildlife Photography", "cameras",
     ["wildlife", "action", "micro-four-thirds", "APS-C", "burst-speed"],
     "Comparing the top wildlife-focused cameras from OM System and Fujifilm, emphasizing speed and autofocus."),
    ("Leica Q3 vs Sony RX1R III: Premium Compact Cameras Compared", "cameras",
     ["compact", "full-frame", "luxury", "street-photography", "fixed-lens"],
     "A comparison of two high-end compact cameras for discerning photographers who prioritize portability and image quality."),
    ("Anker Prime GaN 67W vs Baseus GaN5 Pro 65W: Best Compact Charger", "chargers",
     ["GaN", "compact", "fast-charging", "USB-C", "travel"],
     "Which compact GaN charger offers the best power delivery and portability for everyday carry."),
    ("Samsung 45W Travel Adapter vs Spigen ArcStation 45W: Best for Galaxy Phones", "chargers",
     ["Samsung", "fast-charging", "USB-C", "travel", "compact"],
     "A comparison of two 45W chargers optimized for Samsung Galaxy smartphones."),
    ("Apple 35W Dual USB-C vs Anker 511 Charger: Best for iPhone and AirPods", "chargers",
     ["Apple", "dual-port", "travel", "iPhone", "compact"],
     "Which dual-port charger is the best choice for charging an iPhone and AirPods simultaneously."),
    ("UGREEN Nexode 200W vs Anker Prime GaN 200W: Desktop Charging Hub", "chargers",
     ["desktop", "high-wattage", "multi-port", "GaN", "workstation"],
     "A comparison of two high-wattage desktop chargers for powering multiple devices at once."),
    ("Belkin BoostCharge Pro 60W vs Anker PowerPort III 60W: Best for MacBooks", "chargers",
     ["MacBook", "USB-C", "60W", "fast-charging", "reliable"],
     "Which 60W charger is the most reliable and efficient for charging a MacBook Air or Pro."),
    ("Mophie Speedport 120 vs Anker Prime GaN 120W: Best for Road Warriors", "chargers",
     ["high-wattage", "travel", "GaN", "multi-device", "durable"],
     "A comparison of two powerful GaN chargers designed for travelers with multiple devices."),
    ("Samsung Galaxy Buds 3 Pro vs Google Pixel Buds Pro 2: Best for Android", "earbuds",
     ["Android", "noise-canceling", "wireless", "Samsung", "Google"],
     "Which premium earbuds offer the best integration and audio quality for Android users."),
    ("Jabra Elite 10 Gen 2 vs Sony WF-1000XM6: Best for Calls", "earbuds",
     ["calls", "noise-canceling", "microphone", "wireless", "premium"],
     "A comparison focusing on call quality and microphone performance in two top-tier earbuds."),
    ("Nothing Ear 2 vs OnePlus Buds 3: Best Mid-Range Earbuds", "earbuds",
     ["mid-range", "wireless", "design", "value", "transparent"],
     "Which stylish mid-range earbuds offer the best combination of features and price."),
    ("Beats Fit Pro vs Powerbeats Pro 2: Best for Workouts", "earbuds",
     ["fitness", "workout", "secure-fit", "Beats", "Apple"],
     "A comparison of Beats' fitness-focused earbuds for active users."),
    ("Sennheiser Momentum True Wireless 4 vs Bowers & Wilkins Pi8: Audiophile's Choice", "earbuds",
     ["audiophile", "sound-quality", "premium", "wireless", "high-fidelity"],
     "Which high-end earbuds deliver the best sound quality for discerning listeners."),
    ("Anker Soundcore Liberty 4 Pro vs Sony WF-1000XM6: Best Under $200", "earbuds",
     ["value", "noise-canceling", "under-200", "wireless", "Anker"],
     "A comparison of two feature-rich earbuds that offer excellent performance without breaking the bank."),
    ("Segway Ninebot Max G2 vs Niu KQi3 Max: Best for Commuters", "escooters",
     ["commuter", "long-range", "durable", "Segway", "Niu"],
     "Which electric scooter offers the best range and ride quality for daily commuting."),
    ("Apollo City Pro vs Vsett 10+: Best High-Performance Scooter", "escooters",
     ["high-performance", "speed", "range", "premium", "off-road"],
     "A comparison of two powerful electric scooters for enthusiasts seeking speed and range."),
    ("Unagi Model One Voyager vs Fluid Mosquito: Best Ultra-Portable Scooter", "escooters",
     ["portable", "lightweight", "urban", "foldable", "design"],
     "Which ultra-portable scooter is the best choice for last-mile travel and city dwellers."),
    ("Inokim Light 2 vs Glion Dolly: Best Budget Scooter", "escooters",
     ["budget", "affordable", "commuter", "lightweight", "reliable"],
     "A comparison of two affordable electric scooters for budget-conscious riders."),
    ("Dualtron Thunder 3 vs Kaabo Wolf King GT Pro: King of Speed", "escooters",
     ["speed", "powerful", "off-road", "dual-motor", "flagship"],
     "Which high-speed electric scooter reigns supreme for adrenaline seekers."),
    ("Segway Ninebot F40 vs Xiaomi Mi Electric Scooter 4 Pro: Best Entry-Level", "escooters",
     ["entry-level", "affordable", "reliable", "Segway", "Xiaomi"],
     "A comparison of two popular entry-level scooters for new riders."),
    ("Nintendo Switch 2 vs ASUS ROG Ally: Best Handheld for Gamers", "gaming-consoles",
     ["handheld", "portable", "Nintendo", "ASUS", "gaming"],
     "Which handheld gaming device offers the best library and performance for on-the-go play."),
    ("PlayStation 5 Pro vs Xbox Series X: 4K Gaming Powerhouse", "gaming-consoles",
     ["4K", "console", "Sony", "Microsoft", "performance"],
     "A comparison of the most powerful consoles from Sony and Microsoft for 4K gaming."),
    ("Steam Deck OLED vs ASUS ROG Ally X: Best PC Handheld", "gaming-consoles",
     ["PC-gaming", "handheld", "Steam", "ASUS", "OLED"],
     "Which PC gaming handheld offers the best battery life and screen quality."),
    ("Meta Quest 3 vs PlayStation VR2: Best VR Gaming Experience", "gaming-consoles",
     ["VR", "virtual-reality", "Meta", "PlayStation", "immersive"],
     "A comparison of the leading VR headsets for gaming and immersive experiences."),
    ("Xbox Series S vs Nintendo Switch 2: Best Budget Console", "gaming-consoles",
     ["budget", "entry-level", "Microsoft", "Nintendo", "value"],
     "Which affordable console offers the best value for casual and family gamers."),
    ("PlayStation Portal vs Logitech G Cloud: Best for Remote Play", "gaming-consoles",
     ["remote-play", "cloud-gaming", "handheld", "streaming", "Sony"],
     "A comparison of dedicated devices for streaming games from your console or the cloud."),
    ("Bose QuietComfort Earbuds II vs Sony WF-1000XM6: Best Noise Canceling", "headphones",
     ["noise-canceling", "wireless", "premium", "Bose", "Sony"],
     "Which earbuds offer the best active noise cancellation for travel and work."),
    ("Apple AirPods Max 2 vs Bose QuietComfort Ultra Headphones: Over-Ear Battle", "headphones",
     ["over-ear", "premium", "Apple", "Bose", "noise-canceling"],
     "A comparison of the top over-ear noise-canceling headphones from Apple and Bose."),
    ("Sennheiser Momentum 4 vs Sony WH-1000XM6: Best for Sound Quality", "headphones",
     ["sound-quality", "audiophile", "wireless", "Sennheiser", "Sony"],
     "Which wireless headphones deliver superior audio fidelity for music lovers."),
    ("Focal Bathys vs Bowers & Wilkins Px8: Luxury Wireless Headphones", "headphones",
     ["luxury", "high-fidelity", "wireless", "Focal", "Bowers-Wilkins"],
     "A comparison of two premium wireless headphones for discerning audiophiles."),
    ("Sony WH-1000XM6 vs Sennheiser Momentum 4: Best for Travel", "headphones",
     ["travel", "noise-canceling", "comfort", "battery-life", "Sony"],
     "Which headphones are the best companion for long flights and commutes."),
    ("Beats Studio Pro vs Sony WH-1000XM6: Best for Apple Users", "headphones",
     ["Apple", "Beats", "Sony", "noise-canceling", "ecosystem"],
     "A comparison of two popular headphones for users deeply integrated into the Apple ecosystem."),
    ("Keychron V1 vs Epomaker TH80 Pro: Best Budget Mechanical Keyboard", "keyboards",
     ["mechanical", "budget", "hot-swappable", "Keychron", "Epomaker"],
     "Which affordable mechanical keyboard offers the best customization and typing experience."),
    ("Razer Huntsman Mini vs Ducky One 3 Mini: Best 60% Keyboard", "keyboards",
     ["60-percent", "compact", "gaming", "Razer", "Ducky"],
     "A comparison of two popular 60% keyboards for gamers and minimalists."),
    ("Logitech G Pro X TKL vs SteelSeries Apex Pro TKL: Best for Esports", "keyboards",
     ["esports", "gaming", "TKL", "Logitech", "SteelSeries"],
     "Which tenkeyless keyboard offers the fastest response and best features for competitive gaming."),
    ("NuPhy Air75 V2 vs Keychron K3 Pro: Best Low-Profile Mechanical", "keyboards",
     ["low-profile", "mechanical", "portable", "wireless", "NuPhy"],
     "A comparison of two slim mechanical keyboards for productivity and portability."),
    ("Wooting 60HE+ vs Razer Huntsman V3 Pro Mini: Best Analog Keyboard", "keyboards",
     ["analog", "gaming", "rapid-trigger", "Wooting", "Razer"],
     "Which analog keyboard offers the best magnetic switch technology for gaming."),
    ("Corsair K70 Pro Mini Wireless vs Logitech G915 X: Best Wireless Gaming", "keyboards",
     ["wireless", "gaming", "low-latency", "Corsair", "Logitech"],
     "A comparison of two high-performance wireless gaming keyboards."),
    ("Razer DeathAdder V3 Pro vs Logitech G Pro X Superlight 2: Best Esports Mouse", "mice",
     ["esports", "wireless", "lightweight", "Razer", "Logitech"],
     "Which ultralight wireless mouse is the top choice for competitive gamers."),
    ("Logitech G502 X Plus vs Razer Basilisk V3 Pro: Best MMO Mouse", "mice",
     ["MMO", "gaming", "wireless", "customizable", "Logitech"],
     "A comparison of two feature-rich mice with many buttons for MMO and RPG players."),
    ("Apple Magic Mouse 2 vs Logitech MX Master 3S: Best for Mac", "mice",
     ["Mac", "productivity", "ergonomic", "Apple", "Logitech"],
     "Which mouse offers the best ergonomics and features for Mac users."),
    ("Pulsar X2H vs Finalmouse Starlight-12: Best Ultralight Mouse", "mice",
     ["ultralight", "gaming", "wireless", "Pulsar", "Finalmouse"],
     "A comparison of two ultra-lightweight mice for FPS gamers seeking the lowest weight."),
    ("Zowie EC2-CW vs Vaxee XE Wireless: Best for Competitive FPS", "mice",
     ["FPS", "competitive", "wireless", "Zowie", "Vaxee"],
     "Which esports-focused mouse offers the best shape and performance for first-person shooters."),
    ("Corsair Scimitar Elite vs Razer Naga V2 Pro: Best for MMO", "mice",
     ["MMO", "gaming", "side-buttons", "Corsair", "Razer"],
     "A comparison of two MMO mice with extensive side button arrays."),
    ("Rode NT1 5th Gen vs Shure SM7B: Best for Home Studios", "microphones",
     ["studio", "XLR", "USB", "Rode", "Shure"],
     "Which microphone offers the best vocal recording quality for home studio setups."),
    ("Blue Yeti X vs Elgato Wave:3: Best for Streaming", "microphones",
     ["streaming", "USB", "podcast", "Blue", "Elgato"],
     "A comparison of two popular USB microphones for streamers and content creators."),
    ("Samson Q2U vs Audio-Technica ATR2100x-USB: Best Budget Dynamic", "microphones",
     ["budget", "dynamic", "USB", "XLR", "podcast"],
     "Which affordable dynamic microphone is the best choice for podcasting on a budget."),
    ("Shure MV7 vs Rode PodMic: Best for Podcasting", "microphones",
     ["podcast", "dynamic", "USB", "XLR", "Shure"],
     "A comparison of two industry-standard dynamic microphones for podcasters."),
    ("HyperX QuadCast S vs Razer Seiren V2 Pro: Best RGB Microphone", "microphones",
     ["RGB", "gaming", "USB", "HyperX", "Razer"],
     "Which stylish RGB microphone offers the best audio quality for gamers."),
    ("Sennheiser Profile vs Rode NT-USB+: Best USB Condenser", "microphones",
     ["USB", "condenser", "desktop", "Sennheiser", "Rode"],
     "A comparison of two high-quality USB condenser microphones for desktop use."),
    ("Dell U2724D vs ASUS ProArt PA278CV: Best for Designers", "monitors",
     ["design", "color-accurate", "IPS", "Dell", "ASUS"],
     "Which 27-inch monitor offers the best color accuracy for graphic designers."),
    ("Samsung Odyssey G7 vs LG 27GP850: Best 1440p Gaming Monitor", "monitors",
     ["1440p", "gaming", "high-refresh-rate", "Samsung", "LG"],
     "A comparison of two top-tier 1440p gaming monitors for competitive and immersive play."),
    ("Apple Studio Display vs LG UltraFine 5K: Best for Mac", "monitors",
     ["Mac", "5K", "retina", "Apple", "LG"],
     "Which high-resolution monitor is the best companion for a MacBook or Mac Studio."),
    ("Alienware AW3423DWF vs Samsung Odyssey OLED G8: Best OLED Ultrawide", "monitors",
     ["OLED", "ultrawide", "gaming", "Alienware", "Samsung"],
     "A comparison of two stunning OLED ultrawide monitors for gaming and productivity."),
    ("Gigabyte M32U vs ASUS ROG Swift PG32UQ: Best 4K 32-Inch Monitor", "monitors",
     ["4K", "32-inch", "gaming", "Gigabyte", "ASUS"],
     "Which 32-inch 4K monitor offers the best balance of features and price for gamers."),
    ("BenQ PD3225U vs ViewSonic VP3286-4K: Best for Video Editing", "monitors",
     ["video-editing", "4K", "color-accurate", "BenQ", "ViewSonic"],
     "A comparison of two professional monitors optimized for video editing and color grading."),
    ("Jackery Explorer 1000 Pro vs Bluetti AC70: Best Mid-Range Power Station", "power-stations",
     ["mid-range", "portable", "solar", "Jackery", "Bluetti"],
     "Which portable power station offers the best capacity and features for camping and emergencies."),
    ("EcoFlow River 2 Pro vs Anker Solix C1000: Best for Camping", "power-stations",
     ["camping", "portable", "fast-charging", "EcoFlow", "Anker"],
     "A comparison of two compact power stations ideal for outdoor adventures."),
    ("Goal Zero Yeti 1500X vs Jackery Explorer 1500 Pro: Best for Home Backup", "power-stations",
     ["home-backup", "large-capacity", "solar", "Goal-Zero", "Jackery"],
     "Which large power station is best for keeping essential appliances running during outages."),
    ("Bluetti AC300 vs EcoFlow Delta Pro: Best Expandable System", "power-stations",
     ["expandable", "high-capacity", "home-backup", "Bluetti", "EcoFlow"],
     "A comparison of two modular power stations that can be expanded for whole-home backup."),
    ("Anker Solix F1200 vs Jackery Explorer 1000: Best Value Power Station", "power-stations",
     ["value", "mid-range", "portable", "Anker", "Jackery"],
     "Which power station offers the best price-to-performance ratio for most users."),
    ("EcoFlow Delta 2 vs Bluetti AC180: Best for RV Living", "power-stations",
     ["RV", "portable", "high-capacity", "EcoFlow", "Bluetti"],
     "A comparison of two popular power stations for RV and van life enthusiasts."),
    ("TP-Link Archer AX6000 vs ASUS RT-AX86U: Best Gaming Router", "routers",
     ["gaming", "Wi-Fi-6", "high-performance", "TP-Link", "ASUS"],
     "Which Wi-Fi 6 router offers the best performance and features for online gaming."),
    ("Netgear Nighthawk RAXE500 vs ASUS ROG Rapture GT-AXE11000: Best Wi-Fi 6E", "routers",
     ["Wi-Fi-6E", "high-speed", "gaming", "Netgear", "ASUS"],
     "A comparison of two top-tier Wi-Fi 6E routers for maximum speed and coverage."),
    ("Google Nest WiFi Pro vs Amazon Eero Pro 6E: Best Mesh System", "routers",
     ["mesh", "Wi-Fi-6E", "whole-home", "Google", "Amazon"],
     "Which mesh Wi-Fi system offers the best coverage and ease of use for large homes."),
    ("TP-Link Deco XE75 vs ASUS ZenWiFi XD6: Best Mid-Range Mesh", "routers",
     ["mesh", "Wi-Fi-6", "value", "TP-Link", "ASUS"],
     "A comparison of two affordable mesh systems for reliable whole-home coverage."),
    ("Ubiquiti UniFi Dream Machine vs TP-Link Omada ER605: Best for Prosumers", "routers",
     ["prosumer", "business", "advanced", "Ubiquiti", "TP-Link"],
     "Which networking solution offers the best control and features for tech-savvy users."),
    ("Linksys Atlas Pro 6 vs Netgear Orbi 960: Best High-End Mesh", "routers",
     ["mesh", "high-end", "Wi-Fi-6", "Linksys", "Netgear"],
     "A comparison of two premium mesh systems for the ultimate home network experience."),
    ("Amazon Echo Dot 5th Gen vs Google Nest Mini 2nd Gen: Best Smart Speaker", "smart-home",
     ["smart-speaker", "voice-assistant", "Amazon", "Google", "budget"],
     "Which compact smart speaker offers the best voice assistant and smart home control."),
    ("Philips Hue Play Gradient vs Govee Neon Rope Light 2: Best TV Backlight", "smart-home",
     ["TV-backlight", "RGB", "smart-lighting", "Philips", "Govee"],
     "A comparison of two popular TV backlighting solutions for immersive viewing."),
    ("Ring Floodlight Cam Wired Pro vs Arlo Pro 5S Floodlight: Best Security Light", "smart-home",
     ["security", "floodlight", "camera", "Ring", "Arlo"],
     "Which smart floodlight camera offers the best video quality and features."),
    ("Ecobee Smart Thermostat Premium vs Nest Learning Thermostat 4th Gen: Best Smart Thermostat", "smart-home",
     ["thermostat", "smart", "energy-saving", "Ecobee", "Nest"],
     "A comparison of the two leading smart thermostats for energy savings and comfort."),
    ("August Wi-Fi Smart Lock vs Yale Assure Lock 2: Best Smart Lock", "smart-home",
     ["smart-lock", "security", "keyless", "August", "Yale"],
     "Which smart lock offers the best convenience and security for your home."),
    ("SwitchBot Curtain vs IKEA Fyrtur: Best Smart Blinds", "smart-home",
     ["smart-blinds", "automation", "budget", "SwitchBot", "IKEA"],
     "A comparison of two affordable smart blind solutions for home automation."),
    ("Samsung Galaxy S24 Ultra vs Google Pixel 9 Pro: Best Android Flagship", "smartphones",
     ["Android", "flagship", "Samsung", "Google", "camera"],
     "Which Android flagship offers the best overall experience in 2024."),
    ("iPhone 16 Pro vs iPhone 16 Pro Max: Which Pro is for You?", "smartphones",
     ["Apple", "iPhone", "Pro", "size", "comparison"],
     "A comparison of the two Pro iPhone models to help you choose the right size and features."),
    ("Google Pixel 9 vs Samsung Galaxy S24: Best Mid-Range Flagship", "smartphones",
     ["mid-range", "Android", "value", "Google", "Samsung"],
     "Which affordable flagship offers the best camera and software experience."),
    ("OnePlus 12 vs Samsung Galaxy S24 Plus: Best for Power Users", "smartphones",
     ["performance", "fast-charging", "Android", "OnePlus", "Samsung"],
     "A comparison of two high-performance Android phones for demanding users."),
    ("Nothing Phone 2 vs Google Pixel 8a: Best Budget Android", "smartphones",
     ["budget", "Android", "design", "Nothing", "Google"],
     "Which affordable Android phone offers the best design and software experience."),
    ("Sony Xperia 1 VI vs Samsung Galaxy S24 Ultra: Best for Creators", "smartphones",
     ["creator", "camera", "video", "Sony", "Samsung"],
     "A comparison of two smartphones optimized for content creation and professional photography."),
    ("Garmin Venu 3 vs Apple Watch Series 9: Best for Fitness", "smartwatches",
     ["fitness", "GPS", "health", "Garmin", "Apple"],
     "Which smartwatch offers the best fitness tracking and health features for athletes."),
    ("Samsung Galaxy Watch 6 Classic vs Google Pixel Watch 2: Best Wear OS Watch", "smartwatches",
     ["Wear-OS", "smartwatch", "Samsung", "Google", "design"],
     "A comparison of the two best Wear OS smartwatches for Android users."),
    ("Apple Watch Ultra 2 vs Garmin Epix Pro Gen 2: Best for Adventurers", "smartwatches",
     ["adventure", "rugged", "GPS", "Apple", "Garmin"],
     "Which rugged smartwatch is the best companion for extreme outdoor activities."),
    ("Fitbit Charge 6 vs Garmin Vivosmart 5: Best Fitness Tracker", "smartwatches",
     ["fitness-tracker", "health", "budget", "Fitbit", "Garmin"],
     "A comparison of two popular fitness trackers for daily health monitoring."),
    ("Withings ScanWatch 2 vs Garmin Lily 2: Best Hybrid Smartwatch", "smartwatches",
     ["hybrid", "analog", "health", "Withings", "Garmin"],
     "Which hybrid smartwatch offers the best blend of classic style and modern health tracking."),
    ("Amazfit T-Rex 2 vs Coros Vertix 2: Best for Hiking", "smartwatches",
     ["hiking", "rugged", "GPS", "battery-life", "Amazfit"],
     "A comparison of two durable smartwatches built for hiking and outdoor navigation."),
    ("Roku Streaming Stick 4K vs Amazon Fire TV Stick 4K Max: Best Streaming Stick", "streaming",
     ["streaming-stick", "4K", "Roku", "Amazon", "value"],
     "Which streaming stick offers the best interface and performance for cord-cutters."),
    ("Google TV Streamer vs Apple TV 4K: Best for Google Ecosystem", "streaming",
     ["streaming", "4K", "Google", "Apple", "smart-home"],
     "A comparison of the latest streaming devices from Google and Apple for their respective ecosystems."),
    ("Nvidia Shield TV Pro vs Apple TV 4K: Best for Gamers", "streaming",
     ["gaming", "streaming", "4K", "Nvidia", "Apple"],
     "Which streaming device offers the best gaming capabilities and media playback."),
    ("Chromecast with Google TV HD vs Roku Express 4K+: Best Budget Streamer", "streaming",
     ["budget", "streaming", "HD", "Google", "Roku"],
     "A comparison of two affordable streaming devices for basic streaming needs."),
    ("Amazon Fire TV Cube vs Apple TV 4K: Best for Voice Control", "streaming",
     ["voice-control", "streaming", "4K", "Amazon", "Apple"],
     "Which streaming device offers the best hands-free voice control and smart home integration."),
    ("TiVo Stream 4K vs Walmart Onn 4K Pro: Best Value Streamer", "streaming",
     ["value", "4K", "Android-TV", "TiVo", "Walmart"],
     "A comparison of two budget-friendly Android TV streaming devices."),
    ("Samsung Galaxy Tab S9 Ultra vs iPad Pro M4: Best Large Tablet", "tablets",
     ["large-screen", "productivity", "Samsung", "Apple", "premium"],
     "Which large tablet offers the best experience for productivity and creativity."),
    ("iPad Air M2 vs iPad Pro M4: Best for Students", "tablets",
     ["student", "value", "Apple", "iPad", "education"],
     "A comparison of two iPad models to help students choose the best balance of performance and price."),
    ("Microsoft Surface Pro 10 vs iPad Pro M4: Best 2-in-1", "tablets",
     ["2-in-1", "productivity", "Windows", "Apple", "detachable"],
     "Which detachable tablet is the best laptop replacement for professionals."),
    ("Amazon Fire Max 11 vs Samsung Galaxy Tab A9+: Best Budget Tablet", "tablets",
     ["budget", "entertainment", "Amazon", "Samsung", "value"],
     "Which affordable tablet offers the best media consumption experience."),
    ("Lenovo Tab P12 Pro vs Xiaomi Pad 6 Pro: Best Android Tablet", "tablets",
     ["Android", "productivity", "Lenovo", "Xiaomi", "value"],
     "A comparison of two high-performance Android tablets for work and play."),
    ("Google Pixel Tablet vs iPad 10th Gen: Best Smart Display Tablet", "tablets",
     ["smart-display", "tablet", "Google", "Apple", "home"],
     "Which tablet doubles as the best smart display for home control and entertainment."),
    ("Logitech StreamCam vs Razer Kiyo Pro Ultra: Best for Streaming", "webcams",
     ["streaming", "1080p", "Logitech", "Razer", "auto-focus"],
     "Which webcam offers the best video quality and features for live streaming."),
    ("Elgato Facecam vs Logitech Brio 4K: Best for Content Creators", "webcams",
     ["content-creation", "4K", "Elgato", "Logitech", "studio"],
     "A comparison of two popular webcams for YouTube and video production."),
    ("Dell UltraSharp Webcam vs HP 965 4K: Best for Business", "webcams",
     ["business", "4K", "conferencing", "Dell", "HP"],
     "Which premium webcam offers the best image quality for professional video calls."),
    ("Anker PowerConf C200 vs Logitech C920s: Best Budget Webcam", "webcams",
     ["budget", "1080p", "webcam", "Anker", "Logitech"],
     "A comparison of two affordable webcams for home office and video calls."),
    ("Razer Kiyo X vs Logitech C922: Best for Gamers", "webcams",
     ["gaming", "streaming", "1080p", "Razer", "Logitech"],
     "Which webcam offers the best features for game streaming and recording."),
    ("Opal Tadpole vs Insta360 Link: Best Portable Webcam", "webcams",
     ["portable", "4K", "design", "Opal", "Insta360"],
     "A comparison of two innovative and portable webcams for on-the-go professionals."),
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
