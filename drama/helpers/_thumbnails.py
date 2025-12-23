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

    async def generate(self, song: Track, size=(720, 900)) -> str:
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            await self.save_thumb(temp, song.thumbnail)
            
            # --------------------------------------------------------------------------
            # BLURRED BACKGROUND + CENTERED POSTER DESIGN
            # --------------------------------------------------------------------------
            
            # 1. Load and blur thumbnail as background
            thumb = Image.open(temp).convert("RGBA")
            
            # Resize to cover the entire canvas
            thumb_ratio = thumb.width / thumb.height
            target_ratio = size[0] / size[1]
            
            if thumb_ratio > target_ratio:
                new_height = size[1]
                new_width = int(new_height * thumb_ratio)
            else:
                new_width = size[0]
                new_height = int(new_width / thumb_ratio)
            
            thumb_bg = thumb.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center crop for background
            left = (new_width - size[0]) // 2
            top = (new_height - size[1]) // 2
            thumb_bg = thumb_bg.crop((left, top, left + size[0], top + size[1]))
            
            # Apply blur and darken
            image = thumb_bg.filter(ImageFilter.GaussianBlur(30))
            image = ImageEnhance.Brightness(image).enhance(0.35)
            
            # Add gradient overlay
            overlay = Image.new('RGBA', size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Bottom gradient
            for i in range(350):
                alpha = int((i / 350) * 200)
                overlay_draw.rectangle([(0, size[1] - 350 + i), (size[0], size[1] - 349 + i)], 
                                      fill=(0, 0, 0, alpha))
            
            image = Image.alpha_composite(image.convert('RGBA'), overlay)
            
            # 2. Add centered poster thumbnail
            poster_size = (420, 560)
            poster_x = (size[0] - poster_size[0]) // 2
            poster_y = 70
            
            # Reload original for poster
            poster_thumb = Image.open(temp).convert("RGBA")
            poster_img = ImageOps.fit(poster_thumb, poster_size, method=Image.LANCZOS, centering=(0.5, 0.3))
            
            # Rounded corners
            mask = Image.new("L", poster_size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, poster_size[0], poster_size[1]), radius=20, fill=255)
            poster_img.putalpha(mask)
            
            # White border
            border_img = Image.new('RGBA', poster_size, (0,0,0,0))
            ImageDraw.Draw(border_img).rounded_rectangle(
                (0, 0, poster_size[0], poster_size[1]), 
                radius=20, 
                outline=(255, 255, 255, 120), 
                width=3
            )
            poster_img = Image.alpha_composite(poster_img, border_img)
            
            image.paste(poster_img, (poster_x, poster_y), poster_img)
            
            # 3. Draw text (centered below poster)
            draw = ImageDraw.Draw(image)
            
            font_title = ImageFont.truetype("drama/helpers/Raleway-Bold.ttf", 38)
            font_episode = ImageFont.truetype("drama/helpers/Raleway-Bold.ttf", 30)
            font_tags = ImageFont.truetype("drama/helpers/Inter-Light.ttf", 22)
            font_indicator = ImageFont.truetype("drama/helpers/Raleway-Bold.ttf", 16)

            # Clean Title
            import re
            title_text = re.sub(r'\s*[-|]?\s*(?:EP|Episode)\s*\d+', '', song.title, flags=re.IGNORECASE).strip()
            title_text = re.sub(r'\s*-\s*$', '', title_text).strip()
            
            # Word wrap title
            max_title_width = size[0] - 60
            words = title_text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font_title)
                if bbox[2] - bbox[0] <= max_title_width:
                    current_line = test_line
                else:
                    if current_line: lines.append(current_line)
                    current_line = word
            if current_line: lines.append(current_line)
            
            if len(lines) > 2:
                lines = lines[:2]
                lines[1] = lines[1][:20] + "..."
            
            # Position text below poster
            center_x = size[0] // 2
            text_y = poster_y + poster_size[1] + 40
            
            # Draw Title
            for line in lines:
                draw.text((center_x, text_y), line, font=font_title, fill=(255, 255, 255), anchor="mm")
                text_y += 48
            
            # Episode
            episode_match = re.search(r'(?:EP|Episode)\s*(\d+)', song.title, re.IGNORECASE)
            if episode_match:
                episode_text = f"Episode {episode_match.group(1)}"
                draw.text((center_x, text_y + 10), episode_text, font=font_episode, fill=(255, 180, 180), anchor="mm")
                text_y += 45
            
            # Tags
            if hasattr(song, 'tags') and song.tags:
                tags_text = song.tags.upper()
                draw.text((center_x, text_y + 15), tags_text, font=font_tags, fill=(180, 180, 180), anchor="mm")

            # 4. NOW PLAYING Indicator (Top left)
            indicator_y = 30
            dot_x = 30
            dot_y = indicator_y + 3
            
            draw.ellipse([(dot_x, dot_y), (dot_x + 12, dot_y + 12)], fill=(255, 70, 70))
            draw.text((dot_x + 22, indicator_y), "NOW PLAYING", font=font_indicator, fill=(255, 255, 255))

            # 5. Branding
            brand_font = ImageFont.truetype("drama/helpers/Inter-Light.ttf", 14)
            draw.text((size[0] - 30, 35), "DramaBot", font=brand_font, fill=(255, 255, 255, 150), anchor="rm")

            image = image.convert('RGB')
            image.save(output)
            os.remove(temp)
            return output
        except Exception as e:
            print(f"Thumbnail generation error: {e}")
            return config.DEFAULT_THUMB


thumb = Thumbnail()
