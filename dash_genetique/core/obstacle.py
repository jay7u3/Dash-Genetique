"""Obstacle: rectangle AABB avec type de collision et clé de sprite."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass


OBSTACLE_TYPES = ("p", "bs")  # 'p' = pique (létal), 'bs' = bloc surface (marchable)


@dataclass
class Obstacle:
    x1: float
    y1: float
    x2: float
    y2: float
    type: str  # 'p' ou 'bs'
    sprite_key: str = ""  # 'pique', 'pique_reverse', 'bloc', etc.

    def clone(self) -> "Obstacle":
        return dataclasses.replace(self)

    def shift(self, dx: float) -> None:
        self.x1 += dx
        self.x2 += dx

    def hits(self, x: float, y: float, w: float, h: float) -> bool:
        """Test de collision AABB complet entre le rectangle (x,y,w,h) et l'obstacle."""
        return (
            x < self.x2
            and x + w > self.x1
            and y < self.y2
            and y + h > self.y1
        )

    @property
    def p1(self):  # compat lecture (x1, y1)
        return (self.x1, self.y1)

    @property
    def p2(self):  # compat lecture (x2, y2)
        return (self.x2, self.y2)

    def __str__(self) -> str:
        return f"{self.type}({self.x1:.0f},{self.y1:.0f})->({self.x2:.0f},{self.y2:.0f})"
