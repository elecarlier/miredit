from dataclasses import dataclass


@dataclass
class PrintSettings:
    lpi: float   # linéature (lignes par pouce)
    hdpi: int    # résolution horizontale d'impression
    vdpi: int    # résolution verticale d'impression

    @property
    def px_per_line(self) -> float:
        """Largeur d'une ligne lenticulaire en pixels (horizontal)."""
        return self.hdpi / self.lpi

    def mm_to_px_h(self, mm: float) -> int:
        """Convertit des millimètres en pixels horizontaux."""
        return round(mm * self.hdpi / 25.4)

    def mm_to_px_v(self, mm: float) -> int:
        """Convertit des millimètres en pixels verticaux."""
        return round(mm * self.vdpi / 25.4)

    def line_frac_px(self, fraction: float) -> int:
        """Largeur en pixels d'une fraction de ligne lenticulaire. Ex: line_frac_px(1/4)"""
        return round(self.px_per_line * fraction)
