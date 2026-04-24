"""Opérateurs de sélection: tournoi principalement."""

from __future__ import annotations

from random import Random
from typing import Sequence

from ..ai.agent import Agent


def tournament_pick(pool: Sequence[Agent], k: int, rng: Random) -> Agent:
    """Sélection par tournoi: tire k candidats, retourne le meilleur par fitness."""
    if not pool:
        raise ValueError("tournament_pick: pool vide")
    k = max(1, min(k, len(pool)))
    candidates = rng.sample(list(pool), k) if k < len(pool) else list(pool)
    return max(candidates, key=lambda a: a.fitness)
