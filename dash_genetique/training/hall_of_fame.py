"""Hall of Fame: conserve les N meilleurs agents rencontrés durant l'entraînement."""

from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from typing import List, Tuple

from ..ai.agent import Agent
from ..ai.neurons import Neuron


@dataclass
class HallEntry:
    fitness: float
    generation: int
    network: Neuron


@dataclass
class HallOfFame:
    capacity: int = 10
    entries: List[HallEntry] = field(default_factory=list)

    def submit(self, agent: Agent, generation: int) -> bool:
        """Tente d'insérer un agent. Retourne True si inséré."""
        if len(self.entries) < self.capacity:
            self.entries.append(HallEntry(agent.fitness, generation, agent.network.clone()))
            self.entries.sort(key=lambda e: e.fitness, reverse=True)
            return True

        worst = self.entries[-1]
        if agent.fitness > worst.fitness:
            self.entries[-1] = HallEntry(agent.fitness, generation, agent.network.clone())
            self.entries.sort(key=lambda e: e.fitness, reverse=True)
            return True
        return False

    def best(self) -> HallEntry | None:
        return self.entries[0] if self.entries else None
