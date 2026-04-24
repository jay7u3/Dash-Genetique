"""Sérialisation JSON symétrique des réseaux de neurones."""

from __future__ import annotations

import json
from typing import Any, Dict

from .neurons import LogicGate, Neuron, ObstacleDetector


def network_to_dict(n: Neuron) -> Dict[str, Any]:
    if isinstance(n, ObstacleDetector):
        return {
            "kind": "detector",
            "offset_x": n.offset_x,
            "offset_y": n.offset_y,
            "obstacle_type": n.obstacle_type,
        }
    if isinstance(n, LogicGate):
        return {
            "kind": "gate",
            "operator": n.operator,
            "negation": n.negation,
            "children": [network_to_dict(c) for c in n.children],
        }
    raise TypeError(f"Neurone non sérialisable: {type(n).__name__}")


def network_from_dict(d: Dict[str, Any]) -> Neuron:
    kind = d.get("kind")
    if kind == "detector":
        return ObstacleDetector(
            offset_x=float(d["offset_x"]),
            offset_y=float(d["offset_y"]),
            obstacle_type=str(d["obstacle_type"]),
        )
    if kind == "gate":
        return LogicGate(
            operator=str(d["operator"]),
            negation=bool(d["negation"]),
            children=[network_from_dict(c) for c in d.get("children", [])],
        )
    raise ValueError(f"kind inconnu: {kind!r}")


def save_network(path: str, n: Neuron, meta: Dict[str, Any] | None = None) -> None:
    payload = {"version": 1, "network": network_to_dict(n)}
    if meta:
        payload["meta"] = meta
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def load_network(path: str) -> Neuron:
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return network_from_dict(payload["network"])
