# Copyright (c) 2025 DramaBot
# Bot untuk streaming drama ke Telegram voice chat

import aiohttp
from ntgcalls import (ConnectionNotFound, TelegramServerError,
                      RTMPStreamingUnsupported)
from pyrogram import enums
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls import PyTgCalls, exceptions, types
from pytgcalls.pytgcalls_session import PyTgCallsSession

from drama import app, config, db, logger, queue, userbot
from drama.helpers import Media, Track, buttons, thumb


class TgCall(PyTgCalls):
    def __init__(self):
        self.clients = []

    async def get_my_client(self, chat_id: int):
        await db.get_assistant(chat_id)
        if chat_id in db.assistant:
            client_index = db.assistant[chat_id] - 1
            return self.clients[client_index]
        return self.clients[0]

    async def pause(self, chat_id: int) -> bool:
        client = await self.get_my_client(chat_id)
        await db.playing(chat_id, paused=True)
        return await client.pause(chat_id)

    async def resume(self, chat_id: int) -> bool:
        client = await self.get_my_client(chat_id)
        await db.playing(chat_id, paused=False)
        return await client.resume(chat_id)

    async def stop(self, chat_id: int) -> None:
        client = await self.get_my_client(chat_id)
        try:
            queue.clear(chat_id)
            await db.remove_call(chat_id)
        except:
            pass

        try:
            await client.leave_call(chat_id)
        except:
            pass

    async def _check_url(self, url: str) -> bool:
        """Check if URL is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=5) as resp:
                    return resp.status == 200
        except:
            return False

    async def play_media(
        self,
        chat_id: int,
        message: Message,
        media: Media | Track,
        seek_time: int = 0,
    ) -> None:
        client = await self.get_my_client(chat_id)
        _thumb = (
            await thumb.generate(media)
            if isinstance(media, Track)
            else config.DEFAULT_THUMB
        )

        if not media.file_path and not media.urls:
            await message.edit_text("❌ File tidak ditemukan. Hubungi owner!")
            return await self.play_next(chat_id)

        # Determine valid URL (try list first, then single file_path)
        valid_url = None

        if media.urls:
            # Sort urls by quality (descending)
            # Ensure quality is int
            sorted_urls = sorted(media.urls, key=lambda x: int(x.get("quality", 0)), reverse=True)

            await message.edit_text("⏳ Memeriksa kualitas stream terbaik...")

            for u in sorted_urls:
                url = u.get("url")
                if not url: continue

                # Verify if stream is accessible
                if await self._check_url(url):
                    valid_url = url
                    logger.info(f"Selected stream quality: {u.get('quality')}p")
                    break

        if not valid_url:
            valid_url = media.file_path

        if not valid_url:
             await message.edit_text("❌ Semua link streaming mati. Coba lagi nanti.")
             return await self.play_next(chat_id)

        stream = types.MediaStream(
            media_path=valid_url,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=(
                types.MediaStream.Flags.AUTO_DETECT
                if media.video
                else types.MediaStream.Flags.IGNORE
            ),
            ffmpeg_parameters=f"-ss {seek_time}" if seek_time > 1 else None,
        )
        try:
            await client.play(
                chat_id=chat_id,
                stream=stream,
                config=types.GroupCallConfig(auto_start=False),
            )
            if not seek_time:
                media.time = 1
                await db.add_call(chat_id)
                text = f"🎬 <b>Sekarang Diputar</b>\n\n"
                text += f"📺 <b>Judul:</b> {media.title}\n"
                
                # Extract and show episode number if available
                import re
                episode_match = re.search(r'(?:EP|Episode)\s*(\d+)', media.title, re.IGNORECASE)
                if episode_match:
                    text += f"📌 <b>Episode:</b> {episode_match.group(1)}\n"
                
                if getattr(media, "tags", None):
                    text += f"🏷 <b>Tags:</b> {media.tags}"
                keyboard = buttons.controls(chat_id)
                try:
                    await message.edit_media(
                        media=InputMediaPhoto(
                            media=_thumb,
                            caption=text,
                            parse_mode=enums.ParseMode.HTML,
                        ),
                        reply_markup=keyboard,
                    )
                except MessageIdInvalid:
                    media.message_id = (await app.send_photo(
                        chat_id=chat_id,
                        photo=_thumb,
                        caption=text,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=keyboard,
                    )).id
        except FileNotFoundError:
            await message.edit_text("❌ File tidak ditemukan. Hubungi owner!")
            await self.play_next(chat_id)
        except exceptions.NoActiveGroupCall:
            await self.stop(chat_id)
            await message.edit_text("❌ Tidak ada voice chat aktif.")
        except exceptions.NoAudioSourceFound:
            await message.edit_text("❌ Tidak ada sumber audio ditemukan.")
            await self.play_next(chat_id)
        except (ConnectionNotFound, TelegramServerError):
            await self.stop(chat_id)
            await message.edit_text("❌ Error koneksi ke server Telegram.")
        except RTMPStreamingUnsupported:
            await self.stop(chat_id)
            await message.edit_text("❌ RTMP streaming tidak didukung.")


    async def replay(self, chat_id: int) -> None:
        if not await db.get_call(chat_id):
            return

        media = queue.get_current(chat_id)
        msg = await app.send_message(chat_id=chat_id, text="🔄 Memutar ulang...")
        await self.play_media(chat_id, msg, media)


    async def play_next(self, chat_id: int) -> None:
        media = queue.get_next(chat_id)
        try:
            if media.message_id:
                await app.delete_messages(
                    chat_id=chat_id,
                    message_ids=media.message_id,
                    revoke=True,
                )
                media.message_id = 0
        except:
            pass

        if not media:
            return await self.stop(chat_id)

        msg = await app.send_message(chat_id=chat_id, text="⏭ Memutar episode berikutnya...")
        
        # For drama, file_path should already be the video URL
        # No need to download like YouTube
        if not media.file_path and not media.urls:
            await self.stop(chat_id)
            return await msg.edit_text(
                "❌ URL episode tidak ditemukan. Hubungi owner!"
            )

        media.message_id = msg.id
        await self.play_media(chat_id, msg, media)


    async def ping(self) -> float:
        pings = [client.ping for client in self.clients]
        return round(sum(pings) / len(pings), 2)


    async def decorators(self, client: PyTgCalls) -> None:
        for client in self.clients:
            @client.on_update()
            async def update_handler(_, update: types.Update) -> None:
                if isinstance(update, types.StreamEnded):
                    if update.stream_type == types.StreamEnded.Type.AUDIO:
                        await self.play_next(update.chat_id)
                elif isinstance(update, types.ChatUpdate):
                    if update.status in [
                        types.ChatUpdate.Status.KICKED,
                        types.ChatUpdate.Status.LEFT_GROUP,
                        types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                    ]:
                        await self.stop(update.chat_id)


    async def boot(self) -> None:
        PyTgCallsSession.notice_displayed = True
        for ub in userbot.clients:
            client = PyTgCalls(ub, cache_duration=100)
            await client.start()
            self.clients.append(client)
            await self.decorators(client)
        logger.info("PyTgCalls client(s) started.")
