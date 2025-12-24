# Copyright (c) 2025 DramaBot
# Resume playback


from pyrogram import filters
from pyrogram.types import Message

from drama import app, drama_call, db


@app.on_message(filters.command("resume") & filters.group)
async def resume_command(_, message: Message):
    """Resume paused playback"""
    chat_id = message.chat.id
    
    if not await db.get_call(chat_id):
        return await message.reply_text("❌ Tidak ada yang sedang diputar!")
    
    try:
        await drama_call.resume(chat_id)
        await message.reply_text("▶️ **Resumed**")
        
        # Auto delete command message
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
