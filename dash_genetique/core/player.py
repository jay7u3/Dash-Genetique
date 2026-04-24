"""Player (Bob): état + physique (saut, gravité, surface)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .obstacle import Obstacle


@dataclass
class Player:
    x: float
    y: float
    width: float
    height: float
    ground_y: float

    gravity: float = 0.05
    jump_speed: float = 2.5
    jump_height: int = 35

    velocity_y: float = 0.0
    jump_frame: int = 0
    jumping: bool = False
    alive: bool = True
    current_surface: float = field(init=False)
    sprite_index: int = 0

    def __post_init__(self) -> None:
        self.current_surface = self.ground_y

    def try_jump(self) -> None:
        """Déclenche le saut uniquement si Bob est au sol et pas déjà en l'air."""
        if not self.jumping and self.y >= self.current_surface:
            self.jumping = True
            self.jump_frame = 0
            self.velocity_y = 0.0

    def _apply_gravity(self) -> None:
        if self.y < self.current_surface:
            self.velocity_y += self.gravity
            self.y += min(self.velocity_y, self.current_surface - self.y)

    def _apply_jump(self) -> None:
        if self.jump_frame < self.jump_height:
            self.jump_frame += 1
            self.y -= self.jump_speed
        else:
            self.jumping = False

    def update_surface(self, obstacles: Iterable[Obstacle]) -> None:
        """Recalcule la surface courante (sol ou top d'un bloc "bs" sous Bob)."""
        new_surface = self.ground_y
        for o in obstacles:
            if o.type != "bs":
                continue
            if self.y + self.height <= o.y1:  # Bob au-dessus
                if o.x1 <= self.x <= o.x2 or o.x1 <= self.x + self.width <= o.x2:
                    new_surface = min(new_surface, o.y1 - self.height)
        self.current_surface = new_surface

    def step(self, obstacles: Iterable[Obstacle]) -> None:
        """Une frame de physique: gravité OU saut, puis mise à jour de la surface."""
        if self.jumping:
            self._apply_jump()
        else:
            self._apply_gravity()
        self.update_surface(obstacles)

    def __bool__(self) -> bool:
        return self.alive
