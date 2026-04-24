"""Rendu pygame (séparé de la simulation pour permettre un mode headless)."""

from __future__ import annotations

import sys
from typing import Sequence

import pygame

from ..ai.agent import Agent
from ..resources import Resources
from .level import Level


class Renderer:
    """Rend un Level et ses agents sur une surface pygame."""

    def __init__(self, resources: Resources, fps: int = 160):
        self.resources = resources
        self.fps = fps
        self.screen = pygame.display.set_mode((resources.largeur, resources.hauteur))
        self.font = pygame.font.Font("freesansbold.ttf", 16)
        self.clock = pygame.time.Clock()
        self.sol1_pos = 0
        self.sol2_pos = resources.largeur

    def _scroll_ground(self, speed: float) -> None:
        if self.sol1_pos <= -self.resources.largeur:
            self.sol1_pos = self.resources.largeur
        if self.sol2_pos <= -self.resources.largeur:
            self.sol2_pos = self.resources.largeur
        self.sol1_pos -= speed
        self.sol2_pos -= speed

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

    def render(
        self,
        level: Level,
        agents: Sequence[Agent],
        *,
        generation: int = 0,
        previous_score: float = 0.0,
    ) -> None:
        self._handle_events()

        self.screen.blit(self.resources.fond, (0, 0))

        gen_txt = self.font.render(f"Generation: {generation}", True, (255, 255, 255))
        score_txt = self.font.render(
            f"Score: {previous_score:.0f}", True, (255, 255, 255)
        )
        self.screen.blit(gen_txt, (0, 0))
        self.screen.blit(score_txt, (0, gen_txt.get_size()[1]))

        for o in level.visible_obstacles(stop_on_out=False):
            sprite = self.resources.sprites.get(o.sprite_key)
            if sprite is not None:
                self.screen.blit(sprite, (o.x1, o.y1))

        for agent in agents:
            p = agent.player
            if not p.alive:
                continue
            img = self.resources.bob_pics[p.sprite_index % len(self.resources.bob_pics)]
            self.screen.blit(img, (p.x, p.y))

        self._scroll_ground(level.speed)
        self.screen.blit(self.resources.sol, (self.sol1_pos, self.resources.hauteur_sol))
        self.screen.blit(self.resources.sol, (self.sol2_pos, self.resources.hauteur_sol))

        pygame.display.update()
        self.clock.tick(self.fps)
