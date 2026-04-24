"""Tests de la sélection par tournoi."""

from random import Random

from dash_genetique.ai.agent import Agent
from dash_genetique.ai.neurons import ObstacleDetector
from dash_genetique.core.player import Player
from dash_genetique.training.selection import tournament_pick


def _make(fitness: float) -> Agent:
    return Agent(
        network=ObstacleDetector(0, 0, "p"),
        player=Player(x=0, y=0, width=1, height=1, ground_y=0),
        fitness=fitness,
    )


def test_tournament_picks_best_of_sample():
    rng = Random(0)
    pool = [_make(f) for f in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
    # k = len(pool) => renvoie toujours le meilleur
    picked = tournament_pick(pool, len(pool), rng)
    assert picked.fitness == 10


def test_tournament_k_one_is_random():
    rng = Random(0)
    pool = [_make(f) for f in range(100)]
    picks = {tournament_pick(pool, 1, rng).fitness for _ in range(30)}
    assert len(picks) > 5  # au moins un peu d'aléa


def test_tournament_raises_on_empty():
    import pytest
    rng = Random(0)
    with pytest.raises(ValueError):
        tournament_pick([], 3, rng)
