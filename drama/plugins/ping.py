# Copyright (c) 2025 DramaBot
# Ping command


from pyrogram import filters
from pyrogram.types import Message
import time

from drama import app, config, drama_call, boot


@app.on_message(filters.command("ping"))
async def ping_command(_, message: Message):
    """Check bot ping and uptime"""
    start = time.time()
    msg = await message.reply_text("🏓 Pinging...")
    end = time.time()
    
    # Calculate uptime
    uptime_sec = int(time.time() - boot)
    uptime_min = uptime_sec // 60
    uptime_hour = uptime_min // 60
    uptime_day = uptime_hour // 24
    
    uptime_str = f"{uptime_day}d " if uptime_day else ""
    uptime_str += f"{uptime_hour % 24}h {uptime_min % 60}m"
    
    # Get pytgcalls ping
    try:
        tgcalls_ping = await drama_call.ping()
    except:
        tgcalls_ping = 0.0
    
    text = (
        f"🏓 **Pong!**\n\n"
        f"> 📡 **Ping:** `{round((end - start) * 1000, 2)}ms`\n"
        f"> 🎵 **PyTgCalls:** `{tgcalls_ping}ms`\n"
        f"> ⏰ **Uptime:** `{uptime_str}`\n"
    )
    
    await msg.edit_text(text)
