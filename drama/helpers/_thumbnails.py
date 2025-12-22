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

    async def generate(self, song: Track, size=(720, 1280)) -> str:
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            await self.save_thumb(temp, song.thumbnail)
            # --------------------------------------------------------------------------
            # PREMIUM THUMBNAIL DESIGN
            # --------------------------------------------------------------------------
            
            # 1. Background (Darkened & Blurred)
            thumb = Image.open(temp).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
            blur = thumb.filter(ImageFilter.GaussianBlur(30))
            # Darken significantly for cinematic feel
            image = ImageEnhance.Brightness(blur).enhance(0.3)
            
            # Vignette / Gradient Overlay
            overlay = Image.new('RGBA', size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Top Gradient (Subtle)
            for i in range(250):
                alpha = int((1 - i / 250) * 150)
                overlay_draw.rectangle([(0, i), (size[0], i + 1)], fill=(0, 0, 0, alpha))
                
            # Bottom Gradient (Strong for text readability)
            for i in range(500):
                alpha = int((i / 500) * 255)
                overlay_draw.rectangle([(0, size[1] - 500 + i), (size[0], size[1] - 499 + i)], 
                                      fill=(0, 0, 0, alpha))
            
            image = Image.alpha_composite(image.convert('RGBA'), overlay)

            # 2. Floating Poster with Shadow
            poster_width = 540
            poster_height = 780
            poster_x = (size[0] - poster_width) // 2
            poster_y = 120 # Move up slightly

            # Drop Shadow (Simulated)
            shadow_offset = 20
            shadow_blur_radius = 40
            shadow_img = Image.new('RGBA', size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            # Draw shadow rect
            shadow_rect = [poster_x + shadow_offset, poster_y + shadow_offset, 
                          poster_x + poster_width - shadow_offset, poster_y + poster_height + shadow_offset]
            shadow_draw.rounded_rectangle(shadow_rect, radius=40, fill=(0, 0, 0, 180))
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_blur_radius))
            
            image = Image.alpha_composite(image, shadow_img)

            # The Poster itself
            poster_img = ImageOps.fit(thumb, (poster_width, poster_height), method=Image.LANCZOS, centering=(0.5, 0.5))
            
            # Rounded corners for poster
            mask = Image.new("L", (poster_width, poster_height), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, poster_width, poster_height), radius=30, fill=255)
            poster_img.putalpha(mask)
            
            # Thin white stroke (Border) for pop
            border_img = Image.new('RGBA', (poster_width, poster_height), (0,0,0,0))
            ImageDraw.Draw(border_img).rounded_rectangle((0,0,poster_width, poster_height), radius=30, outline=(255,255,255, 80), width=3)
            poster_img = Image.alpha_composite(poster_img, border_img)
            
            image.paste(poster_img, (poster_x, poster_y), poster_img)

            # Draw Object
            draw = ImageDraw.Draw(image)

            # Fonts
            font_title = ImageFont.truetype("drama/helpers/Raleway-Bold.ttf", 44)
            font_meta = ImageFont.truetype("drama/helpers/Inter-Light.ttf", 26)
            font_badge = ImageFont.truetype("drama/helpers/Raleway-Bold.ttf", 22)

            # 3. Text & Typography
            
            # Clean Title
            import re
            title_text = re.sub(r'\s*[-|]?\s*(?:EP|Episode)\s*\d+', '', song.title, flags=re.IGNORECASE).strip()
            title_text = re.sub(r'\s*-\s*$', '', title_text).strip()
            
            max_title_width = size[0] - 60
            
            # Wrap title
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
                lines[1] = lines[1][:30] + "..."
            
            text_y = poster_y + poster_height + 50
            center_x = size[0] // 2
            
            for line in lines:
                draw.text((center_x, text_y), line, font=font_title, fill=(255, 255, 255), anchor="mm")
                text_y += 55
            
            # 4. Pill Badges (Episode & Tags)
            badges = []
            
            # Episode Badge
            match = re.search(r'(?:EP|Episode)\s*(\d+)', song.title, re.IGNORECASE)
            if match:
                badges.append(f"EPISODE {match.group(1)}")
            
            # Tags Badge
            if hasattr(song, 'tags') and song.tags:
                tags = song.tags.split(',')
                if tags:
                    badges.append(tags[0].strip().upper()) # First tag only to keep it clean, or max 2
            
            # Start position for badges
            badge_y = text_y + 15
            badge_spacing = 20
            
            # Calculate total width to center them
            total_badges_width = 0
            badge_widths = []
            
            for b_text in badges:
                bbox = draw.textbbox((0, 0), b_text, font=font_badge)
                w = bbox[2] - bbox[0] + 40 # Padding
                badge_widths.append(w)
                total_badges_width += w
            
            total_badges_width += (len(badges) - 1) * badge_spacing
            current_badge_x = (size[0] - total_badges_width) // 2
            
            for i, b_text in enumerate(badges):
                w = badge_widths[i]
                h = 44 # specific height
                
                # Glassmorphism Pill (Semi-transparent white/grey)
                pill_x1, pill_y1 = current_badge_x, badge_y
                pill_x2, pill_y2 = current_badge_x + w, badge_y + h
                
                # Draw pill
                draw.rounded_rectangle([(pill_x1, pill_y1), (pill_x2, pill_y2)], radius=22, fill=(255, 255, 255, 30))
                # Border for pill
                draw.rounded_rectangle([(pill_x1, pill_y1), (pill_x2, pill_y2)], radius=22, outline=(255, 255, 255, 80), width=2)
                
                # Text
                draw.text((pill_x1 + w//2, pill_y1 + h//2), b_text, font=font_badge, fill=(255, 255, 255), anchor="mm")
                
                current_badge_x += w + badge_spacing


            # 5. NOW PLAYING / LIVE Indicator (Top Left)
            # Small, red pulsating style dot + Text
            ind_text = "NOW PLAYING"
            ind_font = ImageFont.truetype("drama/helpers/Raleway-Bold.ttf", 24)
            
            # Position
            ind_x = 40
            ind_y = 40
            
            # Red Dot
            dot_radius = 8
            draw.ellipse([(ind_x, ind_y + 8), (ind_x + dot_radius*2, ind_y + 8 + dot_radius*2)], fill=(255, 50, 50))
            
            # Text
            draw.text((ind_x + 30, ind_y + 6), ind_text, font=ind_font, fill=(255, 255, 255))
            
            # Progress Bar (Fake Visual)
            bar_width = size[0]
            bar_height = 8
            draw.rectangle([(0, size[1] - bar_height), (bar_width, size[1])], fill=(255, 255, 255, 50)) # Track
            draw.rectangle([(0, size[1] - bar_height), (bar_width * 0.35, size[1])], fill=(225, 29, 72)) # Progress (Red)

            image = image.convert('RGB')
            image.save(output)
            os.remove(temp)
            return output
        except Exception as e:
            print(f"Thumbnail generation error: {e}")
            return config.DEFAULT_THUMB
