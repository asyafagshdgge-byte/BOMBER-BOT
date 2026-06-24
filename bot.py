#!/usr/bin/env python3
# DEMON 😈 BOMBER BOT - RAILWAY FIXED EDITION

import logging
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from bomber import bomber
from config import BOT_TOKEN, BOMB_DURATION, API_LIST

# ========== LOGGING ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== KEYBOARDS ==========
main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("💣 START 5-MIN BOMB"), KeyboardButton("🛑 STOP BOMBING")],
    [KeyboardButton("📊 STATUS"), KeyboardButton("ℹ️ HELP")],
    [KeyboardButton("👨‍💻 ABOUT DEMON")]
], resize_keyboard=True)

inline_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("☢️ START MEGA BOMB (ALL 9 APIS)", callback_data="start_mega")],
    [InlineKeyboardButton("⏱️ START 5-MIN TIMER BOMB", callback_data="start_timer")],
    [InlineKeyboardButton("🛑 STOP BOMBING", callback_data="stop")],
    [InlineKeyboardButton("📊 CHECK STATUS", callback_data="status")],
    [InlineKeyboardButton("❌ CANCEL", callback_data="cancel")]
])

# ========== COMMANDS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"""🔥 *DEMON 😈 BOMBER BOT v3.0 - RAILWAY EDITION*

*👤 User:* `{user.first_name}`
*🆔 ID:* `{user.id}`

*💀 Features:*
• ☢️ ALL 9 APIs ek saath
• ⏱️ 5-Minute auto-stop
• 🔄 Manual toggle ON/OFF
• 📊 Real-time status

*📌 Commands:*
`/start` - Show this
`/help` - Full guide
`/bomb <phone>` - Start 5-min bomb
`/stop` - Stop bombing
`/status` - Check status

*🔥 Quick Start:*
Send `/bomb 9876543210` or use buttons!
""",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

async def bomb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ *CHUTIYE! Phone number do!*\n\nUsage: `/bomb 9876543210`",
            parse_mode='Markdown'
        )
        return
        
    phone = args[0]
    if not phone.isdigit() or len(phone) < 10:
        await update.message.reply_text("❌ *Invalid phone!*", parse_mode='Markdown')
        return
    
    user_id = update.effective_user.id
    status = bomber.get_status(user_id)
    if status["active"]:
        await update.message.reply_text(
            f"⚠️ *Already bombing!* Remaining: `{status['remaining']}`s",
            parse_mode='Markdown'
        )
        return
    
    status_msg = await update.message.reply_text(
        f"""☢️ *MEGA BOMB INITIATED!*
📱 *Target:* `{phone}`
⏱️ *Auto-stop:* 5 minutes
⚡ *DEMON 😈 is attacking!*""",
        parse_mode='Markdown'
    )
    
    result = await bomber.continuous_bombing(phone, user_id, BOMB_DURATION)
    
    await status_msg.edit_text(
        f"""💀 *BOMBING COMPLETED!*
📱 *Target:* `{result['phone']}`
🔄 *Cycles:* `{result['total_cycles']}`
⏱️ *Duration:* `{result['duration']}`s
😈 *DEMON 😈 RETREATS!*""",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await bomber.stop_bombing(user_id):
        await update.message.reply_text("🛑 *BOMBING STOPPED!*", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ *No active bombing!*", parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    status = bomber.get_status(user_id)
    if status["active"]:
        await update.message.reply_text(
            f"""📊 *STATUS*
🟢 Active: ✅
📱 Target: `{status['phone']}`
⏳ Remaining: `{status['remaining']}`s""",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("📊 *Status:* 🔴 IDLE", parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """💀 *HELP MENU*
`/bomb <phone>` - Start 5-min bomb
`/stop` - Stop bombing
`/status` - Check status

*Auto-stops after 5 minutes!*""",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "💣 START 5-MIN BOMB":
        await update.message.reply_text("📱 *Enter phone number:*", parse_mode='Markdown')
        context.user_data['awaiting_phone'] = True
        
    elif text == "🛑 STOP BOMBING":
        await stop_command(update, context)
        
    elif text == "📊 STATUS":
        await status_command(update, context)
        
    elif text == "ℹ️ HELP":
        await help_command(update, context)
        
    elif text == "👨‍💻 ABOUT DEMON":
        await update.message.reply_text(
            """🔥 *DEMON 😈 BOMBER v3.0*
👨‍💻 Developer: DEMON 😈
🚂 Host: Railway (24/7)
📡 APIs: 9
😈 "No rules. No excuses."""",
            parse_mode='Markdown'
        )
        
    elif context.user_data.get('awaiting_phone'):
        phone = text.strip()
        if phone.isdigit() and len(phone) >= 10:
            context.user_data['awaiting_phone'] = False
            context.user_data['phone'] = phone
            
            user_id = update.effective_user.id
            status = bomber.get_status(user_id)
            if status["active"]:
                await update.message.reply_text("⚠️ *Already bombing!*", parse_mode='Markdown')
                return
            
            status_msg = await update.message.reply_text(
                f"""☢️ *BOMBING STARTED!* 📱 `{phone}`""",
                parse_mode='Markdown'
            )
            
            result = await bomber.continuous_bombing(phone, user_id, BOMB_DURATION)
            
            await status_msg.edit_text(
                f"""💀 *DONE!* 📱 `{phone}` 🔄 `{result['total_cycles']}` cycles""",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ *Invalid phone!*", parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    
    if data == "cancel":
        await query.edit_message_text("❌ *Cancelled!*", parse_mode='Markdown')
        return
    
    if data == "start_mega" or data == "start_timer":
        phone = context.user_data.get('phone')
        if not phone:
            await query.edit_message_text("❌ *No phone!* Use /bomb", parse_mode='Markdown')
            return
        
        status = bomber.get_status(user_id)
        if status["active"]:
            await query.edit_message_text(f"⚠️ *Already bombing!*", parse_mode='Markdown')
            return
        
        await query.edit_message_text(f"""☢️ *BOMBING!* 📱 `{phone}`""", parse_mode='Markdown')
        result = await bomber.continuous_bombing(phone, user_id, BOMB_DURATION)
        await query.edit_message_text(
            f"""💀 *DONE!* 📱 `{phone}` 🔄 `{result['total_cycles']}` cycles""",
            parse_mode='Markdown'
        )
        return
    
    if data == "stop":
        if await bomber.stop_bombing(user_id):
            await query.edit_message_text("🛑 *STOPPED!*", parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ *No active bombing!*", parse_mode='Markdown')
        return
    
    if data == "status":
        status = bomber.get_status(user_id)
        if status["active"]:
            await query.edit_message_text(
                f"""📊 *ACTIVE* 📱 `{status['phone']}` ⏳ `{status['remaining']}`s""",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("📊 *IDLE*", parse_mode='Markdown')

# ========== MAIN WITH WEB SERVER FOR RAILWAY ==========

async def web_server():
    """Simple HTTP server for Railway healthcheck"""
    from aiohttp import web
    
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
    logger.info(f"[🌐] Web server running on port {port}")
    
    # Keep running
    await asyncio.Event().wait()

async def run_bot():
    """Run Telegram bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("bomb", bomb_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("[⚡] DEMON 😈 BOT IS ALIVE!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep running
    await asyncio.Event().wait()

async def main():
    """Run both bot and web server"""
    await asyncio.gather(
        run_bot(),
        web_server()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[🛑] Shutting down...")
