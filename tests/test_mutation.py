"""Tests des opérateurs de mutation."""

from random import Random

from dash_genetique.ai.mutation import mutate
from dash_genetique.ai.neurons import LogicGate, ObstacleDetector
from dash_genetique.config import MutationConfig


def _cfg(**overrides) -> MutationConfig:
    base = MutationConfig(
        detector_coord_rate=0.0,
        detector_type_rate=0.0,
        detector_to_gate_rate=0.0,
        gate_operator_flip_rate=0.0,
        gate_negation_flip_rate=0.0,
        gate_add_child_rate=0.0,
        child_mutate_rate=0.0,
        child_remove_rate=0.0,
    )
    for k, v in overrides.items():
        setattr(base, k, v)
    return base


def test_detector_to_gate_transformation_is_returned():
    """Regression: la transformation DetecteurObstacle -> PorteLogique était PERDUE."""
    rng = Random(0)
    detector = ObstacleDetector(10, 20, "p")
    cfg = _cfg(detector_to_gate_rate=1.0)
    result = mutate(detector, rng, cfg, bounds=(800, 400))
    assert isinstance(result, LogicGate)
    assert any(isinstance(c, ObstacleDetector) for c in result.children)


def test_mutation_never_empties_children():
    """Regression: une PorteLogique ne doit jamais finir sans enfant après mutation."""
    rng = Random(42)
    gate = LogicGate("and", False, [ObstacleDetector(0, 0, "p")])
    cfg = _cfg(child_remove_rate=1.0)
    for _ in range(50):
        result = mutate(gate, rng, cfg, bounds=(800, 400))
        assert isinstance(result, LogicGate)
        assert len(result.children) >= 1


def test_mutation_removes_children_respects_list_iteration():
    """Regression: modifier la liste pendant l'itération sautait des éléments."""
    rng = Random(0)
    gate = LogicGate(
        "and",
        False,
        [ObstacleDetector(i, 0, "p") for i in range(10)],
    )
    cfg = _cfg(child_remove_rate=0.5)
    result = mutate(gate, rng, cfg, bounds=(800, 400))
    assert isinstance(result, LogicGate)
    assert 1 <= len(result.children) <= 10


def test_size_is_correct():
    gate = LogicGate("and", False, [
        ObstacleDetector(0, 0, "p"),
        LogicGate("or", True, [ObstacleDetector(1, 1, "bs")]),
    ])
    # 1 porte + 1 détecteur + 1 porte + 1 détecteur = 4
    assert gate.size() == 4


def test_empty_gate_neutral_element():
    """AND vide = True; OR vide = False."""
    g_and = LogicGate("and", False, [])
    g_or = LogicGate("or", False, [])
    assert g_and.evaluate([], (0.0, 0.0)) is True
    assert g_or.evaluate([], (0.0, 0.0)) is False

    g_and_neg = LogicGate("and", True, [])
    assert g_and_neg.evaluate([], (0.0, 0.0)) is False
