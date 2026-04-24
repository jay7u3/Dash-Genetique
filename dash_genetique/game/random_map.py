"""Génération de niveaux aléatoires par assemblage d'étapes pré-définies.

Les coordonnées des stages sont **relatives à 0** (recalées par ``random_level``).
Référentiel: y=0 en haut, y=300 = sol; les blocs et piques font 50x50.
"""

from __future__ import annotations

from random import Random
from typing import Dict, List

from ..core.obstacle import Obstacle
from .levels_data import _block, _spike_down, _spike_up


# --------------------------------------------------------------------------- Stages

def _stage_couloir() -> List[Obstacle]:
    """Couloir d'entrée: rampe + 3 piques au sol + plateforme + tunnel haut.

    Difficulté moyenne. Apprend à sauter au-dessus de groupes de piques.
    """
    return [
        _block(0, 250), _spike_up(50), _spike_up(100), _spike_up(150),
        _block(200, 200), _block(250, 200),
        _spike_down(450, 150), _block(450, 100), _block(450, 50), _block(450, 0),
    ]


def _stage_long_parcours() -> List[Obstacle]:
    """Long parcours en escalier ascendant avec pièges variés à la fin.

    Difficulté élevée. Mélange tous les types d'obstacles.
    """
    return [
        _block(0, 250), _spike_up(50), _spike_up(100), _spike_up(150),
        _block(250, 200),
        _block(500, 150),
        _block(750, 100),
        _block(850, 150),
        _spike_down(900, 30), _block(900, -20),
        _block(950, 200),
        _spike_down(1000, 0), _spike_up(1000),
        _block(1050, 250), Obstacle(1050, 200, 1100, 250, "p", "pique"),
    ]


def _stage_court() -> List[Obstacle]:
    """Stage très court d'introduction: tunnel + un pique."""
    return [
        _spike_up(0),
        _spike_down(0, 100), _block(0, 50), _block(0, 0),
        _block(50, 250), _spike_up(100),
    ]


# ------- NOUVEAUX STAGES -------------------------------------------------------

def _stage_trio_piques() -> List[Obstacle]:
    """Trois piques collés: doivent être sautés en un seul bond.

    Pattern simple mais demande un timing de saut anticipé.
    """
    return [
        _spike_up(0), _spike_up(50), _spike_up(100),
    ]


def _stage_escalier_montant() -> List[Obstacle]:
    """Escalier ascendant à 4 marches espacées.

    Apprend à enchaîner les sauts à fréquence régulière.
    """
    return [
        _block(0, 250),
        _block(120, 200),
        _block(240, 150),
        _block(360, 100),
    ]


def _stage_pyramide() -> List[Obstacle]:
    """Pyramide montante puis descendante.

    Cinq blocs disposés en triangle: monter trois marches puis redescendre deux.
    """
    return [
        _block(0, 250),
        _block(60, 200),
        _block(120, 150),
        _block(180, 200),
        _block(240, 250),
    ]


def _stage_ile_au_dessus_pique() -> List[Obstacle]:
    """Plateforme de départ, pique au sol, plateforme d'arrivée plus haute.

    Force un saut long depuis une plateforme vers une autre, par-dessus un pique.
    """
    return [
        _block(0, 250), _block(50, 250),       # plateforme de départ (sol)
        _spike_up(150),                          # pique à éviter
        _block(280, 200), _block(330, 200),    # plateforme d'arrivée plus haute
    ]


def _stage_tunnel_bas() -> List[Obstacle]:
    """Plafond bas obligatoire (rester au sol, ne PAS sauter) puis pique en sortie.

    Pattern intéressant car il requiert l'absence d'action puis une action précise.
    """
    return [
        _block(0, 100), _block(50, 100), _block(100, 100), _block(150, 100),
        _spike_up(350),
    ]


# --------------------------------------------------------------------------- API

STAGES: Dict[str, List[Obstacle]] = {
    "couloir": _stage_couloir(),
    "long_parcours": _stage_long_parcours(),
    "court": _stage_court(),
    "trio_piques": _stage_trio_piques(),
    "escalier_montant": _stage_escalier_montant(),
    "pyramide": _stage_pyramide(),
    "ile_au_dessus_pique": _stage_ile_au_dessus_pique(),
    "tunnel_bas": _stage_tunnel_bas(),
}


def default_stages() -> List[List[Obstacle]]:
    """Retourne une copie indépendante de tous les stages disponibles."""
    return [[o.clone() for o in stage] for stage in STAGES.values()]


def random_level(
    rng: Random,
    start_x: int,
    n_stages: int = 5,
    spacing: int = 400,
    stages: List[List[Obstacle]] | None = None,
) -> List[Obstacle]:
    """Concatène ``n_stages`` étapes aléatoires, espacées de ``spacing`` px.

    Args:
        rng: générateur aléatoire (pour reproductibilité).
        start_x: abscisse du premier obstacle.
        n_stages: nombre d'étapes assemblées.
        spacing: distance horizontale entre la fin d'un stage et le début du suivant.
        stages: stages personnalisés à utiliser (par défaut: ``default_stages()``).
    """
    if stages is None:
        stages = default_stages()
    if not stages:
        raise ValueError("random_level: aucun stage disponible")

    obstacles: List[Obstacle] = []
    cursor = start_x
    for _ in range(n_stages):
        stage = [o.clone() for o in rng.choice(stages)]
        for o in stage:
            o.shift(cursor)
        obstacles.extend(stage)
        cursor = max(o.x2 for o in stage) + spacing
    return obstacles


# Rétro-compatibilité: certaines parties du code (et des tests) référencent _stages
def _stages() -> List[List[Obstacle]]:
    return default_stages()
