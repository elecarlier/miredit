from PIL import Image, ImageDraw

from models import PrintSettings


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
    strip_h = settings.mm_to_px_v(bord_mire_mm) #selon la resolution verticale
    margin = settings.mm_to_px_h(3.0) #later -> change 3.00 ? (2+1)

    total_w = w + 2 * margin
    total_h = strip_h + h + strip_h
 
    mire_strip = _crop_mire_centered(mire, w, strip_h)


 
    result = Image.new("RGBA", (w, total_h), (0, 0, 0, 0)) #crée une toile vierge : même largeur que l'image originale mais une hauteur augmentée des deux bandes de mire (une en haut, une en bas)
 
    result.paste(mire_strip, (margin, 0))
    result.paste(img,        (margin, strip_h))
    result.paste(mire_strip, (margin, strip_h + h))

    draw = ImageDraw.Draw(result)
    black = (0, 0, 0, 255) 
    red = (255, 0, 0, 255) 


    x1 = margin - settings.mm_to_px_h(2.0) #position du bord gauche du trait 1 : 2mm à gauche de l'image
    w1 = settings.line_frac_px(1 / 4) #épaisseur du trait 1
    x2 = margin - settings.mm_to_px_h(1.0) #position du bord gauche du trait 2 : 1mm à gauche de l'image
    w2 = settings.line_frac_px(1 / 6) #épaisseur du trait 2


    #hauteur totale : y_haut = 0 et y_bas=total_h - 1
    # draw.rectangle([x1,                0, x1 + w1 - 1,           total_h - 1], fill=black)
    # draw.rectangle([x2,                0, x2 + w2 - 1,           total_h - 1], fill=black)
    # draw.rectangle([total_w - x1 - w1, 0, total_w - x1 - 1,      total_h - 1], fill=black)
    # draw.rectangle([total_w - x2 - w2, 0, total_w - x2 - 1,      total_h - 1], fill=black)

    #en rouge pour pouvoir le visualiser 
    draw.rectangle([x1,                0, x1 + w1 - 1,           total_h - 1], fill=red)
    draw.rectangle([x2,                0, x2 + w2 - 1,           total_h - 1], fill=red)
    draw.rectangle([total_w - x1 - w1, 0, total_w - x1 - 1,      total_h - 1], fill=red)
    draw.rectangle([total_w - x2 - w2, 0, total_w - x2 - 1,      total_h - 1], fill=red)

    return result
