# Copyright (c) 2025 DramaBot
# Callback handlers untuk inline buttons


from pyrogram import filters, enums
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from drama import app, api, drama_call, db, queue, config
from drama.helpers import buttons


@app.on_callback_query(filters.regex(r"^drama_(\d+)_(\d+)$"))
async def drama_detail_callback(_, query: CallbackQuery):
    """Show drama detail when user clicks drama button"""
    book_id = query.matches[0].group(1)
    owner_id = int(query.matches[0].group(2))
    
    # Check if user is the requester
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer("Loading...")
    
    try:
        # Get drama detail and episodes
        msg = await query.message.edit_text("⏳ Mengambil info drama...")
        
        drama = await api.get_drama_detail(book_id)
        episodes = await api.get_all_episodes(book_id)
        
        if not episodes:
            return await msg.edit_text("❌ Gagal mengambil episode drama ini.")
        
        # Build caption text using HTML
        caption = f"🎬 <b>{drama.title if drama else 'Drama Detail'}</b>\n\n"
        
        if drama and drama.description:
            # Use expandable blockquote for description
            desc = drama.description[:800] + "..." if len(drama.description) > 800 else drama.description
            # Escape HTML characters
            desc = desc.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            caption += f"<blockquote expandable>{desc}</blockquote>\n\n"
        
        caption += f"🆔 <b>Book ID:</b> <code>{book_id}</code>\n"
        caption += f"🏷 <b>Tags:</b> Drama, Romance\n"
        caption += f"📺 <b>Total Episode:</b> {len(episodes)}\n"
        
        if drama and drama.views:
            caption += f"👁 <b>Views:</b> {drama.views}\n"
        
        caption += f"\n💡 Pilih episode untuk streaming:"
        
        # Create episode buttons in grid (4 per row for "Eps X")
        page = 0
        start_idx = page * 10
        end_idx = start_idx + 10
        page_episodes = episodes[start_idx:end_idx]
        
        keyboard = []
        row = []
        for ep in page_episodes:
            row.append(InlineKeyboardButton(f"Eps {ep.episode_num}", callback_data=f"play_{book_id}_{ep.episode_num}_{owner_id}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:  # Add remaining buttons
            keyboard.append(row)
        
        # Play All button
        keyboard.append([
            InlineKeyboardButton("▶️ Play Semua", callback_data=f"playall_{book_id}_{owner_id}")
        ])
        
        # Calculate total pages
        total_pages = (len(episodes) + 9) // 10  # ceiling division
        current_page = 1
        
        # Navigation buttons with page indicator
        nav_row = []
        if total_pages > 1:
            nav_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
            nav_row.append(InlineKeyboardButton("Berikutnya »", callback_data=f"episodes_{book_id}_1_{owner_id}"))
        nav_row.append(InlineKeyboardButton("🗑 Tutup", callback_data="close"))
        keyboard.append(nav_row)
        
        # Delete old message and send new with photo
        await query.message.delete()
        
        if drama and drama.cover_url:
            await query.message.reply_photo(
                photo=drama.cover_url,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.message.reply_text(
                caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
    except Exception as e:
        await query.message.edit_text(f"❌ Error: {str(e)}")


@app.on_callback_query(filters.regex(r"^episodes_(\d+)_(\d+)_(\d+)$"))
async def episodes_page_callback(_, query: CallbackQuery):
    """Handle episode pagination"""
    book_id = query.matches[0].group(1)
    page = int(query.matches[0].group(2))
    owner_id = int(query.matches[0].group(3))
    
    # Check if user is the requester
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer()
    
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
        
        # Build caption using HTML
        caption = f"🎬 <b>{drama.title if drama else 'Drama Detail'}</b>\n\n"
        
        if drama and drama.description:
             # Use expandable blockquote for description
             desc = drama.description[:800] + "..." if len(drama.description) > 800 else drama.description
             # Escape HTML characters
             desc = desc.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             caption += f"<blockquote expandable>{desc}</blockquote>\n\n"
             
        caption += f"🆔 <b>Book ID:</b> <code>{book_id}</code>\n"
        caption += f"🏷 <b>Tags:</b> Drama, Romance\n"
        caption += f"📺 Episode {start_idx + 1}-{min(end_idx, len(episodes))} dari {len(episodes)}\n"
        caption += f"\n💡 Pilih episode untuk streaming:"
        
        # Create episode buttons in grid (4 per row for "Eps X")
        keyboard = []
        row = []
        for ep in page_episodes:
            row.append(InlineKeyboardButton(f"Eps {ep.episode_num}", callback_data=f"play_{book_id}_{ep.episode_num}_{owner_id}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:  # Add remaining buttons
            keyboard.append(row)
        
        # Calculate total pages
        total_pages = (len(episodes) + 9) // 10  # ceiling division
        current_page = page + 1  # page is 0-indexed
        
        # Play All button
        keyboard.append([
            InlineKeyboardButton("▶️ Play Semua", callback_data=f"playall_{book_id}_{owner_id}")
        ])
        
        # Navigation with page indicator
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("« Sebelumnya", callback_data=f"episodes_{book_id}_{page-1}_{owner_id}"))
        nav_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        if end_idx < len(episodes):
            nav_row.append(InlineKeyboardButton("Berikutnya »", callback_data=f"episodes_{book_id}_{page+1}_{owner_id}"))
        keyboard.append(nav_row)
        
        keyboard.append([InlineKeyboardButton("🗑 Tutup", callback_data="close")])
        
        await query.message.edit_caption(
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^playall_(\d+)_(\d+)$"))
async def play_all_episodes_callback(_, query: CallbackQuery):
    """Handle play all episodes button"""
    book_id = query.matches[0].group(1)
    owner_id = int(query.matches[0].group(2))
    
    # Check if user is the requester
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer("Memuat semua episode...")
    
    chat_id = query.message.chat.id
    
    # Check if in group
    if chat_id > 0:
        return await query.message.edit_caption(
            "❌ Command ini hanya bisa digunakan di grup!\n"
            "Tambahkan bot ke grup dan gunakan di voice chat."
        )
    
    try:
        msg = await query.message.reply_text("⏳ Mengambil semua episode...")
        
        # Get all episodes
        episodes = await api.get_all_episodes(book_id)
        drama = await api.get_drama_detail(book_id)
        
        if not episodes:
            return await msg.edit_text("❌ Tidak ada episode ditemukan.")
        
        # Calculate how many can be added
        current_queue = len(queue.get_queue(chat_id))
        available_slots = config.QUEUE_LIMIT - current_queue
        
        if available_slots <= 0:
            return await msg.edit_text(
                f"❌ Queue sudah penuh! (max: {config.QUEUE_LIMIT})\n"
                f"Gunakan `/skip` atau `/stop` untuk clear queue."
            )
        
        # Import Track class
        from drama.helpers import Track
        
        # Add episodes to queue (limit to available slots)
        episodes_to_add = episodes[:available_slots]
        added_count = 0
        
        for episode in episodes_to_add:
            if not episode.video_url and not episode.urls:
                continue
                
            full_title = f"{drama.title} - {episode.title}" if drama else episode.title
            
            track = Track(
                id=f"{book_id}_{episode.episode_num}",
                channel_name="Drama Stream",
                title=full_title,
                duration=f"{episode.duration//60}:{episode.duration%60:02d}" if episode.duration else "Unknown",
                duration_sec=episode.duration or 0,
                url=episode.video_url,
                file_path=episode.video_url,
                thumbnail=drama.cover_url if drama and drama.cover_url else (episode.thumbnail or config.DEFAULT_THUMB),
                user=query.from_user.mention,
                book_id=book_id,
                tags="Drama, Romance",
                video=True,
                message_id=msg.id,
                urls=episode.urls
            )
            queue.add(chat_id, track)
            added_count += 1
        
        if added_count == 0:
            return await msg.edit_text("❌ Tidak ada episode yang bisa ditambahkan.")
        
        # Check if bot is in voice chat
        if not await db.get_call(chat_id):
            # Start playing first track
            first_track = queue.get_current(chat_id)
            if first_track:
                await msg.edit_text(f"✅ {added_count} episode ditambahkan!\nMemulai playback...")
                await drama_call.play_media(chat_id, msg, first_track)
        else:
            await msg.edit_text(
                f"✅ **{added_count} Episode Ditambahkan ke Queue!**\n\n"
                f"📺 {drama.title if drama else 'Drama'}\n"
                f"📍 Total di queue: {len(queue.get_queue(chat_id))}\n\n"
                f"Gunakan `/queue` untuk lihat antrian."
            )
        
    except Exception as e:
        await query.message.reply_text(f"❌ Error: {str(e)}")


@app.on_callback_query(filters.regex(r"^play_(\d+)_(\d+)_(\d+)$"))
async def play_episode_callback(_, query: CallbackQuery):
    """Handle play episode button"""
    book_id = query.matches[0].group(1)
    episode_num = int(query.matches[0].group(2))
    owner_id = int(query.matches[0].group(3))
    
    # Check if user is the requester
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer("Memulai...")
    
    chat_id = query.message.chat.id
    
    # Check if in group
    if chat_id > 0:
        return await query.message.edit_text(
            "❌ Command ini hanya bisa digunakan di grup!\n"
            "Tambahkan bot ke grup dan gunakan di voice chat."
        )
    
    msg = await query.message.reply_text(f"⏳ Mengambil episode {episode_num}...")
            
    try:
        # Get episode and drama details
        episode = await api.get_episode(book_id, episode_num)
        drama = await api.get_drama_detail(book_id)
        
        if not episode or not episode.video_url:
            return await msg.edit_text("❌ Episode tidak ditemukan atau link tidak tersedia.")
        
        # Create full title: "Drama Name - Episode Title"
        full_title = f"{drama.title} - {episode.title}" if drama else episode.title
        
        # Create Track object
        from drama.helpers import Track
        
        track = Track(
            id=f"{book_id}_{episode_num}",
            channel_name="Drama Stream",
            title=full_title,
            duration=f"{episode.duration//60}:{episode.duration%60:02d}" if episode.duration else "Unknown",
            duration_sec=episode.duration or 0,
            url=episode.video_url,
            file_path=episode.video_url,
            thumbnail=drama.cover_url if drama and drama.cover_url else (episode.thumbnail or config.DEFAULT_THUMB),
            user=query.from_user.mention,
            book_id=book_id,
            tags="Drama, Romance", # Default tags
            video=True,
            message_id=msg.id,
            urls=episode.urls # Pass full list of URLs
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


@app.on_callback_query(filters.regex(r"^controls (pause|resume|replay|skip|stop|status|playpause) (-?\d+)"))
async def playback_control_callback(_, query: CallbackQuery):
    """Handle playback control buttons"""
    action = query.matches[0].group(1)
    chat_id = int(query.matches[0].group(2))
    
    if not await db.get_call(chat_id):
        return await query.answer("❌ Tidak ada yang sedang diputar!", show_alert=True)
    
    try:
        if action == "status":
            await query.answer("📺 Sedang diputar...")
        elif action == "playpause":
            # Toggle pause/resume based on current state
            # playing() returns True if playing, False if paused
            is_playing = await db.playing(chat_id)
            if is_playing:
                await drama_call.pause(chat_id)
                await query.answer("⏸ Paused")
            else:
                await drama_call.resume(chat_id)
                await query.answer("▶️ Resumed")
        elif action == "pause":
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
