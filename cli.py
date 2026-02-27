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
        default=None,
        help="Template de mire à utiliser. Par défaut: détecté automatiquement depuis mires_templates/{HDPI}x{VDPI}/{LPI}.png"
    )
    parser.add_argument(
        "--mode",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help=(
            "Mode 1: plaque plus grande — ajout bandes de mire haut/bas et traits noirs latéraux. "
            "Mode 2: modification des colonnes de bord existantes. " \
            "Mode 3: mode 1 + modification des bords"
            "(1 par défaut)"
        )
    )
    parser.add_argument(
        "--LPI",
        type=float,
        default=50.0,
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
        type=str,
        default=None,
        help="Nom du fichier de sortie (sans chemin). Par défaut: <image>_mod.png"
    )
    parser.add_argument(
        "-d", "--output_dir",
        type=Path,
        default=None,
        help="Dossier de sortie. Par défaut: même dossier que l'image d'entrée."
    )
    parser.add_argument(
        "-c", "--cadre",
        type=int,
        default=4,
        help="Cadre de mire crée par lenticular suite, 4mm par defaut"
    )
    parser.add_argument(
        "--trait_noir_mm",
        type=float,
        default=1.0,
        help="Hauteur en mm du trait noir à la jonction mire/image (modes 1 et 2). (1.0 par défaut)"
    )

    return parser.parse_args()
