# Copyright (c) 2025 DramaBot
# Plugin untuk mencari drama


from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from drama import app, api, config


@app.on_message(filters.command("search"))
async def search_command(_, message: Message):
    """Handler untuk /search command"""
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Cara penggunaan:**\n"
            "`/search <judul drama>`\n\n"
            "**Contoh:**\n"
            "`/search pewaris`"
        )
    
    query = " ".join(message.command[1:])
    msg = await message.reply_text(f"🔍 Mencari drama: **{query}**...")
    
    try:
        dramas = await api.search(query, limit=10)
        
        if not dramas:
            return await msg.edit_text(
                f"❌ Tidak ditemukan drama dengan kata kunci: **{query}**\n\n"
                f"Coba kata kunci lain atau lihat:\n"
                f"• `/trending` - Drama trending\n"
                f"• `/latest` - Drama terbaru"
            )
        
        text = f"🔍 **Hasil pencarian:** `{query}`\n\n"
        keyboard = []
        
        for i, drama in enumerate(dramas, 1):
            # Only show title
            text += f"**{i}. {drama.title}**\n"
        
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
        await message.reply_text(
            text=text,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}\nCoba lagi nanti.")
