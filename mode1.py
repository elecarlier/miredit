from PIL import Image, ImageDraw

from models import PrintSettings


def _crop_mire_centered(mire: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Découpe la mire centrée à la taille cible (target_w x target_h)."""
    mw, mh = mire.size
    left = max((mw - target_w) // 2, 0)
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
    Mode 1 — plaque plus grande.

    - Ajoute une bande de mire en haut et en bas (hauteur = bord_mire_mm).
    - Ajoute deux traits noirs verticaux de chaque côté (gauche + droite),
      sur toute la hauteur de l'image finale :
        * Trait 1 : largeur = 1/4 de ligne, bord gauche du trait à 2mm du bord image.
        * Trait 2 : largeur = 1/6 de ligne, bord gauche du trait à 3mm du bord image (2+1).
    """
    w, h = img.size
    strip_h = settings.mm_to_px_v(bord_mire_mm)

    # Bande de mire centrée, même largeur que l'image
    mire_strip = _crop_mire_centered(mire, w, strip_h)

    # Composition : mire_haut / image / mire_bas
    total_h = strip_h + h + strip_h
    result = Image.new(img.mode, (w, total_h))
    result.paste(mire_strip, (0, 0))
    result.paste(img, (0, strip_h))
    result.paste(mire_strip, (0, strip_h + h))

    # Traits noirs verticaux
    draw = ImageDraw.Draw(result)
    black = (0, 0, 0) if img.mode in ("RGB", "RGBA") else 0

    x1 = settings.mm_to_px_h(2.0)      # position bord gauche du trait 1
    w1 = settings.line_frac_px(1 / 4)  # largeur trait 1 (1/4 de ligne)
    x2 = settings.mm_to_px_h(3.0)      # position bord gauche du trait 2 (2 + 1mm)
    w2 = settings.line_frac_px(1 / 6)  # largeur trait 2 (1/6 de ligne)

    # Côté gauche
    draw.rectangle([x1, 0, x1 + w1 - 1, total_h - 1], fill=black)
    draw.rectangle([x2, 0, x2 + w2 - 1, total_h - 1], fill=black)

    # Côté droit (symétrie)
    draw.rectangle([w - x1 - w1, 0, w - x1 - 1, total_h - 1], fill=black)
    draw.rectangle([w - x2 - w2, 0, w - x2 - 1, total_h - 1], fill=black)

    return result
