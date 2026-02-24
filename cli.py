import argparse
from pathlib import Path


def parse_args():
    """Définition des arguments CLI."""
    parser = argparse.ArgumentParser(
        description="Modifications sur images lenticulaires (ajout mire, traits de repérage)."
    )

    parser.add_argument(
        "-i", "--image",
        type=Path,
        required=True,
        help="Chemin de l'image lenticulaire à modifier."
    )
    parser.add_argument(
        "-m", "--mire",
        type=Path,
        default=Path("mires_templates/720x360/40.png"),
        help="Template de mire à utiliser. (mires_templates/720x360/40.png par défaut)"
    )
    parser.add_argument(
        "--mode",
        type=int,
        choices=[1, 2],
        default=1,
        help=(
            "Mode 1: plaque plus grande — ajout bandes de mire haut/bas et traits noirs latéraux. "
            "Mode 2: modification des colonnes de bord existantes. "
            "(1 par défaut)"
        )
    )
    parser.add_argument(
        "--LPI",
        type=float,
        default=40.0,
        help="Linéature de la plaque en lignes/pouce. (40.0 par défaut)"
    )
    parser.add_argument(
        "--HDPI",
        type=int,
        default=720,
        help="Résolution horizontale d'impression. (720 par défaut)"
    )
    parser.add_argument(
        "--VDPI",
        type=int,
        default=360,
        help="Résolution verticale d'impression. (360 par défaut)"
    )
    parser.add_argument(
        "--bord_mire",
        type=float,
        default=4.0,
        help="[Mode 1] Hauteur de la bande de mire à ajouter en mm. (4.0 par défaut)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Chemin du fichier de sortie. Par défaut: <image>_mod.<ext>"
    )
    parser.add_argument(
        "-c", "--cadre",
        type=int,
        default=5,
        help="Cadre de mire crée par lenticular suite, 5mm par defaut"
    )
    parser.add_argument(
        "--bord_image",
        type=float,
        default=1.0,
        help="[Mode 2] Largeur en mm du trait noir conservé côté image sur les lignes latérales. (1.0 par défaut)"
    )

    return parser.parse_args()
