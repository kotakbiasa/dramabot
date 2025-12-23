# Copyright (c) 2025 DramaBot
# Execute Python code (sudo only - for debugging)


import io
import sys
import traceback

from pyrogram import filters
from pyrogram.types import Message

from drama import app


@app.on_message(filters.command("eval"))
async def eval_command(_, message: Message):
    """Execute Python code (DANGEROUS - sudo only)"""
    # Check sudo
    if message.from_user.id not in app.sudoers:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Usage:**\n"
            "Reply ke code atau `/eval <code>`"
        )
    
    code = message.text.split(None, 1)[1] if len(message.command) >= 2 else message.reply_to_message.text
    
    if not code:
        return await message.reply_text("❌ Tidak ada code untuk dieksekusi!")
    
    msg = await message.reply_text("⏳ Executing...")
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = output = io.StringIO()
    
    try:
        exec(code, globals(), locals())
        result = output.getvalue()
        
        if result:
            await msg.edit_text(f"**Output:**\n```\n{result[:4000]}\n```")
        else:
            await msg.edit_text("✅ Executed successfully (no output)")
            
    except Exception:
        error = traceback.format_exc()
        await msg.edit_text(f"❌ **Error:**\n```\n{error[:4000]}\n```")
    finally:
        sys.stdout = old_stdout
