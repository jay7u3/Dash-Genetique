"""Level: boucle de simulation pure (pas de pygame ici)."""

from __future__ import annotations

from typing import Iterator, List, Sequence

from ..ai.agent import Agent
from ..core.obstacle import Obstacle


class Level:
    def __init__(
        self,
        obstacles: Sequence[Obstacle],
        *,
        largeur: int,
        hauteur: int,
        hauteur_sol: int,
        speed: float = 2.5,
    ) -> None:
        self.obstacles: List[Obstacle] = sorted(
            [o.clone() for o in obstacles], key=lambda o: o.x1
        )
        self.largeur = largeur
        self.hauteur = hauteur
        self.hauteur_sol = hauteur_sol
        self.speed = speed

        self.frame = 0
        self.distance = 0.0
        self._current_idx = 0

    def visible_obstacles(self, stop_on_out: bool = True) -> Iterator[Obstacle]:
        """Yielde les obstacles encore pertinents (dans ou proches du champ de vision)."""
        i = self._current_idx
        while i < len(self.obstacles):
            o = self.obstacles[i]
            if o.x2 < 0:
                self._current_idx = i + 1
                i += 1
                continue
            if stop_on_out and o.x1 > self.largeur:
                return
            yield o
            i += 1

    def active_obstacles(self) -> List[Obstacle]:
        return list(self.visible_obstacles(stop_on_out=True))

    def finished(self, agents: Sequence[Agent]) -> bool:
        if not any(a.alive for a in agents):
            return True
        if not self.obstacles or self.obstacles[-1].x2 <= 0:
            return True
        return False

    def step(self, agents: Sequence[Agent]) -> None:
        """Avance d'une frame la simulation pour tous les agents."""
        for o in self.visible_obstacles(stop_on_out=False):
            o.shift(-self.speed)

        self.distance += self.speed
        self.frame += 1

        visible = self.active_obstacles()

        for agent in agents:
            p = agent.player
            if not p.alive:
                continue

            p.step(visible)

            collided = False
            for o in visible:
                if o.hits(p.x, p.y, p.width, p.height):
                    collided = True
                    break

            if collided:
                p.alive = False
                continue

            # Score = frame survécue (proportionnel à la distance parcourue)
            # Mis à jour à CHAQUE frame, y compris pour les survivants en fin de niveau.
            if self.frame > agent.fitness:
                agent.fitness = float(self.frame)

            # Décision du réseau
            if agent.network.evaluate(visible, (p.x, p.y)):
                p.try_jump()

    def run(self, agents: Sequence[Agent], *, max_frames: int | None = None,
            on_frame=None) -> None:
        """Exécute la simulation jusqu'à fin (tous morts ou niveau terminé)."""
        while not self.finished(agents):
            self.step(agents)
            if on_frame is not None:
                on_frame(self, agents)
            if max_frames is not None and self.frame >= max_frames:
                break

        # Bonus de fin pour les survivants (motivation à terminer le niveau)
        bonus = float(self.frame) * 0.1
        for agent in agents:
            if agent.alive:
                agent.fitness += bonus
