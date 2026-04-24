"""Fonctions pures de mutation d'un arbre de neurones (pilotées par un ``Random``)."""

from __future__ import annotations

from random import Random
from typing import Tuple

from ..config import MutationConfig
from .neurons import LogicGate, Neuron, ObstacleDetector


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _mutate_detector(
    n: ObstacleDetector,
    rng: Random,
    cfg: MutationConfig,
    bounds: Tuple[int, int],
) -> Neuron:
    max_x, max_y = bounds
    if rng.random() < cfg.detector_coord_rate:
        n.offset_x = _clamp(
            n.offset_x + rng.randint(-cfg.coord_delta, cfg.coord_delta), 0, max_x
        )
        n.offset_y = _clamp(
            n.offset_y + rng.randint(-cfg.coord_delta, cfg.coord_delta), 0, max_y
        )

    if rng.random() < cfg.detector_type_rate:
        n.obstacle_type = "p" if n.obstacle_type == "bs" else "bs"

    if rng.random() < cfg.detector_to_gate_rate:
        return LogicGate(
            operator=rng.choice(("and", "or")),
            negation=bool(rng.randint(0, 1)),
            children=[n],
        )
    return n


def _mutate_gate(
    g: LogicGate,
    rng: Random,
    cfg: MutationConfig,
    bounds: Tuple[int, int],
) -> Neuron:
    max_x, max_y = bounds
    if rng.random() < cfg.gate_operator_flip_rate:
        g.operator = "or" if g.operator == "and" else "and"

    if rng.random() < cfg.gate_negation_flip_rate:
        g.negation = not g.negation

    if rng.random() < cfg.gate_add_child_rate:
        if rng.random() < cfg.gate_add_gate_vs_detector:
            g.children.append(LogicGate.random(rng, max_x, max_y))
        else:
            g.children.append(ObstacleDetector.random(rng, max_x, max_y))

    # Nouvelle liste d'enfants: on itère sur une copie et on réassigne le résultat
    new_children = []
    for child in list(g.children):
        if rng.random() < cfg.child_remove_rate:
            continue
        if rng.random() < cfg.child_mutate_rate:
            child = mutate(child, rng, cfg, bounds)  # réassignation explicite
        new_children.append(child)

    # Garde-fou: une porte sans enfant est dégénérée. On réinjecte au moins un détecteur.
    if not new_children:
        new_children.append(ObstacleDetector.random(rng, max_x, max_y))

    g.children = new_children
    return g


def mutate(
    n: Neuron,
    rng: Random,
    cfg: MutationConfig,
    bounds: Tuple[int, int],
) -> Neuron:
    """Mute un neurone. Retourne TOUJOURS le neurone résultant (peut avoir changé de type).

    ``bounds`` = (max_x, max_y) utilisés pour clamper les coordonnées des détecteurs.
    """
    if isinstance(n, ObstacleDetector):
        return _mutate_detector(n, rng, cfg, bounds)
    if isinstance(n, LogicGate):
        return _mutate_gate(n, rng, cfg, bounds)
    raise TypeError(f"Neurone inconnu: {type(n).__name__}")
