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

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO  = os.environ.get("GITHUB_REPO", "sagarhalder7865-hub/my-telegram-bot")
DATA_FILE    = "bot_data.json"

# Gist Config for Script Key Automation
GIST_ID = "e155b8f93a7476556fa1c8b2dfc9b164"
FILE_NAME = "status.txt"

DATA_DIR = "/opt/render/project/src" if os.path.exists("/opt/render/project/src") else os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(DATA_DIR, "bot_data.db")
QR_PATH  = os.path.join(DATA_DIR, "payment_qr.png")

if not os.path.exists(QR_PATH):
    QR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "payment_qr.png")

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
            <p style="color:#00ff66;">⚡ Status: Running 24/7 Ultra High Speed Online</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

Thread(target=run_web_server, daemon=True).start()

# --- GIST AUTO-UPDATER FOR SCRIPT KEYS ---
def append_to_gist(device_id, days):
    try:
        expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y%m%d")
        new_entry = f"HGTOKEN=={expiry}={device_id}"
        
        token = GITHUB_TOKEN.strip() if GITHUB_TOKEN else ""
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "HappyGamerTelegramBot/1.0"
        }
        
        # 1. Fetch current content directly from Gist API
        get_url = f"https://api.github.com/gists/{GIST_ID}"
        get_res = requests.get(get_url, headers=headers)
        
        if get_res.status_code != 200:
            # Fallback to token prefix
            headers["Authorization"] = f"token {token}"
            get_res = requests.get(get_url, headers=headers)
            
        current_content = ""
        if get_res.status_code == 200:
            files_data = get_res.json().get("files", {})
            if FILE_NAME in files_data:
                current_content = files_data[FILE_NAME].get("content", "")
        else:
            # Fallback to public raw read
            raw_url = f"https://gist.githubusercontent.com/sagarhalder7865-hub/{GIST_ID}/raw/{FILE_NAME}?t={int(time.time())}"
            raw_res = requests.get(raw_url)
            if raw_res.status_code == 200:
                current_content = raw_res.text

        # Combine with new line
        if current_content:
            updated_content = current_content.strip() + "\n" + new_entry
        else:
            updated_content = "STATUS=ON\n" + new_entry

        # 2. Patch to GitHub Gist
        patch_payload = {
            "files": {
                FILE_NAME: {
                    "content": updated_content
                }
            }
        }
        
        patch_res = requests.patch(get_url, headers=headers, json=patch_payload)
        
        if patch_res.status_code in [200, 201]:
            return True, expiry, None
        else:
            err_msg = patch_res.json().get("message", patch_res.text)
            return False, expiry, f"Status {patch_res.status_code}: {err_msg}"
    except Exception as e:
        return False, None, str(e)

# --- GITHUB CLOUD AUTO-SYNC ---
def push_data_to_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return
    try:
        data_dump = export_database_json()
        content_str = json.dumps(data_dump, indent=2)
        content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        
        token = GITHUB_TOKEN.strip()
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "HappyGamerTelegramBot"
        }
        
        sha = None
        get_res = requests.get(url, headers=headers)
        if get_res.status_code == 200:
            sha = get_res.json().get("sha")
            
        payload = {
            "message": "Auto-sync VIP bot data from Telegram Engine",
            "content": content_b64
        }
        if sha:
            payload["sha"] = sha
            
        requests.put(url, headers=headers, json=payload)
    except Exception as e:
        print(f"GitHub Sync Error: {e}")

def pull_data_from_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return None
    try:
        token = GITHUB_TOKEN.strip()
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "HappyGamerTelegramBot"
        }
        res = requests.get(url, headers=headers)
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
    return {
        "users": users,
        "balances": balances,
        "keys": keys,
        "resellers": resellers,
        "prices": prices,
        "order_history": orders
    }

# --- DATABASE SETUP ---
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
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
        """)
        
        gh_data = pull_data_from_github()
        if gh_data:
            db.execute("DELETE FROM users")
            db.execute("DELETE FROM balances")
            db.execute("DELETE FROM keys")
            db.execute("DELETE FROM resellers")
            db.execute("DELETE FROM prices")
            db.execute("DELETE FROM order_history")
            
            for u in gh_data.get("users", []):
                db.execute("INSERT OR REPLACE INTO users (user_id, first_name, username) VALUES (?,?,?)", (u["user_id"], u.get("first_name",""), u.get("username","")))
            for b in gh_data.get("balances", []):
                db.execute("INSERT OR REPLACE INTO balances (user_id, amount) VALUES (?,?)", (b["user_id"], b["amount"]))
            for k in gh_data.get("keys", []):
                db.execute("INSERT OR REPLACE INTO keys (id, plan, key) VALUES (?,?,?)", (k["id"], k["plan"], k["key"]))
            for r in gh_data.get("resellers", []):
                db.execute("INSERT OR REPLACE INTO resellers (user_id) VALUES (?)", (r["user_id"],))
            for p in gh_data.get("prices", []):
                db.execute("INSERT OR REPLACE INTO prices (plan, game, label, regular, reseller) VALUES (?,?,?,?,?)",
                           (p["plan"], p["game"], p["label"], p["regular"], p["reseller"]))
            for o in gh_data.get("order_history", []):
                db.execute("INSERT OR REPLACE INTO order_history (id, user_id, game, plan_label, price, key_delivered, timestamp) VALUES (?,?,?,?,?,?,?)",
                           (o["id"], o["user_id"], o["game"], o["plan_label"], o["price"], o["key_delivered"], o["timestamp"]))
        else:
            db.execute("DELETE FROM prices")
            defaults = [
                ("acn_3d",  "AIM Carrom Normal", "3 Days",  250, 220),
                ("acn_7d",  "AIM Carrom Normal", "1 Week",  360, 330),
                ("acn_30d", "AIM Carrom Normal", "1 Month", 1000, 950),
                ("acp_3d",  "AIM Carrom Premium", "3 Days",  310, 280),
                ("acp_7d",  "AIM Carrom Premium", "1 Week",  480, 460),
                ("acp_30d", "AIM Carrom Premium", "1 Month", 1250, 1180),
                ("b1",  "KOS 8 Ball", "1 Day",   180, 150),
                ("b7",  "KOS 8 Ball", "7 Days",  500, 450),
                ("b15", "KOS 8 Ball", "15 Days", 900, 800),
                ("b30", "KOS 8 Ball", "30 Days", 1600, 1400),
                ("c1",  "KOS Carrom", "1 Day",   120, 100),
                ("c7",  "KOS Carrom", "7 Days",  300, 230),
                ("c15", "KOS Carrom", "15 Days", 490, 400),
                ("c30", "KOS Carrom", "30 Days", 800, 670),
                ("f1",  "KOS FreeFire Panel", "1 Day",   200, 180),
                ("f7",  "KOS FreeFire Panel", "7 Days",  600, 500),
                ("f30", "KOS FreeFire Panel", "30 Days", 1800, 1500),
                ("bit7",  "Bitaim ⚡", "7 Days",    65, 50),
                ("bit30", "Bitaim ⚡", "30 Days",   165, 160),
                ("bit90", "Bitaim ⚡", "3 Months",  380, 340),
                ("bitlt", "Bitaim ⚡", "Life Time", 1860, 1790),
                ("snkc_3d",  "Snake Carrom", "3 Days",  190, 160),
                ("snkc_10d", "Snake Carrom", "10 Days", 450, 400),
                ("snkc_30d", "Snake Carrom", "30 Days", 900, 830),
                ("snk8_3d",  "Snake 8Ball", "3 Days",  320, 290),
                ("snk8_10d", "Snake 8Ball", "10 Days", 650, 630),
                ("snk8_30d", "Snake 8Ball", "30 Days", 1200, 1150),
            ]
            db.executemany(
                "INSERT INTO prices (plan,game,label,regular,reseller) VALUES (?,?,?,?,?)",
                defaults
            )

def db_register_user(user_id, first_name, username):
    with get_db() as db:
        db.execute(
            "INSERT INTO users (user_id, first_name, username) VALUES (?,?,?) ON CONFLICT(user_id) DO UPDATE SET first_name=?, username=?",
            (user_id, first_name, username, first_name, username)
        )
    push_data_to_github()

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
        return db.execute("SELECT * FROM prices WHERE plan=?", (plan_id,)).fetchone()

def db_set_price(plan_id, regular, reseller):
    with get_db() as db:
        db.execute("UPDATE prices SET regular=?, reseller=? WHERE plan=?", (regular, reseller, plan_id))
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
    p = db_get_plan(plan_id)
    if not p: return 0
    return p["reseller"] if db_is_reseller(user_id) else p["regular"]

def stock_text():
    lines = [
        "╔═══════════════════════════╗",
        "║  📦 <b>LIVE WAREHOUSE INVENTORY</b>  ║",
        "╚═══════════════════════════╝",
        "\n👑 <b>AIM CARROM KING INVENTORY:</b>"
    ]
    for p in ["acn_3d","acn_7d","acn_30d","acp_3d","acp_7d","acp_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  💎 <code>{plan['game']} ({plan['label']})</code> ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n🔥 <b>KOS ENGINE KEYS:</b>")
    for p in ["b1","b7","b15","b30","c1","c7","c15","c30","f1","f7","f30"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  ⚡ <code>{plan['game']} ({plan['label']})</code> ➜ <b>{db_count_keys(p)} Pcs</b>")
    
    lines.append("\n⚡ <b>BITAIM HACK SLOTS:</b>")
    for p in ["bit7","bit30","bit90","bitlt"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  🔮 <code>Bitaim {plan['label']:10}</code> ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n🐍 <b>SNAKE ENGINE SLOTS:</b>")
    for p in ["snkc_3d","snkc_10d","snkc_30d","snk8_3d","snk8_10d","snk8_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  🐍 <code>{plan['game']} ({plan['label']})</code> ➜ <b>{db_count_keys(p)} Pcs</b>")
        
    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

def price_list_text():
    lines = [
        "╔═══════════════════════════╗",
        "║  💎 <b>OFFICIAL VIP PRICE CATALOG</b> ║",
        "╚═══════════════════════════╝",
        "\n👑 <b>AIM CARROM KING (Normal):</b>"
    ]
    for p in ["acn_3d","acn_7d","acn_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  💎 <b>{plan['label']}</b> ➜ <code>₹{plan['regular']}</code> <i>[Reseller: ₹{plan['reseller']}]</i>")
        
    lines.append("\n👑 <b>AIM CARROM KING (Premium Auto Queue):</b>")
    for p in ["acp_3d","acp_7d","acp_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  ⚡ <b>{plan['label']}</b> ➜ <code>₹{plan['regular']}</code> <i>[Reseller: ₹{plan['reseller']}]</i>")

    lines.append("\n🔥 <b>KOS ENGINE VIP KEYS:</b>")
    for p in ["b1","b7","b15","b30","c1","c7","c15","c30","f1","f7","f30"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  🔮 <b>{plan['game']} {plan['label']}</b> ➜ <code>₹{plan['regular']}</code> <i>[Reseller: ₹{plan['reseller']}]</i>")
    
    lines.append("\n⚡ <b>BITAIM PREMIUM HACK:</b>")
    for p in ["bit7","bit30","bit90","bitlt"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  🎯 <b>Bitaim {plan['label']}</b> ➜ <code>₹{plan['regular']}</code> <i>[Reseller: ₹{plan['reseller']}]</i>")

    lines.append("\n🐍 <b>SNAKE ENGINE VIP:</b>")
    for p in ["snkc_3d","snkc_10d","snkc_30d","snk8_3d","snk8_10d","snk8_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  🐍 <b>{plan['game']} {plan['label']}</b> ➜ <code>₹{plan['regular']}</code> <i>[Reseller: ₹{plan['reseller']}]</i>")
        
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
        [InlineKeyboardButton("👑 AIM CARROM KING", callback_data="aim_menu")],
        [InlineKeyboardButton("🔥 KOS Engine Keys", callback_data="kos_menu"), InlineKeyboardButton("⚡ Bitaim Hack", callback_data="bitaim_menu")],
        [InlineKeyboardButton("🐍 Snake Engine", callback_data="snk_menu")],
        [InlineKeyboardButton("💳 ➕ Add Balance", callback_data="add_bal"), InlineKeyboardButton("📜 🛍️ My Orders", callback_data="orders_hist")],
        [InlineKeyboardButton("💎 👑 Apply For Reseller Panel", callback_data="become_reseller")]
    ]
    
    if uid in ADMINS:
        inline_kbd.insert(4, [InlineKeyboardButton("🛠️ ⚡ Script Key Generator [Admin]", callback_data="script_key_menu")])

    msg = (
        f"╔═══════════════════════════╗\n"
        f"║  👑 <b>HAPPY GAMER VIP STORE</b> 👑  ║\n"
        f"╚═══════════════════════════╝\n"
        f"✨ <i>The Most Advanced Instant Key Automation System</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Client:</b> <code>{name}</code>\n"
        f"💰 <b>Wallet Balance:</b> <code>₹{bal}.00</code> 💳\n"
        f"🛡️ <b>Account Tier:</b> <b>{role}</b>\n"
        f"📦 <b>Recent Purchase:</b> <i>{last_buy}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📖 <b>Instant Buying Guide (কীভাবে কি কিনবেন):</b>\n"
        f"1️⃣ <b>Add Balance</b> বাটন চেপে অ্যাকাউন্টে টাকা যোগ করুন।\n"
        f"2️⃣ আপনার পছন্দের <b>VIP Hack Engine</b> সিলেক্ট করুন।\n"
        f"3️⃣ <b>Confirm</b> করলেই তাৎক্ষণিক ১-ট্যাপ কপি কি পেয়ে যাবেন!"
    )
    return msg, InlineKeyboardMarkup(inline_kbd)

def get_reply_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 All Hack Key buy", "Check Balance 💰"],
        ["➕Add Balance 💰", "📦 Stock"],
        ["📞 Admin Help"]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username or ""
    
    db_register_user(uid, name, username)
    
    msg, inline_markup = get_main_dashboard(uid, name)
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=get_reply_keyboard())
    await update.message.reply_text("👇 <b>Select your VIP Hack to Proceed:</b>", parse_mode="HTML", reply_markup=inline_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text    = update.message.text
    user_id = update.effective_user.id
    name    = update.effective_user.first_name
    username = update.effective_user.username or ""

    db_register_user(user_id, name, username)

    # 1. ADMIN SCRIPT KEY GENERATION VIA CHAT INPUT
    if user_id in ADMINS and "script_gen_days" in context.user_data:
        days = context.user_data.pop("script_gen_days")
        device_id = text.strip()
        
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        vip_key = f"HGVIP{days}{random_code}"
        
        status_msg = await update.message.reply_text("⏳ <i>Updating GitHub Gist status.txt & Generating Key...</i>", parse_mode="HTML")
        
        success, expiry, err = append_to_gist(device_id, days)
        
        if success:
            receipt_msg = (
                f"╔═══════════════════════════╗\n"
                f"║  👑 <b>SCRIPT KEY GENERATED!</b>   ║\n"
                f"╚═══════════════════════════╝\n"
                f"👤 <b>Admin:</b> {name}\n"
                f"⏳ <b>Validity:</b> {days} Days (Expires: <code>{expiry}</code>)\n"
                f"📱 <b>Device ID:</b> <code>{device_id}</code>\n"
                f"☁️ <b>GitHub Gist:</b> <i>Updated Successfully ✅</i>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔑 <b>YOUR VIP KEY:</b> <i>(👇 Tap to Copy)</i>\n\n"
                f"<code>{vip_key}</code>"
            )
            await status_msg.edit_text(receipt_msg, parse_mode="HTML")
        else:
            await status_msg.edit_text(
                f"❌ <b>GitHub Gist Update Failed!</b>\n\n"
                f"<b>Reason:</b> <code>{err}</code>\n\n"
                f"👉 Make sure your <b>GITHUB_TOKEN</b> has the <code>gist</code> permission.",
                parse_mode="HTML"
            )
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
        db_record_order(user_id, plan['game'], plan['label'], price, f"Gmail: {text}")

        success_msg = (
            f"╔═══════════════════════════╗\n"
            f"║  🎉 <b>BITAIM ORDER CONFIRMED</b>  ║\n"
            f"╚═══════════════════════════╝\n"
            f"🎮 <b>Item:</b> {plan['game']} ({plan['label']})\n"
            f"💰 <b>Charged:</b> ₹{price}\n"
            f"📧 <b>Account Gmail:</b> <code>{text}</code>\n"
            f"💳 <b>Remaining Balance:</b> ₹{new_bal}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <i>Admin has been notified. Activation inside 10 minutes!</i>"
        )

        await update.message.reply_text(success_msg, parse_mode="HTML")

        try:
            for admin_id in ADMINS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"🚨 <b>NEW BITAIM ACTIVATION DISPATCH!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 <b>Client:</b> {user_id} ({name})\n"
                        f"🎮 <b>Plan:</b> {plan['game']} ({plan['label']})\n"
                        f"💰 <b>Amount:</b> ₹{price}\n"
                        f"📧 <b>User Gmail:</b> <code>{text}</code>"
                    ),
                    parse_mode="HTML"
                )
        except Exception: pass
        return

    if text in ["/start", "🔑 All Hack Key buy"]:
        msg, inline_markup = get_main_dashboard(user_id, name)
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=inline_markup)

    elif text in ["Check Balance 💰", "💰 Balance"]:
        bal = db_get_balance(user_id)
        role = " [👑 VIP Reseller]" if db_is_reseller(user_id) else " [Customer]"
        await update.message.reply_text(
            f"╔═══════════════════════════╗\n"
            f"║      💳 <b>WALLET OVERVIEW</b>       ║\n"
            f"╚═══════════════════════════╝\n"
            f"💰 <b>Available Balance:</b> <code>₹{bal}.00</code>\n"
            f"🏷️ <b>Account Rank:</b> <b>{role}</b>\n\n"
            f"👉 <i>Click 'Add Balance' to deposit instant funds!</i>",
            parse_mode="HTML"
        )

    elif text in ["➕Add Balance 💰", "➕ Add Balance"]:
        caption = (
            "╔═══════════════════════════╗\n"
            "║    💳 <b>SECURE UPI PAYMENT</b>     ║\n"
            "╚═══════════════════════════╝\n\n"
            "📌 <b>Official UPI ID:</b> <code>sagarhalder22@axl</code> <i>(Tap to copy)</i>\n\n"
            "⚡ <b>Instructions:</b>\n"
            "1️⃣ Scan QR Code & complete payment.\n"
            "2️⃣ Send the payment screenshot in this chat.\n"
            "3️⃣ Funds will be added instantly inside 5 minutes!"
        )
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

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    user_id = query.from_user.id
    name    = query.from_user.first_name
    await query.answer()

    if query.data == "back_main":
        msg, inline_markup = get_main_dashboard(user_id, name)
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=inline_markup)
        return

    if query.data == "script_key_menu":
        if user_id not in ADMINS:
            await query.answer("❌ Admin only option!", show_alert=True)
            return
        keyboard = [
            [InlineKeyboardButton("⚡ 1 Day License", callback_data="sk_d_1"), InlineKeyboardButton("⚡ 7 Days License", callback_data="sk_d_7")],
            [InlineKeyboardButton("⚡ 30 Days License", callback_data="sk_d_30"), InlineKeyboardButton("⚡ Custom Duration", callback_data="sk_d_custom")],
            [InlineKeyboardButton("◀️ Return to Main", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║   🛠️ <b>SCRIPT KEY GENERATOR</b>   ║\n"
            "╚═══════════════════════════╝\n\n"
            "Select license validity duration:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if query.data.startswith("sk_d_"):
        if user_id not in ADMINS: return
        d_val = query.data.replace("sk_d_", "")
        if d_val == "custom":
            await query.edit_message_text("💡 <b>Use syntax:</b>\n<code>/scriptkey &lt;days&gt; &lt;device_id&gt;</code>", parse_mode="HTML")
            return
        days = int(d_val)
        context.user_data["script_gen_days"] = days
        await query.edit_message_text(f"Selected: <b>{days} Days License</b>\n\n👉 Now enter the <b>Device ID</b> in chat:", parse_mode="HTML")
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
            f"╔═══════════════════════════╗\n"
            f"║   🟢 <b>AIM CARROM (NORMAL)</b>     ║\n"
            f"╚═══════════════════════════╝\n"
            f"💎 <b>Instant Pricing:</b>\n"
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
            f"╔═══════════════════════════╗\n"
            f"║   🔥 <b>AIM CARROM (AUTO QUEUE)</b>  ║\n"
            f"╚═══════════════════════════╝\n"
            f"💎 <b>Instant Pricing:</b>\n"
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
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║    🔥 <b>KOS ENGINE PLATFORM</b>    ║\n"
            "╚═══════════════════════════╝\n\n"
            "Select target game to purchase VIP Key:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if query.data == "kos_8b":
        p1 = get_price(user_id, "b1"); p7 = get_price(user_id, "b7")
        p15 = get_price(user_id, "b15"); p30 = get_price(user_id, "b30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_b1"), InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_b7")],
            [InlineKeyboardButton(f"⚡ 15 Days (₹{p15})", callback_data="buy_b15"), InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_b30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        text = f"🎱 <b>KOS 8 BALL POOL VIP</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n• 1 Day ➜ <code>₹{p1}</code>\n• 7 Days ➜ <code>₹{p7}</code>\n• 15 Days ➜ <code>₹{p15}</code>\n• 30 Days ➜ <code>₹{p30}</code>"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_cp":
        p1 = get_price(user_id, "c1"); p7 = get_price(user_id, "c7")
        p15 = get_price(user_id, "c15"); p30 = get_price(user_id, "c30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_c1"), InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_c7")],
            [InlineKeyboardButton(f"⚡ 15 Days (₹{p15})", callback_data="buy_c15"), InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_c30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        text = f"🎯 <b>KOS CARROM POOL VIP</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n• 1 Day ➜ <code>₹{p1}</code>\n• 7 Days ➜ <code>₹{p7}</code>\n• 15 Days ➜ <code>₹{p15}</code>\n• 30 Days ➜ <code>₹{p30}</code>"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_ff":
        p1 = get_price(user_id, "f1"); p7 = get_price(user_id, "f7"); p30 = get_price(user_id, "f30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_f1"), InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_f7")],
            [InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_f30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        text = f"🔥 <b>KOS FREEFIRE PANEL VIP</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n• 1 Day ➜ <code>₹{p1}</code>\n• 7 Days ➜ <code>₹{p7}</code>\n• 30 Days ➜ <code>₹{p30}</code>"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # BITAIM MENU
    if query.data == "bitaim_menu":
        p7 = get_price(user_id, "bit7"); p30 = get_price(user_id, "bit30")
        p90 = get_price(user_id, "bit90"); plt = get_price(user_id, "bitlt")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_bit7"), InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_bit30")],
            [InlineKeyboardButton(f"⚡ 3 Months (₹{p90})", callback_data="buy_bit90"), InlineKeyboardButton(f"⚡ Lifetime (₹{plt})", callback_data="buy_bitlt")],
            [InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]
        ]
        text = f"⚡ <b>BITAIM OFFICIAL SYSTEM</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n• 7 Days ➜ <code>₹{p7}</code>\n• 30 Days ➜ <code>₹{p30}</code>\n• 3 Months ➜ <code>₹{p90}</code>\n• Lifetime ➜ <code>₹{plt}</code>"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # SNAKE MENU
    if query.data == "snk_menu":
        keyboard = [
            [InlineKeyboardButton("🎯 Snake Carrom Pool", callback_data="snkc_sub")],
            [InlineKeyboardButton("🎱 Snake 8 Ball Pool", callback_data="snk8_sub")],
            [InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║    🐍 <b>SNAKE ENGINE VIP</b>     ║\n"
            "╚═══════════════════════════╝\n\n"
            "Select game variant:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if query.data == "snkc_sub":
        p3 = get_price(user_id, "snkc_3d"); p10 = get_price(user_id, "snkc_10d"); p30 = get_price(user_id, "snkc_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_snkc_3d"), InlineKeyboardButton(f"⚡ 10 Days (₹{p10})", callback_data="buy_snkc_10d")],
            [InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_snkc_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="snk_menu")]
        ]
        text = f"🐍 <b>SNAKE CARROM POOL</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n• 3 Days ➜ <code>₹{p3}</code>\n• 10 Days ➜ <code>₹{p10}</code>\n• 30 Days ➜ <code>₹{p30}</code>"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "snk8_sub":
        p3 = get_price(user_id, "snk8_3d"); p10 = get_price(user_id, "snk8_10d"); p30 = get_price(user_id, "snk8_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_snk8_3d"), InlineKeyboardButton(f"⚡ 10 Days (₹{p10})", callback_data="buy_snk8_10d")],
            [InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_snk8_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="snk_menu")]
        ]
        text = f"🐍 <b>SNAKE 8 BALL POOL</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n• 3 Days ➜ <code>₹{p3}</code>\n• 10 Days ➜ <code>₹{p10}</code>\n• 30 Days ➜ <code>₹{p30}</code>"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
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
        confirm_text = (
            f"╔═══════════════════════════╗\n"
            f"║   🛒 <b>CHECKOUT CONFIRMATION</b>   ║\n"
            f"╚═══════════════════════════╝\n"
            f"🎮 <b>Item:</b> {plan['game']}\n"
            f"⏳ <b>Duration:</b> {plan['label']}\n"
            f"💰 <b>Total Price:</b> <code>₹{price}</code>\n\n"
            f"<i>Tap below to deduct balance and generate your VIP Key instantly.</i>"
        )
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
                "╔═══════════════════════════╗\n"
                "║   ❌ <b>INSUFFICIENT FUNDS</b>    ║\n"
                "╚═══════════════════════════╝\n"
                f"Required: <b>₹{price}</b> | Your Balance: <b>₹{bal}</b>\n\n"
                "👉 Please deposit funds to continue.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Add Balance Now", callback_data="add_bal")]])
            )
            return

        if "bit" in plan_id:
            awaiting_gmail[user_id] = plan_id
            await query.edit_message_text(
                "╔═══════════════════════════╗\n"
                "║   📧 <b>GMAIL ID REQUIRED</b>     ║\n"
                "╚═══════════════════════════╝\n\n"
                "Please type & send your <b>Google Play Gmail ID</b> in chat to activate Bitaim Hack:",
                parse_mode="HTML"
            )
            return

        if db_count_keys(plan_id) == 0:
            await query.edit_message_text(
                f"⚠️ <b>OUT OF STOCK TEMPORARILY!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Admin is restocking now. Contact {ADMIN_USERNAME} for priority delivery.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Return to Menu", callback_data="back_main")]])
            )
            return

        new_bal = bal - price
        db_set_balance(user_id, new_bal)
        key = db_pop_key(plan_id)
        db_record_order(user_id, plan['game'], plan['label'], price, key)

        # 👑 THE ONE-TAP COPY LUXURY VOUCHER
        success_receipt = (
            f"╔═══════════════════════════╗\n"
            f"║  🎉 <b>OFFICIAL PURCHASE RECEIPT</b> ║\n"
            f"╚═══════════════════════════╝\n"
            f"👤 <b>Customer:</b> {name}\n"
            f"🎮 <b>Item:</b> {plan['game']} ({plan['label']})\n"
            f"💰 <b>Amount Paid:</b> <code>₹{price}</code>\n"
            f"💳 <b>Remaining Balance:</b> <code>₹{new_bal}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔑 <b>YOUR VIP KEY:</b> <i>(👇 Tap key below to Copy)</i>\n\n"
            f"<code>{key}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Paste this key into Happy Gamer App & Enjoy!</i> 🚀"
        )

        await query.edit_message_text(success_receipt, parse_mode="HTML")
        return

    if query.data == "orders_hist":
        orders = db_get_user_orders(user_id)
        if not orders:
            await query.edit_message_text(
                "📜 <b>ORDER HISTORY</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<i>You have not made any purchases yet!</i>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]])
            )
            return
        msg = "📜 <b>YOUR LAST 10 PURCHASES:</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for o in orders:
            msg += f"💎 <b>{o['game']} ({o['plan_label']})</b>\n  💰 Paid: <code>₹{o['price']}</code> | 🕒 {o['timestamp']}\n  🔑 Key: <code>{o['key_delivered']}</code>\n\n"
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]]))
        return

    if query.data == "add_bal":
        caption = (
            "╔═══════════════════════════╗\n"
            "║    💳 <b>SECURE UPI PAYMENT</b>     ║\n"
            "╚═══════════════════════════╝\n\n"
            "📌 <b>UPI ID:</b> <code>sagarhalder22@axl</code> <i>(Tap to copy)</i>\n\n"
            "1️⃣ স্ক্যানার দিয়ে পেমেন্ট সম্পন্ন করুন।\n"
            "2️⃣ পেমেন্টের স্ক্রিনশটটি এই চ্যাটে সেন্ড করুন।\n"
            "⏰ ৫ মিনিটের মধ্যে ভেরিফাই করে ব্যালেন্স যোগ হবে!"
        )
        if os.path.exists(QR_PATH):
            with open(QR_PATH, "rb") as f:
                await context.bot.send_photo(chat_id=user_id, photo=f, caption=caption, parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=user_id, text=caption, parse_mode="HTML")
        return

    if query.data == "become_reseller":
        await query.edit_message_text(
            f"╔═══════════════════════════╗\n"
            f"║  👑 <b>BECOME AN OFFICIAL RESELLER</b> ║\n"
            f"╚═══════════════════════════╝\n\n"
            f"Get wholesale discount prices on all hack keys & resell at high profit!\n\n"
            f"👉 <b>Contact Founder:</b> {ADMIN_USERNAME}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]])
        )
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
                f"╔═══════════════════════════╗\n"
                f"║  🎉 <b>PAYMENT APPROVED</b>       ║\n"
                f"╚═══════════════════════════╝\n"
                f"💰 <b>₹{amount}</b> has been credited to your wallet.\n"
                f"💳 <b>Current Balance:</b> <code>₹{new_bal}.00</code>",
                parse_mode="HTML"
            )
        except Exception: pass
        await query.edit_message_caption(f"✅ <b>Approved ₹{amount} for User {target_id}</b>", parse_mode="HTML")
        return

    if query.data.startswith("verify_"):
        cust_id = int(query.data.split("_")[1])
        if cust_id != user_id: return
        if cust_id not in payment_requests:
            await query.edit_message_caption("⚠️ Request timed out. Please send screenshot again.")
            return
        photo_id = payment_requests[cust_id]["photo_id"]
        user_obj = query.from_user
        name     = user_obj.full_name
        username = f"@{user_obj.username}" if user_obj.username else "No username"
        role_lbl = "👑 Reseller" if db_is_reseller(cust_id) else "👤 Customer"
        await query.edit_message_caption("⏳ <b>Verifying... Admin is reviewing your receipt!</b>", parse_mode="HTML")
        
        amounts = [50, 60, 65, 100, 120, 150, 160, 165, 180, 190, 200, 220, 230, 250, 280, 290, 300, 310, 320, 330, 340, 360, 380, 400, 410, 450, 460, 480, 490, 500, 600, 630, 650, 670, 750, 800, 830, 850, 870, 900, 950, 1000, 1150, 1180, 1200, 1250, 1400, 1500, 1600, 1790, 1800, 1860]
        row, kbd = [], []
        for amt in amounts:
            row.append(InlineKeyboardButton(f"₹{amt}", callback_data=f"pay_{cust_id}_{amt}"))
            if len(row) == 3: kbd.append(row); row = []
        if row: kbd.append(row)
        kbd.append([InlineKeyboardButton("❌ Reject Payment", callback_data=f"pay_{cust_id}_reject")])
        
        for admin_id in ADMINS:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id, photo=photo_id,
                    caption=f"🔔 <b>NEW PAYMENT SUBMISSION</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 <b>ID:</b> <code>{cust_id}</code>\n📝 <b>Name:</b> {name}\n🔗 <b>Handle:</b> {username}\n🏷️ <b>Role:</b> {role_lbl}\n💳 <b>Current Bal:</b> ₹{db_get_balance(cust_id)}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(kbd)
                )
            except Exception: pass
        return

async def expire_payment(user_id, context):
    await asyncio.sleep(PAYMENT_TIMEOUT)
    if user_id in payment_requests:
        del payment_requests[user_id]
        try: await context.bot.send_message(user_id, "⚠️ Payment request timed out. Send screenshot again.")
        except Exception: pass

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id  = update.effective_user.id
    
    if user_id in payment_requests:
        old = payment_requests[user_id].get("task")
        if old: old.cancel()
    photo_id = update.message.photo[-1].file_id
    task     = asyncio.create_task(expire_payment(user_id, context))
    payment_requests[user_id] = {"timestamp": time.time(), "photo_id": photo_id, "task": task}
    await update.message.reply_photo(
        photo=photo_id,
        caption="📸 <b>Payment Receipt Captured!</b>\n\nClick below to forward to Admin for verification:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚡ Verify Payment Now", callback_data=f"verify_{user_id}")]])
    )

# --- 📢 MASS BROADCAST ANNOUNCEMENT ---
async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    if not context.args:
        await update.message.reply_text("💡 <b>Usage:</b>\n<code>/broadcast &lt;Your Announcement or Offer Text&gt;</code>", parse_mode="HTML")
        return

    offer_message = " ".join(context.args)
    all_users = db_get_all_users()
    
    status_msg = await update.message.reply_text(f"⏳ <b>Broadcasting to {len(all_users)} clients...</b>", parse_mode="HTML")
    
    success_count = 0
    fail_count = 0
    
    formatted_broadcast = (
        f"╔═══════════════════════════╗\n"
        f"║  📢 <b>SPECIAL VIP ANNOUNCEMENT</b> ║\n"
        f"╚═══════════════════════════╝\n\n"
        f"{offer_message}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛒 <i>Tap /start to explore the VIP Store!</i> 🚀"
    )
    
    for uid in all_users:
        try:
            await context.bot.send_message(chat_id=uid, text=formatted_broadcast, parse_mode="HTML")
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            fail_count += 1

    await status_msg.edit_text(
        f"╔═══════════════════════════╗\n"
        f"║  ✅ <b>BROADCAST DISPATCHED</b>   ║\n"
        f"╚═══════════════════════════╝\n"
        f"👥 <b>Total Target Users:</b> {len(all_users)}\n"
        f"🚀 <b>Successfully Delivered:</b> {success_count}\n"
        f"❌ <b>Blocked / Failed:</b> {fail_count}",
        parse_mode="HTML"
    )

# --- ADMIN COMMAND PANEL ---
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    help_text = (
        "╔═══════════════════════════╗\n"
        "║   👑 <b>ADMIN CONTROL PANEL</b>   ║\n"
        "╚═══════════════════════════╝\n"
        "📢 <b>Mass Broadcast:</b>\n• <code>/broadcast &lt;offer text&gt;</code>\n\n"
        "💳 <b>Wallet Controls:</b>\n• <code>/add &lt;id&gt; &lt;amount&gt;</code>\n\n"
        "🔑 <b>Key & Inventory Controls:</b>\n• <code>/addkey &lt;plan&gt; &lt;key&gt;</code>\n• <code>/scriptkey &lt;days&gt; &lt;device_id&gt;</code>\n• <code>/stock</code>\n• <code>/deliver &lt;id&gt; &lt;key&gt;</code>\n• <code>/reply &lt;id&gt; &lt;msg&gt;</code>\n\n"
        "💎 <b>Price Management:</b>\n• <code>/setprice &lt;plan&gt; &lt;regular&gt; &lt;reseller&gt;</code>\n• <code>/prices</code>\n\n"
        "👑 <b>Reseller Management:</b>\n• <code>/addreseller &lt;id&gt;</code>\n• <code>/removereseller &lt;id&gt;</code>\n• <code>/resellers</code>"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

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
        await update.message.reply_text(f"✅ Credited <b>₹{amount}</b> to User <code>{uid}</code>\n💳 New Balance: <b>₹{new_bal}</b>", parse_mode="HTML")
        try: await context.bot.send_message(uid, f"🎉 <b>Admin added ₹{amount} to your wallet!</b>\n💳 Current Balance: ₹{new_bal}", parse_mode="HTML")
        except Exception: pass
    except Exception: await update.message.reply_text("Usage: <code>/add &lt;user_id&gt; &lt;amount&gt;</code>", parse_mode="HTML")

async def cmd_addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        plan = context.args[0].lower(); new_key = context.args[1]
        db_add_key(plan, new_key)
        await update.message.reply_text(f"✅ <b>Stock Added for {plan}:</b> <code>{new_key}</code>\n📦 Total Stock: <b>{db_count_keys(plan)}</b>", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/addkey &lt;plan_code&gt; &lt;key&gt;</code>", parse_mode="HTML")

async def cmd_scriptkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    if len(context.args) < 2:
        await update.message.reply_text("💡 <b>Format:</b> <code>/scriptkey &lt;days&gt; &lt;device_id&gt;</code>", parse_mode="HTML")
        return
    try:
        days = int(context.args[0])
        device_id = context.args[1].strip()
        
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        vip_key = f"HGVIP{days}{random_code}"
        
        status_msg = await update.message.reply_text("⏳ <i>Syncing with GitHub Gist...</i>", parse_mode="HTML")
        
        success, expiry, err = append_to_gist(device_id, days)
        
        if success:
            receipt_msg = (
                f"╔═══════════════════════════╗\n"
                f"║  👑 <b>SCRIPT KEY GENERATED!</b>   ║\n"
                f"╚═══════════════════════════╝\n"
                f"👤 <b>Admin:</b> {update.effective_user.first_name}\n"
                f"⏳ <b>Validity:</b> {days} Days (Expires: <code>{expiry}</code>)\n"
                f"📱 <b>Device ID:</b> <code>{device_id}</code>\n"
                f"☁️ <b>GitHub Gist:</b> <i>Updated Successfully ✅</i>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔑 <b>YOUR VIP KEY:</b> <i>(👇 Tap to Copy)</i>\n\n"
                f"<code>{vip_key}</code>"
            )
            await status_msg.edit_text(receipt_msg, parse_mode="HTML")
        else:
            await status_msg.edit_text(
                f"❌ <b>GitHub Gist Update Failed!</b>\n\n"
                f"<b>Reason:</b> <code>{err}</code>\n\n"
                f"👉 Make sure Render Environment Variable <b>GITHUB_TOKEN</b> has Gist permissions.",
                parse_mode="HTML"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode="HTML")

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
        await update.message.reply_text(f"✅ <b>Price Set for {plan}:</b> Regular ₹{reg}, Reseller ₹{res}", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/setprice &lt;plan_code&gt; &lt;regular&gt; &lt;reseller&gt;</code>", parse_mode="HTML")

async def cmd_addreseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_add_reseller(uid)
        await update.message.reply_text(f"👑 <b>User {uid} elevated to Official VIP Reseller!</b>", parse_mode="HTML")
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
    await update.message.reply_text("👑 <b>OFFICIAL RESELLERS DIRECTORY:</b>\n" + "\n".join(f"• <code>{r}</code>" for r in rlist), parse_mode="HTML")

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set.")
        exit(1)
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",          start))
    app.add_handler(CommandHandler("help",           cmd_help))
    app.add_handler(CommandHandler("broadcast",      cmd_broadcast))
    app.add_handler(CommandHandler("sendall",        cmd_broadcast))
    app.add_handler(CommandHandler("reply",          cmd_reply))
    app.add_handler(CommandHandler("add",            cmd_add))
    app.add_handler(CommandHandler("addkey",         cmd_addkey))
    app.add_handler(CommandHandler("scriptkey",      cmd_scriptkey))
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
    print("👑 Happy Gamer Ultra-VIP Telegram Engine Running 24/7...")
    app.run_polling()
