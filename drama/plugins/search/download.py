# Copyright (c) 2025 DramaBot
# Plugin untuk download drama episode

from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from drama import app, api, config, logger
import os
import time
import asyncio
import aiohttp
from pyrogram.errors import FloodWait
import zipfile
import shutil
from pathlib import Path


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


@app.on_callback_query(filters.regex(r"^download_drama_(\d+)_(\d+)$"))
async def download_drama_button_callback(_, query: CallbackQuery):
    """Handle download button from drama detail"""
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
        caption = f"📥 <b>{drama.title if drama and drama.title else f'Drama {book_id}'}</b>\n\n"
        
        if drama and drama.description:
            desc = drama.description[:300] + "..." if len(drama.description) > 300 else drama.description
            desc_escaped = desc.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            caption += f"<blockquote expandable>{desc_escaped}</blockquote>\n\n"
        
        caption += f"🆔 <b>Book ID:</b> <code>{book_id}</code>\n"
        caption += f"📺 <b>Total Episode:</b> {len(episodes)}\n"
        
        if drama and drama.views:
            caption += f"👁 <b>Views:</b> {drama.views}\n"
        
        caption += "\n💡 Pilih episode untuk download:"
        
        # Build episode buttons (4 per row)
        keyboard = []
        row = []
        for ep in episodes[:10]:
            row.append(InlineKeyboardButton(f"📥 {ep.episode_num}", callback_data=f"dl_{book_id}_{ep.episode_num}_{owner_id}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        # Batch download button (single button below all episodes)
        keyboard.append([InlineKeyboardButton("📦 Batch Download", callback_data=f"batchstart_{book_id}_{owner_id}")])
        
        # Pagination
        total_pages = (len(episodes) + 9) // 10
        if total_pages > 1:
            keyboard.append([InlineKeyboardButton("Berikutnya »", callback_data=f"dl_episodes_{book_id}_1_{owner_id}")])
        
        keyboard.append([InlineKeyboardButton("🗑 Close", callback_data="close")])
        
        await msg.delete()
        
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
        
        # Batch download button
        keyboard.append([InlineKeyboardButton("📦 Batch Download", callback_data=f"batchstart_{book_id}_{owner_id}")])
        
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
        
        # Batch download button
        keyboard.append([InlineKeyboardButton("📦 Batch Download", callback_data=f"batchstart_{book_id}_{owner_id}")])
        
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
        logger.info(f"Download episode clicked: book_id={book_id}, episode_num={episode_num}")
        
        episode = await api.get_episode(book_id, episode_num)
        
        if not episode:
            logger.warning(f"Episode not found: {book_id} ep {episode_num}")
            return await query.answer("❌ Episode tidak ditemukan", show_alert=True)
        
        logger.info(f"Episode found: {episode.title}")
        
        drama = await api.get_drama_detail(book_id)
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
        
        logger.info(f"Available resolutions: {resolutions}")
        logger.info(f"Episode URLs data: {episode.urls}")
        
        caption = (
            f"📥 <b>Download Episode</b>\n\n"
            f"🎬 <b>{title}</b>\n"
            f"📺 Episode: {episode_num}\n\n"
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
        
        logger.info("Quality selection message sent")
        
    except Exception as e:
        logger.error(f"Error in download_episode_callback: {e}", exc_info=True)
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^dlres_(\d+)_(\d+)_(\d+)_(\d+)$"))
async def download_with_resolution_callback(_, query: CallbackQuery):
    """Download episode with selected resolution and progress tracking"""
    import aiohttp
    import os
    import asyncio
    import time
    from pyrogram.errors import FloodWait
    
    book_id = query.matches[0].group(1)
    episode_num = int(query.matches[0].group(2))
    resolution = int(query.matches[0].group(3))
    owner_id = int(query.matches[0].group(4))
    
    # Check if user is the requester
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer(f"📥 Memulai download {resolution}p...")
    
    try:
        episode = await api.get_episode(book_id, episode_num)
        drama = await api.get_drama_detail(book_id)
        
        if not episode or not episode.video_url:
            return await query.answer("❌ Episode tidak ditemukan", show_alert=True)
        
        # Find video URL with selected resolution
        video_url = episode.video_url
        if episode.urls:
            for u in episode.urls:
                if int(u.get("quality", 0)) == resolution:
                    video_url = u.get("url", episode.video_url)
                    break
        
        drama_title = drama.title if drama and drama.title else f"Drama {book_id}"
        episode_title = episode.title or f"Episode {episode_num}"
        
        caption = (
            f"🎬 <b>{drama_title}</b>\n"
            f"📺 {episode_title}\n"
            f"💿 {resolution}p\n\n"
            f"🤖 @DracinStreamingBot"
        )
        
        msg = await query.message.reply_text(
            f"⬆️ <b>Mengirim Video</b>\n\n"
            f"<blockquote>"
            f"🎬 {drama_title}\n"
            f"📺 {episode_title}\n"
            f"💿 {resolution}p\n\n"
            f"⏳ Sedang mengirim video..."
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        
        try:
            # Send video URL directly (Telegram will handle the download)
            await query.message.reply_video(
                video=video_url,
                caption=caption,
                supports_streaming=True,
                parse_mode=enums.ParseMode.HTML
            )
            
            await msg.delete()
            # Delete quality selection message
            try:
                await query.message.delete()
            except:
                pass
            
        except Exception as e:
            await msg.edit_text(f"❌ <b>Gagal mengirim video.</b>\n\nError: {str(e)}", parse_mode=enums.ParseMode.HTML)
                    
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


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


# ==================== BATCH DOWNLOAD HANDLERS ====================

@app.on_callback_query(filters.regex(r"^batchstart_(\d+)_(\d+)$"))
async def batch_start_handler(_, query: CallbackQuery):
    """Show batch download episode range selection"""
    book_id = query.matches[0].group(1)
    owner_id = int(query.matches[0].group(2))
    
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer("📦 Batch Download")
    
    try:
        episodes = await api.get_all_episodes(book_id)
        total_eps = len(episodes)
        drama = await api.get_drama_detail(book_id)
        
        caption = (
            f"📦 <b>Batch Download</b>\n\n"
            f"🎬 <b>{drama.title if drama else 'Drama'}</b>\n"
            f"📊 Total Episodes: {total_eps}\n\n"
            f"💡 Pilih range download:"
        )
        
        keyboard = []
        row = []
        
        # Quick range buttons
        ranges = [
            (5, "5 Episode Pertama"),
            (10, "10 Episode Pertama"),
            (total_eps, f"Semua ({total_eps} eps)")
        ]
        
        for count, label in ranges:
            if count <= total_eps:
                end_ep = min(count, total_eps)
                keyboard.append([InlineKeyboardButton(
                    label,
                    callback_data=f"batchqual_{book_id}_1_{end_ep}_{owner_id}"
                )])
        
        keyboard.append([InlineKeyboardButton("« Kembali", callback_data=f"download_drama_{book_id}_{owner_id}")])
        
        await query.message.edit_text(
            caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^batch_(\d+)_(\d+)_(\d+)$"))
async def batch_range_selector(_, query: CallbackQuery):
    """Show batch range selection"""
    book_id = query.matches[0].group(1)
    start_ep = int(query.matches[0].group(2))
    owner_id = int(query.matches[0].group(3))
    
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer("📦 Batch Download")
    
    try:
        episodes = await api.get_all_episodes(book_id)
        total_eps = len(episodes)
        
        if start_ep >= total_eps:
            return await query.answer("❌ Episode tidak valid", show_alert=True)
        
        caption = (
            f"📦 <b>Batch Download</b>\n\n"
            f"📺 <b>Start from EP {start_ep}</b>\n"
            f"📊 Total Available: {total_eps} episodes\n\n"
            f"💡 Pilih range download:"
        )
        
        keyboard = []
        row = []
        
        # Quick range buttons
        ranges = [1, 5, 10]
        for r in ranges:
            end_ep = min(start_ep + r - 1, total_eps)
            if end_ep >= start_ep:
                btn_text = f"+{r} Eps" if r > 1 else f"EP {start_ep} saja"
                row.append(InlineKeyboardButton(
                    btn_text,
                    callback_data=f"batchqual_{book_id}_{start_ep}_{end_ep}_{owner_id}"
                ))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
        
        if row:
            keyboard.append(row)
        
        # All remaining episodes
        if total_eps > start_ep:
            keyboard.append([InlineKeyboardButton(
                f"📥 All ({total_eps - start_ep + 1} eps)",
                callback_data=f"batchqual_{book_id}_{start_ep}_{total_eps}_{owner_id}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Kembali", callback_data=f"download_drama_{book_id}_{owner_id}")])
        
        await query.message.edit_text(
            caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^batchqual_(\d+)_(\d+)_(\d+)_(\d+)$"))
async def batch_quality_selector(_, query: CallbackQuery):
    """Show quality selection for batch download"""
    book_id = query.matches[0].group(1)
    start_ep = int(query.matches[0].group(2))
    end_ep = int(query.matches[0].group(3))
    owner_id = int(query.matches[0].group(4))
    
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer("Loading...")
    
    try:
        # Get first episode to check available resolutions
        episode = await api.get_episode(book_id, start_ep)
        
        if not episode or not episode.urls:
            return await query.answer("❌ Episode tidak ditemukan", show_alert=True)
        
        # Get available resolutions
        resolutions = sorted(list(set(int(u.get("quality", 0)) for u in episode.urls if u.get("quality"))), reverse=True)
        
        if not resolutions:
            resolutions = [720]
        
        total_eps = end_ep - start_ep + 1
        
        caption = (
            f"📦 <b>Batch Download</b>\n\n"
            f"📺 <b>Episodes:</b> {start_ep} - {end_ep} ({total_eps} eps)\n\n"
            f"💡 Pilih kualitas video:"
        )
        
        keyboard = []
        row = []
        for res in resolutions:
            row.append(InlineKeyboardButton(
                f"{res}p",
                callback_data=f"batchdl_{book_id}_{start_ep}_{end_ep}_{res}_{owner_id}"
            ))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("« Kembali", callback_data=f"batch_{book_id}_{start_ep}_{owner_id}")])
        
        await query.message.edit_text(
            caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^batchdl_(\d+)_(\d+)_(\d+)_(\d+)_(\d+)$"))
async def batch_download_handler(_, query: CallbackQuery):
    """Handle batch download and compression"""
    book_id = query.matches[0].group(1)
    start_ep = int(query.matches[0].group(2))
    end_ep = int(query.matches[0].group(3))
    resolution = int(query.matches[0].group(4))
    owner_id = int(query.matches[0].group(5))
    
    if query.from_user.id != owner_id:
        return await query.answer("❌ Ini bukan permintaan kamu!", show_alert=True)
    
    await query.answer(f"📦 Memulai batch download {resolution}p...")
    
    try:
        drama = await api.get_drama_detail(book_id)
        drama_title = drama.title if drama and drama.title else f"Drama_{book_id}"
        
        # Clean title for filename
        safe_title = "".join(x for x in drama_title if x.isalnum() or x in [' ', '-', '_']).strip()
        
        # Create temp directory
        timestamp = int(time.time())
        batch_dir = Path(f"downloads/batch_{book_id}_{timestamp}")
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        total_eps = end_ep - start_ep + 1
        zip_path = None  # Initialize to prevent UnboundLocalError in cleanup
        
        msg = await query.message.reply_text(
            f"📦 <b>Batch Download</b>\n\n"
            f"<blockquote>"
            f"🎬 {drama_title}\n"
            f"📺 Episodes {start_ep}-{end_ep}\n"
            f"💿 {resolution}p\n\n"
            f"⏬ Initializing..."
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        
        try:
            downloaded_files = []
            failed_episodes = []
            
            # Download each episode
            for idx, ep_num in enumerate(range(start_ep, end_ep + 1), 1):
                try:
                    episode = await api.get_episode(book_id, ep_num)
                    
                    if not episode:
                        failed_episodes.append(ep_num)
                        continue
                    
                    # Find video URL with selected resolution
                    video_url = episode.video_url
                    if episode.urls:
                        for u in episode.urls:
                            if int(u.get("quality", 0)) == resolution:
                                video_url = u.get("url", episode.video_url)
                                break
                    
                    # Update progress (rate limited to avoid FLOOD_WAIT)
                    if idx % 3 == 0 or idx == total_eps:  # Update every 3 episodes
                        try:
                            await msg.edit_text(
                                f"📦 <b>Batch Download</b>\n\n"
                                f"<blockquote>"
                                f"🎬 {drama_title}\n"
                                f"📺 Episodes {start_ep}-{end_ep}\n"
                                f"💿 {resolution}p\n\n"
                                f"⏬ Downloading: EP {ep_num} ({idx}/{total_eps})"
                                f"</blockquote>",
                                parse_mode=enums.ParseMode.HTML
                            )
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                        except:
                            pass
                    
                    # Download file
                    filename = f"EP_{ep_num:03d}_{resolution}p.mp4"
                    filepath = batch_dir / filename
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(video_url) as response:
                            if response.status != 200:
                                failed_episodes.append(ep_num)
                                continue
                            
                            with open(filepath, 'wb') as f:
                                async for chunk in response.content.iter_chunked(1024 * 1024):
                                    f.write(chunk)
                    
                    downloaded_files.append(filepath)
                    
                except Exception as e:
                    logger.error(f"Failed to download EP {ep_num}: {e}")
                    failed_episodes.append(ep_num)
                    continue
            
            if not downloaded_files:
                await msg.edit_text("❌ <b>Gagal mendownload semua episode</b>", parse_mode=enums.ParseMode.HTML)
                shutil.rmtree(batch_dir)
                return
            
            # Split files into parts (25 episodes per part)
            EPISODES_PER_PART = 25
            parts = []
            
            for i in range(0, len(downloaded_files), EPISODES_PER_PART):
                part_files = downloaded_files[i:i + EPISODES_PER_PART]
                part_num = (i // EPISODES_PER_PART) + 1
                total_parts = (len(downloaded_files) + EPISODES_PER_PART - 1) // EPISODES_PER_PART
                
                # Determine episode range for this part
                first_ep = start_ep + i
                last_ep = min(start_ep + i + len(part_files) - 1, end_ep)
                
                parts.append({
                    'files': part_files,
                    'part_num': part_num,
                    'total_parts': total_parts,
                    'first_ep': first_ep,
                    'last_ep': last_ep
                })
            
            # Create ZIP files
            await msg.edit_text(
                f"📦 <b>Batch Download</b>\n\n"
                f"<blockquote>"
                f"🎬 {drama_title}\n"
                f"📺 Episodes {start_ep}-{end_ep}\n"
                f"💿 {resolution}p\n\n"
                f"📁 Creating {len(parts)} ZIP part(s)..."
                f"</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            
            zip_paths = []
            for part in parts:
                if len(parts) > 1:
                    zip_filename = f"{drama_title} Eps {part['first_ep']}-{part['last_ep']} {resolution}p Part{part['part_num']}.zip"
                else:
                    zip_filename = f"{drama_title} Eps {start_ep}-{end_ep} {resolution}p.zip"
                
                zip_path = batch_dir.parent / zip_filename
                
                # Use ZIP_STORED (no compression) for speed
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as zipf:
                    for file in part['files']:
                        zipf.write(file, file.name)
                
                zip_paths.append({
                    'path': zip_path,
                    'part_num': part['part_num'],
                    'total_parts': part['total_parts'],
                    'first_ep': part['first_ep'],
                    'last_ep': part['last_ep']
                })
            
            # Upload all parts in parallel
            # Upload all parts in parallel
            async def upload_part(zip_info, progress=None):
                """Upload a single ZIP part"""
                part_caption = (
                    f"📦 <b>{drama_title}</b>\n"
                    f"📺 Episodes {zip_info['first_ep']}-{zip_info['last_ep']}\n"
                    f"💿 {resolution}p\n"
                )
                
                if zip_info['total_parts'] > 1:
                    part_caption += f"📦 Part {zip_info['part_num']} of {zip_info['total_parts']}\n\n"
                else:
                    part_caption += f"📁 {len(downloaded_files)} file(s)\n\n"
                
                if failed_episodes:
                    part_caption += f"⚠️ Failed: EP {', '.join(map(str, failed_episodes))}\n\n"
                
                part_caption += f"🤖 @DracinStreamingBot"
                
                await query.message.reply_document(
                    document=str(zip_info['path']),
                    caption=part_caption,
                    parse_mode=enums.ParseMode.HTML,
                    progress=progress
                )
            
            # Upload all parts in parallel
            await msg.edit_text(
                f"⬆️ <b>Uploading {len(zip_paths)} part(s)...</b>\n\n"
                f"<blockquote>"
                f"🎬 {drama_title}\n"
                f"📺 Episodes {start_ep}-{end_ep}\n"
                f"💿 {resolution}p\n\n"
                f"� Uploading to Telegram..."
                f"</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            
            # Unified progress tracking
            # Format: {part_num: {'status': 'pending/uploading/done', 'progress': 0}}
            upload_status = {
                part['part_num']: {'status': '⏳ Pending', 'progress': 0} 
                for part in zip_paths
            }
            
            last_edit_time = [0]
            
            async def update_global_progress():
                """Update the single message with all parts status"""
                now = time.time()
                # Rate limit edits (max 1 edit per 3 seconds)
                if now - last_edit_time[0] < 3:
                    return
                
                last_edit_time[0] = now
                
                status_text = f"📦 <b>Uploading {len(zip_paths)} Parts</b>\n\n"
                status_text += f"🎬 <b>{drama_title}</b>\n"
                status_text += f"💿 {resolution}p\n\n"
                
                all_done = True
                for part_num in sorted(upload_status.keys()):
                    info = upload_status[part_num]
                    # Visual progress bar for uploading parts
                    if info['status'] == '⬆️':
                         prog = info['progress']
                         bar_len = 10
                         filled = int((prog / 100) * bar_len)
                         bar = '▰' * filled + '▱' * (bar_len - filled)
                         status_line = f"Start Part {part_num}: {info['status']} <code>[{bar}] {int(prog)}%</code>"
                         all_done = False
                    elif info['status'] == '✅':
                         status_line = f"Start Part {part_num}: ✅ <b>Done</b>"
                    else:
                         status_line = f"Start Part {part_num}: {info['status']}"
                         all_done = False
                    
                    status_text += f"{status_line}\n"
                
                try:
                    if not all_done:
                        await msg.edit_text(status_text, parse_mode=enums.ParseMode.HTML)
                except:
                    pass

            # Limit parallel uploads
            sem = asyncio.Semaphore(2)

            async def upload_part_safe(zip_info):
                part_num = zip_info['part_num']
                
                async def part_progress(current, total):
                    percent = (current / total) * 100
                    upload_status[part_num]['status'] = '⬆️'
                    upload_status[part_num]['progress'] = percent
                    await update_global_progress()
                
                async with sem:
                    # Update status to uploading (0%)
                    upload_status[part_num]['status'] = '⬆️'
                    await update_global_progress()
                    
                    await upload_part(zip_info, progress=part_progress)
                    
                    # Update status to done
                    upload_status[part_num]['status'] = '✅'
                    upload_status[part_num]['progress'] = 100
                    await update_global_progress()

            # Upload in limited parallel
            upload_tasks = [upload_part_safe(zip_info) for zip_info in zip_paths]
            await asyncio.gather(*upload_tasks)
            
            # Cleanup zip files
            for zip_info in zip_paths:
                if zip_info['path'].exists():
                    os.remove(zip_info['path'])
            
            await msg.delete()
            try:
                await query.message.delete()
            except:
                pass
            
        except Exception as e:
            await msg.edit_text(f"❌ <b>Gagal batch download.</b>\n\nError: {str(e)}", parse_mode=enums.ParseMode.HTML)
        finally:
            # Cleanup
            try:
                if batch_dir.exists():
                    shutil.rmtree(batch_dir)
                if zip_path and zip_path.exists():
                    os.remove(zip_path)
            except:
                pass
    
    except Exception as e:
        # Don't use query.answer here - query may have expired
        logger.error(f"Batch download error: {e}")
        try:
            await query.message.reply_text(f"❌ <b>Error batch download:</b>\n\n{str(e)}", parse_mode=enums.ParseMode.HTML)
        except:
            pass
