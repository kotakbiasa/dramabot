# Copyright (c) 2025 DramaBot
# Settings command untuk konfigurasi bot

from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from drama import app, db
from drama.helpers._admins import admin_check


# Available resolutions
RESOLUTIONS = [360, 480, 720, 1080]


async def get_settings_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """Create settings menu with toggle buttons"""
    # Get current settings
    current_res = await db.get_resolution(chat_id)
    cmd_delete = await db.get_cmd_delete(chat_id)
    admin_play = await db.get_play_mode(chat_id)
    
    # Toggle icons
    on = "✅"
    off = "❌"
    
    buttons = [
        # Resolution row
        [
            InlineKeyboardButton("📺 Resolusi", callback_data="noop"),
            InlineKeyboardButton(f"{current_res}p ▼", callback_data="show_resolution")
        ],
        # Auto Delete Command
        [
            InlineKeyboardButton("🗑 Hapus Command", callback_data="noop"),
            InlineKeyboardButton(on if cmd_delete else off, callback_data="toggle_cmd_delete")
        ],
        # Admin Only Play
        [
            InlineKeyboardButton("👮 Admin Only", callback_data="noop"),
            InlineKeyboardButton(on if admin_play else off, callback_data="toggle_admin_play")
        ],
        # Close button
        [InlineKeyboardButton("🗑 Tutup", callback_data="close")]
    ]
    
    return InlineKeyboardMarkup(buttons)


def resolution_keyboard(current: int) -> InlineKeyboardMarkup:
    """Create resolution selection keyboard"""
    buttons = []
    row = []
    for res in RESOLUTIONS:
        label = f"✅ {res}p" if res == current else f"{res}p"
        row.append(InlineKeyboardButton(label, callback_data=f"setres_{res}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("« Kembali", callback_data="back_settings")])
    return InlineKeyboardMarkup(buttons)


@app.on_message(filters.command(["settings", "pengaturan"]) & filters.group)
@admin_check
async def settings_command(_, message: Message):
    """Show settings menu"""
    chat_id = message.chat.id
    
    text = (
        "⚙️ <b>Pengaturan Bot</b>\n\n"
        "Klik tombol untuk mengubah pengaturan:\n\n"
        "• <b>Resolusi</b> - Kualitas video streaming\n"
        "• <b>Hapus Command</b> - Auto hapus pesan command\n"
        "• <b>Admin Only</b> - Hanya admin yang bisa play\n"
    )
    
    await message.reply_text(
        text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=await get_settings_keyboard(chat_id)
    )


@app.on_callback_query(filters.regex("^noop$"))
async def noop_callback(_, query: CallbackQuery):
    """Do nothing - label buttons"""
    await query.answer()


@app.on_callback_query(filters.regex("^show_resolution$"))
async def show_resolution_callback(_, query: CallbackQuery):
    """Show resolution selection"""
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    
    admins = await db.get_admins(chat_id)
    if user_id not in admins:
        return await query.answer("❌ Hanya admin!", show_alert=True)
    
    current_res = await db.get_resolution(chat_id)
    
    text = (
        "📺 <b>Pilih Resolusi Video</b>\n\n"
        "• <code>360p</code> - Hemat bandwidth\n"
        "• <code>480p</code> - Standard\n"
        "• <code>720p</code> - HD (default)\n"
        "• <code>1080p</code> - Full HD\n"
    )
    
    await query.message.edit_text(
        text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=resolution_keyboard(current_res)
    )
    await query.answer()


@app.on_callback_query(filters.regex(r"^setres_(\d+)$"))
async def set_resolution_callback(_, query: CallbackQuery):
    """Handle resolution change"""
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    
    admins = await db.get_admins(chat_id)
    if user_id not in admins:
        return await query.answer("❌ Hanya admin!", show_alert=True)
    
    resolution = int(query.matches[0].group(1))
    
    if resolution not in RESOLUTIONS:
        return await query.answer("❌ Resolusi tidak valid!", show_alert=True)
    
    await db.set_resolution(chat_id, resolution)
    await query.answer(f"✅ Resolusi: {resolution}p")
    
    # Update keyboard to show selection
    await query.message.edit_reply_markup(
        reply_markup=resolution_keyboard(resolution)
    )


@app.on_callback_query(filters.regex("^back_settings$"))
async def back_settings_callback(_, query: CallbackQuery):
    """Go back to main settings"""
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    
    admins = await db.get_admins(chat_id)
    if user_id not in admins:
        return await query.answer("❌ Hanya admin!", show_alert=True)
    
    text = (
        "⚙️ <b>Pengaturan Bot</b>\n\n"
        "Klik tombol untuk mengubah pengaturan:\n\n"
        "• <b>Resolusi</b> - Kualitas video streaming\n"
        "• <b>Hapus Command</b> - Auto hapus pesan command\n"
        "• <b>Admin Only</b> - Hanya admin yang bisa play\n"
    )
    
    await query.message.edit_text(
        text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=await get_settings_keyboard(chat_id)
    )
    await query.answer()


@app.on_callback_query(filters.regex("^toggle_cmd_delete$"))
async def toggle_cmd_delete_callback(_, query: CallbackQuery):
    """Toggle auto delete command"""
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    
    admins = await db.get_admins(chat_id)
    if user_id not in admins:
        return await query.answer("❌ Hanya admin!", show_alert=True)
    
    # Get current state and toggle
    current = await db.get_cmd_delete(chat_id)
    new_state = not current
    await db.set_cmd_delete(chat_id, new_state)
    
    status = "ON" if new_state else "OFF"
    await query.answer(f"🗑 Hapus Command: {status}")
    
    # Refresh keyboard
    await query.message.edit_reply_markup(
        reply_markup=await get_settings_keyboard(chat_id)
    )


@app.on_callback_query(filters.regex("^toggle_admin_play$"))
async def toggle_admin_play_callback(_, query: CallbackQuery):
    """Toggle admin only play mode"""
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    
    admins = await db.get_admins(chat_id)
    if user_id not in admins:
        return await query.answer("❌ Hanya admin!", show_alert=True)
    
    # Get current state and toggle
    current = await db.get_play_mode(chat_id)
    await db.set_play_mode(chat_id, remove=current)
    
    new_state = not current
    status = "ON" if new_state else "OFF"
    await query.answer(f"👮 Admin Only: {status}")
    
    # Refresh keyboard
    await query.message.edit_reply_markup(
        reply_markup=await get_settings_keyboard(chat_id)
    )
