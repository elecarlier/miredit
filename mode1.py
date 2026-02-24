import logging
import numpy as np
from PIL import Image, ImageDraw

from models import PrintSettings

logger = logging.getLogger(__name__)


def _crop_mire_centered(mire: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """
    Découpe un rectangle de target_w × target_h pixels dans la mire, centré.

    Si la mire est plus large que target_w, on coupe des deux côtés également.
    Si la mire est plus haute que target_h, on coupe en haut et en bas également.
    Le max(..., 0) protège contre un index négatif si la mire est plus petite que la cible.
    """
    mw, mh = mire.size

    # Décalage pour centrer horizontalement : écart total / 2
    left = max((mw - target_w) // 2, 0)
    # Décalage pour centrer verticalement
    top = max((mh - target_h) // 2, 0)

    right = left + target_w
    bottom = top + target_h

    return mire.crop((left, top, right, bottom))


def apply_mode1(
    img: Image.Image,
    mire: Image.Image,
    settings: PrintSettings,
    bord_mire_mm: float,
) -> Image.Image:
    """
    Mode 1 — plaque physique plus grande que l'image lenticulaire.
    """
    img = img.convert("RGBA")
    mire = mire.convert("RGBA")

    w, h = img.size
    strip_h = settings.mm_to_px_v(bord_mire_mm)
    margin = settings.mm_to_px_h(3.0)

    total_w = w + 2 * margin
    total_h = strip_h + h + strip_h



    logger.info(f"Bande mire : {strip_h}px  |  marge : {margin}px  |  canvas : {total_w}x{total_h}px")

    mire_strip = _crop_mire_centered(mire, total_w, strip_h)
    logger.debug(f"Mire recadrée : {mire_strip.size}")

    img_center = margin + w // 2          # centre de l'image dans le canvas
    mire_x     = img_center - mire_strip.width // 2

    logger.info(f"Centre image dans canvas : {img_center}px  |  paste mire à x={mire_x}px")


    mire_strip_full = Image.new("RGBA", (total_w, strip_h), (0, 0, 0, 0))

# Recadrer la mire à sa propre taille (juste pour limiter la hauteur à strip_h)
    mire_cropped = _crop_mire_centered(mire, mire.width, strip_h)

    # Coller la mire centrée horizontalement
    x_offset = (total_w - mire_cropped.width) // 2
    mire_strip_full.paste(mire_cropped, (x_offset, 0), mire_cropped)  # masque alpha

    result = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    result.paste(mire_strip_full, (0, 0),            mire_strip_full)
    result.paste(img,             (margin, strip_h), img)
    result.paste(mire_strip_full, (0, strip_h + h),  mire_strip_full)
    logger.info("Bandes mire et image collées")

    draw = ImageDraw.Draw(result)
    black = (0, 0, 0, 255)
    red = (255, 0, 0, 255)

    x1 = margin - settings.mm_to_px_h(2.0)
    w1 = settings.line_frac_px(1 / 4)
    x2 = margin - settings.mm_to_px_h(1.0)
    w2 = settings.line_frac_px(1 / 6)

    logger.debug(f"Traits repérage — x1={x1} w1={w1}px  |  x2={x2} w2={w2}px")


    draw.rectangle([x1,                0, x1 + w1 - 1,           total_h - 1], fill=black)
    draw.rectangle([x2,                0, x2 + w2 - 1,           total_h - 1], fill=black)
    draw.rectangle([total_w - x1 - w1, 0, total_w - x1 - 1,      total_h - 1], fill=black)
    draw.rectangle([total_w - x2 - w2, 0, total_w - x2 - 1,      total_h - 1], fill=black)
    logger.info("Traits de repérage dessinés")

    return result