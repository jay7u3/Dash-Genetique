"""Crossover d'arbres de neurones: échange d'un sous-arbre entre deux parents."""

from __future__ import annotations

from random import Random
from typing import List, Tuple

from .neurons import LogicGate, Neuron


def _collect_gates(node: Neuron, out: List[LogicGate]) -> None:
    if isinstance(node, LogicGate):
        out.append(node)
        for c in node.children:
            _collect_gates(c, out)


def crossover(parent_a: Neuron, parent_b: Neuron, rng: Random) -> Tuple[Neuron, Neuron]:
    """Retourne deux enfants clonés par échange d'un sous-arbre aléatoire.

    Si un des parents n'a aucune porte logique (feuille pure), on renvoie simplement
    des clones échangés (pas de point de recombinaison interne possible).
    """
    a = parent_a.clone()
    b = parent_b.clone()

    gates_a: List[LogicGate] = []
    gates_b: List[LogicGate] = []
    _collect_gates(a, gates_a)
    _collect_gates(b, gates_b)

    if not gates_a or not gates_b:
        return b, a  # échange simple

    ga = rng.choice(gates_a)
    gb = rng.choice(gates_b)
    if not ga.children or not gb.children:
        return a, b

    ia = rng.randrange(len(ga.children))
    ib = rng.randrange(len(gb.children))
    ga.children[ia], gb.children[ib] = gb.children[ib], ga.children[ia]
    return a, b
