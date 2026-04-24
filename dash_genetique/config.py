"""Configuration centralisée: hyperparamètres du GA, de la mutation et de l'entraînement."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class MutationConfig:
    """Paramètres contrôlant la mutation des neurones."""

    # DetecteurObstacle
    detector_coord_rate: float = 0.5
    detector_type_rate: float = 0.2
    detector_to_gate_rate: float = 0.5
    coord_delta: int = 20

    # PorteLogique
    gate_operator_flip_rate: float = 0.1
    gate_negation_flip_rate: float = 0.1
    gate_add_child_rate: float = 0.25
    gate_add_gate_vs_detector: float = 0.66  # prob. d'ajouter une porte plutôt qu'un détecteur
    child_mutate_rate: float = 0.5
    child_remove_rate: float = 1.0 / 7.0

    # Crossover
    crossover_rate: float = 0.2


@dataclass
class TrainingConfig:
    """Paramètres de la boucle d'entraînement (GA)."""

    population: int = 200
    generations: int = 500

    # Parts de la population (doivent sommer à 1.0)
    elite_pct: float = 0.10
    children_pct: float = 0.70
    random_pct: float = 0.20

    tournament_k: int = 5

    # Pénalité: fitness_ajustée = fitness - weight * taille_reseau
    size_penalty_weight: float = 0.0

    # Adaptation: au bout de N générations sans amélioration on booste la mutation
    adaptive_stagnation: int = 10
    adaptive_mutation_boost: float = 2.0

    # Rendu / performances
    render: bool = True
    render_every: int = 1  # ne dessiner que 1 génération sur N (0 = jamais)
    fps: int = 160
    workers: int = 1  # > 1 => multiprocessing (headless uniquement)

    seed: Optional[int] = None


@dataclass
class Config:
    mutation: MutationConfig = field(default_factory=MutationConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    level_name: str = "level_1"
    save_path: str = "./saved.json"
    stats_csv: Optional[str] = None
    stats_plot: Optional[str] = None

    def to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            mutation=MutationConfig(**data.get("mutation", {})),
            training=TrainingConfig(**data.get("training", {})),
            level_name=data.get("level_name", "level_1"),
            save_path=data.get("save_path", "./saved.json"),
            stats_csv=data.get("stats_csv"),
            stats_plot=data.get("stats_plot"),
        )
