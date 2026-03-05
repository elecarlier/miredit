# miredit

![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-1.24+-013243?logo=numpy&logoColor=white)
![Pillow](https://img.shields.io/badge/pillow-10+-hotpink?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-green)

**CLI image processing tool for lenticular print preparation.**

> Vous cherchez un guide d'utilisation en français, sans jargon technique ? → [GUIDE.md](GUIDE.md)

Lenticular printing requires precise registration marks and mire (test chart) strips so that the print aligns exactly with the lenticular lens sheet. `miredit` automates the pixel-level modifications needed on images exported from [Lenticular Suite](https://www.lenticularsuite.com/), adapting them for three plate configurations.

---

## Context

Lenticular Suite generates print-ready images with a registration frame — black columns on the sides and red alignment lines on the top and bottom. Depending on plate sizing and workflow, those marks need different adjustments before going to press. This tool handles that step programmatically, preserving ICC color profiles and print DPI metadata throughout.

---

## Modes

**Mode 1 — Oversized plate**
Adds mire strips above and below the image, and draws lateral registration marks. Used when the print plate is larger than the lenticular image.

**Mode 2 — Same-size plate**
Modifies the existing frame in place: erases one black column per side and converts the red alignment lines into black registration marks.

**Mode 3 — Combined**
Runs Mode 2's frame modifications first, then applies Mode 1's mire strip addition. For oversized plates where the frame also needs adjustment.

---

## Technical stack

| | |
|---|---|
| **Python** | CLI tooling with `argparse`, structured logging |
| **NumPy** | Pixel-level array manipulation — frame detection, column/line indexing, color thresholding |
| **Pillow** | Image I/O, compositing, drawing, ICC profile and DPI metadata handling |

---

## Installation

```bash
git clone --recurse-submodules https://github.com/elecarlier/print_calibrator.git
cd miredit
pip install pillow numpy
```

---

## Usage

```bash
python main.py -i <image> --mode <1|2|3> [options]
```

### Common arguments

| Argument | Default | Description |
|---|---|---|
| `-i`, `--image` | *(required)* | Input lenticular image (TIF, PNG…) |
| `--mode` | `1` | Processing mode (see above) |
| `--LPI` | `50.0` | Screen ruling in lines per inch |
| `--HDPI` | `720` | Horizontal print resolution (dpi) |
| `--VDPI` | `360` | Vertical print resolution (dpi) |
| `-o`, `--output` | `<input>_mod.png` | Output filename |
| `-d`, `--output_dir` | same as input | Output folder |
| `-m`, `--mire` | *(auto-detected)* | Override mire template path |

### Modes 1 & 3

| Argument | Default | Description |
|---|---|---|
| `--bord_mire` | `4.0` | Height of the mire strip to add, in mm |
| `--trait_noir_mm` | `1.0` | Height (mm) of the black registration mark at the image/mire boundary |

### Modes 2 & 3

| Argument | Default | Description |
|---|---|---|
| `-c`, `--cadre` | `4` | Frame size as configured in Lenticular Suite (mm) |
| `--trait_noir_mm` | `1.0` | Height (mm) of the black mark on the outer red lines at the image edge |

---

## Examples

```bash
# Mode 1 — add mire strips for a larger plate
python main.py -i "image.tif" --mode 1 --LPI 40 --bord_mire 4

# Mode 2 — modify existing frame in place
python main.py -i "image.tif" --mode 2 --cadre 4 -d /output

# Mode 2 — custom output name, 50 LPI
python main.py -i "image.tif" --mode 2 --LPI 50 -o "result.png" -d /output

# Mode 3 — combined: adjust frame then add mire strips
python main.py -i "image.tif" --mode 3 --LPI 50 --cadre 4 --bord_mire 4 -d /output
```

---

## Project structure

```
miredit/
├── main.py              # Entry point and orchestration
├── cli.py               # CLI argument definitions (argparse)
├── models.py            # PrintSettings dataclass + px/mm conversions
├── mode1.py             # Mode 1: mire strip addition + registration marks
├── mode2.py             # Mode 2 & 3: in-place frame modification
├── center_padding.py    # Pre-processing: centers the image if needed
└── mires_templates/     # PNG templates, auto-selected by LPI/DPI (gitignored)
    └── {HDPI}x{VDPI}/
        └── {LPI}.png
```

---

## Mire templates

Templates are auto-selected based on `--LPI`, `--HDPI`, and `--VDPI`, from the shared folder at the repo root:

```
mires_templates/
└── {HDPI}x{VDPI}/    e.g. 720x360/
    ├── 20.png
    ├── 28.png
    ├── 40.png
    └── 50.png
```

To add support for a new resolution or LPI, drop the corresponding PNG in the right subfolder.

---

## Logging

Steps are logged to stdout at `INFO` level. For pixel-level debug output (detected line positions, intermediate dimensions), set `level=logging.DEBUG` in `main.py`.
