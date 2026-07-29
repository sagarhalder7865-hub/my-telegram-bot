import os
import json
import asyncio
import time
import sqlite3
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- RENDER WEB SERVER (Port Error & Timeout Fix) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

# Background Thread for Web Server
Thread(target=run_web_server, daemon=True).start()
# --------------------------------------------------

TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 8546348748

BOT_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BOT_DIR, "bot_data.db")
QR_PATH  = os.path.join(BOT_DIR, "payment_qr.png")

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
        """)
        existing = db.execute("SELECT COUNT(*) FROM prices").fetchone()[0]
        if existing == 0:
            defaults = [
                ("c1",  "KOS",          "1 Day",   110,  100),
                ("c7",  "KOS",          "7 Days",  310,  260),
                ("c15", "KOS",          "15 Days", 500,  470),
                ("c30", "KOS",          "30 Days", 840,  760),
                ("s3",  "SNAKE ENGINE", "3 Days",  190,  170),
                ("s10", "SNAKE ENGINE", "10 Days", 460,  420),
                ("s30", "SNAKE ENGINE", "30 Days", 890,  820),
                ("s90", "SNAKE ENGINE", "90 Days", 2400, 2000),
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

def db_pop_key(plan):
    with get_db() as db:
        row = db.execute("SELECT id,key FROM keys WHERE plan=? ORDER BY id LIMIT 1", (plan,)).fetchone()
        if row:
            db.execute("DELETE FROM keys WHERE id=?", (row["id"],))
            return row["key"]
    return None

def db_is_reseller(user_id):
    with get_db() as db:
        return db.execute("SELECT 1 FROM resellers WHERE user_id=?", (user_id,)).fetchone() is not None

def db_add_reseller(user_id):
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO resellers (user_id) VALUES (?)", (user_id,))

def db_remove_reseller(user_id):
    with get_db() as db:
        db.execute("DELETE FROM resellers WHERE user_id=?", (user_id,))

def db_all_resellers():
    with get_db() as db:
        return [r["user_id"] for r in db.execute("SELECT user_id FROM resellers").fetchall()]

def db_get_plan(plan_id):
    with get_db() as db:
        return db.execute("SELECT * FROM prices WHERE plan=?", (plan_id,)).fetchone()

def db_set_price(plan_id, regular, reseller):
    with get_db() as db:
        db.execute("UPDATE prices SET regular=?, reseller=? WHERE plan=?", (regular, reseller, plan_id))

ALL_PLANS = ["c1","c7","c15","c30","s3","s10","s30","s90"]

def get_price(user_id, plan_id):
    p = db_get_plan(plan_id)
    return p["reseller"] if db_is_reseller(user_id) else p["regular"]

def stock_text():
    lines = ["📦 *Current Stock*\n", "*KOS:*"]
    for p in ["c1","c7","c15","c30"]:
        plan = db_get_plan(p)
        lines.append(f"  {plan['label']:8} : {db_count_keys(p)}")
    lines.append("\n*SNAKE ENGINE:*")
    for p in ["s3","s10","s30","s90"]:
        plan = db_get_plan(p)
        lines.append(f"  {plan['label']:8} : {db_count_keys(p)}")
    return "\n".join(lines)

def price_list_text():
    lines = ["💰 *Current Price List*\n", "*KOS:*"]
    for p in ["c1","c7","c15","c30"]:
        plan = db_get_plan(p)
        lines.append(f"  {plan['label']:8} → ₹{plan['regular']}  (Reseller: ₹{plan['reseller']})")
    lines.append("\n*SNAKE ENGINE:*")
    for p in ["s3","s10","s30","s90"]:
        plan = db_get_plan(p)
        lines.append(f"  {plan['label']:8} → ₹{plan['regular']}  (Reseller: ₹{plan['reseller']})")
    return "\n".join(lines)

pending_orders   = {}
payment_requests = {}
PAYMENT_TIMEOUT  = 300

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    role = "🏷 Reseller" if db_is_reseller(uid) else "👤 Customer"
    bal  = db_get_balance(uid)
    keyboard = [
        ["🛒 Buy",        "💰 Balance"],
        ["➕ Add Balance", "📦 Stock"],
        ["📞 Admin Help"]
    ]
    await update.message.reply_text(
        f"⚡ *Welcome!*\n\n🆔 Your ID: `{uid}`\n{role}\n💰 Balance: ₹{bal}",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text    = update.message.text
    user_id = update.effective_user.id

    if text == "🛒 Buy":
        keyboard = [
            [InlineKeyboardButton("🐍 SNAKE ENGINE",                  callback_data="snake")],
            [InlineKeyboardButton("🎮 KOS",                           callback_data="kos")],
            [InlineKeyboardButton("⚡ Blitz Engine — Coming Soon 🔜", callback_data="blitz")],
        ]
        await update.message.reply_text("🎮 Select Game:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "💰 Balance":
        bal  = db_get_balance(user_id)
        role = " 🏷 (Reseller)" if db_is_reseller(user_id) else ""
        await update.message.reply_text(f"💰 Balance: ₹{bal}{role}")

    elif text == "➕ Add Balance":
        with open(QR_PATH, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=(
                    "💳 *Scan & Pay via PhonePe*\n\n"
                    "UPI: `sagarhalder22@axl`\n\n"
                    "✅ After payment, send the *screenshot* here\n"
                    "⏰ Verify within 5 minutes"
                ),
                parse_mode="Markdown"
            )

    elif text == "📦 Stock":
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Admin only")
            return
        await update.message.reply_text(stock_text(), parse_mode="Markdown")

    elif text == "📞 Admin Help":
        plans_data = {p: db_get_plan(p) for p in ALL_PLANS}
        await update.message.reply_text(
            "📞 *Admin:* @happy_gamer2\n\n"
            "💼 *Want Reseller prices? Contact admin!*\n\n"
            "🏷 *Reseller Price List:*\n"
            f"SNAKE 3D → ₹{plans_data['s3']['reseller']} | 10D → ₹{plans_data['s10']['reseller']}\n"
            f"SNAKE 30D → ₹{plans_data['s30']['reseller']} | 90D → ₹{plans_data['s90']['reseller']}\n\n"
            f"KOS 1D → ₹{plans_data['c1']['reseller']} | 7D → ₹{plans_data['c7']['reseller']}\n"
            f"KOS 15D → ₹{plans_data['c15']['reseller']} | 30D → ₹{plans_data['c30']['reseller']}",
            parse_mode="Markdown"
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data.startswith("pay_"):
        parts     = query.data.split("_")
        target_id = int(parts[1])
        action    = parts[2]
        if action == "reject":
            req = payment_requests.pop(target_id, None)
            if req and req.get("task"): req["task"].cancel()
            try:
                await context.bot.send_message(target_id, "❌ Payment rejected.\nContact admin @happy_gamer2")
            except Exception: pass
            await query.edit_message_caption("❌ Payment Rejected")
            return
        amount = int(action)
        req = payment_requests.pop(target_id, None)
        if req and req.get("task"): req["task"].cancel()
        new_bal = db_add_balance(target_id, amount)
        try:
            await context.bot.send_message(
                target_id,
                f"✅ *Payment Verified!*\n💰 ₹{amount} added.\nNew balance: ₹{new_bal}",
                parse_mode="Markdown"
            )
        except Exception: pass
        await query.edit_message_caption(f"✅ Approved ₹{amount} → user {target_id}")
        return

    if query.data.startswith("verify_"):
        cust_id = int(query.data.split("_")[1])
        if cust_id != user_id: return
        if cust_id not in payment_requests:
            await query.edit_message_caption("⚠️ Expired. Please send screenshot again.")
            return
        photo_id = payment_requests[cust_id]["photo_id"]
        user_obj = query.from_user
        name     = user_obj.full_name
        username = f"@{user_obj.username}" if user_obj.username else "No username"
        role_lbl = "🏷 Reseller" if db_is_reseller(cust_id) else "👤 Customer"
        await query.edit_message_caption("⏳ *Verifying...*\nAdmin is reviewing. Please wait.", parse_mode="Markdown")
        all_prices = sorted(set(
            val for p in ALL_PLANS
            for val in [db_get_plan(p)["regular"], db_get_plan(p)["reseller"]]
        ))
        row, kbd = [], []
        for price in all_prices:
            row.append(InlineKeyboardButton(f"✅ ₹{price}", callback_data=f"pay_{cust_id}_{price}"))
            if len(row) == 3: kbd.append(row); row = []
        if row: kbd.append(row)
        kbd.append([InlineKeyboardButton("❌ Reject", callback_data=f"pay_{cust_id}_reject")])
        await context.bot.send_photo(
            chat_id=ADMIN_ID, photo=photo_id,
            caption=(
                f"💳 *Payment Request*\n\n"
                f"🆔 ID: `{cust_id}`\n👤 Name: {name}\n"
                f"📱 Username: {username}\n🏷 Role: {role_lbl}\n"
                f"💰 Balance: ₹{db_get_balance(cust_id)}\n\n⏰ Auto-cancels in 5 min"
            ),
            reply_markup=InlineKeyboardMarkup(kbd), parse_mode="Markdown"
        )
        return

    if query.data == "blitz":
        await query.answer("⚡ Blitz Engine — Coming Soon! Stay tuned 🔜", show_alert=True)
        return

    if query.data == "kos":
        keyboard = [
            [InlineKeyboardButton(f"1 Day  — ₹{get_price(user_id,'c1')}",   callback_data="c1")],
            [InlineKeyboardButton(f"7 Days — ₹{get_price(user_id,'c7')}",   callback_data="c7")],
            [InlineKeyboardButton(f"15 Days — ₹{get_price(user_id,'c15')}", callback_data="c15")],
            [InlineKeyboardButton(f"30 Days — ₹{get_price(user_id,'c30')}", callback_data="c30")],
        ]
        await query.edit_message_text("🎮 *KOS Plans:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "snake":
        keyboard = [
            [InlineKeyboardButton(f"3 Days  — ₹{get_price(user_id,'s3')}",  callback_data="s3")],
            [InlineKeyboardButton(f"10 Days — ₹{get_price(user_id,'s10')}", callback_data="s10")],
            [InlineKeyboardButton(f"30 Days — ₹{get_price(user_id,'s30')}", callback_data="s30")],
            [InlineKeyboardButton(f"90 Days — ₹{get_price(user_id,'s90')}", callback_data="s90")],
        ]
        await query.edit_message_text("🐍 *SNAKE ENGINE Plans:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data in ALL_PLANS:
        plan  = db_get_plan(query.data)
        price = get_price(user_id, query.data)
        pending_orders[user_id] = query.data
        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data="confirm")],
            [InlineKeyboardButton("❌ Cancel",  callback_data="cancel")],
        ]
        await query.edit_message_text(
            f"🧾 *Confirm Order*\n\n{plan['game']} — {plan['label']}\n💰 ₹{price}",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

    elif query.data == "confirm":
        if user_id not in pending_orders:
            await query.edit_message_text("❌ No pending order.")
            return
        plan_id = pending_orders[user_id]
        plan    = db_get_plan(plan_id)
        price   = get_price(user_id, plan_id)
        bal     = db_get_balance(user_id)
        if bal < price:
            await query.edit_message_text("❌ Not enough balance.\nPlease add balance first.")
            return
        if db_count_keys(plan_id) == 0:
            await query.edit_message_text("❌ Out of stock!\nContact admin @happy_gamer2")
            return
        db_set_balance(user_id, bal - price)
        key = db_pop_key(plan_id)
        pending_orders.pop(user_id, None)
        await query.edit_message_text(
            f"✅ *Purchase Successful!*\n\n"
            f"🎮 {plan['game']} — {plan['label']}\n"
            f"💰 ₹{price} deducted\n\n🔑 Your Key:\n`{key}`",
            parse_mode="Markdown"
        )

    elif query.data == "cancel":
        pending_orders.pop(user_id, None)
        await query.edit_message_text("❌ Order Cancelled")

async def expire_payment(user_id, context):
    await asyncio.sleep(PAYMENT_TIMEOUT)
    if user_id in payment_requests:
        del payment_requests[user_id]
        try:
            await context.bot.send_message(user_id, "⏰ Payment request expired (5 min).\nPlease send screenshot again.")
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
        caption=(
            "📸 *Screenshot received!*\n\n"
            "👇 Tap the button below to send for verification.\n"
            "⏰ Must verify within 5 minutes."
        ),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Verify Payment", callback_data=f"verify_{user_id}")
        ]]),
        parse_mode="Markdown"
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(
        "🛠 *Admin Commands*\n\n"
        "*Balance:*\n`/add <id> <amount>`\n\n"
        "*Keys:*\n`/addkey <plan> <key>`\n`/stock`\n`/deliver <id> <key>`\n\n"
        "*Prices:*\n`/setprice <plan> <regular> <reseller>`\n`/prices`\n\n"
        "*Resellers:*\n`/addreseller <id>`\n`/removereseller <id>`\n`/resellers`\n\n"
        "*Plan codes:*\n"
        "`c1` KOS 1D | `c7` KOS 7D | `c15` KOS 15D | `c30` KOS 30D\n"
        "`s3` SNK 3D | `s10` SNK 10D | `s30` SNK 30D | `s90` SNK 90D",
        parse_mode="Markdown"
    )

async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        uid = int(context.args[0]); amount = int(context.args[1])
        new_bal = db_add_balance(uid, amount)
        await update.message.reply_text(f"✅ Added ₹{amount} to `{uid}`\nBalance: ₹{new_bal}", parse_mode="Markdown")
        try: await context.bot.send_message(uid, f"✅ Admin added ₹{amount}.\nNew balance: ₹{new_bal}")
        except Exception: pass
    except Exception:
        await update.message.reply_text("Usage: /add <user_id> <amount>")

async def cmd_addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        plan = context.args[0].lower(); new_key = context.args[1]
        if plan not in ALL_PLANS:
            await update.message.reply_text("❌ Invalid plan\nValid: " + " ".join(ALL_PLANS)); return
        db_add_key(plan, new_key)
        p = db_get_plan(plan)
        await update.message.reply_text(
            f"✅ *Key Added*\n`{p['game']} {p['label']}`\nKey: `{new_key}`\nStock: {db_count_keys(plan)}",
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text("Usage: /addkey <plan> <key>\nPlans: c1 c7 c15 c30  s3 s10 s30 s90")

async def cmd_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(stock_text(), parse_mode="Markdown")

async def cmd_setprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        plan = context.args[0].lower(); regular = int(context.args[1]); reseller = int(context.args[2])
        if plan not in ALL_PLANS:
            await update.message.reply_text("❌ Invalid plan"); return
        db_set_price(plan, regular, reseller)
        p = db_get_plan(plan)
        await update.message.reply_text(
            f"✅ *Price Updated!*\n`{p['game']} {p['label']}`\nRegular: ₹{regular}\nReseller: ₹{reseller}",
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text("Usage: /setprice <plan> <regular> <reseller>\nExample: /setprice s3 200 180")

async def cmd_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(price_list_text(), parse_mode="Markdown")

async def cmd_deliver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /deliver <user_id> <key>"); return
    uid = int(context.args[0]); key = " ".join(context.args[1:])
    await context.bot.send_message(uid, f"🔑 *Your Key:*\n\n`{key}`", parse_mode="Markdown")
    await update.message.reply_text(f"✅ Key delivered to {uid}")

async def cmd_addreseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        uid = int(context.args[0])
        db_add_reseller(uid)
        await update.message.reply_text(f"✅ `{uid}` is now a Reseller 🏷", parse_mode="Markdown")
        try:
            await context.bot.send_message(uid, "🎉 You are now a *Reseller*!\nSpecial prices active.\nUse /start to refresh.", parse_mode="Markdown")
        except Exception: pass
    except Exception:
        await update.message.reply_text("Usage: /addreseller <user_id>")

async def cmd_removereseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        uid = int(context.args[0])
        db_remove_reseller(uid)
        await update.message.reply_text(f"✅ `{uid}` removed from resellers", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("Usage: /removereseller <user_id>")

async def cmd_resellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    rlist = db_all_resellers()
    if not rlist:
        await update.message.reply_text("No resellers yet.")
        return
    await update.message.reply_text("🏷 *Resellers:*\n" + "\n".join(f"• `{r}`" for r in rlist), parse_mode="Markdown")

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set.")
        exit(1)
    init_db()
    print("Database ready ✅")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",          start))
    app.add_handler(CommandHandler("help",           cmd_help))
    app.add_handler(CommandHandler("add",            cmd_add))
    app.add_handler(CommandHandler("addkey",         cmd_addkey))
    app.add_handler(CommandHandler("stock",          cmd_stock))
    app.add_handler(CommandHandler("setprice",       cmd_setprice))
    app.add_handler(CommandHandler("prices",         cmd_prices))
    app.add_handler(CommandHandler("deliver",        cmd_deliver))
    app.add_handler(CommandHandler("addreseller",    cmd_addreseller))
    app.add_handler(CommandHandler("removereseller", cmd_removereseller))
    app.add_handler(CommandHandler("resellers",      cmd_resellers))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    print("Bot is running... 🚀")
    app.run_polling()
        
