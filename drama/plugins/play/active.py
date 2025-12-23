# Copyright (c) 2025 DramaBot
# Active voice chats list


from pyrogram import filters
from pyrogram.types import Message

from drama import app, db


@app.on_message(filters.command("active"))
async def active_command(_, message: Message):
    """Show active voice chats (sudo only)"""
    # Check if user is sudo
    if message.from_user.id not in app.sudoers:
        return
        
    if not db.active_calls:
        return await message.reply_text("📭 Tidak ada voice chat aktif saat ini.")
    
    text = f"📡 **Active Voice Chats** ({len(db.active_calls)})\n\n"
    
    for i, chat_id in enumerate(db.active_calls, 1):
        try:
            chat = await app.get_chat(chat_id)
            text += f"{i}. **{chat.title}**\n"
            text += f"   ID: `{chat_id}`\n"
        except:
            text += f"{i}. Chat ID: `{chat_id}`\n"
    
    await message.reply_text(text)
