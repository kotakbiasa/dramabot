# Copyright (c) 2025 DramaBot
# Stop playback and clear queue


from pyrogram import filters
from pyrogram.types import Message

from drama import app, drama_call, db


@app.on_message(filters.command("stop") & filters.group)
async def stop_command(_, message: Message):
    """Stop playback and clear queue"""
    chat_id = message.chat.id
    
    if not await db.get_call(chat_id):
        return await message.reply_text("❌ Tidak ada yang sedang diputar!")
    
    try:
        await drama_call.stop(chat_id)
        await message.reply_text("⏹ **Stopped**\nQueue telah dibersihkan.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
