# Copyright (c) 2025 DramaBot
# Inline query handler (currently minimal)


from pyrogram import filters
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from drama import app


@app.on_inline_query()
async def inline_query_handler(_, query: InlineQuery):
    """Handle inline queries"""
    
    # Simple inline query response
    results = [
        InlineQueryResultArticle(
            title="DramaBot",
            description="Bot untuk streaming drama",
            input_message_content=InputTextMessageContent(
                "🎬 **DramaBot**\n\n"
                "Bot untuk streaming drama ke voice chat Telegram!\n\n"
                "Gunakan `/start` untuk mulai."
            )
        )
    ]
    
    await query.answer(results, cache_time=1)
