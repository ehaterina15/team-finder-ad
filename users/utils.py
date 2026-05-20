import io
import random

from django.core.files.base import ContentFile

from PIL import Image, ImageDraw, ImageFont

from .constants import AVATAR_COLORS, AVATAR_FONT_SIZE, AVATAR_SIZE


def generate_avatar(email, name):
    color = random.choice(AVATAR_COLORS)
    letter = name[0].upper() if name else '?'

    img = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', AVATAR_FONT_SIZE)
    except OSError:
        font = ImageFont.load_default(size=AVATAR_FONT_SIZE)

    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(
        ((AVATAR_SIZE - w) / 2 - bbox[0], (AVATAR_SIZE - h) / 2 - bbox[1]),
        letter,
        fill='white',
        font=font,
    )

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue(), name=f'avatar_{email}.png')
