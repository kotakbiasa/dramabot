# Copyright (c) 2025 DramaBot
# Skip to next episode


from pyrogram import filters
from pyrogram.types import Message

from drama import app, drama_call, db


@app.on_message(filters.command("skip") & filters.group)
async def skip_command(_, message: Message):
    """Skip to next episode in queue"""
    chat_id = message.chat.id
    
    if not await db.get_call(chat_id):
        return await message.reply_text("❌ Tidak ada yang sedang diputar!")
    
    try:
        await drama_call.play_next(chat_id)
        await message.reply_text("⏭ **Skipped ke episode berikutnya**")
        
        # Auto delete command message
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
