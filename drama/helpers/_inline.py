# Copyright (c) 2025 DramaBot
# Bot untuk streaming drama ke Telegram voice chat


from pyrogram import types

from drama import app, config


class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, callback_data=f"cancel_dl")]])

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
    ) -> types.InlineKeyboardMarkup:
        keyboard = []
        if status:
            keyboard.append(
                [self.ikb(text=status, callback_data=f"controls status {chat_id}")]
            )
        elif timer:
            keyboard.append(
                [self.ikb(text=timer, callback_data=f"controls status {chat_id}")]
            )

        if not remove:
            keyboard.append(
                [
                    self.ikb(text="⏹", callback_data=f"controls stop {chat_id}"),
                    self.ikb(text="⏯", callback_data=f"controls playpause {chat_id}"),
                    self.ikb(text="⏭", callback_data=f"controls skip {chat_id}"),
                ]
            )
            keyboard.append(
                [self.ikb(text="❌ Tutup", callback_data="close")]
            )
        return self.ikm(keyboard)

    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        # Contact owner directly
        return self.ikm([[self.ikb(text=text, url=f"tg://user?id={config.OWNER_ID}")]])

    def play_queued(
        self, chat_id: int, item_id: str, text: str
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=text, callback_data=f"controls force {chat_id} {item_id}"
                    )
                ]
            ]
        )

    def queue_markup(
        self, chat_id: int, text: str, playing: bool
    ) -> types.InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm(
            [[self.ikb(text=text, callback_data=f"controls {_action} {chat_id} q")]]
        )

    def start_key(self, private: bool = False) -> types.InlineKeyboardMarkup:
        rows = [
            [
                self.ikb(
                    text="➕ Tambah ke Grup",
                    url=f"https://t.me/{app.username}?startgroup=true",
                )
            ],
            [
                self.ikb(text="📺 Trending", callback_data="browse_trending"),
                self.ikb(text="🆕 Terbaru", callback_data="browse_latest"),
            ],
            [
                self.ikb(text="👤 Owner", url=f"tg://user?id={config.OWNER_ID}"),
            ],
        ]
        return self.ikm(rows)

    def drama_key(self, drama_id: str) -> types.InlineKeyboardMarkup:
        """Keyboard untuk drama detail"""
        return self.ikm(
            [
                [
                    self.ikb(text="▶️ Play Episode 1", callback_data=f"play_{drama_id}_1")
                ],
                [
                    self.ikb(text="📋 Lihat Semua Episode", callback_data=f"episodes_{drama_id}")
                ],
            ]
        )


buttons = Inline()
