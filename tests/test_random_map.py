"""Tests des stages et de la génération aléatoire de niveaux."""

from random import Random

import pytest

from dash_genetique.ai.agent import Agent
from dash_genetique.ai.neurons import LogicGate, ObstacleDetector
from dash_genetique.core.obstacle import OBSTACLE_TYPES
from dash_genetique.core.player import Player
from dash_genetique.game.level import Level
from dash_genetique.game.random_map import (
    STAGES,
    default_stages,
    random_level,
)


# ------------------------------------------------------------ Stages individuels


def test_at_least_5_new_stages_total_8():
    """Le module doit exposer au moins 8 stages (3 historiques + 5 nouveaux)."""
    assert len(STAGES) >= 8
    expected_new = {
        "trio_piques",
        "escalier_montant",
        "pyramide",
        "ile_au_dessus_pique",
        "tunnel_bas",
    }
    assert expected_new.issubset(STAGES.keys())


@pytest.mark.parametrize("name", list(STAGES.keys()))
def test_stage_well_formed(name):
    """Chaque stage: non vide, types valides, géométrie cohérente."""
    stage = STAGES[name]
    assert len(stage) > 0, f"stage '{name}' est vide"
    for o in stage:
        assert o.type in OBSTACLE_TYPES, f"type invalide: {o.type!r}"
        assert o.x2 > o.x1, f"géométrie x invalide dans {name}: {o}"
        assert o.y2 > o.y1, f"géométrie y invalide dans {name}: {o}"
        assert o.sprite_key in {"pique", "pique_reverse", "bloc"}


def test_default_stages_returns_independent_clones():
    """default_stages() doit retourner des copies, pas des références partagées."""
    a = default_stages()
    b = default_stages()
    a[0][0].shift(1234)
    assert b[0][0].x1 != a[0][0].x1


# ---------------------------------------------------------- random_level


def test_random_level_obstacles_after_start_x():
    rng = Random(0)
    start = 1000
    obstacles = random_level(rng, start_x=start, n_stages=4)
    assert all(o.x1 >= start for o in obstacles)


def test_random_level_is_sorted_by_x():
    rng = Random(7)
    obstacles = random_level(rng, start_x=500, n_stages=5)
    xs = [o.x1 for o in obstacles]
    assert xs == sorted(xs), "les obstacles doivent être dans l'ordre des x croissants"


def test_random_level_deterministic_with_seed():
    a = random_level(Random(42), start_x=1000, n_stages=4)
    b = random_level(Random(42), start_x=1000, n_stages=4)
    assert len(a) == len(b)
    for oa, ob in zip(a, b):
        assert (oa.x1, oa.y1, oa.x2, oa.y2, oa.type, oa.sprite_key) == (
            ob.x1, ob.y1, ob.x2, ob.y2, ob.type, ob.sprite_key,
        )


def test_random_level_different_seeds_produce_different_layouts():
    a = random_level(Random(1), start_x=1000, n_stages=6)
    b = random_level(Random(2), start_x=1000, n_stages=6)
    coords_a = [(o.x1, o.y1, o.type) for o in a]
    coords_b = [(o.x1, o.y1, o.type) for o in b]
    assert coords_a != coords_b


def test_random_level_respects_stage_spacing():
    """Entre deux stages successifs, l'écart doit être >= spacing."""
    rng = Random(3)
    spacing = 400
    obstacles = random_level(rng, start_x=1000, n_stages=4, spacing=spacing)
    sorted_obs = sorted(obstacles, key=lambda o: o.x1)
    # On détecte les "trous" larges (>= spacing) qui marquent les frontières de stages
    gaps = []
    for prev, cur in zip(sorted_obs, sorted_obs[1:]):
        gap = cur.x1 - prev.x2
        if gap >= spacing - 1:
            gaps.append(gap)
    assert len(gaps) >= 1, "aucune frontière de stage détectée"


def test_random_level_custom_stages():
    """On peut passer ses propres stages (liste réduite => map prévisible)."""
    custom = [STAGES["trio_piques"]]
    obstacles = random_level(Random(0), start_x=0, n_stages=2, spacing=100, stages=custom)
    # 2 stages * 3 piques = 6 obstacles, tous des piques
    assert len(obstacles) == 6
    assert all(o.type == "p" for o in obstacles)


def test_random_level_empty_stages_raises():
    with pytest.raises(ValueError):
        random_level(Random(0), start_x=0, n_stages=2, stages=[])


# ---------------------------------------------------------- Simulabilité


def _runnable_agent() -> Agent:
    """Un agent qui saute en permanence (force la couverture des collisions)."""
    player = Player(x=400, y=250, width=50, height=50, ground_y=250)
    # Détecteur dont la zone englobe Bob => True dès qu'un obstacle est devant lui
    network = LogicGate("or", False, [
        ObstacleDetector(0, 0, "p"),
        ObstacleDetector(0, 0, "bs"),
    ])
    return Agent(network=network, player=player)


@pytest.mark.parametrize("name", list(STAGES.keys()))
def test_each_stage_simulatable_alone(name):
    """Chaque stage tout seul, recalé en x=1000, doit pouvoir tourner sans crash."""
    stage = [o.clone() for o in STAGES[name]]
    for o in stage:
        o.shift(1000)
    level = Level(stage, largeur=800, hauteur=400, hauteur_sol=300)
    agent = _runnable_agent()
    level.run([agent], max_frames=5000)
    assert level.frame > 0


def test_random_level_runnable_in_simulation():
    """Une map aléatoire complète doit pouvoir être simulée."""
    rng = Random(0)
    obstacles = random_level(rng, start_x=1000, n_stages=4, spacing=400)
    level = Level(obstacles, largeur=800, hauteur=400, hauteur_sol=300)
    agent = _runnable_agent()
    level.run([agent], max_frames=10000)
    # L'agent a forcément avancé d'au moins quelques frames
    assert agent.fitness > 0


def test_random_level_via_cli_factory_keyword():
    """Le CLI route ``--level random`` via cli._level_factory: doit fonctionner."""
    from dash_genetique.cli import _level_factory

    rng = Random(99)
    factory = _level_factory("random", rng)
    obstacles = factory()
    assert len(obstacles) > 0
    assert all(o.x1 >= 1000 for o in obstacles)
