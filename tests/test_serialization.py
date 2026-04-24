"""Tests de la sérialisation JSON (idempotence)."""

from dash_genetique.ai.neurons import LogicGate, ObstacleDetector
from dash_genetique.ai.serialization import (
    network_from_dict,
    network_to_dict,
    load_network,
    save_network,
)


def _sample_network():
    return LogicGate(
        "or",
        True,
        [
            ObstacleDetector(10, 20, "p"),
            LogicGate(
                "and",
                False,
                [
                    ObstacleDetector(30, 40, "bs"),
                    ObstacleDetector(50, 60, "p"),
                ],
            ),
        ],
    )


def test_roundtrip_dict():
    net = _sample_network()
    d = network_to_dict(net)
    net2 = network_from_dict(d)
    assert network_to_dict(net2) == d


def test_roundtrip_file(tmp_path):
    net = _sample_network()
    path = tmp_path / "net.json"
    save_network(str(path), net)
    net2 = load_network(str(path))
    assert network_to_dict(net2) == network_to_dict(net)


def test_same_evaluation_after_roundtrip():
    from dash_genetique.core.obstacle import Obstacle
    net = _sample_network()
    d = network_to_dict(net)
    net2 = network_from_dict(d)

    obstacles = [Obstacle(0, 0, 100, 100, "p"), Obstacle(50, 50, 150, 150, "bs")]
    for pos in [(0.0, 0.0), (20.0, 30.0), (50.0, 50.0)]:
        assert net.evaluate(obstacles, pos) == net2.evaluate(obstacles, pos)
