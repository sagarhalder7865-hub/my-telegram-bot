import os
import json
import asyncio
import time
import base64
import requests
import sqlite3
import datetime
import random
import string
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

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

# --- RENDER WEB SERVER ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"VIP Bot is active and running 24/7!")

    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

Thread(target=run_web_server, daemon=True).start()

# --- GIST AUTO-UPDATER FOR SCRIPT KEYS ---
def update_gist(content):
    try:
        url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        payload = {"files": {FILE_NAME: {"content": content}}}
        requests.patch(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Gist Update Error: {e}")

# --- GITHUB AUTO-SYNC SYSTEM ---
def push_data_to_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return
    try:
        data_dump = export_database_json()
        content_str = json.dumps(data_dump, indent=2)
        content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        sha = None
        get_res = requests.get(url, headers=headers)
        if get_res.status_code == 200:
            sha = get_res.json().get("sha")
            
        payload = {
            "message": "Auto-sync bot data from Telegram action",
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
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
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
        balances = [dict(r) for r in db.execute("SELECT * FROM balances").fetchall()]
        keys = [dict(r) for r in db.execute("SELECT * FROM keys").fetchall()]
        resellers = [dict(r) for r in db.execute("SELECT * FROM resellers").fetchall()]
        prices = [dict(r) for r in db.execute("SELECT * FROM prices").fetchall()]
        orders = [dict(r) for r in db.execute("SELECT * FROM order_history").fetchall()]
    return {
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
            db.execute("DELETE FROM balances")
            db.execute("DELETE FROM keys")
            db.execute("DELETE FROM resellers")
            db.execute("DELETE FROM prices")
            db.execute("DELETE FROM order_history")
            
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
    return "No purchases yet"

def db_get_user_orders(user_id):
    with get_db() as db:
        return db.execute("SELECT game, plan_label, price, key_delivered, timestamp FROM order_history WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,)).fetchall()

def get_price(user_id, plan_id):
    p = db_get_plan(plan_id)
    if not p: return 0
    return p["reseller"] if db_is_reseller(user_id) else p["regular"]

def stock_text():
    lines = ["📦 Current Stock Status\n", "👑 AIM CARROM KING:"]
    for p in ["acn_3d","acn_7d","acn_30d","acp_3d","acp_7d","acp_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  {plan['game']} ({plan['label']}) : {db_count_keys(p)}")

    lines.append("\n🔥 KOS Engine Keys:")
    for p in ["b1","b7","b15","b30","c1","c7","c15","c30","f1","f7","f30"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  {plan['game']} ({plan['label']}) : {db_count_keys(p)}")
    
    lines.append("\n⚡ Bitaim Hack:")
    for p in ["bit7","bit30","bit90","bitlt"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  {plan['label']:10} : {db_count_keys(p)}")

    lines.append("\n🐍 Snake Engine:")
    for p in ["snkc_3d","snkc_10d","snkc_30d","snk8_3d","snk8_10d","snk8_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  {plan['game']} ({plan['label']}) : {db_count_keys(p)}")
    return "\n".join(lines)

def price_list_text():
    lines = ["💎 VIP PRICE LIST 💎\n", "👑 AIM CARROM KING:"]
    lines.append("  Normal:")
    for p in ["acn_3d","acn_7d","acn_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"    {plan['label']} → ₹{plan['regular']} (Reseller: ₹{plan['reseller']})")
    lines.append("  Premium (Auto Queue):")
    for p in ["acp_3d","acp_7d","acp_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"    {plan['label']} → ₹{plan['regular']} (Reseller: ₹{plan['reseller']})")

    lines.append("\n🔥 KOS Engine:")
    for p in ["b1","b7","b15","b30","c1","c7","c15","c30","f1","f7","f30"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  {plan['game']} {plan['label']} → ₹{plan['regular']} (Reseller: ₹{plan['reseller']})")
    
    lines.append("\n⚡ Bitaim Hack:")
    for p in ["bit7","bit30","bit90","bitlt"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  Bitaim {plan['label']} → ₹{plan['regular']} (Reseller: ₹{plan['reseller']})")

    lines.append("\n🐍 Snake Engine:")
    for p in ["snkc_3d","snkc_10d","snkc_30d","snk8_3d","snk8_10d","snk8_30d"]:
        plan = db_get_plan(p)
        if plan: lines.append(f"  {plan['game']} {plan['label']} → ₹{plan['regular']} (Reseller: ₹{plan['reseller']})")
    return "\n".join(lines)

pending_orders   = {}
payment_requests = {}
awaiting_gmail   = {}
PAYMENT_TIMEOUT  = 300

def get_main_dashboard(uid, name):
    role = "Reseller" if db_is_reseller(uid) else "Customer"
    bal  = db_get_balance(uid)
    last_buy = db_get_last_purchase(uid)

    inline_kbd = [
        [InlineKeyboardButton("👑 AIM CARROM KING", callback_data="aim_menu")],
        [InlineKeyboardButton("🔥 KOS Engine Keys", callback_data="kos_menu"), InlineKeyboardButton("⚡ Bitaim Hack", callback_data="bitaim_menu")],
        [InlineKeyboardButton("🐍 Snake Engine", callback_data="snk_menu")],
        [InlineKeyboardButton("💵 Add Balance", callback_data="add_bal"), InlineKeyboardButton("📜 Orders History", callback_data="orders_hist")],
        [InlineKeyboardButton("🥰🔥 Reseller Apply", callback_data="become_reseller")]
    ]
    
    if uid in ADMINS:
        inline_kbd.insert(4, [InlineKeyboardButton("🛠️ Script Key Generator (Admin Only)", callback_data="script_key_menu")])

    msg = (
        f"🟢🔴 HAPPY GAMER VIP STORE 🔴🟢\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Welcome: {name}\n"
        f"💳 Balance: ₹{bal}\n"
        f"👤 Status: {role}\n"
        f"📦 Last Purchase: {last_buy}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📖 How to Buy Key / কীভাবে কি কিনবেন:\n"
        f"1️⃣ Click 💵 Add Balance to deposit funds.\n"
        f"2️⃣ Select your desired Hack Engine.\n"
        f"3️⃣ Choose plan & tap Confirm Purchase for instant Key!"
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
    msg, inline_markup = get_main_dashboard(uid, name)
    await update.message.reply_text(msg, reply_markup=get_reply_keyboard())
    await update.message.reply_text("👇 Choose Options Below:", reply_markup=inline_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text    = update.message.text
    user_id = update.effective_user.id
    name    = update.effective_user.first_name

    if user_id in awaiting_gmail:
        plan_id = awaiting_gmail.pop(user_id)
        plan    = db_get_plan(plan_id)
        price   = get_price(user_id, plan_id)
        bal     = db_get_balance(user_id)

        if "@" not in text or "." not in text:
            await update.message.reply_text("❌ Invalid Gmail ID! Please send a valid Gmail address.")
            awaiting_gmail[user_id] = plan_id
            return

        new_bal = bal - price
        db_set_balance(user_id, new_bal)
        db_record_order(user_id, plan['game'], plan['label'], price, f"Gmail: {text}")

        await update.message.reply_text(
            f"🎉 PURCHASE SUBMITTED!\n━━━━━━━━━━━━━━━━━━━━━━\n🎮 Item: {plan['game']} ({plan['label']})\n💰 Price: ₹{price}\n📧 Gmail Submitted: `{text}`\n💳 Remaining Balance: ₹{new_bal}\n━━━━━━━━━━━━━━━━━━━━━━\nAdmin will activate your account shortly!",
            parse_mode="Markdown"
        )

        try:
            for admin_id in ADMINS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🚨 NEW BITAIM ORDER!\n👤 User: {user_id} ({name})\n🎮 Item: {plan['game']} ({plan['label']})\n💰 Price: ₹{price}\n📧 Gmail: `{text}`",
                    parse_mode="Markdown"
                )
        except Exception: pass
        return

    if text in ["/start", "🔑 All Hack Key buy"]:
        msg, inline_markup = get_main_dashboard(user_id, name)
        await update.message.reply_text(msg, reply_markup=inline_markup)

    elif text in ["Check Balance 💰", "💰 Balance"]:
        bal = db_get_balance(user_id)
        role = " (Reseller)" if db_is_reseller(user_id) else ""
        await update.message.reply_text(f"💳 Your Current Balance: ₹{bal}{role}")

    elif text in ["➕Add Balance 💰", "➕ Add Balance"]:
        caption = (
            "💳 Scan & Pay via PhonePe / UPI\n━━━━━━━━━━━━━━━━━━━━━━\n"
            "UPI ID: sagarhalder22@axl\n\n"
            "✅ After paying, send the screenshot here.\n"
            "⏰ Verification inside 5 minutes!"
        )
        if os.path.exists(QR_PATH):
            with open(QR_PATH, "rb") as f:
                await update.message.reply_photo(photo=f, caption=caption)
        else:
            await update.message.reply_text(caption)

    elif text == "📦 Stock":
        if user_id not in ADMINS:
            await update.message.reply_text("❌ Admin command only.")
            return
        await update.message.reply_text(f"```\n{stock_text()}\n```", parse_mode="Markdown")

    elif text == "📞 Admin Help":
        await cmd_help(update, context)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    user_id = query.from_user.id
    name    = query.from_user.first_name
    username = f"@{query.from_user.username}" if query.from_user.username else "No Username"
    await query.answer()

    if query.data == "back_main":
        msg, inline_markup = get_main_dashboard(user_id, name)
        await query.edit_message_text(msg, reply_markup=inline_markup)
        return

    if query.data == "script_key_menu":
        if user_id not in ADMINS:
            await query.answer("❌ Admin only option!", show_alert=True)
            return
        keyboard = [
            [InlineKeyboardButton("🛠️ 1 Day", callback_data="sk_d_1"), InlineKeyboardButton("🛠️ 7 Days", callback_data="sk_d_7")],
            [InlineKeyboardButton("🛠️ 30 Days", callback_data="sk_d_30"), InlineKeyboardButton("🛠️ Custom Days", callback_data="sk_d_custom")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_main")]
        ]
        await query.edit_message_text("🛠️ *SCRIPT KEY GENERATOR*\n\nSelect duration:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data.startswith("sk_d_"):
        if user_id not in ADMINS: return
        d_val = query.data.replace("sk_d_", "")
        if d_val == "custom":
            await query.edit_message_text("Use command:\n`/scriptkey <days> <device_id>`", parse_mode="Markdown")
            return
        days = int(d_val)
        context.user_data["script_gen_days"] = days
        await query.edit_message_text(f"⏱ Selected: {days} Days\n\nNow send the **Device ID** as a message in chat:", parse_mode="Markdown")
        return

    # --- AIM CARROM KING MENU ---
    if query.data == "aim_menu":
        keyboard = [
            [InlineKeyboardButton("🟢 AIM Normal", callback_data="aim_normal"), InlineKeyboardButton("🔥 AIM Premium (Auto Queue)", callback_data="aim_premium")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_main")]
        ]
        await query.edit_message_text("👑 *AIM CARROM KING CATEGORIES*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "aim_normal":
        p3 = get_price(user_id, "acn_3d"); p7 = get_price(user_id, "acn_7d"); p30 = get_price(user_id, "acn_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ Buy 3 Days (₹{p3})", callback_data="buy_acn_3d"), InlineKeyboardButton(f"⚡ Buy 1 Week (₹{p7})", callback_data="buy_acn_7d")],
            [InlineKeyboardButton(f"⚡ Buy 1 Month (₹{p30})", callback_data="buy_acn_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="aim_menu")]
        ]
        text = f"👑 *AIM CARROM KING (Normal)*\n\n🟢 VIP Price List:\n━━━━━━━━━━━━━━━━━━━━━━\n🔥 3 Days  → ₹{p3}\n🔥 1 Week  → ₹{p7}\n🔥 1 Month → ₹{p30}\n━━━━━━━━━━━━━━━━━━━━━━"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "aim_premium":
        p3 = get_price(user_id, "acp_3d"); p7 = get_price(user_id, "acp_7d"); p30 = get_price(user_id, "acp_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ Buy 3 Days (₹{p3})", callback_data="buy_acp_3d"), InlineKeyboardButton(f"⚡ Buy 1 Week (₹{p7})", callback_data="buy_acp_7d")],
            [InlineKeyboardButton(f"⚡ Buy 1 Month (₹{p30})", callback_data="buy_acp_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="aim_menu")]
        ]
        text = f"🔥 *AIM CARROM KING (Premium Auto Queue)*\n\n🟢 VIP Price List:\n━━━━━━━━━━━━━━━━━━━━━━\n🔥 3 Days  → ₹{p3}\n🔥 1 Week  → ₹{p7}\n🔥 1 Month → ₹{p30}\n━━━━━━━━━━━━━━━━━━━━━━"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # --- KOS MENU ---
    if query.data == "kos_menu":
        keyboard = [
            [InlineKeyboardButton("🎱 8 Ball Key", callback_data="kos_8b")],
            [InlineKeyboardButton("🎯 Carrom Pool Key", callback_data="kos_cp")],
            [InlineKeyboardButton("🔥 FF Panel", callback_data="kos_ff")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_main")]
        ]
        await query.edit_message_text("🟢🔴 KOS ENGINE CATEGORIES 🔴🟢", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_8b":
        p1 = get_price(user_id, "b1"); p7 = get_price(user_id, "b7")
        p15 = get_price(user_id, "b15"); p30 = get_price(user_id, "b30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ Buy 1 Day (₹{p1})", callback_data="buy_b1"), InlineKeyboardButton(f"⚡ Buy 7 Days (₹{p7})", callback_data="buy_b7")],
            [InlineKeyboardButton(f"⚡ Buy 15 Days (₹{p15})", callback_data="buy_b15"), InlineKeyboardButton(f"⚡ Buy 30 Days (₹{p30})", callback_data="buy_b30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        text = f"🎱 8 Ball Key Panel\n\n🟢 VIP Price List:\n━━━━━━━━━━━━━━━━━━━━━━\n🔥 1 Day  → ₹{p1}\n🔥 7 Days → ₹{p7}\n🔥 15 Days → ₹{p15}\n🔥 30 Days → ₹{p30}\n━━━━━━━━━━━━━━━━━━━━━━"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_cp":
        p1 = get_price(user_id, "c1"); p7 = get_price(user_id, "c7")
        p15 = get_price(user_id, "c15"); p30 = get_price(user_id, "c30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ Buy 1 Day (₹{p1})", callback_data="buy_c1"), InlineKeyboardButton(f"⚡ Buy 7 Days (₹{p7})", callback_data="buy_c7")],
            [InlineKeyboardButton(f"⚡ Buy 15 Days (₹{p15})", callback_data="buy_c15"), InlineKeyboardButton(f"⚡ Buy 30 Days (₹{p30})", callback_data="buy_c30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        text = f"🎯 Carrom Pool Key Panel\n\n🟢 VIP Price List:\n━━━━━━━━━━━━━━━━━━━━━━\n🔥 1 Day  → ₹{p1}\n🔥 7 Days → ₹{p7}\n🔥 15 Days → ₹{p15}\n🔥 30 Days → ₹{p30}\n━━━━━━━━━━━━━━━━━━━━━━"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_ff":
        p1 = get_price(user_id, "f1"); p7 = get_price(user_id, "f7"); p30 = get_price(user_id, "f30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ Buy 1 Day (₹{p1})", callback_data="buy_f1"), InlineKeyboardButton(f"⚡ Buy 7 Days (₹{p7})", callback_data="buy_f7")],
            [InlineKeyboardButton(f"⚡ Buy 30 Days (₹{p30})", callback_data="buy_f30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        text = f"🔥 FF Panel (Free Fire)\n\n🟢 VIP Price List:\n━━━━━━━━━━━━━━━━━━━━━━\n🔥 1 Day  → ₹{p1}\n🔥 7 Days → ₹{p7}\n🔥 30 Days → ₹{p30}\n━━━━━━━━━━━━━━━━━━━━━━"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # BITAIM MENU
    if query.data == "bitaim_menu":
        p7 = get_price(user_id, "bit7"); p30 = get_price(user_id, "bit30")
        p90 = get_price(user_id, "bit90"); plt = get_price(user_id, "bitlt")
        keyboard = [
            [InlineKeyboardButton(f"⚡ Buy 7 Days (₹{p7})", callback_data="buy_bit7"), InlineKeyboardButton(f"⚡ Buy 30 Days (₹{p30})", callback_data="buy_bit30")],
            [InlineKeyboardButton(f"⚡ Buy 3 Months (₹{p90})", callback_data="buy_bit90"), InlineKeyboardButton(f"⚡ Buy Life Time (₹{plt})", callback_data="buy_bitlt")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_main")]
        ]
        text = f"⚡ Bitaim Hack\n\n🟢 VIP Price List:\n━━━━━━━━━━━━━━━━━━━━━━\n🔥 7 Days   → ₹{p7}\n🔥 30 Days  → ₹{p30}\n🔥 3 Months → ₹{p90}\n🔥 Life Time → ₹{plt}\n━━━━━━━━━━━━━━━━━━━━━━"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # SNAKE MENU
    if query.data == "snk_menu":
        keyboard = [
            [InlineKeyboardButton("🎯 Snake Carrom", callback_data="snkc_sub"), InlineKeyboardButton("🎱 Snake 8Ball", callback_data="snk8_sub")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_main")]
        ]
        await query.edit_message_text("🐍 *SNAKE ENGINE CATEGORIES*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "snkc_sub":
        p3 = get_price(user_id, "snkc_3d"); p10 = get_price(user_id, "snkc_10d"); p30 = get_price(user_id, "snkc_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ Buy 3 Days (₹{p3})", callback_data="buy_snkc_3d"), InlineKeyboardButton(f"⚡ Buy 10 Days (₹{p10})", callback_data="buy_snkc_10d")],
            [InlineKeyboardButton(f"⚡ Buy 30 Days (₹{p30})", callback_data="buy_snkc_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="snk_menu")]
        ]
        text = f"🎯 Snake Carrom\n\n🟢 VIP Price List:\n━━━━━━━━━━━━━━━━━━━━━━\n🔥 3 Days  → ₹{p3}\n🔥 10 Days → ₹{p10}\n🔥 30 Days → ₹{p30}\n━━━━━━━━━━━━━━━━━━━━━━"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "snk8_sub":
        p3 = get_price(user_id, "snk8_3d"); p10 = get_price(user_id, "snk8_10d"); p30 = get_price(user_id, "snk8_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ Buy 3 Days (₹{p3})", callback_data="buy_snk8_3d"), InlineKeyboardButton(f"⚡ Buy 10 Days (₹{p10})", callback_data="buy_snk8_10d")],
            [InlineKeyboardButton(f"⚡ Buy 30 Days (₹{p30})", callback_data="buy_snk8_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="snk_menu")]
        ]
        text = f"🎱 Snake 8Ball\n\n🟢 VIP Price List:\n━━━━━━━━━━━━━━━━━━━━━━\n🔥 3 Days  → ₹{p3}\n🔥 10 Days → ₹{p10}\n🔥 30 Days → ₹{p30}\n━━━━━━━━━━━━━━━━━━━━━━"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- BUYING & CONFIRMATION ---
    if query.data.startswith("buy_"):
        plan_id = query.data.replace("buy_", "")
        plan = db_get_plan(plan_id)
        if not plan:
            await query.answer("❌ Invalid plan", show_alert=True)
            return
        price = get_price(user_id, plan_id)
        pending_orders[user_id] = plan_id
        keyboard = [
            [InlineKeyboardButton("✅ Confirm Purchase", callback_data="confirm_buy")],
            [InlineKeyboardButton("❌ Cancel Order", callback_data="back_main")]
        ]
        await query.edit_message_text(
            f"🧾 ORDER CONFIRMATION\n━━━━━━━━━━━━━━━━━━━━━━\n🎮 Item: {plan['game']}\n⏱ Plan: {plan['label']}\n💰 Price: ₹{price}\n━━━━━━━━━━━━━━━━━━━━━━\nPress confirm to proceed.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if query.data == "confirm_buy":
        if user_id not in pending_orders:
            await query.edit_message_text("❌ No active order.")
            return
        plan_id = pending_orders.pop(user_id)
        plan    = db_get_plan(plan_id)
        price   = get_price(user_id, plan_id)
        bal     = db_get_balance(user_id)

        if bal < price:
            await query.edit_message_text("🔴 INSUFFICIENT BALANCE!\nPlease add funds first using 💵 Add Balance.")
            return

        if "bit" in plan_id:
            awaiting_gmail[user_id] = plan_id
            await query.edit_message_text("📧 GMAIL REQUIRED!\n━━━━━━━━━━━━━━━━━━━━━━\nPlease type & send your Gmail ID in this chat to activate your Bitaim Hack account.")
            return

        if db_count_keys(plan_id) == 0:
            await query.edit_message_text(f"🔴 OUT OF STOCK!\nAdmin will restock soon. Contact {ADMIN_USERNAME}")
            return

        new_bal = bal - price
        db_set_balance(user_id, new_bal)
        key = db_pop_key(plan_id)
        db_record_order(user_id, plan['game'], plan['label'], price, key)

        msg = (
            f"🎉 *Purchase Successful!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Customer:* {name}\n"
            f"🆔 *User ID:* `{user_id}`\n"
            f"🎮 *Item:* {plan['game']} ({plan['label']})\n"
            f"💰 *Amount Paid:* ₹{price}\n"
            f"💳 *Remaining Balance:* ₹{new_bal}\n\n"
            f"🔑 *Your VIP Key (Tap to Copy):*\n"
            f"`{key}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Thank you for buying from HAPPY GAMER STORE!"
        )

        await query.edit_message_text(msg, parse_mode="Markdown")

        try:
            for admin_id in ADMINS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🛒 *NEW KEY PURCHASED!*\n👤 User: {name} ({username})\n🆔 ID: `{user_id}`\n🎮 Item: {plan['game']} - {plan['label']}\n💰 Price: ₹{price}\n💳 Rem. Bal: ₹{new_bal}\n🔑 Key: `{key}`",
                    parse_mode="Markdown"
                )
        except Exception: pass
        return

    if query.data == "orders_hist":
        orders = db_get_user_orders(user_id)
        if not orders:
            await query.edit_message_text("📜 Orders History\n\nYou haven't purchased any keys yet!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]]))
            return
        msg = "📜 YOUR ORDERS HISTORY (LAST 10):\n━━━━━━━━━━━━━━━━━━━━━━\n"
        for o in orders:
            msg += f"🎮 {o['game']} ({o['plan_label']})\n💰 Price: ₹{o['price']}\n🔑 Key/Details: `{o['key_delivered']}`\n🗓 Date: {o['timestamp']}\n━━━━━━━━━━━━━━━━━━━━━━\n"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]]))
        return

    if query.data == "add_bal":
        caption = (
            "💳 Scan & Pay via PhonePe / UPI\n━━━━━━━━━━━━━━━━━━━━━━\n"
            "UPI ID: sagarhalder22@axl\n\n"
            "✅ After paying, send the screenshot here.\n"
            "⏰ Verification inside 5 minutes!"
        )
        if os.path.exists(QR_PATH):
            with open(QR_PATH, "rb") as f:
                await context.bot.send_photo(chat_id=user_id, photo=f, caption=caption)
        else:
            await context.bot.send_message(chat_id=user_id, text=caption)
        return

    if query.data == "become_reseller":
        await query.edit_message_text(
            f"💎 BECOME AN OFFICIAL RESELLER\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Get discounted VIP prices on all hack keys!\n\n"
            f"📩 Contact Admin to activate Reseller status:\n"
            f"👤 Admin: {ADMIN_USERNAME}",
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
            try: await context.bot.send_message(target_id, "❌ Payment rejected by admin.")
            except Exception: pass
            await query.edit_message_caption("❌ Payment Rejected")
            return
        amount = int(action)
        req = payment_requests.pop(target_id, None)
        if req and req.get("task"): req["task"].cancel()
        new_bal = db_add_balance(target_id, amount)
        try:
            await context.bot.send_message(target_id, f"✅ *Payment Approved!*\n💰 ₹{amount} added to your account.\nNew Balance: ₹{new_bal}", parse_mode="Markdown")
        except Exception: pass
        await query.edit_message_caption(f"✅ Approved ₹{amount} → User {target_id}")
        return

    if query.data.startswith("verify_"):
        cust_id = int(query.data.split("_")[1])
        if cust_id != user_id: return
        if cust_id not in payment_requests:
            await query.edit_message_caption("⚠️ Request expired. Send screenshot again.")
            return
        photo_id = payment_requests[cust_id]["photo_id"]
        user_obj = query.from_user
        name     = user_obj.full_name
        username = f"@{user_obj.username}" if user_obj.username else "No username"
        role_lbl = "Reseller" if db_is_reseller(cust_id) else "Customer"
        await query.edit_message_caption("⏳ Verifying...\nAdmin is reviewing your payment.")
        
        amounts = [50, 60, 65, 100, 120, 150, 160, 165, 180, 190, 200, 220, 230, 250, 280, 290, 300, 310, 320, 330, 340, 360, 380, 400, 410, 450, 460, 480, 490, 500, 600, 630, 650, 670, 750, 800, 830, 850, 870, 900, 950, 1000, 1150, 1180, 1200, 1250, 1400, 1500, 1600, 1790, 1800, 1860]
        row, kbd = [], []
        for amt in amounts:
            row.append(InlineKeyboardButton(f"✅ ₹{amt}", callback_data=f"pay_{cust_id}_{amt}"))
            if len(row) == 3: kbd.append(row); row = []
        if row: kbd.append(row)
        kbd.append([InlineKeyboardButton("❌ Reject", callback_data=f"pay_{cust_id}_reject")])
        
        for admin_id in ADMINS:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id, photo=photo_id,
                    caption=f"💳 *Payment Request*\n🆔 ID: `{cust_id}`\n👤 Name: {name}\n📱 User: {username}\n🏷 Role: {role_lbl}\n💰 Current Bal: ₹{db_get_balance(cust_id)}",
                    reply_markup=InlineKeyboardMarkup(kbd), parse_mode="Markdown"
                )
            except Exception: pass
        return

async def expire_payment(user_id, context):
    await asyncio.sleep(PAYMENT_TIMEOUT)
    if user_id in payment_requests:
        del payment_requests[user_id]
        try: await context.bot.send_message(user_id, "⏰ Payment request expired. Please send screenshot again.")
        except Exception: pass

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id  = update.effective_user.id
    
    if user_id in ADMINS and "script_gen_days" in context.user_data:
        days = context.user_data.pop("script_gen_days")
        device_id = update.message.text.strip()
        
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        vip_key = f"HGVIP{days}{random_code}"
        
        expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y%m%d")
        gist_entry = f"HGTOKEN=Hgvip653={expiry}={device_id}"
        
        try:
            raw_url = f"https://gist.githubusercontent.com/sagarhalder7865-hub/{GIST_ID}/raw/{FILE_NAME}?{time.time()}"
            current_data = requests.get(raw_url).text
            update_gist(current_data + "\n" + gist_entry)
        except Exception as e:
            print(f"Gist Sync Error: {e}")

        receipt_msg = (
            f"🎉 *Script Key Generated!* (Admin)\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Customer:* {update.effective_user.first_name}\n"
            f"🆔 *User ID:* `{user_id}`\n"
            f"🎮 *Item:* Script KEY ({days} Days)\n"
            f"📱 *Device ID:* `{device_id}`\n\n"
            f"🔑 *Your VIP Key (Tap to Copy):*\n"
            f"`{vip_key}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Updated to GitHub Gist successfully!"
        )
        await update.message.reply_text(receipt_msg, parse_mode="Markdown")
        return

    if user_id in payment_requests:
        old = payment_requests[user_id].get("task")
        if old: old.cancel()
    photo_id = update.message.photo[-1].file_id
    task     = asyncio.create_task(expire_payment(user_id, context))
    payment_requests[user_id] = {"timestamp": time.time(), "photo_id": photo_id, "task": task}
    await update.message.reply_photo(
        photo=photo_id,
        caption="📸 Screenshot received!\n\n👇 Click below to send to admin for verification.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Verify Payment", callback_data=f"verify_{user_id}")]])
    )

# --- ADMIN COMMANDS LIST ---
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    help_text = (
        "🛠 Admin Commands\n\n"
        "Balance:\n/add <id> <amount>\n\n"
        "Keys & Gist:\n/addkey <plan> <key>\n/scriptkey <days> <device_id>\n/stock\n/deliver <id> <key>\n/reply <id> <message>\n\n"
        "Prices:\n/setprice <plan> <regular> <reseller>\n/prices\n\n"
        "Resellers:\n/addreseller <id>\n/removereseller <id>\n/resellers"
    )
    await update.message.reply_text(f"```\n{help_text}\n```", parse_mode="Markdown")

async def cmd_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        target_id = int(context.args[0])
        msg_text  = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=target_id, text=f"💬 Message from Admin:\n\n{msg_text}")
        await update.message.reply_text(f"✅ Message sent to {target_id}")
    except Exception: await update.message.reply_text("Usage: /reply <user_id> <message>")

async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0]); amount = int(context.args[1])
        new_bal = db_add_balance(uid, amount)
        await update.message.reply_text(f"✅ Added ₹{amount} to {uid}\nBalance: ₹{new_bal} (Synced to GitHub ☁️)")
        try: await context.bot.send_message(uid, f"✅ Admin added ₹{amount}.\nNew balance: ₹{new_bal}")
        except Exception: pass
    except Exception: await update.message.reply_text("Usage: /add <user_id> <amount>")

async def cmd_addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        plan = context.args[0].lower(); new_key = context.args[1]
        db_add_key(plan, new_key)
        await update.message.reply_text(f"✅ Key Added for {plan}: `{new_key}`\nTotal Stock: {db_count_keys(plan)} (Synced to GitHub ☁️)", parse_mode="Markdown")
    except Exception: await update.message.reply_text("Usage: /addkey <plan_code> <key>")

async def cmd_scriptkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        days = int(context.args[0])
        device_id = context.args[1]
        
        # ইউনিক কি জেনারেশন (HGVIP + দিন + ৬ ডিজিটের র্যান্ডম কোড)
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        vip_key = f"HGVIP{days}{random_code}"
        
        expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y%m%d")
        gist_entry = f"HGTOKEN=Hgvip653={expiry}={device_id}"
        
        raw_url = f"https://gist.githubusercontent.com/sagarhalder7865-hub/{GIST_ID}/raw/{FILE_NAME}?{time.time()}"
        current_data = requests.get(raw_url).text
        update_gist(current_data + "\n" + gist_entry)
        
        receipt_msg = (
            f"🎉 *Script Key Generated!* (Admin)\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Customer:* {update.effective_user.first_name}\n"
            f"🆔 *User ID:* `{update.effective_user.id}`\n"
            f"🎮 *Item:* Script KEY ({days} Days)\n"
            f"📱 *Device ID:* `{device_id}`\n\n"
            f"🔑 *Your VIP Key (Tap to Copy):*\n"
            f"`{vip_key}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Updated to GitHub Gist successfully!"
        )
        await update.message.reply_text(receipt_msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Format: /scriptkey <days> <device_id>\nError: {e}")

async def cmd_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    await update.message.reply_text(f"```\n{stock_text()}\n```", parse_mode="Markdown")

async def cmd_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    await update.message.reply_text(f"```\n{price_list_text()}\n```", parse_mode="Markdown")

async def cmd_deliver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /deliver <user_id> <key>"); return
    uid = int(context.args[0]); key = " ".join(context.args[1:])
    await context.bot.send_message(uid, f"🔑 Your VIP Key:\n\n`{key}`", parse_mode="Markdown")
    await update.message.reply_text(f"✅ Key delivered to {uid}")

async def cmd_setprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        plan = context.args[0].lower(); reg = int(context.args[1]); res = int(context.args[2])
        db_set_price(plan, reg, res)
        await update.message.reply_text(f"✅ Price Updated for {plan}: Regular ₹{reg}, Reseller ₹{res} (Synced to GitHub ☁️)")
    except Exception: await update.message.reply_text("Usage: /setprice <plan_code> <regular> <reseller>")

async def cmd_addreseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_add_reseller(uid)
        await update.message.reply_text(f"✅ {uid} is now a Reseller (Synced to GitHub ☁️)")
    except Exception: await update.message.reply_text("Usage: /addreseller <user_id>")

async def cmd_removereseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_remove_reseller(uid)
        await update.message.reply_text(f"✅ {uid} removed from Resellers (Synced to GitHub ☁️)")
    except Exception: await update.message.reply_text("Usage: /removereseller <user_id>")

async def cmd_resellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    rlist = db_all_resellers()
    if not rlist:
        await update.message.reply_text("No resellers added yet.")
        return
    await update.message.reply_text("🏷 Resellers List:\n" + "\n".join(f"• {r}" for r in rlist))

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set.")
        exit(1)
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",          start))
    app.add_handler(CommandHandler("help",           cmd_help))
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
    print("VIP Bot Updated & Running with Cloud Sync... 🚀")
    app.run_polling()
