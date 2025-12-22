# Copyright (c) 2025 DramaBot  
# Plugin untuk menampilkan drama trending


from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from drama import app, api


@app.on_message(filters.command("trending"))
async def trending_command(_, message: Message):
    """Handler untuk /trending command"""
    msg = await message.reply_text("🔍 Mencari drama trending...")
    
    try:
        dramas = await api.get_trending(limit=10)
        
        if not dramas:
            return await msg.edit_text("❌ Tidak ada drama trending saat ini.")
        
        text = "🔥 **Drama Trending**\n\n"
        keyboard = []
        
        for i, drama in enumerate(dramas, 1):
            # Format lebih clean tanpa blockquote
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


@app.on_callback_query(filters.regex(r"^browse_trending$"))
async def browse_trending_callback(_, query):
    """Handler untuk callback browse trending"""
    await query.answer("Loading...")
    
    try:
        dramas = await api.get_trending(limit=5)
        
        if not dramas:
            return await query.message.edit_text("❌ Tidak ada drama trending.")
        
        text = "🔥 **Drama Trending**\n\n"
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
