# Copyright (c) 2025 DramaBot
# Sudo user management


from pyrogram import filters, types

from drama import app, db, config
from drama.helpers import utils


@app.on_message(filters.command(["addsudo", "rmsudo"]))
async def sudo_command(_, m: types.Message):
    """Add/remove sudo users (owner only)"""
    # Only owner can manage sudo
    if m.from_user.id != config.OWNER_ID:
        return

    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text("❌ User tidak ditemukan!")

    if user.id == config.OWNER_ID:
        return await m.reply_text("❌ Owner tidak perlu sudo!")

    if m.command[0] == "addsudo":
        await db.add_sudo(user.id)
        app.sudoers.add(user.id)
        await m.reply_text(f"✅ {user.mention} ditambahkan sebagai sudo user.")
    else:
        await db.rm_sudo(user.id)
        app.sudoers.discard(user.id)
        await m.reply_text(f"✅ {user.mention} dihapus dari sudo users.")


@app.on_message(filters.command("sudolist"))
async def sudolist_command(_, m: types.Message):
    """List all sudo users"""
    # Check sudo
    if m.from_user.id not in app.sudoers:
        return

    text = f"👑 **Sudo Users** ({len(app.sudoers)})\n\n"
    
    for i, user_id in enumerate(app.sudoers, 1):
        try:
            user = await app.get_users(user_id)
            text += f"{i}. {user.mention} (`{user_id}`)\n"
        except:
            text += f"{i}. User ID: `{user_id}`\n"
    
    await m.reply_text(text)
