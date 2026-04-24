"""Tests de la boucle de simulation (score continu, bonus de fin)."""

from dash_genetique.ai.agent import Agent
from dash_genetique.ai.neurons import ObstacleDetector
from dash_genetique.core.obstacle import Obstacle
from dash_genetique.core.player import Player
from dash_genetique.game.level import Level


def _make_agent(network=None):
    player = Player(x=100, y=250, width=50, height=50, ground_y=250)
    return Agent(
        network=network or ObstacleDetector(0, 0, "p"),
        player=player,
    )


def test_score_updated_every_frame_even_without_death():
    """Regression: un agent qui SURVIT au niveau doit avoir une fitness > 0."""
    # Pas d'obstacle: l'agent survit forcément.
    level = Level([Obstacle(100000, 100000, 100001, 100001, "p")],
                  largeur=800, hauteur=400, hauteur_sol=300)
    agent = _make_agent()
    level.run([agent], max_frames=100)
    assert agent.alive
    assert agent.fitness > 0  # était = 0 dans l'ancien code


def test_score_frozen_at_death():
    """À la mort, la fitness ne continue pas de grimper."""
    level = Level([Obstacle(120, 240, 180, 280, "p")],  # sur le chemin
                  largeur=800, hauteur=400, hauteur_sol=300, speed=2.5)
    agent = _make_agent()
    level.run([agent], max_frames=500)
    fitness_at_death = agent.fitness
    assert not agent.alive
    # On avance encore: fitness ne doit pas bouger
    for _ in range(20):
        level.step([agent])
    assert agent.fitness == fitness_at_death


def test_aabb_collision_via_level():
    """L'obstacle qui englobe Bob déclenche bien la mort (bug AABB corrigé)."""
    # Obstacle très large et haut qui contient le joueur dès le début
    level = Level([Obstacle(50, 200, 250, 350, "p")],
                  largeur=800, hauteur=400, hauteur_sol=300)
    agent = _make_agent()
    level.step([agent])
    assert not agent.alive
