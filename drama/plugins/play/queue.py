# Copyright (c) 2025 DramaBot
# Queue management


from pyrogram import filters
from pyrogram.types import Message

from drama import app, queue, db
from drama.helpers import buttons


@app.on_message(filters.command("queue") & filters.group)
async def queue_command(_, message: Message):
    """Show current queue"""
    chat_id = message.chat.id
    
    q = queue.get_queue(chat_id)
    
    if not q:
        return await message.reply_text("📋 Queue kosong.\n\nGunakan `/play` untuk menambah episode.")
    
    text = "📋 **Current Queue**\n\n"
    
    # Current playing
    current = queue.get_current(chat_id)
    if current:
        text += f"🎬 **Sekarang Diputar:**\n"
        text += f"├ {current.title}\n"
        text += f"└ Durasi: {current.duration}\n\n"
    
    # Queue list
    if len(q) > 1:
        text += f"**Selanjutnya:** ({len(q)-1} episode)\n"
        for i, item in enumerate(q[1:], 1):
            if i > 10:  # Limit display
                text += f"\n... dan {len(q) - 11} episode lainnya"
                break
            text += f"{i}. {item.title}\n"
    
    # Check if playing
    is_playing = await db.get_call(chat_id)
    paused = await db.is_paused(chat_id) if is_playing else False
    
    status_text = "▶️ Playing" if is_playing and not paused else "⏸ Paused" if paused else "⏹ Stopped"
    
    await message.reply_text(
        text,
        reply_markup=buttons.queue_markup(chat_id, status_text, is_playing and not paused)
    )
