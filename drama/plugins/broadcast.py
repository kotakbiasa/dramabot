# Copyright (c) 2025 DramaBot
# Broadcast message


import asyncio
from pyrogram import filters
from pyrogram.types import Message

from drama import app, db


@app.on_message(filters.command("broadcast"))
async def broadcast_command(_, message: Message):
    """Broadcast message to all users (sudo only)"""
    # Check sudo
    if message.from_user.id not in app.sudoers:
        return

    if not message.reply_to_message:
        return await message.reply_text(
            "❌ Reply ke pesan yang ingin dibroadcast!\n\n"
            "**Usage:** Reply ke pesan, lalu `/broadcast`"
        )
    
    msg = await message.reply_text("📡 Memulai broadcast...")
    
    users = await db.get_all_users()
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            success += 1
        except:
            failed += 1
        
        # Update progress every 50 users
        if (success + failed) % 50 == 0:
            await msg.edit_text(
                f"📡 **Broadcasting...**\n\n"
                f"✅ Success: {success}\n"
                f"❌ Failed: {failed}"
            )
        
        await asyncio.sleep(0.1)  # Avoid flood
    
    await msg.edit_text(
        f"✅ **Broadcast Selesai!**\n\n"
        f"📊 Total: {success + failed}\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}"
    )
