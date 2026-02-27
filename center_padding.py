import logging
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from models import PrintSettings

logger = logging.getLogger(__name__)


def image_center(img: Image.Image) -> int:
    """Retourne le pixel du milieu horizontal de l'image."""
    return img.width // 2


def is_red(arr: np.ndarray) -> np.ndarray:
    """
    Masque booléen : pixel rouge si R est nettement supérieur à G et B (écart > 30).
    arr : tableau numpy de shape (..., 3 ou 4), valeurs int.
    """
    r = arr[..., 0].astype(int)
    g = arr[..., 1].astype(int)
    b = arr[..., 2].astype(int)
    return (r > g + 30) & (r > b + 30)


def find_middle_red_center(img: Image.Image, settings: PrintSettings) -> int | None:
    """
    Trouve la position x du centre de la ligne rouge du milieu dans l'image.
    Scanne uniquement les 2mm supérieurs de l'image où se trouve la bande mire.
    Retourne None si aucune ligne rouge n'est trouvée.
    """
    arr = np.array(img.convert("RGBA"))
    scan_rows = settings.mm_to_px_v(2.0)
    top_strip = arr[:scan_rows, :, :]
    red_pixels = is_red(top_strip)
    red_cols = red_pixels.any(axis=0)

    padded = np.concatenate(([False], red_cols, [False]))
    starts = np.where(~padded[:-1] & padded[1:])[0]
    ends   = np.where( padded[:-1] & ~padded[1:])[0] - 1
    runs = list(zip(starts.tolist(), ends.tolist()))

    logger.debug(f"Lignes rouges détectées ({len(runs)}) : {runs}")
    logger.debug(f"Largeur image : {img.width}px  |  centre image : {img.width // 2}px")

    if not runs:
        return None

    mid_idx = len(runs) // 2
    xs, xe = runs[mid_idx]
    center = (xs + xe) // 2
    logger.debug(f"Ligne rouge du milieu [idx={mid_idx}] : x={xs}–{xe}  |  centre={center}px")
    return center


def center_padding(
    img: Image.Image,
    settings: PrintSettings,
    debug_path: Path | None = None,
) -> Image.Image:
    """
    Détecte la ligne rouge du milieu (dans les 2mm supérieurs), calcule le padding
    transparent nécessaire pour la centrer horizontalement, applique le padding
    et retourne l'image centrée.

    Si debug_path est fourni, sauvegarde l'image intermédiaire avec un trait vert
    au centre pour vérification visuelle.
    """
    red_center = find_middle_red_center(img, settings)
    if red_center is None:
        logger.warning("Aucune ligne rouge trouvée — pas de centrage appliqué")
        return img

    w = img.width
    mid = image_center(img)

    if red_center == mid:
        logger.debug("Ligne rouge déjà centrée, pas de padding nécessaire")
        return img

    arr = np.array(img.convert("RGBA"))
    h = arr.shape[0]

    if red_center < mid:
        pad_left  = w - 2 * red_center
        pad_right = 0
    else:
        pad_left  = 0
        pad_right = 2 * red_center - w

    new_w = w + pad_left + pad_right
    new_arr = np.zeros((h, new_w, 4), dtype=arr.dtype)
    new_arr[:, pad_left:pad_left + w, :] = arr

    logger.debug(
        f"Centrage ligne rouge milieu : x={red_center}, centre image={mid}  |  "
        f"pad_left={pad_left}px  pad_right={pad_right}px  → nouvelle largeur={new_w}px"
    )

    result = Image.fromarray(new_arr, mode="RGBA")

    if debug_path is not None:
        debug_img = result.copy()
        draw = ImageDraw.Draw(debug_img)
        cx = image_center(debug_img)
        draw.line([(cx, 0), (cx, debug_img.height - 1)], fill=(0, 255, 0, 255), width=3)
        debug_img.save(str(debug_path))
        logger.debug(f"Image centrée sauvegardée : {debug_path}  (trait vert = centre x={cx})")

    return result
