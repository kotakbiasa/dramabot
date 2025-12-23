# Copyright (c) 2025 DramaBot
# Bot statistics


from pyrogram import filters
from pyrogram.types import Message

from drama import app, db


@app.on_message(filters.command("stats"))
async def stats_command(_, message: Message):
    """Show bot statistics"""
    msg = await message.reply_text("📊 Mengambil statistik...")
    
    try:
        total_chats = await db.count_chats()
        total_users = await db.count_users()
        sudo_count = len(app.sudoers)
        active_calls = len(db.active_calls)
        
        text = (
            f"📊 **Bot Statistics**\n\n"
            f"👥 **Total Users:** `{total_users}`\n"
            f"💬 **Total Chats:** `{total_chats}`\n"
            f"🎬 **Active Calls:** `{active_calls}`\n"
            f"👑 **Sudo Users:** `{sudo_count}`\n"
        )
        
        await msg.edit_text(text)
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
