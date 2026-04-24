"""Réseau neuronal symbolique: arbre de portes logiques et détecteurs d'obstacles."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from random import Random
from typing import List, Sequence, Tuple

from ..core.obstacle import Obstacle, OBSTACLE_TYPES


class Neuron(ABC):
    """Interface d'un neurone: évaluable, clonable, mesurable."""

    @abstractmethod
    def evaluate(self, obstacles: Sequence[Obstacle], pos: Tuple[float, float]) -> bool:
        ...

    @abstractmethod
    def clone(self) -> "Neuron":
        ...

    @abstractmethod
    def size(self) -> int:
        """Nombre de noeuds dans le sous-arbre."""
        ...


@dataclass
class ObstacleDetector(Neuron):
    """Feuille: détecte un obstacle d'un certain type à un offset (dx, dy) de Bob."""

    offset_x: float
    offset_y: float
    obstacle_type: str  # 'p' ou 'bs'

    def evaluate(self, obstacles, pos):
        x = pos[0] + self.offset_x
        y = pos[1] + self.offset_y
        for o in obstacles:
            if o.type == self.obstacle_type and o.x1 < x < o.x2 and o.y1 < y < o.y2:
                return True
        return False

    def clone(self) -> "ObstacleDetector":
        return ObstacleDetector(self.offset_x, self.offset_y, self.obstacle_type)

    def size(self) -> int:
        return 1

    @classmethod
    def random(cls, rng: Random, max_x: int, max_y: int) -> "ObstacleDetector":
        return cls(
            offset_x=rng.randint(0, max_x // 2),
            offset_y=rng.randint(0, max_y),
            obstacle_type=rng.choice(OBSTACLE_TYPES),
        )

    def __str__(self) -> str:
        return f"DO({self.obstacle_type},[{self.offset_x:.0f},{self.offset_y:.0f}])"

    __repr__ = __str__


@dataclass
class LogicGate(Neuron):
    """Porte logique ET/OU, éventuellement négative, sur une liste d'enfants."""

    operator: str  # 'and' ou 'or'
    negation: bool
    children: List[Neuron] = field(default_factory=list)

    def evaluate(self, obstacles, pos):
        if not self.children:
            base = self.operator == "and"  # élément neutre: AND vide = True, OR vide = False
        elif self.operator == "and":
            base = True
            for c in self.children:
                if not c.evaluate(obstacles, pos):
                    base = False
                    break
        else:  # 'or' avec court-circuit
            base = False
            for c in self.children:
                if c.evaluate(obstacles, pos):
                    base = True
                    break
        return not base if self.negation else base

    def clone(self) -> "LogicGate":
        return LogicGate(
            operator=self.operator,
            negation=self.negation,
            children=[c.clone() for c in self.children],
        )

    def size(self) -> int:
        return 1 + sum(c.size() for c in self.children)

    @classmethod
    def random(cls, rng: Random, max_x: int, max_y: int) -> "LogicGate":
        return cls(
            operator=rng.choice(("and", "or")),
            negation=bool(rng.randint(0, 1)),
            children=[ObstacleDetector.random(rng, max_x, max_y)],
        )

    def __str__(self) -> str:
        neg = "!" if self.negation else ""
        op = "&" if self.operator == "and" else "|"
        return f"{neg}({op.join(str(c) for c in self.children)})"

    __repr__ = __str__
