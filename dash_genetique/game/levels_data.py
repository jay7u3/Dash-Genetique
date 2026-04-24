"""Définitions statiques des niveaux (listes d'obstacles)."""

from __future__ import annotations

from typing import Callable, Dict, List

from ..core.obstacle import Obstacle


def _spike_up(x: float) -> Obstacle:
    return Obstacle(x, 250, x + 50, 300, "p", "pique")


def _spike_down(x: float, y: float = 100) -> Obstacle:
    return Obstacle(x, y, x + 50, y + 50, "p", "pique_reverse")


def _block(x: float, y: float) -> Obstacle:
    return Obstacle(x, y, x + 50, y + 50, "bs", "bloc")


def level_1() -> List[Obstacle]:
    """Niveau d'origine, reproduit fidèlement."""
    obs: List[Obstacle] = []
    obs.append(_spike_up(1000))
    obs.append(_spike_down(1000, 100))
    obs.append(_block(1000, 50))
    obs.append(_block(1000, 0))
    obs.append(_block(1050, 250))
    obs.append(_spike_up(1100))
    obs.append(_block(1320, 200))
    obs.append(_block(1500, 200))
    obs.append(_block(1550, 200))
    obs.append(_spike_down(1600, 100))
    obs.append(_block(1600, 50))
    obs.append(_block(1600, 0))
    obs.append(_spike_up(1580))
    obs.append(_spike_up(1820))
    obs.append(_spike_up(2050))
    obs.append(_block(2100, 250))
    obs.append(_spike_up(2150))
    obs.append(_spike_up(2200))
    obs.append(_spike_up(2250))
    obs.append(_block(2300, 250))
    obs.append(_block(2350, 250))
    obs.append(_block(2400, 250))
    obs.append(_spike_up(2450))
    obs.append(_block(2500, 250))
    obs.append(_block(2550, 250))
    obs.append(_block(2550, 50))
    obs.append(_block(2550, 0))
    obs.append(_block(2600, 250))
    obs.append(_spike_up(2650))
    obs.append(_spike_up(2700))
    obs.append(_spike_up(2750))
    obs.append(_block(2750, 200))
    obs.append(_spike_up(2800))
    obs.append(_spike_up(2850))
    obs.append(_spike_up(2900))
    obs.append(_block(2900, 150))
    obs.append(_spike_down(2950, 0))
    obs.append(_spike_up(3200))
    obs.append(_block(3250, 250))
    obs.append(_spike_down(3250, 100))
    obs.append(_block(3250, 50))
    obs.append(_block(3250, 0))
    return obs


def level_2() -> List[Obstacle]:
    """Niveau minimaliste pour test/démo."""
    return [_block(1000, 250)]


LEVELS: Dict[str, Callable[[], List[Obstacle]]] = {
    "level_1": level_1,
    "level_2": level_2,
}
