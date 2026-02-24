#!/usr/bin/env python3
import logging
from pathlib import Path
from PIL import Image

from cli import parse_args
from models import PrintSettings
from mode1 import apply_mode1
from mode2 import apply_mode2

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "mires_templates"


def find_mire(lpi: float, hdpi: int, vdpi: int) -> Path:
    resolution_dir = TEMPLATES_DIR / f"{hdpi}x{vdpi}"
    mire_path = resolution_dir / f"{int(lpi)}.png"

    if not resolution_dir.exists():
        available = [d.name for d in TEMPLATES_DIR.iterdir() if d.is_dir()]
        raise FileNotFoundError(
            f"Aucun dossier de templates pour {hdpi}x{vdpi}.\n"
            f"Résolutions disponibles : {available}"
        )
    if not mire_path.exists():
        available = [f.stem for f in resolution_dir.glob("*.png")]
        raise FileNotFoundError(
            f"Aucune mire pour LPI={int(lpi)} à {hdpi}x{vdpi}.\n"
            f"LPI disponibles : {available}"
        )
    return mire_path


def run(args):
    Image.MAX_IMAGE_PIXELS = None

    settings = PrintSettings(lpi=args.LPI, hdpi=args.HDPI, vdpi=args.VDPI)
    logger.debug(f"Paramètres : LPI={args.LPI}, HDPI={args.HDPI}, VDPI={args.VDPI}")

    logger.info(f"Chargement image : {args.image}")
    img = Image.open(args.image)
    logger.debug(f"Taille image : {img.size}")

    mire_path = args.mire if args.mire else find_mire(args.LPI, args.HDPI, args.VDPI)
    logger.info(f"Mire : {mire_path}")
    mire = Image.open(mire_path)

    logger.info(f"Mode {args.mode}")
    if args.mode == 1:
        result = apply_mode1(img, mire, settings, bord_mire_mm=args.bord_mire)
    elif args.mode == 2:
        result = apply_mode2(img, settings, cadre_mm=args.cadre, trait_noir_mm=args.trait_noir_mm)

    out_name = args.output if args.output else (args.image.stem + "_mod.png")
    out_dir  = args.output_dir if args.output_dir else args.image.parent
    out_path = out_dir / out_name
    logger.info(f"Sauvegarde : {out_path}")
    result.save(str(out_path))
    logger.info("Terminé.")



def main():
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
