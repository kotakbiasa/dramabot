# Copyright (c) 2025 DramaBot
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance,
                 ImageFilter, ImageFont, ImageOps)

from drama import config
from drama.helpers import Track


class Thumbnail:
    def __init__(self):
        self.rect = (914, 514)
        self.fill = (255, 255, 255)
        self.mask = Image.new("L", self.rect, 0)
        self.font1 = ImageFont.truetype("drama/helpers/Raleway-Bold.ttf", 30)
        self.font2 = ImageFont.truetype("drama/helpers/Inter-Light.ttf", 30)

    async def save_thumb(self, output_path: str, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                open(output_path, "wb").write(await resp.read())
            return output_path

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            await self.save_thumb(temp, song.thumbnail)
            thumb = Image.open(temp).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
            blur = thumb.filter(ImageFilter.GaussianBlur(25))
            image = ImageEnhance.Brightness(blur).enhance(.40)

            _rect = ImageOps.fit(thumb, self.rect, method=Image.LANCZOS, centering=(0.5, 0.5))
            ImageDraw.Draw(self.mask).rounded_rectangle((0, 0, self.rect[0], self.rect[1]), radius=20, fill=255)
            _rect.putalpha(self.mask)
            image.paste(_rect, (183, 30), _rect)

            draw = ImageDraw.Draw(image)
            
            # Draw Title (Larger, Centered or Left aligned below image)
            # Actually, let's keep it similar but cleaner
            
            # Simple "NOW STREAMING" badge/text
            font_small = ImageFont.truetype("drama/helpers/Inter-Light.ttf", 25)
            font_large = ImageFont.truetype("drama/helpers/Raleway-Bold.ttf", 50)
            
            # Calculate text positioning
            # Center horizontally? Or Left aligned under image
            
            # Let's simplify: Remove progress bar, center Title below image
            # Image is at (183, 30) with size (914, 514) -> Center X = 183 + 457 = 640
            
            # Draw Title Centered
            title_text = song.title[:50]
            if len(song.title) > 50:
                title_text += "..."
                
            draw.text((640, 580), title_text, font=font_large, fill=self.fill, anchor="mm")
            
            # Draw Subtitle (Channel Name)
            sub_text = "Drama Stream"
            if song.user:
                 sub_text += f" • Req by {song.user.replace('@', '')}"
            draw.text((640, 640), sub_text, font=font_small, fill=self.fill, anchor="mm")

            image.save(output)
            os.remove(temp)
            return output
        except:
            config.DEFAULT_THUMB
