# Copyright (c) 2025 DramaBot
# Main play command for drama streaming


from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from drama import app, api, queue, config, drama_call, db
from drama.helpers import Track


@app.on_message(filters.command(["play", "vplay"]) & filters.group & ~app.bl_users)
async def play_command(_, message: Message):
    """Play drama episode"""
    
    # Check usage
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Cara penggunaan:**\n"
            "`/play <judul drama>` - Cari drama untuk diputar\n\n"
            "**Contoh:**\n"
            "`/play cinta`\n"
            "`/play 41000116666 1` (Direct ID)"
        )
    
    # Check if Direct ID mode (ID + Episode Num)
    is_direct_play = False
    if len(message.command) >= 3:
        try:
            # Check if 1st and 2nd args are valid numbers (ID might be string but usually digits)
            # DramaBox IDs are long digits.
            if message.command[1].isdigit() and message.command[2].isdigit():
                is_direct_play = True
        except:
            pass
            
    if is_direct_play:
        await play_direct(message)
    else:
        await play_search(message)


async def play_search(message: Message):
    """Handle text search for play"""
    
    query = " ".join(message.command[1:])
    msg = await message.reply_text(f"🔍 Mencari drama untuk diputar: **{query}**...")
    
    try:
        dramas = await api.search(query, limit=10)
        
        if not dramas:
            return await msg.edit_text(
                f"❌ Tidak ditemukan drama dengan kata kunci: **{query}**\n"
                f"Coba judul lain atau gunakan `/trending`."
            )
            
        # Improved UI for search results
        text = f"🔍 **Hasil pencarian:** `{query}`\n\n"
        keyboard = []
        
        for i, drama in enumerate(dramas, 1):
            text += f"**{i}. {drama.title}**\n"
            text += f"   📺 {drama.episode_count} Eps | 👁 {drama.views or 'N/A'}\n"
        
        text += "\n💡 Klik tombol di bawah untuk memilih drama!"
        
        row = []
        for i, drama in enumerate(dramas, 1):
            row.append(InlineKeyboardButton(str(i), callback_data=f"drama_{drama.book_id}"))
            if i % 5 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("🗑 Tutup", callback_data="close")])
                
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")


async def play_direct(message: Message):
    """Handle direct play by ID"""
    book_id = message.command[1]
    episode_num = int(message.command[2])
    chat_id = message.chat.id
    
    # Check queue limit
    if len(queue.get_queue(chat_id)) >= config.QUEUE_LIMIT:
        return await message.reply_text(
            f"❌ Queue sudah penuh! (max: {config.QUEUE_LIMIT})\n"
            f"Gunakan `/skip` atau `/stop` untuk clear queue."
        )
    
    msg = await message.reply_text(f"⏳ Mengambil episode {episode_num}...")
    
    try:
        # Get episode and drama details from API
        episode = await api.get_episode(book_id, episode_num)
        drama = await api.get_drama_detail(book_id)
        
        if not episode or not episode.video_url:
            return await msg.edit_text(
                f"❌ Episode {episode_num} tidak ditemukan!\n"
                f"Cek jumlah episode dengan `/search` terlebih dahulu."
            )
        
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
            file_path=episode.video_url,  # Direct URL for streaming
            thumbnail=drama.cover_url if drama and drama.cover_url else (episode.thumbnail or config.DEFAULT_THUMB),
            user=message.from_user.mention,
            book_id=book_id,
            tags="Drama, Romance",
            video=True,
            message_id=msg.id,
            urls=episode.urls # Pass full list of URLs
        )
        
        # Check if bot is in voice chat
        if not await db.get_call(chat_id):
            if not await db.get_client(chat_id): # Ensure we have assistant
                 pass 
                 
            queue.add(chat_id, track)
            await msg.edit_text("✅ Episode ditambahkan ke queue!\nMemulai playback...")
            await drama_call.play_media(chat_id, msg, track)
        else:
            queue.add(chat_id, track)
            await msg.edit_text(
                f"✅ **Ditambahkan ke Queue!**\n\n"
                f"📺 {track.title}\n"
                f"📍 Posisi: #{len(queue.get_queue(chat_id))}\n\n"
                f"Gunakan `/queue` untuk lihat antrian."
            )
        
        # Auto delete command if enabled
        if await db.get_cmd_delete(chat_id):
            try:
                await message.delete()
            except:
                pass
                
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
