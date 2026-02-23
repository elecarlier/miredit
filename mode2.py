from PIL import Image

from models import PrintSettings


def apply_mode2(img: Image.Image, settings: PrintSettings) -> Image.Image:
    """
    Mode 2 — modification des colonnes de bord noirs existants.

    À définir. Modifications prévues sur les colonnes noires latérales
    générées par Lenticular Suite (ex: mettre l'avant-dernière colonne
    de chaque côté en blanc, etc.).
    """
    raise NotImplementedError("Mode 2 à implémenter.")
