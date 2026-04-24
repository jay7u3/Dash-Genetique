"""Chargement des ressources graphiques.

Permet un mode ``headless`` (pas de fenêtre) via ``SDL_VIDEODRIVER=dummy``.
Les constantes de taille (LARGEUR, HAUTEUR, HAUTEUR_SOL) sont dérivées des sprites
pour rester fidèles aux assets existants.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import pygame


@dataclass
class Resources:
    largeur: int
    hauteur: int
    hauteur_sol: int
    bob_largeur: int
    bob_hauteur: int

    bob_pics: List["pygame.Surface"]
    fond: "pygame.Surface"
    sol: "pygame.Surface"
    sprites: Dict[str, "pygame.Surface"]  # clés: 'pique', 'pique_reverse', 'bloc'

    _headless: bool = False

    @classmethod
    def load(cls, headless: bool = False, assets_dir: str = "ressources") -> "Resources":
        """Charge les sprites. En mode headless, utilise le driver SDL 'dummy'."""
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        if not pygame.get_init():
            pygame.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1, 1))
        if not pygame.font.get_init():
            pygame.font.init()

        def _p(name: str) -> str:
            return os.path.join(assets_dir, name)

        bob_names = ["violet", "bleu", "gris", "jaune", "noir", "rouge", "vert"]
        bob_pics = [pygame.image.load(_p(f"bob_{c}.png")) for c in bob_names]
        fond = pygame.image.load(_p("fond.png"))
        sol = pygame.image.load(_p("sol.png"))
        pique = pygame.image.load(_p("pique.png"))
        bloc = pygame.image.load(_p("bloc.png"))
        pique_reverse = pygame.transform.rotate(pique, 180)

        largeur, hauteur = fond.get_size()
        hauteur_sol = hauteur - sol.get_size()[1]
        bob_largeur, bob_hauteur = bob_pics[0].get_size()

        return cls(
            largeur=largeur,
            hauteur=hauteur,
            hauteur_sol=hauteur_sol,
            bob_largeur=bob_largeur,
            bob_hauteur=bob_hauteur,
            bob_pics=bob_pics,
            fond=fond,
            sol=sol,
            sprites={"pique": pique, "pique_reverse": pique_reverse, "bloc": bloc},
            _headless=headless,
        )
