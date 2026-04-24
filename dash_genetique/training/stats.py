"""Historique des statistiques par génération + export CSV / plot matplotlib."""

from __future__ import annotations

import csv
import logging
import statistics
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from ..ai.agent import Agent


log = logging.getLogger("dash_genetique.stats")


@dataclass
class GenerationRecord:
    generation: int
    best: float
    mean: float
    median: float
    worst: float
    size_mean: float
    alive_count: int


@dataclass
class Stats:
    records: List[GenerationRecord] = field(default_factory=list)

    def record(self, generation: int, agents: Sequence[Agent]) -> GenerationRecord:
        fitnesses = [a.fitness for a in agents]
        sizes = [a.network.size() for a in agents]
        rec = GenerationRecord(
            generation=generation,
            best=max(fitnesses) if fitnesses else 0.0,
            mean=statistics.mean(fitnesses) if fitnesses else 0.0,
            median=statistics.median(fitnesses) if fitnesses else 0.0,
            worst=min(fitnesses) if fitnesses else 0.0,
            size_mean=statistics.mean(sizes) if sizes else 0.0,
            alive_count=sum(1 for a in agents if a.alive),
        )
        self.records.append(rec)
        log.info(
            "gen=%d best=%.1f mean=%.1f size_avg=%.1f alive=%d",
            rec.generation, rec.best, rec.mean, rec.size_mean, rec.alive_count,
        )
        return rec

    def to_csv(self, path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["generation", "best", "mean", "median", "worst", "size_mean", "alive"])
            for r in self.records:
                w.writerow([r.generation, r.best, r.mean, r.median, r.worst, r.size_mean, r.alive_count])

    def plot(self, path: Optional[str] = None) -> None:
        """Trace best/mean/median par génération. Sauve en PNG si ``path`` est fourni."""
        try:
            import matplotlib
            if path is not None:
                matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            log.warning("matplotlib non installé; plot désactivé")
            return

        gens = [r.generation for r in self.records]
        plt.figure(figsize=(10, 6))
        plt.plot(gens, [r.best for r in self.records], label="best")
        plt.plot(gens, [r.mean for r in self.records], label="mean")
        plt.plot(gens, [r.median for r in self.records], label="median")
        plt.xlabel("Génération")
        plt.ylabel("Fitness (frames)")
        plt.title("Évolution de la fitness")
        plt.legend()
        plt.grid(True, alpha=0.3)
        if path:
            plt.savefig(path, dpi=100, bbox_inches="tight")
            plt.close()
        else:
            plt.show()
