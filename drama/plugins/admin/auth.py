# Copyright (c) 2025 DramaBot
# Authorization management


import time
from pyrogram import filters, types

from drama import app, db
from drama.helpers import admin_check, is_admin, utils


@app.on_message(filters.command(["auth", "unauth"]) & filters.group & ~app.bl_users)
@admin_check
async def auth_command(_, m: types.Message):
    """Add/remove authorized users"""
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text("❌ User tidak ditemukan!")

    if m.command[0] == "auth":
        if await is_admin(m.chat.id, user.id):
            return await m.reply_text("❌ User ini sudah admin!")

        await db.add_auth(m.chat.id, user.id)
        await m.reply_text(f"✅ {user.mention} ditambahkan ke authorized users.")
    else:
        await db.rm_auth(m.chat.id, user.id)
        await m.reply_text(f"✅ {user.mention} dihapus dari authorized users.")


rel_hist = {}

@app.on_message(filters.command(["admincache", "reload"]) & filters.group & ~app.bl_users)
async def admincache_command(_, m: types.Message):
    """Reload admin cache"""
    if m.from_user.id in rel_hist:
        if time.time() < rel_hist[m.from_user.id]:
            return await m.reply_text("⏳ Tunggu 3 menit sebelum reload lagi.")

    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Hanya admin yang bisa reload cache!")

    rel_hist[m.from_user.id] = time.time() + 180
    await db.get_admins(m.chat.id, reload=True)
    await m.reply_text("✅ Admin cache berhasil direload!")
