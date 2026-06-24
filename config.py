# DEMON 😈 CONFIG - RAILWAY EDITION
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8643322725:AAG45lf0GkMuRLChKNa6K2f2mSRa8tY-FiM")

# ⏱️ TIMER CONFIG
BOMB_DURATION = 300  # 5 minutes in seconds
CHECK_INTERVAL = 10  # Check every 10 seconds

# 📡 ALL 9 APIs (Ek saath use hongi)
API_LIST = [
    {
        "name": "🔥 Ultra Bomber",
        "url": "https://ultra-bomber-wo5r.onrender.com/bomb",
        "params": {"key": "admin123"},
        "phone_param": "phone"
    },
    {
        "name": "💀 Ultra Brutal",
        "url": "https://ultra-brutal-bomber-njde.onrender.com/bomb",
        "params": {},
        "phone_param": "phone"
    },
    {
        "name": "🚀 Part 1",
        "url": "https://bomber-part-1-kzn0.onrender.com/bomb",
        "params": {"key": "shuvo"},
        "phone_param": "phone"
    },
    {
        "name": "⚡ Part 2",
        "url": "https://brutal-bomber-part-2-6dhd.onrender.com/bomb",
        "params": {"key": "shuvo"},
        "phone_param": "phone"
    },
    {
        "name": "💣 Bomber Pro",
        "url": "https://bomber-pro-r88e.onrender.com/bomb",
        "params": {"key": "shuvo", "cycles": 10},
        "phone_param": "phone"
    },
    {
        "name": "🎯 Bomber APIs",
        "url": "https://bomber-apis-g0sf.onrender.com/bom",
        "params": {"key": "felix"},
        "phone_param": "num"
    },
    {
        "name": "🐍 Felix Bomber",
        "url": "https://felix-bom-irju.onrender.com/bom",
        "params": {"key": "demo"},
        "phone_param": "num"
    },
    {
        "name": "🤖 Bomber 3SKM",
        "url": "https://bomber-3skm.onrender.com/bom",
        "params": {"key": "felix"},
        "phone_param": "num"
    },
    {
        "name": "👾 Shuvo Bomber",
        "url": "https://bomber-by-shuvo.onrender.com/bomb",
        "params": {},
        "phone_param": "phone"
    }
]
