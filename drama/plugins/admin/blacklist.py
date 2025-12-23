# Copyright (c) 2025 DramaBot
# Blacklist management


from pyrogram import filters, types

from drama import app, db
from drama.helpers import utils


@app.on_message(filters.command(["blacklist", "unblacklist"]))
async def blacklist_command(_, m: types.Message):
    """Blacklist/unblacklist users (sudo only)"""
    # Check sudo
    if message.from_user.id not in app.sudoers:
        return

    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text("❌ User tidak ditemukan!")

    if user.id in app.sudoers:
        return await m.reply_text("❌ Tidak bisa blacklist sudo user!")

    if m.command[0] == "blacklist":
        await db.add_blacklist(user.id)
        app.bl_users.add(user.id)
        await m.reply_text(f"✅ {user.mention} telah diblacklist.")
    else:
        await db.rm_blacklist(user.id)
        app.bl_users.discard(user.id)
        await m.reply_text(f"✅ {user.mention} dihapus dari blacklist.")
