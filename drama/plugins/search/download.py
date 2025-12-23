# Copyright (c) 2025 DramaBot
# Plugin untuk download drama episode

from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from drama import app, api, config


@app.on_message(filters.command("download"))
async def download_command(_, message: Message):
    """Handler untuk /download command - search drama untuk download"""
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Cara penggunaan:**\n"
            "`/download <judul drama>`\n\n"
            "**Contoh:**\n"
            "`/download cinta`"
        )
    
    query = " ".join(message.command[1:])
    msg = await message.reply_text(f"🔍 Mencari drama: **{query}**...")
    
    try:
        dramas = await api.search(query, limit=10)
        
        if not dramas:
            return await msg.edit_text(
                f"❌ Tidak ditemukan drama dengan kata kunci: **{query}**\n"
                f"Coba judul lain."
            )
        
        text = f"📥 **Download Drama**\n"
        text += f"🔍 Hasil pencarian: `{query}`\n\n"
        keyboard = []
        
        for i, drama in enumerate(dramas, 1):
            text += f"**{i}. {drama.title}**\n"
        
        text += "\n💡 Klik tombol untuk pilih drama!"
        
        user_id = message.from_user.id
        row = []
        for i, drama in enumerate(dramas, 1):
            row.append(InlineKeyboardButton(str(i), callback_data=f"dldrama_{drama.book_id}_{user_id}"))
            if i % 5 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("🗑 Tutup", callback_data="close")])
                
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")


@app.on_callback_query(filters.regex(r"^dldrama_(\d+)_(\d+)$"))
async def download_drama_callback(_, query: CallbackQuery):
    """Show drama episodes for download"""
    book_id = query.matches[0].group(1)
    owner_id = int(query.matches[0].group(2))
    
    # Check if user is the requester
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer("Loading...")
    
    try:
        msg = await query.message.edit_text("⏳ Mengambil info drama...")
        
        drama = await api.get_drama_detail(book_id)
        episodes = await api.get_all_episodes(book_id)
        
        if not episodes:
            return await msg.edit_text("❌ Gagal mengambil episode.")
        
        # Build caption
        caption = f"📥 <b>{drama.title if drama else 'Drama Detail'}</b>\n\n"
        
        if drama and drama.description:
            desc = drama.description[:800] + "..." if len(drama.description) > 800 else drama.description
            desc = desc.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            caption += f"<blockquote expandable>{desc}</blockquote>\n\n"
        
        caption += f"🆔 <b>Book ID:</b> <code>{book_id}</code>\n"
        caption += f"🏷 <b>Tags:</b> Drama, Romance\n"
        caption += f"📺 <b>Total Episode:</b> {len(episodes)}\n"
        
        if drama and drama.views:
            caption += f"👁 <b>Views:</b> {drama.views}\n"

        caption += f"\n💡 Pilih episode untuk download:"
        
        # Episode buttons (first page)
        page = 0
        start_idx = page * 10
        end_idx = start_idx + 10
        page_episodes = episodes[start_idx:end_idx]
        
        keyboard = []
        row = []
        for ep in page_episodes:
            row.append(InlineKeyboardButton(f"📥 {ep.episode_num}", callback_data=f"dl_{book_id}_{ep.episode_num}_{owner_id}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        # Pagination
        total_pages = (len(episodes) + 9) // 10
        current_page = 1
        
        nav_row = []
        if total_pages > 1:
            nav_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
            nav_row.append(InlineKeyboardButton("Berikutnya »", callback_data=f"dlpage_{book_id}_1_{owner_id}"))
        nav_row.append(InlineKeyboardButton("🗑 Tutup", callback_data="close"))
        keyboard.append(nav_row)
        
        # Delete old and send with photo
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


@app.on_callback_query(filters.regex(r"^dlpage_(\d+)_(\d+)_(\d+)$"))
async def download_page_callback(_, query: CallbackQuery):
    """Handle download pagination"""
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
        
        start_idx = page * 10
        end_idx = start_idx + 10
        page_episodes = episodes[start_idx:end_idx]
        
        if not page_episodes:
            return await query.answer("❌ Halaman tidak ada", show_alert=True)
        
        caption = f"📥 <b>Download: {drama.title if drama else 'Drama'}</b>\n\n"
        caption += f"📺 Episode {start_idx + 1}-{min(end_idx, len(episodes))} dari {len(episodes)}\n"
        caption += f"\n💡 Pilih episode untuk download:"
        
        keyboard = []
        row = []
        for ep in page_episodes:
            row.append(InlineKeyboardButton(f"📥 {ep.episode_num}", callback_data=f"dl_{book_id}_{ep.episode_num}_{owner_id}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        # Pagination
        total_pages = (len(episodes) + 9) // 10
        current_page = page + 1
        
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("« Sebelumnya", callback_data=f"dlpage_{book_id}_{page-1}_{owner_id}"))
        nav_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        if end_idx < len(episodes):
            nav_row.append(InlineKeyboardButton("Berikutnya »", callback_data=f"dlpage_{book_id}_{page+1}_{owner_id}"))
        keyboard.append(nav_row)
        
        keyboard.append([InlineKeyboardButton("🗑 Tutup", callback_data="close")])
        
        await query.message.edit_caption(
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^dl_(\d+)_(\d+)_(\d+)$"))
async def download_episode_callback(_, query: CallbackQuery):
    """Show resolution selection for download"""
    book_id = query.matches[0].group(1)
    episode_num = int(query.matches[0].group(2))
    owner_id = int(query.matches[0].group(3))
    
    # Check if user is the requester
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer("Loading...")
    
    try:
        episode = await api.get_episode(book_id, episode_num)
        drama = await api.get_drama_detail(book_id)
        
        if not episode:
            return await query.answer("❌ Episode tidak ditemukan", show_alert=True)
        
        title = f"{drama.title} - {episode.title}" if drama else episode.title
        
        # Get available resolutions
        resolutions = []
        if episode.urls:
            for u in episode.urls:
                quality = int(u.get("quality", 0))
                if quality > 0 and quality not in resolutions:
                    resolutions.append(quality)
            resolutions.sort(reverse=True)
        
        if not resolutions:
            # No resolution info, just download default
            resolutions = [720]
        
        caption = (
            f"📥 <b>Download Episode</b>\n\n"
            f"🎬 <b>{title}</b>\n"
            f"📺 Episode: {episode_num}\n"
            f"⏱ Durasi: {episode.duration // 60}:{episode.duration % 60:02d}\n\n"
            f"💡 Pilih kualitas video:"
        )
        
        # Resolution buttons
        keyboard = []
        row = []
        for res in resolutions:
            row.append(InlineKeyboardButton(f"📥 {res}p", callback_data=f"dlres_{book_id}_{episode_num}_{res}_{owner_id}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🗑 Batal", callback_data="close")])
        
        await query.message.reply_text(
            caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^dlres_(\d+)_(\d+)_(\d+)_(\d+)$"))
async def download_with_resolution_callback(_, query: CallbackQuery):
    """Download episode with selected resolution"""
    book_id = query.matches[0].group(1)
    episode_num = int(query.matches[0].group(2))
    resolution = int(query.matches[0].group(3))
    owner_id = int(query.matches[0].group(4))
    
    # Check if user is the requester
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer(f"📥 Mendownload {resolution}p...")
    
    msg = await query.message.reply_text(f"⏳ Mengambil episode {episode_num} ({resolution}p)...")
    
    try:
        episode = await api.get_episode(book_id, episode_num)
        drama = await api.get_drama_detail(book_id)
        
        if not episode or not episode.video_url:
            return await msg.edit_text("❌ Episode tidak ditemukan.")
        
        await msg.edit_text(f"📥 Mendownload: **{episode.title}** ({resolution}p)...")
        
        # Find video URL with selected resolution
        video_url = episode.video_url
        if episode.urls:
            for u in episode.urls:
                if int(u.get("quality", 0)) == resolution:
                    video_url = u.get("url", episode.video_url)
                    break
        
        title = f"{drama.title} - {episode.title}" if drama else episode.title
        
        await msg.edit_text(f"📤 Mengirim video: **{title}** ({resolution}p)...")
        
        caption = (
            f"🎬 <b>{title}</b>\n\n"
            f"📺 Episode: {episode_num}\n"
            f"📊 Kualitas: {resolution}p\n"
            f"⏱ Durasi: {episode.duration // 60}:{episode.duration % 60:02d}\n\n"
            f"🤖 @DramaBot"
        )
        
        await query.message.reply_video(
            video=video_url,
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            thumb=drama.cover_url if drama and drama.cover_url else None,
            supports_streaming=True
        )
        
        await msg.delete()
        # Delete resolution selection message
        try:
            await query.message.delete()
        except:
            pass
        
    except Exception as e:
        await msg.edit_text(f"❌ Error download: {str(e)}")


# Keep dlmenu for the button in drama detail page
@app.on_callback_query(filters.regex(r"^dlmenu_(\d+)_(\d+)$"))
async def download_menu_callback(_, query: CallbackQuery):
    """Show download episode selection menu from drama detail"""
    book_id = query.matches[0].group(1)
    owner_id = int(query.matches[0].group(2))
    
    # Check if user is the requester
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer("Loading...")
    
    try:
        drama = await api.get_drama_detail(book_id)
        episodes = await api.get_all_episodes(book_id)
        
        if not episodes:
            return await query.answer("❌ Episode tidak ditemukan", show_alert=True)
        
        page = 0
        start_idx = page * 10
        end_idx = start_idx + 10
        page_episodes = episodes[start_idx:end_idx]
        
        caption = f"📥 <b>Download: {drama.title if drama else 'Drama'}</b>\n\n"
        caption += f"📺 Total Episode: {len(episodes)}\n"
        caption += f"\n💡 Pilih episode untuk download:"
        
        keyboard = []
        row = []
        for ep in page_episodes:
            row.append(InlineKeyboardButton(f"📥 {ep.episode_num}", callback_data=f"dl_{book_id}_{ep.episode_num}_{owner_id}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        total_pages = (len(episodes) + 9) // 10
        
        nav_row = []
        if total_pages > 1:
            nav_row.append(InlineKeyboardButton("1/" + str(total_pages), callback_data="noop"))
            nav_row.append(InlineKeyboardButton("Berikutnya »", callback_data=f"dlpage_{book_id}_1_{owner_id}"))
        keyboard.append(nav_row)
        
        keyboard.append([InlineKeyboardButton("🗑 Tutup", callback_data="close")])
        
        await query.message.reply_text(
            caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)
