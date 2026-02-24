# Documentation technique — miredit

## Vue d'ensemble

`miredit` modifie des images lenticulaires qui possèdent déjà un cadre généré par Lenticular Suite. Il opère en deux modes selon la taille de la plaque d'impression par rapport à l'image.

---

## Architecture

```
miredit/
├── main.py          # Point d'entrée, orchestration
├── cli.py           # Définition des arguments CLI (argparse)
├── models.py        # Dataclass PrintSettings + conversions px/mm
├── mode1.py         # Mode 1 : ajout de bandes mire + traits de repérage
├── mode2.py         # Mode 2 : modification du cadre Lenticular Suite
└── mires_templates/
    └── {HDPI}x{VDPI}/
        └── {LPI}.png
```

### `main.py`

Charge l'image d'entrée, résout le template de mire (automatiquement ou via `-m`), instancie `PrintSettings`, appelle le mode correspondant, et sauvegarde le résultat.

La fonction `find_mire()` cherche le fichier `mires_templates/{hdpi}x{vdpi}/{int(lpi)}.png` et lève une `FileNotFoundError` explicite si la résolution ou le LPI n'existe pas.

### `models.py`

```python
PrintSettings(lpi, hdpi, vdpi)
```

Méthodes utiles :

| Méthode | Description |
|---|---|
| `mm_to_px_h(mm)` | Convertit mm → pixels horizontaux (`mm * hdpi / 25.4`) |
| `mm_to_px_v(mm)` | Convertit mm → pixels verticaux (`mm * vdpi / 25.4`) |
| `line_frac_px(f)` | Fraction d'une ligne lenticulaire en px (`hdpi / lpi * f`) |

---

## Mode 1 — Plaque plus grande que l'image

L'image d'entrée possède un cadre Lenticular Suite. La plaque d'impression étant plus grande, on ajoute des bandes de mire supplémentaires en haut et en bas.

### Ce qu'il fait

1. Recadre le template de mire à la largeur de l'image et à la hauteur `bord_mire_mm`
2. Crée un canvas `largeur × (strip_h + h + strip_h)` et y colle : mire en haut, image (avec son cadre) au milieu, mire en bas
3. Dessine 4 traits de repérage verticaux de part et d'autre de l'image (actuellement en rouge pour visualisation)

### Valeurs codées en dur à connaître

| Valeur | Emplacement | Description |
|---|---|---|
| `margin = 3mm` | `mode1.py:42` | Marge latérale autour de l'image |
| `x1 = margin - 2mm` | `mode1.py:62` | Position du trait extérieur (bord gauche) |
| `x2 = margin - 1mm` | `mode1.py:63` | Position du trait intérieur |
| `w1 = 1/4 ligne` | `mode1.py:62` | Épaisseur du trait extérieur |
| `w2 = 1/6 ligne` | `mode1.py:64` | Épaisseur du trait intérieur |
| Couleur traits = rouge | `mode1.py:74-77` | Actuellement rouge (pour visualisation) — changer `red` en `black` pour la prod |

### Pour passer les traits de rouge à noir

Dans `mode1.py`, remplacer `fill=red` par `fill=black` sur les 4 `draw.rectangle(...)`.

---

## Mode 2 — Plaque même taille que l'image

L'image d'entrée possède un cadre Lenticular Suite. La plaque étant à la même taille, on modifie directement le cadre existant sans rien ajouter.

### Ce qu'il fait

Le cadre Lenticular Suite est composé de :
- Colonnes noires verticales sur les bords gauche et droit
- Lignes rouges verticales dans les bandes haut et bas

Le mode 2 :
1. Met en blanc la 2ème colonne noire depuis chaque bord
2. Met en noir la ligne rouge du milieu (cadre haut et bas)
3. Ajoute `trait_noir_mm` mm de noir sur la ligne rouge extérieure gauche et droite, du côté image

### Détection du cadre (`detect_frame_lines`)

**Colonnes noires :** scan horizontal à `y = h // 2` (milieu de l'image), sur les `cadre_px_h` premiers et derniers pixels en x.

**Lignes rouges :** scan horizontal à `y = cadre_px_v // 2` (milieu de la bande haut), sur toute la largeur.

**Seuils de couleur :**

| Couleur | Condition |
|---|---|
| Noir | `R < 30` et `G < 30` et `B < 30` |
| Rouge | `R > 150` et `G < 30` et `B < 30` |

Pour ajuster si des pixels ne sont pas détectés, modifier ces seuils dans `detect_frame_lines()` (lignes ~99-103 et ~126-130).

### Modifications appliquées

| Cible | Action | Index |
|---|---|---|
| Colonnes noires gauche | Mise en blanc | `black_left[1]` |
| Colonnes noires droite | Mise en blanc | `black_right[-2]` |
| Ligne rouge milieu | Mise en noir (cadre haut + bas) | `red_lines[n // 2]` |
| Ligne rouge extérieure gauche | `trait_noir_mm` mm en noir côté image | `red_lines[0]` |
| Ligne rouge extérieure droite | `trait_noir_mm` mm en noir côté image | `red_lines[-1]` |

### Points clés à modifier

- **Changer quelle colonne noire est effacée :** modifier l'index `[1]` / `[-2]` dans `apply_mode2()`
- **Changer quelle ligne rouge devient noire :** modifier `n // 2` pour un autre index
- **Changer les lignes rouges modifiées par `trait_noir_mm` :** actuellement `red_lines[0]` et `red_lines[-1]`
- **Côté du trait noir :** pour le cadre haut, "côté image" = bas de la bande (`cadre_px_v - bord_px_v` à `cadre_px_v`). Pour le cadre bas, = haut de la bande (`h - cadre_px_v` à `h - cadre_px_v + bord_px_v`)

---

## Templates de mire

Structure attendue :

```
mires_templates/
└── {HDPI}x{VDPI}/    ex: 720x360/
    └── {LPI}.png      ex: 40.png
```

Le fichier est sélectionné automatiquement depuis `--LPI`, `--HDPI`, `--VDPI`. Pour ajouter une nouvelle résolution ou un nouveau LPI, créer le dossier et y placer le fichier PNG correspondant.

---

## Logging

Le logging est configuré dans `main.py` via `logging.basicConfig(level=logging.INFO)`.

| Niveau | Contenu |
|---|---|
| `INFO` | Étapes principales : chargement, mode, modifications, sauvegarde |
| `DEBUG` | Détail pixel : positions des lignes détectées, dimensions intermédiaires |
| `WARNING` | Anomalies non bloquantes : aucune ligne rouge détectée, etc. |

Pour afficher les logs `DEBUG`, changer le niveau dans `main.py` :

```python
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
```
