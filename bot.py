
import os
import json
import base64
import time
import asyncio
import requests
import sqlite3
import datetime
import random
import string
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMINS   = [8546348748, 8737475340]
ADMIN_USERNAME = "@happy_gamer2"

# GitHub Configuration (Supports GH_TOKEN & GITHUB_TOKEN)
GITHUB_TOKEN = (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
GITHUB_REPO  = (os.environ.get("GH_REPO") or os.environ.get("GITHUB_REPO") or "sagarhalder7865-hub/my-telegram-bot").strip()
DATA_FILE    = "bot_data.json"

# Gist Config for Script Key Automation
GIST_ID   = "e155b8f93a7476556fa1c8b2dfc9b164"
FILE_NAME = "status.txt"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "bot_data.db")
QR_PATH  = os.path.join(BASE_DIR, "payment_qr.png")

# --- 24/7 ULTRA CLOUD WEB SERVER ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = """
        <html>
        <head><title>Happy Gamer VIP Cloud</title></head>
        <body style="background:#0b0e14;color:#00e5ff;font-family:sans-serif;text-align:center;padding-top:50px;">
            <h1>👑 HAPPY GAMER VIP BOT ENGINE</h1>
            <p style="color:#00ff66;">⚡ Status: Running 24/7 Online On GitHub Actions (100% Fresh DB Engine)</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), DummyHandler)
        server.serve_forever()
    except Exception:
        pass

Thread(target=run_web_server, daemon=True).start()

# DEFAULT FRESH INITIAL PRICES
DEFAULT_PRICES = {
    # 👿 AIM-AI ENGINE (CARROM)
    "aim_1d":  {"game": "AIM-AI Carrom", "label": "01 Day",   "reg": 120, "res": 100},
    "aim_3d":  {"game": "AIM-AI Carrom", "label": "03 Days",  "reg": 200, "res": 180},
    "aim_7d":  {"game": "AIM-AI Carrom", "label": "07 Days",  "reg": 300, "res": 260},
    "aim_15d": {"game": "AIM-AI Carrom", "label": "15 Days",  "reg": 500, "res": 490},
    "aim_30d": {"game": "AIM-AI Carrom", "label": "30 Days",  "reg": 830, "res": 780},
    "aim_90d": {"game": "AIM-AI Carrom", "label": "90 Days",  "reg": 2100, "res": 2000},

    # AIM CARROM KING
    "acn_3d":  {"game": "AIM Carrom Normal", "label": "3 Days",  "reg": 250, "res": 220},
    "acn_7d":  {"game": "AIM Carrom Normal", "label": "1 Week",  "reg": 360, "res": 330},
    "acn_30d": {"game": "AIM Carrom Normal", "label": "1 Month", "reg": 1000, "res": 950},
    "acp_3d":  {"game": "AIM Carrom Premium", "label": "3 Days",  "reg": 310, "res": 280},
    "acp_7d":  {"game": "AIM Carrom Premium", "label": "1 Week",  "reg": 480, "res": 460},
    "acp_30d": {"game": "AIM Carrom Premium", "label": "1 Month", "reg": 1250, "res": 1180},

    # KOS ENGINE
    "b1":  {"game": "KOS 8 Ball", "label": "1 Day",   "reg": 180, "res": 150},
    "b7":  {"game": "KOS 8 Ball", "label": "7 Days",  "reg": 500, "res": 450},
    "b15": {"game": "KOS 8 Ball", "label": "15 Days", "reg": 900, "res": 800},
    "b30": {"game": "KOS 8 Ball", "label": "30 Days", "reg": 1600, "res": 1400},
    "c1":  {"game": "KOS Carrom", "label": "1 Day",   "reg": 120, "res": 100},
    "c7":  {"game": "KOS Carrom", "label": "7 Days",  "reg": 300, "res": 230},
    "c15": {"game": "KOS Carrom", "label": "15 Days", "reg": 490, "res": 400},
    "c30": {"game": "KOS Carrom", "label": "30 Days", "reg": 800, "res": 670},
    "f1":  {"game": "KOS FreeFire Panel", "label": "1 Day",   "reg": 200, "res": 180},
    "f7":  {"game": "KOS FreeFire Panel", "label": "7 Days",  "reg": 600, "res": 500},
    "f30": {"game": "KOS FreeFire Panel", "label": "30 Days", "reg": 1800, "res": 1500},

    # BITAIM
    "bit7":  {"game": "Bitaim ⚡", "label": "7 Days",    "reg": 65, "res": 50},
    "bit30": {"game": "Bitaim ⚡", "label": "30 Days",   "reg": 165, "res": 160},
    "bit90": {"game": "Bitaim ⚡", "label": "3 Months",  "reg": 380, "res": 340},
    "bitlt": {"game": "Bitaim ⚡", "label": "Life Time", "reg": 1860, "res": 1790},

    # SNAKE ENGINE
    "snkc_3d":  {"game": "Snake Carrom", "label": "3 Days",  "reg": 190, "res": 160},
    "snkc_10d": {"game": "Snake Carrom", "label": "10 Days", "reg": 450, "res": 400},
    "snkc_30d": {"game": "Snake Carrom", "label": "30 Days", "reg": 900, "res": 830},
    "snk8_3d":  {"game": "Snake 8Ball", "label": "3 Days",  "reg": 320, "res": 290},
    "snk8_10d": {"game": "Snake 8Ball", "label": "10 Days", "reg": 650, "res": 630},
    "snk8_30d": {"game": "Snake 8Ball", "label": "30 Days", "reg": 1200, "res": 1150},
}

# --- GIST UTILS ---
def get_auth_headers():
    token = GITHUB_TOKEN.strip() if GITHUB_TOKEN else ""
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "HappyGamerApp"
    }

def generate_short_key():
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"HG{random_chars}"

def clean_expired_lines(content_text):
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    today_int = int(today_str)
    cleaned_lines = []
    removed_count = 0
    
    for line in content_text.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        
        if line_clean.startswith("HGTOKEN=") or line_clean.startswith("HGTOKEN=="):
            parts = [p for p in line_clean.split("=") if p != ""]
            exp_date_str = None
            for p in parts:
                if len(p) == 8 and p.isdigit():
                    exp_date_str = p
                    break
            
            if exp_date_str:
                try:
                    exp_date_int = int(exp_date_str)
                    if exp_date_int < today_int:
                        removed_count += 1
                        continue
                except Exception:
                    pass
        cleaned_lines.append(line_clean)
        
    return "\n".join(cleaned_lines), removed_count

def append_to_gist(vip_key, device_id, days):
    try:
        if not GITHUB_TOKEN:
            return False, None, "GitHub Token is not set in Environment!"

        expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y%m%d")
        new_entry = f"HGTOKEN={vip_key}={expiry}={device_id}"
        
        headers = get_auth_headers()
        get_url = f"https://api.github.com/gists/{GIST_ID}"
        
        get_res = requests.get(get_url, headers=headers, timeout=10)
        current_content = ""
        if get_res.status_code == 200:
            files_data = get_res.json().get("files", {})
            if FILE_NAME in files_data:
                current_content = files_data[FILE_NAME].get("content", "")
        else:
            raw_url = f"https://gist.githubusercontent.com/sagarhalder7865-hub/{GIST_ID}/raw/{FILE_NAME}?t={int(time.time())}"
            raw_res = requests.get(raw_url, timeout=10)
            if raw_res.status_code == 200:
                current_content = raw_res.text

        filtered_content, removed = clean_expired_lines(current_content)

        if filtered_content:
            updated_content = filtered_content.strip() + "\n" + new_entry
        else:
            updated_content = "STATUS=ON\n" + new_entry

        patch_payload = {"files": {FILE_NAME: {"content": updated_content}}}
        patch_res = requests.patch(get_url, headers=headers, json=patch_payload, timeout=10)
        
        if patch_res.status_code in [200, 201]:
            return True, expiry, None
        else:
            err_details = patch_res.json().get("message", patch_res.text)
            return False, expiry, f"Status {patch_res.status_code}: {err_details}"
    except Exception as e:
        return False, None, str(e)

def purge_expired_gist_keys():
    if not GITHUB_TOKEN: return 0
    try:
        headers = get_auth_headers()
        get_url = f"https://api.github.com/gists/{GIST_ID}"
        get_res = requests.get(get_url, headers=headers, timeout=10)
        if get_res.status_code != 200: return 0
        
        files_data = get_res.json().get("files", {})
        if FILE_NAME not in files_data: return 0
            
        current_content = files_data[FILE_NAME].get("content", "")
        cleaned_content, removed = clean_expired_lines(current_content)
        
        if removed > 0:
            patch_payload = {"files": {FILE_NAME: {"content": cleaned_content}}}
            requests.patch(get_url, headers=headers, json=patch_payload, timeout=10)
        return removed
    except Exception as e:
        return 0

# --- GITHUB SYNC ---
def push_data_to_github():
    if not GITHUB_TOKEN or not GITHUB_REPO: return
    try:
        data_dump = export_database_json()
        content_str = json.dumps(data_dump, indent=2)
        content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
        headers = get_auth_headers()
        
        sha = None
        get_res = requests.get(url, headers=headers, timeout=10)
        if get_res.status_code == 200:
            sha = get_res.json().get("sha")
            
        payload = {"message": "[skip ci] Auto-sync VIP bot data", "content": content_b64}
        if sha: payload["sha"] = sha
            
        requests.put(url, headers=headers, json=payload, timeout=10)
    except Exception as e:
        print(f"GitHub Sync Error: {e}")

def pull_data_from_github():
    if not GITHUB_TOKEN or not GITHUB_REPO: return None
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
        headers = get_auth_headers()
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            content_b64 = res.json().get("content", "")
            return json.loads(base64.b64decode(content_b64).decode("utf-8"))
    except Exception as e:
        print(f"GitHub Pull Error: {e}")
    return None

def export_database_json():
    with get_db() as db:
        users = [dict(r) for r in db.execute("SELECT * FROM users").fetchall()]
        balances = [dict(r) for r in db.execute("SELECT * FROM balances").fetchall()]
        keys = [dict(r) for r in db.execute("SELECT * FROM keys").fetchall()]
        resellers = [dict(r) for r in db.execute("SELECT * FROM resellers").fetchall()]
        prices = [dict(r) for r in db.execute("SELECT * FROM prices").fetchall()]
        orders = [dict(r) for r in db.execute("SELECT * FROM order_history").fetchall()]
        referrals = [dict(r) for r in db.execute("SELECT * FROM referrals").fetchall()]
        banned = [dict(r) for r in db.execute("SELECT * FROM banned_users").fetchall()]
    return {
        "users": users, "balances": balances, "keys": keys,
        "resellers": resellers, "prices": prices, "order_history": orders,
        "referrals": referrals, "banned_users": banned
    }

# --- DATABASE SETUP ---
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_fresh=False):
    with get_db() as db:
        if force_fresh:
            db.executescript("""
                DROP TABLE IF EXISTS users;
                DROP TABLE IF EXISTS balances;
                DROP TABLE IF EXISTS keys;
                DROP TABLE IF EXISTS resellers;
                DROP TABLE IF EXISTS prices;
                DROP TABLE IF EXISTS order_history;
                DROP TABLE IF EXISTS banned_users;
                DROP TABLE IF EXISTS referrals;
            """)

        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                referred_by INTEGER DEFAULT 0,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS balances (
                user_id INTEGER PRIMARY KEY,
                amount  INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS keys (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                plan    TEXT NOT NULL,
                key     TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS resellers (
                user_id INTEGER PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS prices (
                plan     TEXT PRIMARY KEY,
                game     TEXT NOT NULL,
                label    TEXT NOT NULL,
                regular  INTEGER NOT NULL,
                reseller INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS order_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                game TEXT NOT NULL,
                plan_label TEXT NOT NULL,
                price INTEGER NOT NULL,
                key_delivered TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS banned_users (
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                banned_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS referrals (
                referred_user INTEGER PRIMARY KEY,
                referrer_id INTEGER,
                reward_paid INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 1. Insert default prices
        for pcode, pdata in DEFAULT_PRICES.items():
            db.execute("INSERT OR REPLACE INTO prices (plan, game, label, regular, reseller) VALUES (?,?,?,?,?)",
                       (pcode, pdata["game"], pdata["label"], pdata["reg"], pdata["res"]))

        # 2. Pull persistent data from github ONLY if not fresh
        if not force_fresh:
            gh_data = pull_data_from_github()
            if gh_data:
                for u in gh_data.get("users", []):
                    db.execute("INSERT OR REPLACE INTO users (user_id, first_name, username, referred_by) VALUES (?,?,?,?)", 
                               (u["user_id"], u.get("first_name",""), u.get("username",""), u.get("referred_by", 0)))
                for b in gh_data.get("balances", []):
                    db.execute("INSERT OR REPLACE INTO balances (user_id, amount) VALUES (?,?)", (b["user_id"], b["amount"]))
                for k in gh_data.get("keys", []):
                    db.execute("INSERT OR REPLACE INTO keys (id, plan, key) VALUES (?,?,?)", (k["id"], k["plan"], k["key"]))
                for r in gh_data.get("resellers", []):
                    db.execute("INSERT OR REPLACE INTO resellers (user_id) VALUES (?)", (r["user_id"],))
                for p in gh_data.get("prices", []):
                    db.execute("INSERT OR REPLACE INTO prices (plan, game, label, regular, reseller) VALUES (?,?,?,?,?)",
                               (p["plan"], p["game"], p["label"], p["regular"], p["reseller"]))
                for ban in gh_data.get("banned_users", []):
                    db.execute("INSERT OR REPLACE INTO banned_users (user_id, reason) VALUES (?,?)", (ban["user_id"], ban.get("reason", "Admin Ban")))
                for ref in gh_data.get("referrals", []):
                    db.execute("INSERT OR REPLACE INTO referrals (referred_user, referrer_id, reward_paid) VALUES (?,?,?)", (ref["referred_user"], ref["referrer_id"], ref.get("reward_paid", 1)))
                for o in gh_data.get("order_history", []):
                    db.execute("INSERT OR IGNORE INTO order_history (id, user_id, game, plan_label, price, key_delivered, timestamp) VALUES (?,?,?,?,?,?,?)",
                               (o.get("id"), o["user_id"], o["game"], o["plan_label"], o["price"], o["key_delivered"], o.get("timestamp")))

def db_is_banned(user_id):
    with get_db() as db:
        return db.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user_id,)).fetchone() is not None

def db_ban_user(user_id, reason="Blacklisted"):
    with get_db() as db:
        db.execute("INSERT OR REPLACE INTO banned_users (user_id, reason) VALUES (?,?)", (user_id, reason))
    push_data_to_github()

def db_unban_user(user_id):
    with get_db() as db:
        db.execute("DELETE FROM banned_users WHERE user_id=?", (user_id,))
    push_data_to_github()

def db_register_user(user_id, first_name, username, referrer_id=0):
    with get_db() as db:
        existing = db.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not existing:
            db.execute(
                "INSERT INTO users (user_id, first_name, username, referred_by) VALUES (?,?,?,?)",
                (user_id, first_name, username, referrer_id)
            )
            if referrer_id > 0 and referrer_id != user_id:
                db_add_balance(referrer_id, 1)
                db.execute("INSERT OR IGNORE INTO referrals (referred_user, referrer_id, reward_paid) VALUES (?,?,1)", (user_id, referrer_id))
                push_data_to_github()
                return referrer_id
        else:
            db.execute(
                "UPDATE users SET first_name=?, username=? WHERE user_id=?",
                (first_name, username, user_id)
            )
    push_data_to_github()
    return None

def db_get_referral_count(user_id):
    with get_db() as db:
        row = db.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id=?", (user_id,)).fetchone()
        return row[0] if row else 0

def db_get_all_users():
    with get_db() as db:
        rows = db.execute("SELECT DISTINCT user_id FROM users UNION SELECT DISTINCT user_id FROM balances UNION SELECT DISTINCT user_id FROM order_history").fetchall()
        return [r["user_id"] for r in rows]

def db_get_balance(user_id):
    with get_db() as db:
        row = db.execute("SELECT amount FROM balances WHERE user_id=?", (user_id,)).fetchone()
    return row["amount"] if row else 0

def db_set_balance(user_id, amount):
    with get_db() as db:
        db.execute(
            "INSERT INTO balances (user_id,amount) VALUES (?,?) ON CONFLICT(user_id) DO UPDATE SET amount=?",
            (user_id, amount, amount)
        )
    push_data_to_github()

def db_add_balance(user_id, delta):
    cur = db_get_balance(user_id)
    db_set_balance(user_id, cur + delta)
    return cur + delta

def db_count_keys(plan):
    with get_db() as db:
        return db.execute("SELECT COUNT(*) FROM keys WHERE plan=?", (plan,)).fetchone()[0]

def db_add_key(plan, key):
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO keys (plan,key) VALUES (?,?)", (plan, key))
    push_data_to_github()

def db_pop_key(plan):
    with get_db() as db:
        row = db.execute("SELECT id,key FROM keys WHERE plan=? ORDER BY id LIMIT 1", (plan,)).fetchone()
        if row:
            db.execute("DELETE FROM keys WHERE id=?", (row["id"],))
            push_data_to_github()
            return row["key"]
    return None

def db_is_reseller(user_id):
    with get_db() as db:
        return db.execute("SELECT 1 FROM resellers WHERE user_id=?", (user_id,)).fetchone() is not None

def db_add_reseller(user_id):
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO resellers (user_id) VALUES (?)", (user_id,))
    push_data_to_github()

def db_remove_reseller(user_id):
    with get_db() as db:
        db.execute("DELETE FROM resellers WHERE user_id=?", (user_id,))
    push_data_to_github()

def db_all_resellers():
    with get_db() as db:
        return [r["user_id"] for r in db.execute("SELECT user_id FROM resellers").fetchall()]

def db_get_plan(plan_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM prices WHERE plan=?", (plan_id,)).fetchone()
        if row:
            return dict(row)
    if plan_id in DEFAULT_PRICES:
        item = DEFAULT_PRICES[plan_id]
        return {"plan": plan_id, "game": item["game"], "label": item["label"], "regular": item["reg"], "reseller": item["res"]}
    return None

def db_set_price(plan_id, regular, reseller):
    with get_db() as db:
        row = db.execute("SELECT game, label FROM prices WHERE plan=?", (plan_id,)).fetchone()
        if row:
            db.execute("UPDATE prices SET regular=?, reseller=? WHERE plan=?", (regular, reseller, plan_id))
        else:
            gname = DEFAULT_PRICES.get(plan_id, {}).get("game", plan_id)
            glabel = DEFAULT_PRICES.get(plan_id, {}).get("label", plan_id)
            db.execute("INSERT OR REPLACE INTO prices (plan, game, label, regular, reseller) VALUES (?,?,?,?,?)",
                       (plan_id, gname, glabel, regular, reseller))
    push_data_to_github()

def db_record_order(user_id, game, plan_label, price, key_delivered):
    with get_db() as db:
        db.execute(
            "INSERT INTO order_history (user_id, game, plan_label, price, key_delivered) VALUES (?,?,?,?,?)",
            (user_id, game, plan_label, price, key_delivered)
        )
    push_data_to_github()

def db_get_last_purchase(user_id):
    with get_db() as db:
        row = db.execute("SELECT game, plan_label FROM order_history WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
        if row:
            return f"{row['game']} ({row['plan_label']})"
    return "No Purchases Yet"

def db_get_user_orders(user_id):
    with get_db() as db:
        return db.execute("SELECT game, plan_label, price, key_delivered, timestamp FROM order_history WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,)).fetchall()

def get_price(user_id, plan_id):
    is_res = db_is_reseller(user_id)
    plan = db_get_plan(plan_id)
    if plan:
        return plan["reseller"] if is_res else plan["regular"]
    return 0

def stock_text():
    lines = [
        "╔═══════════════════════════╗",
        "║  📦 <b>LIVE WAREHOUSE INVENTORY</b>  ║",
        "╚═══════════════════════════╝",
        "\n👿 <b>AIM-AI CARROM ENGINE:</b>"
    ]
    for p in ["aim_1d", "aim_3d", "aim_7d", "aim_15d", "aim_30d", "aim_90d"]:
        pl = db_get_plan(p)
        label = pl["label"] if pl else p
        lines.append(f"  🔥 <code>{label:8}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n👑 <b>AIM CARROM KING INVENTORY:</b>")
    for p in ["acn_3d","acn_7d","acn_30d","acp_3d","acp_7d","acp_30d"]:
        pl = db_get_plan(p)
        label = pl["label"] if pl else p
        lines.append(f"  💎 <code>{label:8}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n🔥 <b>KOS ENGINE KEYS:</b>")
    for p in ["b1","b7","b15","b30","c1","c7","c15","c30","f1","f7","f30"]:
        pl = db_get_plan(p)
        gname = f"{pl['game']} ({pl['label']})" if pl else p
        lines.append(f"  ⚡ <code>{gname}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")
    
    lines.append("\n⚡ <b>BITAIM HACK SLOTS:</b>")
    for p in ["bit7","bit30","bit90","bitlt"]:
        pl = db_get_plan(p)
        label = pl["label"] if pl else p
        lines.append(f"  🔮 <code>Bitaim {label:10}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n🐍 <b>SNAKE ENGINE SLOTS:</b>")
    for p in ["snkc_3d","snkc_10d","snkc_30d","snk8_3d","snk8_10d","snk8_30d"]:
        pl = db_get_plan(p)
        gname = f"{pl['game']} ({pl['label']})" if pl else p
        lines.append(f"  🐍 <code>{gname}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")
        
    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

def price_list_text():
    lines = [
        "╔═══════════════════════════╗",
        "║  💎 <b>OFFICIAL VIP PRICE CATALOG</b> ║",
        "╚═══════════════════════════╝",
        "\n👿 <b>AIM-AI ENGINE (CARROM POOL):</b>"
    ]
    for p in ["aim_1d", "aim_3d", "aim_7d", "aim_15d", "aim_30d", "aim_90d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🔥 <b>{item['label']:8}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")

    lines.append("\n👑 <b>AIM CARROM KING (Normal):</b>")
    for p in ["acn_3d","acn_7d","acn_30d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  💎 <b>{item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")
        
    lines.append("\n👑 <b>AIM CARROM KING (Premium Auto Queue):</b>")
    for p in ["acp_3d","acp_7d","acp_30d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  ⚡ <b>{item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")

    lines.append("\n🔥 <b>KOS ENGINE VIP KEYS:</b>")
    for p in ["b1","b7","b15","b30","c1","c7","c15","c30","f1","f7","f30"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🔮 <b>{item['game']} {item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")
    
    lines.append("\n⚡ <b>BITAIM PREMIUM HACK:</b>")
    for p in ["bit7","bit30","bit90","bitlt"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🎯 <b>Bitaim {item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")

    lines.append("\n🐍 <b>SNAKE ENGINE VIP:</b>")
    for p in ["snkc_3d","snkc_10d","snkc_30d","snk8_3d","snk8_10d","snk8_30d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🐍 <b>{item['game']} {item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")
        
    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

pending_orders   = {}
payment_requests = {}
awaiting_gmail   = {}
PAYMENT_TIMEOUT  = 300

def get_main_dashboard(uid, name):
    role = "👑 VIP Reseller [Elite]" if db_is_reseller(uid) else "👤 Verified Customer"
    bal  = db_get_balance(uid)
    last_buy = db_get_last_purchase(uid)

    inline_kbd = [
        [InlineKeyboardButton("👿 AIM-AI CARROM ENGINE 🔥", callback_data="aim_ai_menu")],
        [InlineKeyboardButton("👑 AIM CARROM KING", callback_data="aim_menu")],
        [InlineKeyboardButton("🔥 KOS Engine Keys", callback_data="kos_menu"), InlineKeyboardButton("⚡ Bitaim Hack", callback_data="bitaim_menu")],
        [InlineKeyboardButton("🐍 Snake Engine", callback_data="snk_menu")],
        [InlineKeyboardButton("🎁 👥 Referral & Earn (₹1 Per Friend)", callback_data="referral_menu")],
        [InlineKeyboardButton("💳 ➕ Add Balance", callback_data="add_bal"), InlineKeyboardButton("📜 🛍️ My Orders", callback_data="orders_hist")],
        [InlineKeyboardButton("📥 📂 Download App", url="https://t.me/hgfileall")],
        [InlineKeyboardButton("💎 👑 Apply For Reseller Panel", callback_data="become_reseller")]
    ]
    
    if uid in ADMINS:
        inline_kbd.insert(6, [InlineKeyboardButton("🛠️ ⚡ Script Key Generator [Admin]", callback_data="script_key_menu")])

    msg = (
        "╔═══════════════════════════╗\n"
        "║  👑 <b>HAPPY GAMER VIP STORE</b> 👑  ║\n"
        "╚═══════════════════════════╝\n"
        "✨ <i>The Most Advanced Instant Key Automation System</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Client:</b> <code>{name}</code>\n"
        f"💰 <b>Wallet Balance:</b> <code>₹{bal}.00</code> 💳\n"
        f"🛡️ <b>Account Tier:</b> <b>{role}</b>\n"
        f"📦 <b>Recent Purchase:</b> <i>{last_buy}</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📖 <b>Instant Buying Guide (কীভাবে কি কিনবেন):</b>\n"
        "1️⃣ <b>Add Balance</b> চেপে কিউআর স্ক্যান করে টাকা যোগ করুন।\n"
        "2️⃣ <b>Referral & Earn</b> চেপে বন্ধুদের ইনভাইট করে ফ্রি টাকা ইনকাম করুন!\n"
        "3️⃣ আপনার পছন্দের <b>VIP Hack Engine</b> সিলেক্ট করুন এবং সাথে সাথে কি পেয়ে যান!"
    )
    return msg, InlineKeyboardMarkup(inline_kbd)

def get_reply_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 All Hack Key buy", "Check Balance 💰"],
        ["🎁 Referral & Earn 💰", "➕Add Balance 💰"],
        ["📦 Stock", "📞 Admin Help"]
    ], resize_keyboard=True)

def get_payment_caption():
    return (
        "╔═══════════════════════════════════════╗\n"
        "║   🛡️ <b>HAPPY GAMER OFFICIAL PAYMENT</b> 🛡️   ║\n"
        "╚═══════════════════════════════════════╝\n\n"
        "📌 <b>Official Verified UPI ID:</b>\n"
        "👉 <code>sagarhalder22@axl</code> <i>(Tap to Copy)</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🇧🇩 <b>পেমেন্ট করার নিয়ম (বাংলা):</b>\n"
        "1️⃣ যেকোনো অ্যাপ (GPay/PhonePe/Paytm) দিয়ে QR কোড স্ক্যান করে টাকা পাঠান।\n"
        "2️⃣ টাকা পাঠানোর পর <b>পেমেন্ট স্ক্রিনশট</b> অথবা <b>১২-সংখ্যার UTR / Ref No</b> এই চ্যাটে পাঠিয়ে দিন।\n"
        "3️⃣ এডমিন সাথে সাথে চেক করে আপনার একাউন্টে ব্যালেন্স যোগ করে দেবে।\n\n"
        "🇬🇧 <b>Payment Instructions (English):</b>\n"
        "1️⃣ Scan & Pay via <b>PhonePe / GPay / Paytm / BHIM</b>.\n"
        "2️⃣ Send your <b>Payment Screenshot</b> OR type the <b>12-digit UTR / Ref Number</b> in this chat.\n"
        "3️⃣ Balance will be credited instantly within 5 minutes!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ <i>Time Limit: 5 Minutes to complete verification.</i>"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username or ""

    if db_is_banned(uid):
        await update.message.reply_text("🚫 <b>YOUR ACCOUNT IS BANNED!</b>", parse_mode="HTML")
        return

    referrer_id = 0
    if context.args and len(context.args) > 0:
        param = context.args[0]
        if param.startswith("ref_"):
            try:
                referrer_id = int(param.replace("ref_", ""))
            except Exception: pass

    ref_giver = db_register_user(uid, name, username, referrer_id)
    
    if ref_giver:
        try:
            await context.bot.send_message(
                chat_id=ref_giver,
                text=(
                    "🎉 <b>CONGRATULATIONS! REFERRAL BONUS CREDITED!</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>New Joined User:</b> {name} (@{username})\n"
                    "💰 <b>Earned Reward:</b> +<code>₹1.00</code> credited to your wallet! 💳"
                ),
                parse_mode="HTML"
            )
        except Exception: pass

    msg, inline_markup = get_main_dashboard(uid, name)
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=get_reply_keyboard())
    await update.message.reply_text("👇 <b>Select your VIP Hack to Proceed:</b>", parse_mode="HTML", reply_markup=inline_markup)

async def handle_direct_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, is_photo=False):
    user_id  = update.effective_user.id
    name     = update.effective_user.first_name
    username = update.effective_user.username or ""
    role_lbl = "👑 Reseller" if db_is_reseller(user_id) else "👤 Customer"

    task = asyncio.create_task(expire_payment(user_id, context))
    payment_requests[user_id] = {"task": task}

    amounts = [100, 120, 180, 200, 260, 300, 490, 500, 560, 570, 580, 780, 830, 2000, 2100, 50, 65, 150, 160, 165, 190, 220, 250, 280, 310, 320, 360, 380, 450, 480, 600, 650, 800, 900, 1000, 1200, 1250, 1600, 1800]
    row, kbd = [], []
    for amt in amounts:
        row.append(InlineKeyboardButton(f"₹{amt}", callback_data=f"pay_{user_id}_{amt}"))
        if len(row) == 3: kbd.append(row); row = []
    if row: kbd.append(row)
    kbd.append([InlineKeyboardButton("❌ Reject Payment", callback_data=f"pay_{user_id}_reject")])

    if is_photo:
        photo_id = update.message.photo[-1].file_id
        await update.message.reply_text("✅ <b>পেমেন্ট স্ক্রিনশট পাওয়া গেছে!</b>\n⏳ এডমিন ভেরিফাই করে ৫ মিনিটের মধ্যে ব্যালেন্স অ্যাড করে দিচ্ছে...", parse_mode="HTML")
        for admin_id in ADMINS:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id, photo=photo_id,
                    caption=(
                        "🔔 <b>NEW PAYMENT SCREENSHOT RECEIVED</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 <b>User:</b> {name} (@{username})\n"
                        f"🆔 <b>ID:</b> <code>{user_id}</code> | {role_lbl}\n"
                        f"💳 <b>Current Bal:</b> ₹{db_get_balance(user_id)}\n\n"
                        "👇 <i>সিলেক্ট করুন কত টাকা ব্যালেন্স যোগ করবেন:</i>"
                    ),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(kbd)
                )
            except Exception: pass
    else:
        utr_text = update.message.text.strip()
        await update.message.reply_text(f"✅ <b>UTR / Ref No:</b> <code>{utr_text}</code> পাওয়া গেছে!\n⏳ এডমিন ভেরিফাই করে ৫ মিনিটের মধ্যে ব্যালেন্স যোগ করে দিচ্ছে...", parse_mode="HTML")
        for admin_id in ADMINS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=(
                        "🔔 <b>NEW PAYMENT UTR / REF NUMBER RECEIVED</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 <b>User:</b> {name} (@{username})\n"
                        f"🆔 <b>ID:</b> <code>{user_id}</code> | {role_lbl}\n"
                        f"💳 <b>Current Bal:</b> ₹{db_get_balance(user_id)}\n"
                        f"🛡️ <b>UTR / Ref No:</b> <code>{utr_text}</code>\n\n"
                        "👇 <i>সিলেক্ট করুন কত টাকা ব্যালেন্স যোগ করবেন:</i>"
                    ),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(kbd)
                )
            except Exception: pass

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_direct_payment(update, context, is_photo=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text    = update.message.text
    user_id = update.effective_user.id
    name    = update.effective_user.first_name
    username = update.effective_user.username or ""

    if db_is_banned(user_id): return

    db_register_user(user_id, name, username)

    # 1. ADMIN SCRIPT KEY GENERATION
    if user_id in ADMINS and "script_gen_days" in context.user_data:
        days = context.user_data.pop("script_gen_days")
        device_id = text.strip()
        
        vip_key = generate_short_key()
        status_msg = await update.message.reply_text("⏳ <i>Syncing with GitHub Gist & Generating...</i>", parse_mode="HTML")
        success, expiry, err = append_to_gist(vip_key, device_id, days)
        
        if success:
            receipt_msg = (
                "╔═══════════════════════════╗\n"
                "║  👑 <b>SCRIPT KEY GENERATED!</b>   ║\n"
                "╚═══════════════════════════╝\n"
                f"👤 <b>Admin:</b> {name}\n"
                f"⏳ <b>Validity:</b> {days} Days (Expires: <code>{expiry}</code>)\n"
                f"📱 <b>Device ID:</b> <code>{device_id}</code>\n"
                "☁️ <b>GitHub Gist:</b> <i>Updated & Auto-Cleaned ✅</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔑 <b>YOUR VIP KEY:</b> <i>(👇 Tap to Copy)</i>\n\n"
                f"<code>{vip_key}</code>"
            )
            await status_msg.edit_text(receipt_msg, parse_mode="HTML")
        else:
            await status_msg.edit_text(f"❌ <b>GitHub Gist Update Failed:</b> <code>{err}</code>", parse_mode="HTML")
        return

    # 2. BITAIM GMAIL HANDLER
    if user_id in awaiting_gmail:
        plan_id = awaiting_gmail.pop(user_id)
        plan    = db_get_plan(plan_id)
        price   = get_price(user_id, plan_id)
        bal     = db_get_balance(user_id)

        if "@" not in text or "." not in text:
            await update.message.reply_text("❌ <b>INVALID GMAIL ADDRESS!</b>\nPlease provide a valid Google Play email.", parse_mode="HTML")
            awaiting_gmail[user_id] = plan_id
            return

        new_bal = bal - price
        db_set_balance(user_id, new_bal)
        gname = plan['game'] if plan else "Bitaim"
        glabel = plan['label'] if plan else plan_id
        db_record_order(user_id, gname, glabel, price, f"Gmail: {text}")

        success_msg = (
            "╔═══════════════════════════╗\n"
            "║  🎉 <b>BITAIM ORDER CONFIRMED</b>  ║\n"
            "╚═══════════════════════════╝\n"
            f"🎮 <b>Item:</b> {gname} ({glabel})\n"
            f"💰 <b>Charged:</b> ₹{price}\n"
            f"📧 <b>Account Gmail:</b> <code>{text}</code>\n"
            f"💳 <b>Remaining Balance:</b> ₹{new_bal}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <i>Admin has been notified. Activation inside 10 minutes!</i>"
        )
        await update.message.reply_text(success_msg, parse_mode="HTML")

        for admin_id in ADMINS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🚨 <b>NEW BITAIM ORDER!</b>\n👤 Client: {user_id} ({name})\n🎮 Plan: {gname} ({glabel})\n💰 Price: ₹{price}\n📧 Gmail: <code>{text}</code>",
                    parse_mode="HTML"
                )
            except Exception: pass
        return

    clean_num = text.strip().replace(" ", "")
    if len(clean_num) >= 8 and clean_num.isdigit():
        await handle_direct_payment(update, context, is_photo=False)
        return

    if text in ["/start", "🔑 All Hack Key buy"]:
        msg, inline_markup = get_main_dashboard(user_id, name)
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=inline_markup)

    elif text in ["Check Balance 💰", "💰 Balance"]:
        bal = db_get_balance(user_id)
        role = " [👑 VIP Reseller]" if db_is_reseller(user_id) else " [Customer]"
        await update.message.reply_text(f"💳 <b>Your Wallet Balance:</b> <code>₹{bal}.00</code>\n🏷️ <b>Status:</b> <b>{role}</b>", parse_mode="HTML")

    elif text in ["🎁 Referral & Earn 💰", "/referral", "/ref"]:
        await send_referral_panel(update, context, user_id)

    elif text in ["➕Add Balance 💰", "➕ Add Balance"]:
        caption = get_payment_caption()
        if os.path.exists(QR_PATH):
            with open(QR_PATH, "rb") as f:
                await update.message.reply_photo(photo=f, caption=caption, parse_mode="HTML")
        else:
            await update.message.reply_text(caption, parse_mode="HTML")

    elif text == "📦 Stock":
        if user_id not in ADMINS:
            await update.message.reply_text("❌ <i>Restricted to Administrators only.</i>", parse_mode="HTML")
            return
        await update.message.reply_text(stock_text(), parse_mode="HTML")

    elif text == "📞 Admin Help":
        await cmd_help(update, context)

async def send_referral_panel(update_or_query, context, user_id):
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    ref_count = db_get_referral_count(user_id)
    
    msg = (
        "╔═══════════════════════════╗\n"
        "║  🎁 <b>REFERRAL & EARN CASH</b> 🎁   ║\n"
        "╚═══════════════════════════╝\n"
        "✨ <i>বন্ধুদের ইনভাইট করুন এবং ফ্রি ওয়ালেট ব্যালেন্স জিতে নিন!</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Total Invited Friends:</b> <b>{ref_count} Members</b>\n"
        f"💰 <b>Total Referral Earnings:</b> <code>₹{ref_count * 1}.00</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💎 <b>HOW TO EARN ₹1 PER FRIEND:</b>\n"
        "1️⃣ আপনার বন্ধুদের নিচের রেফারেল লিংকটি পাঠান।\n"
        "2️⃣ আপনার লিংক দিয়ে যে-ই বটে প্রথমবার স্টার্ট করবে, সাথে সাথে আপনার একাউন্টে <b>₹১.০০</b> যোগ হবে!\n\n"
        f"🔗 <b>Your Exclusive Referral Link:</b>\n"
        f"<code>{ref_link}</code> <i>(Tap to Copy)</i>"
    )
    
    kbd = [
        [InlineKeyboardButton("📢 Share Referral Link", url=f"https://t.me/share/url?url={ref_link}&text={requests.utils.quote('🔥 Happy Gamer VIP Bot! Get 100% working game hack keys instantly. Join now:')}")],
        [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_main")]
    ]
    
    if hasattr(update_or_query, 'edit_message_text'):
        await update_or_query.edit_message_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kbd))
    else:
        await update_or_query.message.reply_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kbd))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    user_id = query.from_user.id
    name    = query.from_user.first_name
    await query.answer()

    if db_is_banned(user_id): return

    if query.data == "back_main":
        msg, inline_markup = get_main_dashboard(user_id, name)
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=inline_markup)
        return

    if query.data == "referral_menu":
        await send_referral_panel(query, context, user_id)
        return

    if query.data == "script_key_menu":
        if user_id not in ADMINS: return
        kbd = [
            [InlineKeyboardButton("⚡ 1 Day", callback_data="sgen_1"), InlineKeyboardButton("⚡ 3 Days", callback_data="sgen_3")],
            [InlineKeyboardButton("⚡ 7 Days", callback_data="sgen_7"), InlineKeyboardButton("⚡ 15 Days", callback_data="sgen_15")],
            [InlineKeyboardButton("👑 30 Days", callback_data="sgen_30"), InlineKeyboardButton("⚡ 60 Days", callback_data="sgen_60")],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║  🛠️ <b>SCRIPT KEY GENERATOR</b>   ║\n"
            "╚═══════════════════════════╝\n\n"
            "Select validity duration for the Script VIP Key:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(kbd)
        )
        return

    if query.data.startswith("sgen_"):
        if user_id not in ADMINS: return
        days = int(query.data.replace("sgen_", ""))
        context.user_data["script_gen_days"] = days
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║   📱 <b>DEVICE ID REQUIRED</b>     ║\n"
            "╚═══════════════════════════╝\n\n"
            f"Validity: <b>{days} Days</b>\n\n"
            "👉 Please type & send the <b>Target Device ID</b> (e.g. <code>b19fa2468bb7d5d2</code>) in chat:",
            parse_mode="HTML"
        )
        return

    # --- 👿 AIM-AI CARROM ENGINE MENU (DYNAMIC FROM DB) ---
    if query.data == "aim_ai_menu":
        p1 = get_price(user_id, "aim_1d"); p3 = get_price(user_id, "aim_3d")
        p7 = get_price(user_id, "aim_7d"); p15 = get_price(user_id, "aim_15d")
        p30 = get_price(user_id, "aim_30d"); p90 = get_price(user_id, "aim_90d")

        keyboard = [
            [InlineKeyboardButton(f"⚡ 01 Day (₹{p1})", callback_data="buy_aim_1d"), InlineKeyboardButton(f"⚡ 03 Days (₹{p3})", callback_data="buy_aim_3d")],
            [InlineKeyboardButton(f"🔥 07 Days (₹{p7})", callback_data="buy_aim_7d"), InlineKeyboardButton(f"⚡ 15 Days (₹{p15})", callback_data="buy_aim_15d")],
            [InlineKeyboardButton(f"👑 30 Days (₹{p30})", callback_data="buy_aim_30d"), InlineKeyboardButton(f"⚡ 90 Days (₹{p90})", callback_data="buy_aim_90d")],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_main")]
        ]
        text = (
            "╔═══════════════════════════╗\n"
            "║  👿 <b>A I M - A I ENGINE (CARROM)</b> 🔥 ║\n"
            "╚═══════════════════════════╝\n"
            "💎 <b>OFFICIAL CARROM PRICE CATALOG:</b>\n"
            f"• ⌛ 01 Day    ──── <code>₹{p1}</code>\n"
            f"• ⌛ 03 Days   ──── <code>₹{p3}</code>\n"
            f"• ⌛ 07 Days   ──── <code>₹{p7}</code> 🔥\n"
            f"• ⌛ 15 Days   ──── <code>₹{p15}</code>\n"
            f"• ⌛ 30 Days   ──── <code>₹{p30}</code> 👑\n"
            f"• ⌛ 90 Days   ──── <code>₹{p90}</code> ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 <i>100% Anti-Ban Safe Engine • Instant Auto Key</i>"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- AIM CARROM KING MENU ---
    if query.data == "aim_menu":
        keyboard = [
            [InlineKeyboardButton("🟢 AIM Normal Engine", callback_data="aim_normal")],
            [InlineKeyboardButton("🔥 AIM Premium (Auto Queue)", callback_data="aim_premium")],
            [InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║   👑 <b>AIM CARROM KING STORE</b>   ║\n"
            "╚═══════════════════════════╝\n\n"
            "Select your version to view pricing & slots:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if query.data == "aim_normal":
        p3 = get_price(user_id, "acn_3d"); p7 = get_price(user_id, "acn_7d"); p30 = get_price(user_id, "acn_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_acn_3d"), InlineKeyboardButton(f"⚡ 1 Week (₹{p7})", callback_data="buy_acn_7d")],
            [InlineKeyboardButton(f"⚡ 1 Month (₹{p30})", callback_data="buy_acn_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="aim_menu")]
        ]
        text = (
            "╔═══════════════════════════╗\n"
            "║   🟢 <b>AIM CARROM (NORMAL)</b>     ║\n"
            "╚═══════════════════════════╝\n"
            "💎 <b>Instant Pricing:</b>\n"
            f"• 3 Days ➜ <code>₹{p3}</code>\n"
            f"• 1 Week ➜ <code>₹{p7}</code>\n"
            f"• 1 Month ➜ <code>₹{p30}</code>"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "aim_premium":
        p3 = get_price(user_id, "acp_3d"); p7 = get_price(user_id, "acp_7d"); p30 = get_price(user_id, "acp_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_acp_3d"), InlineKeyboardButton(f"⚡ 1 Week (₹{p7})", callback_data="buy_acp_7d")],
            [InlineKeyboardButton(f"⚡ 1 Month (₹{p30})", callback_data="buy_acp_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="aim_menu")]
        ]
        text = (
            "╔═══════════════════════════╗\n"
            "║   🔥 <b>AIM CARROM (AUTO QUEUE)</b>  ║\n"
            "╚═══════════════════════════╝\n"
            "💎 <b>Instant Pricing:</b>\n"
            f"• 3 Days ➜ <code>₹{p3}</code>\n"
            f"• 1 Week ➜ <code>₹{p7}</code>\n"
            f"• 1 Month ➜ <code>₹{p30}</code>"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- KOS MENU ---
    if query.data == "kos_menu":
        keyboard = [
            [InlineKeyboardButton("🎱 8 Ball Pool Panel", callback_data="kos_8b")],
            [InlineKeyboardButton("🎯 Carrom Pool Panel", callback_data="kos_cp")],
            [InlineKeyboardButton("🔥 FreeFire Ultra Panel", callback_data="kos_ff")],
            [InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]
        ]
        await query.edit_message_text("Select target game:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_8b":
        p1 = get_price(user_id, "b1"); p7 = get_price(user_id, "b7"); p15 = get_price(user_id, "b15"); p30 = get_price(user_id, "b30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_b1"), InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_b7")],
            [InlineKeyboardButton(f"⚡ 15 Days (₹{p15})", callback_data="buy_b15"), InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_b30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        await query.edit_message_text(f"🎱 <b>KOS 8 BALL POOL VIP</b>\n• 1 Day ➜ ₹{p1} | 7 Days ➜ ₹{p7} | 15 Days ➜ ₹{p15} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_cp":
        p1 = get_price(user_id, "c1"); p7 = get_price(user_id, "c7"); p15 = get_price(user_id, "c15"); p30 = get_price(user_id, "c30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_c1"), InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_c7")],
            [InlineKeyboardButton(f"⚡ 15 Days (₹{p15})", callback_data="buy_c15"), InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_c30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        await query.edit_message_text(f"🎯 <b>KOS CARROM POOL VIP</b>\n• 1 Day ➜ ₹{p1} | 7 Days ➜ ₹{p7} | 15 Days ➜ ₹{p15} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_ff":
        p1 = get_price(user_id, "f1"); p7 = get_price(user_id, "f7"); p30 = get_price(user_id, "f30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_f1"), InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_f7")],
            [InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_f30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        await query.edit_message_text(f"🔥 <b>KOS FREEFIRE PANEL VIP</b>\n• 1 Day ➜ ₹{p1} | 7 Days ➜ ₹{p7} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # BITAIM MENU
    if query.data == "bitaim_menu":
        p7 = get_price(user_id, "bit7"); p30 = get_price(user_id, "bit30"); p90 = get_price(user_id, "bit90"); plt = get_price(user_id, "bitlt")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_bit7"), InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_bit30")],
            [InlineKeyboardButton(f"⚡ 3 Months (₹{p90})", callback_data="buy_bit90"), InlineKeyboardButton(f"⚡ Lifetime (₹{plt})", callback_data="buy_bitlt")],
            [InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]
        ]
        await query.edit_message_text(f"⚡ <b>BITAIM OFFICIAL SYSTEM</b>\n• 7 Days ➜ ₹{p7} | 30 Days ➜ ₹{p30} | 3 Months ➜ ₹{p90} | Lifetime ➜ ₹{plt}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # SNAKE MENU
    if query.data == "snk_menu":
        keyboard = [
            [InlineKeyboardButton("🎯 Snake Carrom Pool", callback_data="snkc_sub")],
            [InlineKeyboardButton("🎱 Snake 8 Ball Pool", callback_data="snk8_sub")],
            [InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]
        ]
        await query.edit_message_text("Select Snake variant:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "snkc_sub":
        p3 = get_price(user_id, "snkc_3d"); p10 = get_price(user_id, "snkc_10d"); p30 = get_price(user_id, "snkc_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_snkc_3d"), InlineKeyboardButton(f"⚡ 10 Days (₹{p10})", callback_data="buy_snkc_10d")],
            [InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_snkc_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="snk_menu")]
        ]
        await query.edit_message_text(f"🐍 <b>SNAKE CARROM POOL</b>\n• 3 Days ➜ ₹{p3} | 10 Days ➜ ₹{p10} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "snk8_sub":
        p3 = get_price(user_id, "snk8_3d"); p10 = get_price(user_id, "snk8_10d"); p30 = get_price(user_id, "snk8_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_snk8_3d"), InlineKeyboardButton(f"⚡ 10 Days (₹{p10})", callback_data="buy_snk8_10d")],
            [InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_snk8_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="snk_menu")]
        ]
        await query.edit_message_text(f"🐍 <b>SNAKE 8 BALL POOL</b>\n• 3 Days ➜ ₹{p3} | 10 Days ➜ ₹{p10} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- BUYING & CONFIRMATION ---
    if query.data.startswith("buy_"):
        plan_id = query.data.replace("buy_", "")
        plan = db_get_plan(plan_id)
        if not plan:
            await query.answer("Invalid plan", show_alert=True)
            return
        price = get_price(user_id, plan_id)
        pending_orders[user_id] = plan_id
        keyboard = [
            [InlineKeyboardButton("⚡ Confirm & Deliver Key", callback_data="confirm_buy")],
            [InlineKeyboardButton("❌ Cancel Order", callback_data="back_main")]
        ]
        confirm_text = f"🛒 <b>Confirm Purchase</b>\n🎮 Item: {plan['game']} ({plan['label']})\n💰 Price: <code>₹{price}</code>"
        await query.edit_message_text(confirm_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "confirm_buy":
        if user_id not in pending_orders:
            await query.edit_message_text("⚠️ <b>No active order session found!</b>", parse_mode="HTML")
            return
        plan_id = pending_orders.pop(user_id)
        plan    = db_get_plan(plan_id)
        price   = get_price(user_id, plan_id)
        bal     = db_get_balance(user_id)

        if bal < price:
            await query.edit_message_text(
                f"❌ <b>INSUFFICIENT FUNDS!</b>\nRequired: ₹{price} | Your Bal: ₹{bal}\n👉 Please tap Add Balance.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Add Balance Now", callback_data="add_bal")]])
            )
            return

        if "bit" in plan_id:
            awaiting_gmail[user_id] = plan_id
            await query.edit_message_text("📧 Please send your <b>Google Play Gmail ID</b> in chat:", parse_mode="HTML")
            return

        if db_count_keys(plan_id) == 0:
            await query.edit_message_text(f"⚠️ <b>OUT OF STOCK!</b> Contact {ADMIN_USERNAME} for keys.", parse_mode="HTML")
            return

        new_bal = bal - price
        db_set_balance(user_id, new_bal)
        key = db_pop_key(plan_id)
        gname = plan['game'] if plan else "VIP Hack"
        glabel = plan['label'] if plan else plan_id
        db_record_order(user_id, gname, glabel, price, key)

        success_receipt = (
            "╔═══════════════════════════╗\n"
            "║  🎉 <b>PURCHASE SUCCESSFUL</b>     ║\n"
            "╚═══════════════════════════╝\n"
            f"👤 <b>Customer:</b> {name}\n"
            f"🎮 <b>Item:</b> {gname} ({glabel})\n"
            f"💰 <b>Amount Paid:</b> <code>₹{price}</code>\n"
            f"💳 <b>Remaining Bal:</b> <code>₹{new_bal}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔑 <b>YOUR VIP KEY:</b> <i>(Tap to Copy)</i>\n\n"
            f"<code>{key}</code>\n\n"
            "✨ <i>Enjoy your game!</i> 🚀"
        )
        await query.edit_message_text(success_receipt, parse_mode="HTML")
        return

    if query.data == "orders_hist":
        orders = db_get_user_orders(user_id)
        if not orders:
            await query.edit_message_text("📜 No purchase history yet!", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]]))
            return
        msg = "📜 <b>YOUR LAST 10 PURCHASES:</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for o in orders:
            msg += f"💎 <b>{o['game']} ({o['plan_label']})</b>\n  💰 Paid: ₹{o['price']} | 🕒 {o['timestamp']}\n  🔑 Key: <code>{o['key_delivered']}</code>\n\n"
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]]))
        return

    if query.data == "add_bal":
        caption = get_payment_caption()
        if os.path.exists(QR_PATH):
            with open(QR_PATH, "rb") as f:
                await context.bot.send_photo(chat_id=user_id, photo=f, caption=caption, parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=user_id, text=caption, parse_mode="HTML")
        return

    if query.data == "become_reseller":
        await query.edit_message_text(f"👑 <b>Contact Founder for Reseller Panel:</b> {ADMIN_USERNAME}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]]))
        return

    if query.data.startswith("pay_"):
        parts     = query.data.split("_")
        target_id = int(parts[1])
        action    = parts[2]
        if action == "reject":
            req = payment_requests.pop(target_id, None)
            if req and req.get("task"): req["task"].cancel()
            try: await context.bot.send_message(target_id, "❌ <b>Your payment verification was rejected.</b>", parse_mode="HTML")
            except Exception: pass
            await query.edit_message_caption("❌ <b>Payment Rejected</b>", parse_mode="HTML")
            return
        amount = int(action)
        req = payment_requests.pop(target_id, None)
        if req and req.get("task"): req["task"].cancel()

        new_bal = db_add_balance(target_id, amount)
        try:
            await context.bot.send_message(
                target_id,
                f"🎉 <b>PAYMENT APPROVED!</b>\n💰 <b>₹{amount}</b> has been added to your wallet!\n💳 <b>Current Balance:</b> <code>₹{new_bal}.00</code>",
                parse_mode="HTML"
            )
        except Exception: pass
        await query.edit_message_caption(f"✅ <b>Approved ₹{amount} for User {target_id}</b>", parse_mode="HTML")
        return

async def expire_payment(user_id, context):
    await asyncio.sleep(PAYMENT_TIMEOUT)
    if user_id in payment_requests:
        del payment_requests[user_id]
        try: await context.bot.send_message(user_id, "⚠️ Payment verification session timed out. Please submit your receipt again.")
        except Exception: pass

# --- ALL ADMIN COMMANDS ---
async def cmd_resetdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    init_db(force_fresh=True)
    push_data_to_github()
    await update.message.reply_text("🧹 <b>DATABASE AND CLOUD DATA FULLY RESET!</b>\nAll user balances and data reset to ₹0.", parse_mode="HTML")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    help_text = (
        "╔═══════════════════════════════════════╗\n"
        "║   👑 <b>ADMIN FULL CONTROL & KEY CODES</b>   ║\n"
        "╚═══════════════════════════════════════╝\n\n"
        "🔑 <b>কিভাবে কি (KEY) অ্যাড করবেন (/addkey):</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👿 <b>AIM-AI CARROM:</b>\n"
        "• <code>/addkey aim_1d YOUR_KEY</code> (01 Day)\n"
        "• <code>/addkey aim_3d YOUR_KEY</code> (03 Days)\n"
        "• <code>/addkey aim_7d YOUR_KEY</code> (07 Days)\n"
        "• <code>/addkey aim_15d YOUR_KEY</code> (15 Days)\n"
        "• <code>/addkey aim_30d YOUR_KEY</code> (30 Days)\n"
        "• <code>/addkey aim_90d YOUR_KEY</code> (90 Days)\n\n"
        "👑 <b>AIM CARROM KING (Normal & Premium):</b>\n"
        "• <code>/addkey acn_3d YOUR_KEY</code> (Normal 3 Days)\n"
        "• <code>/addkey acn_7d YOUR_KEY</code> (Normal 1 Week)\n"
        "• <code>/addkey acn_30d YOUR_KEY</code> (Normal 1 Month)\n"
        "• <code>/addkey acp_3d YOUR_KEY</code> (Premium 3 Days)\n"
        "• <code>/addkey acp_7d YOUR_KEY</code> (Premium 1 Week)\n"
        "• <code>/addkey acp_30d YOUR_KEY</code> (Premium 1 Month)\n\n"
        "🔥 <b>KOS ENGINE:</b>\n"
        "• <b>Carrom:</b> <code>/addkey c1 KEY</code> | <code>/addkey c7 KEY</code> | <code>/addkey c15 KEY</code> | <code>/addkey c30 KEY</code>\n"
        "• <b>8 Ball:</b> <code>/addkey b1 KEY</code> | <code>/addkey b7 KEY</code> | <code>/addkey b15 KEY</code> | <code>/addkey b30 KEY</code>\n"
        "• <b>FreeFire:</b> <code>/addkey f1 KEY</code> | <code>/addkey f7 KEY</code> | <code>/addkey f30 KEY</code>\n\n"
        "🐍 <b>SNAKE ENGINE:</b>\n"
        "• <b>Carrom:</b> <code>/addkey snkc_3d KEY</code> | <code>/addkey snkc_10d KEY</code> | <code>/addkey snkc_30d KEY</code>\n"
        "• <b>8 Ball:</b> <code>/addkey snk8_3d KEY</code> | <code>/addkey snk8_10d KEY</code> | <code>/addkey snk8_30d KEY</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛠️ <b>অন্যান্য এডমিন কমান্ড:</b>\n"
        "• <code>/resetdata</code> ➜ সব ব্যালেন্স ও ডাটা 0 করে ফ্রেশ করা\n"
        "• <code>/scriptkey &lt;days&gt; &lt;device_id&gt;</code> ➜ অটো স্ক্রিপ্ট কি জেনারেট\n"
        "• <code>/cleangist</code> ➜ Gist এর পুরনো এক্সপায়ার কি ডিলিট করা\n"
        "• <code>/testgist</code> ➜ Gist কানেকশন টেস্ট\n"
        "• <code>/stock</code> ➜ লাইভ স্টক চেক\n"
        "• <code>/prices</code> ➜ সব প্রাইস তালিকা\n"
        "• <code>/add &lt;id&gt; &lt;amount&gt;</code> ➜ ব্যালেন্স দেওয়া\n"
        "• <code>/broadcast &lt;text&gt;</code> ➜ সব ইউজারকে মেসেজ\n"
        "• <code>/ban &lt;id&gt;</code> / <code>/unban &lt;id&gt;</code> ➜ ব্যান/আনব্যান\n"
        "• <code>/reply &lt;id&gt; &lt;text&gt;</code> ➜ ইউজারকে সরাসরি রিপ্লাই\n"
        "• <code>/deliver &lt;id&gt; &lt;key&gt;</code> ➜ কি ডেলিভারি করা\n"
        "• <code>/setprice &lt;code&gt; &lt;reg&gt; &lt;res&gt;</code> ➜ দাম পরিবর্তন\n"
        "• <code>/addreseller &lt;id&gt;</code> / <code>/removereseller &lt;id&gt;</code> ➜ রিসেলার কন্ট্রোল\n"
        "• <code>/resellers</code> ➜ সব রিসেলারের তালিকা"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

async def cmd_scriptkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    if len(context.args) < 2:
        await update.message.reply_text("💡 <b>Format:</b> <code>/scriptkey &lt;days&gt; &lt;device_id&gt;</code>", parse_mode="HTML")
        return
    try:
        days = int(context.args[0])
        device_id = context.args[1].strip()
        vip_key = generate_short_key()
        
        status_msg = await update.message.reply_text("⏳ <i>Syncing with GitHub Gist & Auto-Pruning Expired Keys...</i>", parse_mode="HTML")
        success, expiry, err = append_to_gist(vip_key, device_id, days)
        
        if success:
            receipt_msg = (
                "╔═══════════════════════════╗\n"
                "║  👑 <b>SCRIPT KEY GENERATED!</b>   ║\n"
                "╚═══════════════════════════╝\n"
                f"👤 <b>Admin:</b> {update.effective_user.first_name}\n"
                f"⏳ <b>Validity:</b> {days} Days (Expires: <code>{expiry}</code>)\n"
                f"📱 <b>Device ID:</b> <code>{device_id}</code>\n"
                "☁️ <b>GitHub Gist:</b> <i>Updated & Cleaned ✅</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔑 <b>YOUR VIP KEY:</b> <i>(👇 Tap to Copy)</i>\n\n"
                f"<code>{vip_key}</code>"
            )
            await status_msg.edit_text(receipt_msg, parse_mode="HTML")
        else:
            await status_msg.edit_text(f"❌ <b>GitHub Gist Update Failed:</b> <code>{err}</code>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode="HTML")

async def cmd_cleangist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    purged = purge_expired_gist_keys()
    await update.message.reply_text(f"🧹 <b>GitHub Gist Cleaned!</b>\nRemoved <code>{purged}</code> expired keys.", parse_mode="HTML")

async def cmd_testgist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    if not GITHUB_TOKEN:
        await update.message.reply_text("❌ GitHub Token is not configured.", parse_mode="HTML")
        return
    headers = get_auth_headers()
    res = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers, timeout=10)
    if res.status_code == 200:
        await update.message.reply_text("✅ <b>GitHub Gist API Connection Successful!</b>", parse_mode="HTML")
    else:
        await update.message.reply_text(f"❌ <b>GitHub Error ({res.status_code}):</b> {res.text}", parse_mode="HTML")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    if not context.args:
        await update.message.reply_text("💡 <b>Usage:</b> <code>/broadcast &lt;Text&gt;</code>", parse_mode="HTML")
        return
    msg = " ".join(context.args)
    users = db_get_all_users()
    for uid in users:
        if db_is_banned(uid): continue
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>OFFICIAL ANNOUNCEMENT:</b>\n\n{msg}", parse_mode="HTML")
            await asyncio.sleep(0.05)
        except Exception: pass
    await update.message.reply_text(f"✅ Broadcast sent to {len(users)} users.", parse_mode="HTML")

async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_ban_user(uid)
        await update.message.reply_text(f"🚨 User {uid} banned.", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/ban &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_unban_user(uid)
        await update.message.reply_text(f"✅ User {uid} unbanned.", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/unban &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        target_id = int(context.args[0])
        msg_text  = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=target_id, text=f"📩 <b>Official Admin Message:</b>\n\n{msg_text}", parse_mode="HTML")
        await update.message.reply_text(f"✅ Message sent to <code>{target_id}</code>", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/reply &lt;user_id&gt; &lt;message&gt;</code>", parse_mode="HTML")

async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0]); amount = int(context.args[1])
        new_bal = db_add_balance(uid, amount)
        await update.message.reply_text(f"✅ Credited ₹{amount} to <code>{uid}</code>\n💳 New Balance: ₹{new_bal}", parse_mode="HTML")
        try: await context.bot.send_message(uid, f"🎉 <b>Admin added ₹{amount} to your wallet!</b>\n💳 Current Balance: ₹{new_bal}", parse_mode="HTML")
        except Exception: pass
    except Exception: await update.message.reply_text("Usage: <code>/add &lt;user_id&gt; &lt;amount&gt;</code>", parse_mode="HTML")

async def cmd_addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        plan = context.args[0].lower(); new_key = context.args[1]
        db_add_key(plan, new_key)
        await update.message.reply_text(f"✅ <b>Stock Added for {plan}:</b> <code>{new_key}</code>\n📦 Total Stock: {db_count_keys(plan)}", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/addkey &lt;plan_code&gt; &lt;key&gt;</code>", parse_mode="HTML")

async def cmd_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    await update.message.reply_text(stock_text(), parse_mode="HTML")

async def cmd_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    await update.message.reply_text(price_list_text(), parse_mode="HTML")

async def cmd_deliver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: <code>/deliver &lt;user_id&gt; &lt;key&gt;</code>", parse_mode="HTML"); return
    uid = int(context.args[0]); key = " ".join(context.args[1:])
    await context.bot.send_message(uid, f"🔑 <b>YOUR VIP KEY:</b>\n\n<code>{key}</code>", parse_mode="HTML")
    await update.message.reply_text(f"✅ Key delivered to <code>{uid}</code>", parse_mode="HTML")

async def cmd_setprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        plan = context.args[0].lower(); reg = int(context.args[1]); res = int(context.args[2])
        db_set_price(plan, reg, res)
        await update.message.reply_text(f"✅ <b>Price Updated for {plan}:</b> Regular ₹{reg}, Reseller ₹{res}", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/setprice &lt;plan_code&gt; &lt;regular&gt; &lt;reseller&gt;</code>", parse_mode="HTML")

async def cmd_addreseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_add_reseller(uid)
        await update.message.reply_text(f"👑 User {uid} elevated to Official VIP Reseller!", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/addreseller &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_removereseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_remove_reseller(uid)
        await update.message.reply_text(f"❌ User {uid} demoted from Resellers", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/removereseller &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_resellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    rlist = db_all_resellers()
    if not rlist:
        await update.message.reply_text("<i>No resellers registered yet.</i>", parse_mode="HTML")
        return
    await update.message.reply_text("👑 <b>OFFICIAL RESELLERS:</b>\n" + "\n".join(f"• <code>{r}</code>" for r in rlist), parse_mode="HTML")

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set.")
        exit(1)
    # Start with fresh DB on initial setup
    init_db(force_fresh=True)
    push_data_to_github()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",          start))
    app.add_handler(CommandHandler("help",           cmd_help))
    app.add_handler(CommandHandler("resetdata",      cmd_resetdata))
    app.add_handler(CommandHandler("cleardb",        cmd_resetdata))
    app.add_handler(CommandHandler("referral",       send_referral_panel))
    app.add_handler(CommandHandler("ref",            send_referral_panel))
    app.add_handler(CommandHandler("broadcast",      cmd_broadcast))
    app.add_handler(CommandHandler("sendall",        cmd_broadcast))
    app.add_handler(CommandHandler("scriptkey",      cmd_scriptkey))
    app.add_handler(CommandHandler("cleangist",      cmd_cleangist))
    app.add_handler(CommandHandler("testgist",       cmd_testgist))
    app.add_handler(CommandHandler("ban",            cmd_ban))
    app.add_handler(CommandHandler("unban",          cmd_unban))
    app.add_handler(CommandHandler("reply",          cmd_reply))
    app.add_handler(CommandHandler("add",            cmd_add))
    app.add_handler(CommandHandler("addkey",         cmd_addkey))
    app.add_handler(CommandHandler("stock",          cmd_stock))
    app.add_handler(CommandHandler("prices",         cmd_prices))
    app.add_handler(CommandHandler("deliver",        cmd_deliver))
    app.add_handler(CommandHandler("setprice",       cmd_setprice))
    app.add_handler(CommandHandler("addreseller",    cmd_addreseller))
    app.add_handler(CommandHandler("removereseller", cmd_removereseller))
    app.add_handler(CommandHandler("resellers",      cmd_resellers))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    print("👑 Happy Gamer VIP Telegram Engine Running 24/7 (Fresh & Clean Database)...")
    app.run_polling()
