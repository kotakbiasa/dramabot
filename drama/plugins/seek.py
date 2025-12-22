# Copyright (c) 2025 DramaBot
# Seek in playback


from pyrogram import filters
from pyrogram.types import Message

from drama import app, drama_call, db, queue


@app.on_message(filters.command("seek") & filters.group)
async def seek_command(_, message: Message):
    """Seek to specific time (format: /seek 1:30)"""
    if not await db.get_call(message.chat.id):
        return await message.reply_text("❌ Tidak ada yang sedang diputar!")
    
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Cara penggunaan:**\n"
            "`/seek <waktu>`\n\n"
            "**Contoh:**\n"
            "• `/seek 1:30` - Seek ke menit 1:30\n"
            "• `/seek 90` - Seek ke detik 90"
        )
    
    try:
        # Parse time (support format: MM:SS or seconds)
        time_str = message.command[1]
        if ":" in time_str:
            parts = time_str.split(":")
            seconds = int(parts[0]) * 60 + int(parts[1])
        else:
            seconds = int(time_str)
        
        if seconds < 0:
            return await message.reply_text("❌ Waktu tidak valid!")
        
        # Get current media
        media = queue.get_current(message.chat.id)
        if not media:
            return await message.reply_text("❌ Tidak ada media saat ini!")
        
        msg = await message.reply_text(f"⏩ Seeking ke {time_str}...")
        
        # Replay with seek time
        await drama_call.play_media(message.chat.id, msg, media, seek_time=seconds)
        
    except ValueError:
        await message.reply_text("❌ Format waktu tidak valid!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
