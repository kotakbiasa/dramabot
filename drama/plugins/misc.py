# Copyright (c) 2025 DramaBot
# Miscellaneous commands


from pyrogram import filters
from pyrogram.types import Message

from drama import app, db


@app.on_message(filters.command("settings") & filters.group)
async def settings_command(_, message: Message):
    """Show group settings"""
    chat_id = message.chat.id
    
    play_mode = await db.get_play_mode(chat_id)
    cmd_delete = await db.get_cmd_delete(chat_id)
    
    text = (
        f"⚙️ **Pengaturan Grup**\n\n"
        f"**Play Mode:**\n"
        f"└ {'🔒 Admin Only' if play_mode else '👥 Everyone'}\n\n"
        f"**Auto Delete Commands:**\n"
        f"└ {'✅ Enabled' if cmd_delete else '❌ Disabled'}\n\n"
        f"Gunakan command berikut untuk mengubah:\n"
        f"• `/playmode` - Toggle play mode\n"
        f"• `/delcmd` - Toggle auto delete"
    )
    
    await message.reply_text(text)


@app.on_message(filters.command("playmode") & filters.group)
async def playmode_command(_, message: Message):
    """Toggle play mode (admin/everyone)"""
    from drama.helpers import is_admin
    
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Hanya admin yang bisa ubah setting!")
    
    chat_id = message.chat.id
    current = await db.get_play_mode(chat_id)
    new_mode = not current
    
    await db.set_play_mode(chat_id, new_mode)
    
    mode_text = "🔒 Admin Only" if new_mode else "👥 Everyone"
    await message.reply_text(f"✅ Play mode diubah ke: **{mode_text}**")


@app.on_message(filters.command("delcmd") & filters.group)
async def delcmd_command(_, message: Message):
    """Toggle auto delete commands"""
    from drama.helpers import is_admin
    
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Hanya admin yang bisa ubah setting!")
    
    chat_id = message.chat.id
    current = await db.get_cmd_delete(chat_id)
    new_mode = not current
    
    await db.set_cmd_delete(chat_id, new_mode)
    
    mode_text = "✅ Enabled" if new_mode else "❌ Disabled"
    await message.reply_text(f"✅ Auto delete commands: **{mode_text}**")
