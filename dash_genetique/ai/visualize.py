"""Visualisation d'un réseau de neurones: texte ASCII et DOT graphviz."""

from __future__ import annotations

from typing import Iterable, List

from .neurons import LogicGate, Neuron, ObstacleDetector


def to_ascii(n: Neuron, indent: int = 0) -> str:
    prefix = "  " * indent
    if isinstance(n, ObstacleDetector):
        return f"{prefix}DETECT({n.obstacle_type}, dx={n.offset_x:.0f}, dy={n.offset_y:.0f})"
    if isinstance(n, LogicGate):
        neg = "NOT " if n.negation else ""
        head = f"{prefix}{neg}{n.operator.upper()}"
        children = "\n".join(to_ascii(c, indent + 1) for c in n.children)
        return f"{head}\n{children}" if children else head
    return f"{prefix}?"


def _dot_nodes(n: Neuron, counter: List[int], lines: List[str]) -> int:
    nid = counter[0]
    counter[0] += 1
    if isinstance(n, ObstacleDetector):
        label = f"DET\\n{n.obstacle_type}\\n({n.offset_x:.0f},{n.offset_y:.0f})"
        lines.append(f'  n{nid} [shape=box, style=filled, fillcolor=lightblue, label="{label}"];')
    elif isinstance(n, LogicGate):
        label = ("NOT " if n.negation else "") + n.operator.upper()
        lines.append(f'  n{nid} [shape=ellipse, style=filled, fillcolor=lightyellow, label="{label}"];')
        for c in n.children:
            cid = _dot_nodes(c, counter, lines)
            lines.append(f"  n{nid} -> n{cid};")
    return nid


def to_dot(n: Neuron) -> str:
    """Retourne la représentation DOT graphviz. À rendre via ``dot -Tpng``."""
    lines: List[str] = ["digraph network {", '  rankdir="TB";']
    _dot_nodes(n, [0], lines)
    lines.append("}")
    return "\n".join(lines)
