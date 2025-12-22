# Copyright (c) 2025 DramaBot
# Callback handlers untuk inline buttons


from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from drama import app, api, drama_call, db, queue, config
from drama.helpers import buttons


@app.on_callback_query(filters.regex(r"^drama_(\d+)$"))
async def drama_detail_callback(_, query: CallbackQuery):
    """Show drama detail when user clicks drama button"""
    await query.answer("Loading...")
    book_id = query.matches[0].group(1)
    
    try:
        # Get drama detail and episodes
        msg = await query.message.edit_text("⏳ Mengambil info drama...")
        
        drama = await api.get_drama_detail(book_id)
        episodes = await api.get_all_episodes(book_id)
        
        if not episodes:
            return await msg.edit_text("❌ Gagal mengambil episode drama ini.")
        
        # Build caption text
        caption = f"🎬 **{drama.title if drama else 'Drama Detail'}**\n\n"
        
        if drama and drama.description:
            # Truncate description and add blockquote to each line
            desc = drama.description[:200] + "..." if len(drama.description) > 200 else drama.description
            caption += "\n".join([f"> {line}" for line in desc.split("\n")]) + "\n\n"
        
        caption += f"> 🆔 **Book ID:** `{book_id}`\n"
        caption += f"> 🏷 **Tags:** Drama, Romance\n"
        caption += f"> 📺 **Total Episode:** {len(episodes)}\n"
        
        if drama and drama.views:
            caption += f"> 👁 **Views:** {drama.views}\n"
        
        caption += f"\n💡 Pilih episode untuk streaming:"
        
        # Create episode buttons in grid (4 per row for "Eps X")
        page = 0
        start_idx = page * 10
        end_idx = start_idx + 10
        page_episodes = episodes[start_idx:end_idx]
        
        keyboard = []
        row = []
        for ep in page_episodes:
            row.append(InlineKeyboardButton(f"Eps {ep.episode_num}", callback_data=f"play_{book_id}_{ep.episode_num}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:  # Add remaining buttons
            keyboard.append(row)
        
        # Navigation buttons
        nav_row = []
        if len(episodes) > 10:
            nav_row.append(InlineKeyboardButton("Berikutnya »", callback_data=f"episodes_{book_id}_1"))
        nav_row.append(InlineKeyboardButton("« Kembali", callback_data="back_to_browse"))
        keyboard.append(nav_row)
        
        # Delete old message and send new with photo
        await query.message.delete()
        
        if drama and drama.cover_url:
            await query.message.reply_photo(
                photo=drama.cover_url,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.message.reply_text(
                caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
    except Exception as e:
        await query.message.edit_text(f"❌ Error: {str(e)}")


@app.on_callback_query(filters.regex(r"^episodes_(\d+)_(\d+)$"))
async def episodes_page_callback(_, query: CallbackQuery):
    """Handle episode pagination"""
    await query.answer()
    book_id = query.matches[0].group(1)
    page = int(query.matches[0].group(2))
    
    try:
        drama = await api.get_drama_detail(book_id)
        episodes = await api.get_all_episodes(book_id)
        
        if not episodes:
            return await query.answer("❌ Episode tidak ditemukan", show_alert=True)
        
        # Calculate pagination
        start_idx = page * 10
        end_idx = start_idx + 10
        page_episodes = episodes[start_idx:end_idx]
        
        if not page_episodes:
            return await query.answer("❌ Halaman tidak ada", show_alert=True)
        
        # Build caption
        caption = f"🎬 **{drama.title if drama else 'Drama Detail'}**\n\n"
        
        if drama and drama.description:
             desc = drama.description[:200] + "..." if len(drama.description) > 200 else drama.description
             caption += "\n".join([f"> {line}" for line in desc.split("\n")]) + "\n\n"
             
        caption += f"> 🆔 **Book ID:** `{book_id}`\n"
        caption += f"> 🏷 **Tags:** Drama, Romance\n"
        caption += f"> 📺 Episode {start_idx + 1}-{min(end_idx, len(episodes))} dari {len(episodes)}\n"
        caption += f"\n💡 Pilih episode untuk streaming:"
        
        # Create episode buttons in grid (4 per row for "Eps X")
        keyboard = []
        row = []
        for ep in page_episodes:
            row.append(InlineKeyboardButton(f"Eps {ep.episode_num}", callback_data=f"play_{book_id}_{ep.episode_num}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:  # Add remaining buttons
            keyboard.append(row)
        
        # Navigation
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("« Sebelumnya", callback_data=f"episodes_{book_id}_{page-1}"))
        if end_idx < len(episodes):
            nav_row.append(InlineKeyboardButton("Berikutnya »", callback_data=f"episodes_{book_id}_{page+1}"))
        if nav_row:
            keyboard.append(nav_row)
        
        keyboard.append([InlineKeyboardButton("« Kembali", callback_data=f"drama_{book_id}")])
        
        await query.message.edit_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^play_(\d+)_(\d+)$"))
async def play_episode_callback(_, query: CallbackQuery):
    """Handle play episode button"""
    await query.answer("Memulai...")
    
    book_id = query.matches[0].group(1)
    episode_num = int(query.matches[0].group(2))
    chat_id = query.message.chat.id
    
    # Check if in group
    if chat_id > 0:
        return await query.message.edit_text(
            "❌ Command ini hanya bisa digunakan di grup!\n"
            "Tambahkan bot ke grup dan gunakan di voice chat."
        )
    
    msg = await query.message.edit_text(f"⏳ Mengambil episode {episode_num}...")
            
    try:
        # Get episode
        episode = await api.get_episode(book_id, episode_num)
        
        if not episode or not episode.video_url:
            return await msg.edit_text("❌ Episode tidak ditemukan atau link tidak tersedia.")
        
        # Create Track object
        from drama.helpers import Track
        
        track = Track(
            id=f"{book_id}_{episode_num}",
            channel_name="Drama Stream",
            title=episode.title,
            duration=f"{episode.duration//60}:{episode.duration%60:02d}" if episode.duration else "Unknown",
            duration_sec=episode.duration or 0,
            url=episode.video_url,
            file_path=episode.video_url,
            thumbnail=episode.thumbnail or config.DEFAULT_THUMB,
            user=query.from_user.mention,
            book_id=book_id,
            tags="Drama, Romance", # Default tags
            video=True,
            message_id=msg.id
        )
        
        # Check queue limit
        if len(queue.get_queue(chat_id)) >= config.QUEUE_LIMIT:
            return await msg.edit_text(
                f"❌ Queue sudah penuh! (max: {config.QUEUE_LIMIT})\n"
                f"Gunakan `/skip` atau `/stop` untuk clear queue."
            )
            
        # Add to queue
        queue.add(chat_id, track)
        
        # Check if bot is in voice chat
        if not await db.get_call(chat_id):
            # Start playing
            await msg.edit_text("✅ Memulai playback...")
            await drama_call.play_media(chat_id, msg, track)
        else:
            # Already playing, notify added to queue
            await msg.edit_text(
                f"✅ **Ditambahkan ke Queue!**\n\n"
                f"📺 {track.title}\n"
                f"📍 Posisi: #{len(queue.get_queue(chat_id))}\n\n"
                f"Gunakan `/queue` untuk lihat antrian."
            )
            
            # Send controls in new message to avoid editing navigation
            # Actually, user might want to continue browsing?
            # For now standard behavior is fine.
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")


@app.on_callback_query(filters.regex(r"^controls (pause|resume|replay|skip|stop) (\d+)"))
async def playback_control_callback(_, query: CallbackQuery):
    """Handle playback control buttons"""
    action = query.matches[0].group(1)
    chat_id = int(query.matches[0].group(2))
    
    if not await db.get_call(chat_id):
        return await query.answer("❌ Tidak ada yang sedang diputar!", show_alert=True)
    
    try:
        if action == "pause":
            await drama_call.pause(chat_id)
            await query.answer("⏸ Paused")
        elif action == "resume":
            await drama_call.resume(chat_id)
            await query.answer("▶️ Resumed")
        elif action == "replay":
            await drama_call.replay(chat_id)
            await query.answer("🔄 Replaying")
        elif action == "skip":
            await drama_call.play_next(chat_id)
            await query.answer("⏭ Skipped")
        elif action == "stop":
            await drama_call.stop(chat_id)
            await query.answer("⏹ Stopped")
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex("^close$"))
async def close_callback(_, query: CallbackQuery):
    """Close/delete message"""
    await query.message.delete()
    await query.answer()


@app.on_callback_query(filters.regex("^back_to_browse$"))
async def back_to_browse_callback(_, query: CallbackQuery):
    """Go back to browse menu"""
    await query.answer()
    text = (
        "🎬 **DramaBot**\n\n"
        "Pilih kategori untuk browse drama:"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 Trending", callback_data="browse_trending"),
            InlineKeyboardButton("🆕 Terbaru", callback_data="browse_latest"),
        ]
    ])
    await query.message.edit_text(text, reply_markup=keyboard)
