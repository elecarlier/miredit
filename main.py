#!/usr/bin/env python3
from PIL import Image

from cli import parse_args
from models import PrintSettings
from mode1 import apply_mode1
from mode2 import apply_mode2


def run(args):
    Image.MAX_IMAGE_PIXELS = None

    settings = PrintSettings(
        lpi=args.LPI,
        hdpi=args.HDPI,
        vdpi=args.VDPI,
    )

    img = Image.open(args.image)
    mire = Image.open(args.mire)

    if args.mode == 1:
        result = apply_mode1(img, mire, settings, bord_mire_mm=args.bord_mire)
    elif args.mode == 2:
        result = apply_mode2(img, settings, cadre_mm=args.cadre)
        # result = apply_mode2(img, settings, cadre_mm=args.cadre, bord_image_mm=args.bord_image)

    out_path = args.output if args.output else args.image.with_stem(args.image.stem + "_mod").with_suffix(".png")
    result.save(str(out_path))
    print(f"Sauvegardé : {out_path}")


def main():
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
