"""Entraînement: orchestration, sélection, stats, hall of fame."""

from .trainer import Trainer
from .selection import tournament_pick
from .stats import Stats
from .hall_of_fame import HallOfFame

__all__ = ["Trainer", "tournament_pick", "Stats", "HallOfFame"]
