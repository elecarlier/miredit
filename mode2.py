import numpy as np
from PIL import Image

from models import PrintSettings


# ─────────────────────────────────────────────
# Utilitaire : détection de plages dans un masque 1D
# ─────────────────────────────────────────────

def _find_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """
    Trouve les plages de pixels True consécutifs dans un masque 1D.
    Retourne une liste de (start, end) en indices inclusifs.
    """

    padded = np.concatenate(([False], mask, [False])) #on ajoute false au début et à la fin 

    # Indices où la valeur passe de False à True (début de plage)
    starts = np.where(~padded[:-1] &  padded[1:])[0]

    # Indices où la valeur passe de True à False (fin de plage, -1 car décalage du padding)
    ends   = np.where( padded[:-1] & ~padded[1:])[0] - 1

    return list(zip(starts.tolist(), ends.tolist()))


# ─────────────────────────────────────────────
# Détection et affichage des lignes du cadre
# ─────────────────────────────────────────────

def debug_red_scan(img: Image.Image, settings: PrintSettings, cadre_mm: float) -> None:
    """
    Diagnostic : cherche tous les pixels non-blanc et non-noir dans
    une bande verticale de ±50px autour du centre horizontal,
    sur toute la hauteur de l'image.
    Permet de localiser les vraies positions des lignes rouges.
    """
    arr = np.array(img.convert("RGBA"))
    h, w = arr.shape[:2]
    mid_x = w // 2

    # Scan horizontal à mi-hauteur du cadre haut, sur toute la largeur
    cadre_px_v = settings.mm_to_px_v(cadre_mm)
    mid_cadre_y = cadre_px_v // 2
    row = arr[mid_cadre_y, :, :]  # shape (W, 4)

    # Cherche tous les pixels ni blanc ni noir (= colorés, potentiellement rouges)
    is_white = (row[:, 0] > 200) & (row[:, 1] > 200) & (row[:, 2] > 200)
    is_black = (row[:, 0] <  30) & (row[:, 1] <  30) & (row[:, 2] <  30)
    colored_xs = np.where(~is_white & ~is_black)[0]

    print(f"\n=== DEBUG scan rouge — ligne y={mid_cadre_y} (mi-hauteur cadre haut) ===")
    if len(colored_xs) == 0:
        print("  Aucun pixel coloré trouvé.")
    else:
        for x in colored_xs:
            r, g, b, a = arr[mid_cadre_y, x]
            print(f"  x={x:5d}  R={r:3d} G={g:3d} B={b:3d} A={a:3d}")
    print()


def detect_frame_lines(
    img: Image.Image,
    settings: PrintSettings,
    cadre_mm: float,
) -> dict:
    """
    Analyse le cadre de mire (créé par Lenticular Suite) et retourne
    les positions de toutes les lignes détectées.

    Détecte :
    - Les lignes noires verticales dans les bandes latérales gauche et droite,
      en scannant une tranche horizontale au milieu de l'image.
    - Les lignes rouges horizontales dans les bandes haut et bas,
      en scannant une tranche verticale au centre horizontal de l'image.

    Retourne un dict avec les clés :
        "black_left"   : liste de (x_start, x_end) — coordonnées absolues
        "black_right"  : liste de (x_start, x_end) — coordonnées absolues
        "red_top"      : liste de (y_start, y_end) — coordonnées absolues
        "red_bottom"   : liste de (y_start, y_end) — coordonnées absolues
    """
    arr = np.array(img.convert("RGBA"))  # shape (H, W, 4), valeurs 0-255 
    h, w = arr.shape[:2]

    # Largeur/hauteur du cadre en pixels
    cadre_px_h = settings.mm_to_px_h(cadre_mm)  # pour les bords gauche/droite
    cadre_px_v = settings.mm_to_px_v(cadre_mm)  # pour les bords haut/bas

    mid_y = h // 2        # ligne horizontale de scan (milieu vertical de l'image)
    mid_cadre_y = cadre_px_v // 2  # ligne au milieu du cadre haut, pour scan rouge

    # ── Lignes noires gauche ──────────────────────────────────────────────────
    # On prend les pixels de la tranche horizontale à mid_y, dans les
    # cadre_px_h premières colonnes.
    # Un pixel est "noir" si R < 30 et G < 30 et B < 30.
    left_row = arr[mid_y, :cadre_px_h, :]          # shape (cadre_px_h, 4)
    black_left_mask = (
        (left_row[:, 0] < 30) &
        (left_row[:, 1] < 30) &
        (left_row[:, 2] < 30)
    )
    black_left = _find_runs(black_left_mask)        # positions relatives au bord gauche

#on obtiet un tableau True false true false true false
    # ── Lignes noires droite ──────────────────────────────────────────────────
    right_row = arr[mid_y, w - cadre_px_h:, :]     # shape (cadre_px_h, 4)
    black_right_mask = (
        (right_row[:, 0] < 30) &
        (right_row[:, 1] < 30) &
        (right_row[:, 2] < 30)
    )
    
    # On convertit en coordonnées absolues (origine = bord gauche de l'image)
    offset_r = w - cadre_px_h
    black_right = [(offset_r + s, offset_r + e) for s, e in _find_runs(black_right_mask)]

    # ── Lignes rouges (scan horizontal dans le cadre du HAUT) ────────────────────
    # Les lignes rouges sont des traits VERTICAUX (colonnes) placés au centre
    # horizontal de l'image, dans la zone du cadre haut.
    # On scanne horizontalement à mi-hauteur du cadre pour trouver leurs positions x.
    # Un pixel est "rouge" si R > 150 et G < 30 et B < 30 (rouge = R=219, G=0, B=0).
    top_row = arr[mid_cadre_y, :, :]        # toute la largeur à mi-hauteur du cadre
    red_mask = (
        (top_row[:, 0] > 150) &
        (top_row[:, 1] <  30) &
        (top_row[:, 2] <  30)
    )
    red_lines = _find_runs(red_mask)        # positions en x (coordonnées absolues)

    return {
        "black_left":  black_left,
        "black_right": black_right,
        "red_lines":   red_lines,
    }


def print_frame_analysis(lines: dict, settings: PrintSettings) -> None:
    """Affiche les positions des lignes détectées, en px et en mm."""

    def px_to_mm_h(px): return px * 25.4 / settings.hdpi
    def px_to_mm_v(px): return px * 25.4 / settings.vdpi

    print("\n=== ANALYSE DU CADRE DE MIRE ===\n")

    print(f"── Lignes noires — bord GAUCHE ({len(lines['black_left'])} lignes) ──")
    for i, (s, e) in enumerate(lines["black_left"]):
        w = e - s + 1
        print(f"  [{i}] x={s}–{e} px  |  largeur={w} px ({px_to_mm_h(w):.2f} mm)  |  bord à {px_to_mm_h(s):.2f} mm du bord gauche")

    print(f"\n── Lignes noires — bord DROIT ({len(lines['black_right'])} lignes) ──")
    for i, (s, e) in enumerate(lines["black_right"]):
        w = e - s + 1
        print(f"  [{i}] x={s}–{e} px  |  largeur={w} px ({px_to_mm_h(w):.2f} mm)  |  bord à {px_to_mm_h(s):.2f} mm du bord gauche")

    print(f"\n── Lignes rouges — cadre HAUT ({len(lines['red_lines'])} traits verticaux) ──")
    for i, (s, e) in enumerate(lines["red_lines"]):
        lw = e - s + 1
        print(f"  [{i}] x={s}–{e} px  |  largeur={lw} px ({px_to_mm_h(lw):.2f} mm)  |  centre à {px_to_mm_h((s+e)//2):.2f} mm du bord gauche")

    print()


# ─────────────────────────────────────────────
# Point d'entrée Mode 2
# ─────────────────────────────────────────────

def apply_mode2(
    img: Image.Image,
    settings: PrintSettings,
    cadre_mm: float,
) -> Image.Image:
    """
    Mode 2 — modification du cadre de mire existant (créé par Lenticular Suite).

    Modifications appliquées :
    - Met en blanc la première ligne noire complète du bord gauche.
    - Met en blanc la première ligne noire complète du bord droit.
    """
    # debug_red_scan(img, settings, cadre_mm)
    lines = detect_frame_lines(img, settings, cadre_mm)
    print_frame_analysis(lines, settings)

    # Travail sur un tableau numpy pour modifier les pixels directement
    arr = np.array(img.convert("RGBA"))
    white = (255, 255, 255, 255)

    # Deuxième ligne noire depuis le bord gauche = black_left[1]
    # black_left[0] (la plus proche du bord) est laissée intacte.
    x_start, x_end = lines["black_left"][1]
    arr[:, x_start:x_end + 1] = white
    print(f"→ Bord gauche : colonne x={x_start}–{x_end} mise en blanc")

    # Deuxième ligne noire depuis le bord droit = black_right[-2]
    # black_right[-1] (la plus proche du bord) est laissée intacte.
    x_start, x_end = lines["black_right"][-2]
    arr[:, x_start:x_end + 1] = white
    print(f"→ Bord droit  : colonne x={x_start}–{x_end} mise en blanc")

    

    return Image.fromarray(arr, mode="RGBA")

