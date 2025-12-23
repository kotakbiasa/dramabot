# Copyright (c) 2025 DramaBot
# Plugin untuk menampilkan drama terbaru


from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from drama import app, api, config


@app.on_message(filters.command("latest"))
async def latest_command(_, message: Message):
    """Handler untuk /latest command"""
    msg = await message.reply_text("🔍 Mencari drama terbaru...")
    
    try:
        dramas = await api.get_latest(limit=10)
        
        if not dramas:
            return await msg.edit_text("❌ Tidak ada drama terbaru saat ini.")
        
        text = "🆕 **Drama Terbaru**\n\n"
        keyboard = []
        
        for i, drama in enumerate(dramas, 1):
            # Format clean
            text += f"**{i}. {drama.title}**\n"
            text += f"📺 {drama.episode_count} episode"
            
            if drama.views:
                text += f" • 👁 {drama.views}"
            text += "\n\n"
        
        text += "💡 Klik nomor drama untuk mulai streaming!"
        
        # Create compact number buttons (5 per row)
        user_id = message.from_user.id
        row = []
        for i, drama in enumerate(dramas, 1):
            row.append(InlineKeyboardButton(str(i), callback_data=f"drama_{drama.book_id}_{user_id}"))
            if i % 5 == 0 or i == len(dramas):
                keyboard.append(row)
                row = []
        
        await msg.delete()
        await message.reply_photo(
            photo=config.BOT_BANNER,
            caption=text,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}\nCoba lagi nanti.")


@app.on_callback_query(filters.regex(r"^browse_latest$"))
async def browse_latest_callback(_, query):
    """Handler untuk callback browse latest"""
    await query.answer("Loading...")
    
    try:
        dramas = await api.get_latest(limit=5)
        
        if not dramas:
            return await query.message.edit_text("❌ Tidak ada drama terbaru.")
        
        text = "🆕 **Drama Terbaru**\n\n"
        keyboard = []
        
        for i, drama in enumerate(dramas, 1):
            text += f"**{i}. {drama.title}**\n"
            text += f"📺 {drama.episode_count} episode\n\n"
        
        # Create compact number buttons (5 per row)
        user_id = query.from_user.id
        row = []
        for i, drama in enumerate(dramas, 1):
            row.append(InlineKeyboardButton(str(i), callback_data=f"drama_{drama.book_id}_{user_id}"))
            if i % 5 == 0 or i == len(dramas):
                keyboard.append(row)
                row = []
        
        keyboard.append([
            InlineKeyboardButton("« Kembali", callback_data="start_home")
        ])
        
        # Check if message has photo, if yes edit caption, if no delete and send photo
        if query.message.photo:
             await query.message.edit_media(
                media=InputMediaPhoto(
                    media=config.BOT_BANNER,
                    caption=text,
                    parse_mode=enums.ParseMode.MARKDOWN
                ),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.message.delete()
            await query.message.reply_photo(
                photo=config.BOT_BANNER,
                caption=text,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
    except Exception as e:
        await query.message.edit_text(f"❌ Error: {str(e)}")
