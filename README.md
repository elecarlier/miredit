# miredit

![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-1.24+-013243?logo=numpy&logoColor=white)
![Pillow](https://img.shields.io/badge/pillow-10+-hotpink)

**CLI image processing tool for lenticular print preparation.**

Lenticular printing requires precise registration marks and mire (test chart) strips so that the print can be aligned exactly with the lenticular lens sheet. `miredit` automates the pixel-level modifications needed on images exported from [Lenticular Suite](https://www.lenticularsuite.com/), adapting them for two common plate configurations.

---

## What it does

Lenticular Suite generates images with a frame of registration marks — black columns on the sides and red alignment lines on the top and bottom borders. Depending on whether the print plate is the same size as the image or larger, different adjustments are needed.

**Mode 1 — Oversized plate**
Adds mire strips above and below the image and draws lateral registration marks for plates larger than the lenticular image.

**Mode 2 — Same-size plate**
Modifies the existing Lenticular Suite frame in place: erases one black column per side and converts the red alignment lines into black registration marks.

---

## Technical stack

- **Python** — CLI tooling with `argparse`, structured logging
- **NumPy** — pixel-level array manipulation for frame detection and modification
- **Pillow** — image I/O, compositing, drawing

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
python main.py -i <image> --mode <1|2> [options]
```

### Common arguments

| Argument | Default | Description |
|---|---|---|
| `-i`, `--image` | *(required)* | Input lenticular image (TIF, PNG…) |
| `--mode` | `1` | `1` = oversized plate · `2` = same-size plate |
| `--LPI` | `40.0` | Screen ruling in lines per inch |
| `--HDPI` | `720` | Horizontal print resolution (dpi) |
| `--VDPI` | `360` | Vertical print resolution (dpi) |
| `-o`, `--output` | `<input>_mod.png` | Output filename |
| `-d`, `--output_dir` | same as input | Output folder |
| `-m`, `--mire` | *(auto-detected)* | Override mire template path |

### Mode 1 options

| Argument | Default | Description |
|---|---|---|
| `--bord_mire` | `4.0` | Height of the mire strip to add, in mm |

### Mode 2 options

| Argument | Default | Description |
|---|---|---|
| `-c`, `--cadre` | `5` | Frame size as configured in Lenticular Suite (mm) |
| `--trait_noir_mm` | `1.0` | Height (mm) of the black mark on outer red lines at the image edge |

---

## Examples

```bash
# Mode 1 — add mire strips for a larger plate
python main.py -i "image.tif" --mode 1 --LPI 40 --bord_mire 4

# Mode 2 — modify existing frame, output to a specific folder
python main.py -i "image.tif" --mode 2 --cadre 5 -d /output

# Mode 2 — custom output name, 50 LPI
python main.py -i "image.tif" --mode 2 --LPI 50 -o "result.png" -d /output
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

To add support for a new resolution or LPI, drop the corresponding PNG in the right folder.

---

## Logging

Steps are logged to stdout at `INFO` level. For pixel-level debug output, set `level=logging.DEBUG` in `main.py`.
