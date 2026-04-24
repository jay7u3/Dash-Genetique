"""Tests du crossover (échange de sous-arbre)."""

from random import Random

from dash_genetique.ai.crossover import crossover
from dash_genetique.ai.neurons import LogicGate, ObstacleDetector


def test_crossover_independence():
    rng = Random(0)
    a = LogicGate("and", False, [
        ObstacleDetector(1, 1, "p"),
        ObstacleDetector(2, 2, "bs"),
    ])
    b = LogicGate("or", True, [
        ObstacleDetector(9, 9, "p"),
        ObstacleDetector(8, 8, "bs"),
    ])

    c1, c2 = crossover(a, b, rng)
    # Les enfants sont des CLONES => muter l'un ne doit pas toucher l'autre ni les parents
    assert c1 is not a
    assert c2 is not b
    # Parents inchangés
    assert a.children[0].offset_x == 1
    assert b.children[0].offset_x == 9


def test_crossover_pure_detectors():
    rng = Random(0)
    a = ObstacleDetector(1, 1, "p")
    b = ObstacleDetector(9, 9, "bs")
    c1, c2 = crossover(a, b, rng)
    # échange simple: c1 issu de b, c2 issu de a
    assert isinstance(c1, ObstacleDetector)
    assert isinstance(c2, ObstacleDetector)
