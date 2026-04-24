"""Tests de la détection de collision AABB."""

from dash_genetique.core.obstacle import Obstacle


def test_hits_overlap():
    o = Obstacle(100, 100, 200, 200, "p")
    assert o.hits(150, 150, 10, 10)
    assert o.hits(90, 90, 20, 20)  # coin haut-gauche inclus
    assert o.hits(190, 190, 20, 20)  # coin bas-droit inclus


def test_hits_no_overlap():
    o = Obstacle(100, 100, 200, 200, "p")
    assert not o.hits(0, 0, 10, 10)
    assert not o.hits(300, 300, 10, 10)
    assert not o.hits(0, 150, 100, 10)  # aligné touche-à-touche => exclu
    assert not o.hits(200, 150, 10, 10)  # aligné touche-à-touche => exclu


def test_hits_player_englobe_obstacle():
    """Le bug de l'ancien is_hit: si le joueur englobe complètement l'obstacle."""
    o = Obstacle(150, 150, 160, 160, "p")  # tout petit obstacle
    assert o.hits(100, 100, 200, 200)  # AABB complet détecte bien


def test_shift():
    o = Obstacle(100, 100, 200, 200, "p")
    o.shift(-50)
    assert (o.x1, o.x2) == (50, 150)


def test_clone_indep():
    o = Obstacle(100, 100, 200, 200, "p")
    c = o.clone()
    c.shift(10)
    assert o.x1 == 100
    assert c.x1 == 110
