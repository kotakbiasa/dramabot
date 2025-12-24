# Copyright (c) 2025 DramaBot
# Bot untuk streaming drama ke Telegram voice chat


import asyncio
import importlib
import threading

from pyrogram import idle

from drama import (drama_call, app, config, db,
                   logger, stop, userbot, api)
from drama.plugins import all_modules


def start_web_server():
    """Start Flask web server in a separate thread"""
    try:
        from drama.web_server import app as flask_app
        logger.info(f"Starting web server on port {config.WEB_PORT}...")
        flask_app.run(
            host='0.0.0.0',
            port=config.WEB_PORT,
            debug=False,
            use_reloader=False  # Important: disable reloader in thread
        )
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")


async def main():
    await db.connect()
    await app.boot()
    await userbot.boot()
    await drama_call.boot()

    for module in all_modules:
        importlib.import_module(f"drama.plugins.{module}")
    logger.info(f"Loaded {len(all_modules)} modules.")

    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)
    app.bl_users.update(await db.get_blacklisted())
    logger.info(f"Loaded {len(app.sudoers)} sudo users.")

    # Start web server in background thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    logger.info("Web server thread started")

    await idle()
    await stop()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass

