"""Agent: un couple (réseau de décision, joueur) évalué par sa fitness."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Optional

from ..core.player import Player
from .neurons import Neuron, ObstacleDetector


@dataclass
class Agent:
    network: Neuron
    player: Player
    fitness: float = 0.0
    size_cache: int = 0  # rempli à la fin de la génération
    sprite_index: int = 0

    @property
    def alive(self) -> bool:
        return self.player.alive

    @classmethod
    def new_random(
        cls,
        rng: Random,
        *,
        largeur: int,
        hauteur: int,
        bob_largeur: float,
        bob_hauteur: float,
        hauteur_sol: float,
    ) -> "Agent":
        player = Player(
            x=largeur // 2 - 25,
            y=hauteur_sol - bob_hauteur,
            width=bob_largeur,
            height=bob_hauteur,
            ground_y=hauteur_sol - bob_hauteur,
        )
        player.sprite_index = rng.randrange(7)
        return cls(
            network=ObstacleDetector.random(rng, largeur, hauteur),
            player=player,
            sprite_index=player.sprite_index,
        )

    def reset_player(
        self,
        rng: Optional[Random],
        *,
        largeur: int,
        hauteur: int,
        bob_largeur: float,
        bob_hauteur: float,
        hauteur_sol: float,
    ) -> None:
        player = Player(
            x=largeur // 2 - 25,
            y=hauteur_sol - bob_hauteur,
            width=bob_largeur,
            height=bob_hauteur,
            ground_y=hauteur_sol - bob_hauteur,
        )
        if rng is not None:
            player.sprite_index = rng.randrange(7)
        else:
            player.sprite_index = self.sprite_index
        self.player = player
        self.fitness = 0.0
        self.sprite_index = player.sprite_index

    def clone(self) -> "Agent":
        new = Agent(network=self.network.clone(), player=self.player)
        new.sprite_index = self.sprite_index
        return new

    def adjusted_fitness(self, size_penalty_weight: float) -> float:
        if size_penalty_weight <= 0.0:
            return self.fitness
        size = self.size_cache or self.network.size()
        return self.fitness - size_penalty_weight * size
