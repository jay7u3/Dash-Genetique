"""Tests de la visualisation texte/DOT."""

from dash_genetique.ai.neurons import LogicGate, ObstacleDetector
from dash_genetique.ai.visualize import to_ascii, to_dot


def test_ascii_non_empty():
    net = LogicGate("and", True, [ObstacleDetector(10, 20, "p")])
    out = to_ascii(net)
    assert "NOT AND" in out
    assert "DETECT" in out
    assert "p" in out


def test_dot_is_valid_structure():
    net = LogicGate("or", False, [
        ObstacleDetector(10, 20, "p"),
        ObstacleDetector(30, 40, "bs"),
    ])
    dot = to_dot(net)
    assert dot.startswith("digraph network")
    assert dot.rstrip().endswith("}")
    assert "n0 -> n1" in dot
    assert "n0 -> n2" in dot
