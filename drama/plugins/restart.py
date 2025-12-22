# Copyright (c) 2025 DramaBot
# Restart bot


from pyrogram import filters
from pyrogram.types import Message
import os
import sys

from drama import app


@app.on_message(filters.command("restart"))
async def restart_command(_, message: Message):
    """Restart bot (sudo only)"""
    # Check sudo
    if message.from_user.id not in app.sudoers:
        return

    msg = await message.reply_text("🔄 **Restarting bot...**")
    
    try:
        await msg.edit_text("✅ Bot akan restart dalam beberapa detik...")
        os.execl(sys.executable, sys.executable, "-m", "drama")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
