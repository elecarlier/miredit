# Guide d'utilisation — miredit

Ce guide explique comment utiliser miredit pour préparer vos images lenticulaires avant impression. Pas besoin de connaissances en programmation.

---

## Ce que fait miredit

Lenticular Suite génère vos images avec un cadre de repérage (colonnes noires sur les bords, lignes rouges en haut et en bas). Selon la configuration de votre plaque d'impression, ce cadre doit être modifié différemment avant d'envoyer le fichier à l'impression. miredit automatise cette étape.

---

## Prérequis

Avant de commencer, vous avez besoin de :

- **Python 3.10 ou plus récent** — [télécharger sur python.org](https://www.python.org/downloads/)
- Les bibliothèques **Pillow** et **NumPy**, à installer une seule fois en ouvrant le Terminal et en tapant :

```
pip install pillow numpy
```

---

## Lancer l'outil

Ouvrez le **Terminal** (dans Applications > Utilitaires > Terminal), placez-vous dans le dossier `miredit`, puis tapez une commande selon votre cas.

---

## Choisir le bon mode

### Mode 1 — Plaque plus grande que l'image

Votre plaque d'impression est **plus grande** que l'image lenticulaire. miredit ajoute des bandes de mire en haut et en bas, et dessine des traits de repérage sur les côtés.

```
python main.py -i "mon_image.tif" --mode 1 --LPI 40 --bord_mire 4
```

Le fichier de sortie s'appellera `mon_image_HC.png`.

---

### Mode 2 — Plaque à la même taille que l'image

Votre plaque d'impression est **à la même taille** que l'image. miredit modifie directement le cadre existant : il efface une colonne noire de chaque côté et transforme les lignes rouges en traits noirs.

```
python main.py -i "mon_image.tif" --mode 2 --cadre 4
```

Le fichier de sortie s'appellera `mon_image_mod.png`.

---

### Mode 3 — Combiné

Votre plaque est **plus grande** que l'image **et** le cadre doit aussi être modifié. miredit effectue d'abord les modifications du Mode 2, puis ajoute les bandes de mire du Mode 1.

```
python main.py -i "mon_image.tif" --mode 3 --LPI 50 --cadre 4 --bord_mire 4
```

Le fichier de sortie s'appellera `mon_image_HC_mod.png`.

---

## Toutes les options disponibles

| Option | Valeur par défaut | Description |
|---|---|---|
| `-i` | *(obligatoire)* | Chemin vers l'image à traiter (TIF, PNG…) |
| `--mode` | `1` | Mode de traitement : 1, 2 ou 3 |
| `--LPI` | `50` | Linéature de votre plaque (lignes par pouce) |
| `--HDPI` | `720` | Résolution horizontale d'impression |
| `--VDPI` | `360` | Résolution verticale d'impression |
| `--cadre` | `4` | Taille du cadre configuré dans Lenticular Suite, en mm |
| `--bord_mire` | `4` | Hauteur de la bande de mire à ajouter, en mm (modes 1 et 3) |
| `--trait_noir` | `1` | Hauteur du trait noir à la jonction mire/image, en mm |
| `-o` | *(automatique)* | Nom du fichier de sortie |
| `-d` | *(même dossier)* | Dossier où enregistrer le fichier de sortie |

---

## Exemples courants

**Traiter une image en mode 1, enregistrer dans un dossier spécifique :**
```
python main.py -i "image.tif" --mode 1 --LPI 40 -d /Users/moi/Bureau/sortie
```

**Traiter une image en mode 2, choisir un nom de fichier :**
```
python main.py -i "image.tif" --mode 2 --cadre 4 -o "image_finale.png"
```

**Traiter une image en mode 2 avec une linéature de 50 LPI :**
```
python main.py -i "image.tif" --mode 2 --LPI 50 --cadre 4
```

---

## Fichiers de sortie

| Mode | Nom par défaut |
|---|---|
| Mode 1 | `<nom_image>_HC.png` |
| Mode 2 | `<nom_image>_mod.png` |
| Mode 3 | `<nom_image>_HC_mod.png` |

Si vous utilisez `-o`, le fichier portera le nom que vous avez indiqué.

---

## En cas de problème

**"Aucun dossier de templates pour…"**
La résolution demandée (HDPI × VDPI) n'a pas de template de mire disponible. Vérifiez que le dossier `mires_templates/{HDPI}x{VDPI}/` existe.

**"Aucune mire pour LPI=…"**
Le fichier de mire pour cette linéature n'existe pas dans le dossier de résolution. Ajoutez le fichier PNG correspondant dans `mires_templates/{HDPI}x{VDPI}/`.

**L'image de sortie ne s'affiche pas correctement**
Vérifiez que les valeurs `--LPI`, `--HDPI`, `--VDPI` et `--cadre` correspondent bien à vos réglages dans Lenticular Suite.
