# Copyright (c) 2025 DramaBot
# Bot untuk streaming drama ke Telegram voice chat


from pyrogram import filters
from pyrogram.types import Message

from drama import app, config
from drama.helpers import buttons


@app.on_message(filters.command("start") & filters.private)
async def start_private(_, message: Message):
    """Handler untuk /start di private chat"""
    text = (
        f"👋 **Halo {message.from_user.mention}!**\n\n"
        f"> 🎬 Selamat datang di **DramaBot**!\n"
        f"> Bot ini dapat memutar drama/series ke voice chat grup Telegram kamu.\n"
        f"> Streaming langsung dari **DramaBox**!\n\n"
        f"**🎯 Fitur Utama:**\n"
        f"> 📺 Browse drama trending & terbaru\n"
        f"> 🔍 Cari drama favorit\n"
        f"> ▶️ Streaming ke voice chat\n"
        f"> 📋 Queue management\n\n"
        f"**📝 Command:**\n"
        f"`/trending` - Drama trending\n"
        f"`/latest` - Drama terbaru\n"
        f"`/search <query>` - Cari drama\n"
        f"`/play <book_id> <episode>` - Play episode\n"
        f"`/queue` - Lihat antrian\n"
        f"`/pause`, `/resume`, `/skip`, `/stop`\n"
        f"`/ping` - Cek bot status\n\n"
        f"> Tambahkan bot ke grup dan nikmati streaming drama! 🍿"
    )
    
    await message.reply_photo(
        photo=config.START_IMG,
        caption=text,
        reply_markup=buttons.start_key(private=True)
    )


@app.on_message(filters.command("start") & filters.group)
async def start_group(_, message: Message):
    """Handler untuk /start di group chat"""
    text = (
        f"✅ **Bot sudah aktif!**\n\n"
        f"Gunakan `/trending` atau `/latest` untuk browse drama.\n"
        f"Atau `/search <judul>` untuk cari drama tertentu."
    )
    
    await message.reply_text(text, reply_markup=buttons.start_key(private=False))


@app.on_message(filters.command("help"))
async def help_command(_, message: Message):
    """Handler untuk /help"""
    text = (
        f"📖 **Panduan DramaBot**\n\n"
        f"**🎬 Browse Drama:**\n"
        f"> • `/trending` - Lihat drama yang sedang trending\n"
        f"> • `/latest` - Lihat drama terbaru\n"
        f"> • `/search <query>` - Cari drama\n"
        f">   Contoh: `/search pewaris`\n\n"
        f"**▶️ Playback:**\n"
        f"> • `/play <book_id> <episode>` - Play episode\n"
        f">   Contoh: `/play 41000116666 1`\n"
        f"> • `/pause` - Pause playback\n"
        f"> • `/resume` - Resume playback\n"
        f"> • `/skip` - Skip ke episode berikutnya\n"
        f"> • `/stop` - Stop dan clear queue\n\n"
        f"**📋 Queue:**\n"
        f"> • `/queue` - Lihat antrian episode\n\n"
        f"**ℹ️ Info:**\n"
        f"> • `/ping` - Cek status bot\n\n"
        f"**💡 Tips:**\n"
        f"> - Bot perlu akses admin untuk join voice chat\n"
        f"> - Pastikan voice chat sudah aktif sebelum play\n"
        f"> - Gunakan tombol inline untuk navigasi lebih mudah"
    )
    
    await message.reply_text(text)
