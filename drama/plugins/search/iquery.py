# Copyright (c) 2025 DramaBot
# Inline query handler for searching dramas


from pyrogram import filters, enums
from pyrogram.types import (
    InlineQuery, 
    InlineQueryResultArticle, 
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from drama import app, api, logger


@app.on_inline_query()
async def inline_query_handler(_, query: InlineQuery):
    """Handle inline queries - search for dramas"""
    
    logger.info(f"Inline query received from {query.from_user.id}: '{query.query}'")
    
    search_query = query.query.strip()
    
    # If no query, show help message
    if not search_query:
        results = [
            InlineQueryResultArticle(
                id="help",
                title="🎬 DramaBot Search",
                description="Ketik judul drama untuk mencari...",
                input_message_content=InputTextMessageContent(
                    "🎬 **DramaBot**\n\n"
                    "Gunakan inline mode untuk search drama:\n"
                    "`@DracinStreamingBot <judul drama>`\n\n"
                    "Contoh: `@DracinStreamingBot cinta`"
                )
            )
        ]
        return await query.answer(results, cache_time=1)
    
    # Search for dramas
    try:
        dramas = await api.search(search_query, limit=10)
        
        if not dramas:
            results = [
                InlineQueryResultArticle(
                    id="no_results",
                    title="❌ Tidak ditemukan",
                    description=f"Tidak ada hasil untuk '{search_query}'",
                    input_message_content=InputTextMessageContent(
                        f"❌ Tidak ditemukan drama dengan kata kunci: **{search_query}**"
                    )
                )
            ]
            return await query.answer(results, cache_time=1)
        
        # Build results
        results = []
        for i, drama in enumerate(dramas):
            # Truncate description
            description = drama.description[:100] + "..." if drama.description and len(drama.description) > 100 else drama.description or "Tidak ada deskripsi"
            
            # Build caption/message with HTML formatting
            message_text = ""
            # Add cover image link for preview
            if drama.cover_url:
                message_text += f"<a href='{drama.cover_url}'>​</a>"  # Zero-width space for invisible link
            
            message_text += f"🎬 <b>{drama.title}</b>\n\n"
            
            # Description in expandable blockquote
            if drama.description:
                desc = drama.description[:500] + "..." if len(drama.description) > 500 else drama.description
                # Escape HTML characters for safety
                desc_escaped = desc.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                message_text += f"<blockquote expandable>{desc_escaped}</blockquote>\n\n"
            
            message_text += f"🆔 <b>Book ID:</b> <code>{drama.book_id}</code>\n"
            
            # Add tags if available
            if drama.tags:
                tags_str = ", ".join(drama.tags) if isinstance(drama.tags, list) else drama.tags
                message_text += f"🏷 <b>Tags:</b> {tags_str}\n"
            
            # Add protagonist if available
            if drama.protagonist:
                message_text += f"👤 <b>Pemeran:</b> {drama.protagonist}\n"
            
            if drama.views:
                message_text += f"👁 <b>Views:</b> {drama.views}\n"
            
            message_text += f"\n💡 Gunakan /search {search_query} untuk detail lengkap!"
            
            result = InlineQueryResultArticle(
                id=f"drama_{drama.book_id}",
                title=drama.title,
                description=description,
                thumb_url=drama.cover_url if drama.cover_url else None,
                input_message_content=InputTextMessageContent(
                    message_text,
                    parse_mode=enums.ParseMode.HTML
                )
            )
            results.append(result)
        
        await query.answer(results, cache_time=0)
        
    except Exception as e:
        results = [
            InlineQueryResultArticle(
                id="error",
                title="❌ Error",
                description="Terjadi kesalahan saat mencari",
                input_message_content=InputTextMessageContent(
                    f"❌ Error: {str(e)}"
                )
            )
        ]
        await query.answer(results, cache_time=1)
