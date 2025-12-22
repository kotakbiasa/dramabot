# Copyright (c) 2025 DramaBot
# Plugin untuk menampilkan drama terbaru


from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from drama import app, api


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
        row = []
        for i, drama in enumerate(dramas, 1):
            row.append(InlineKeyboardButton(str(i), callback_data=f"drama_{drama.book_id}"))
            if i % 5 == 0 or i == len(dramas):
                keyboard.append(row)
                row = []
        
        await msg.edit_text(
            text,
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
        row = []
        for i, drama in enumerate(dramas, 1):
            row.append(InlineKeyboardButton(str(i), callback_data=f"drama_{drama.book_id}"))
            if i % 5 == 0 or i == len(dramas):
                keyboard.append(row)
                row = []
        
        keyboard.append([
            InlineKeyboardButton("« Kembali", callback_data="start_home")
        ])
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await query.message.edit_text(f"❌ Error: {str(e)}")
