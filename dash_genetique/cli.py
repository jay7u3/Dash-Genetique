"""CLI argparse: entraînement, visualisation, rejeu du meilleur."""

from __future__ import annotations

import argparse
import logging
import sys
from random import Random

from .ai.agent import Agent
from .ai.serialization import load_network
from .ai.visualize import to_ascii, to_dot
from .config import Config, MutationConfig, TrainingConfig
from .game.level import Level
from .game.levels_data import LEVELS
from .game.random_map import random_level
from .resources import Resources
from .training.trainer import Trainer


def _level_factory(name: str, rng: Random):
    if name == "random":
        return lambda: random_level(rng, start_x=1000, n_stages=5, spacing=400)
    if name not in LEVELS:
        raise SystemExit(f"Level inconnu: {name!r}. Disponibles: {list(LEVELS) + ['random']}")
    return LEVELS[name]


def _build_config(args: argparse.Namespace) -> Config:
    if args.config:
        cfg = Config.from_json(args.config)
    else:
        cfg = Config(mutation=MutationConfig(), training=TrainingConfig())

    t = cfg.training
    if args.generations is not None:
        t.generations = args.generations
    if args.population is not None:
        t.population = args.population
    if args.seed is not None:
        t.seed = args.seed
    if args.no_render:
        t.render = False
    if args.render_every is not None:
        t.render_every = args.render_every
    if args.workers is not None:
        t.workers = args.workers
    if args.size_penalty is not None:
        t.size_penalty_weight = args.size_penalty
    if args.fps is not None:
        t.fps = args.fps

    if args.level is not None:
        cfg.level_name = args.level
    if args.save is not None:
        cfg.save_path = args.save
    if args.stats_csv is not None:
        cfg.stats_csv = args.stats_csv
    if args.stats_plot is not None:
        cfg.stats_plot = args.stats_plot
    return cfg


def _cmd_train(args: argparse.Namespace) -> int:
    cfg = _build_config(args)
    headless = not cfg.training.render
    resources = Resources.load(headless=headless)
    rng = Random(cfg.training.seed)
    factory = _level_factory(cfg.level_name, rng)
    trainer = Trainer(cfg, resources, factory, rng=rng)
    trainer.run()
    return 0


def _cmd_watch(args: argparse.Namespace) -> int:
    """Rejoue un réseau sauvegardé avec rendu."""
    from .game.renderer import Renderer

    network = load_network(args.path)
    resources = Resources.load(headless=False)
    rng = Random(args.seed)
    factory = _level_factory(args.level, rng)
    obstacles = factory()
    level = Level(
        obstacles,
        largeur=resources.largeur,
        hauteur=resources.hauteur,
        hauteur_sol=resources.hauteur_sol,
    )
    from .core.player import Player

    player = Player(
        x=resources.largeur // 2 - 25,
        y=resources.hauteur_sol - resources.bob_hauteur,
        width=resources.bob_largeur,
        height=resources.bob_hauteur,
        ground_y=resources.hauteur_sol - resources.bob_hauteur,
    )
    agent = Agent(network=network, player=player)
    renderer = Renderer(resources, fps=args.fps)

    def on_frame(lvl: Level, agents):
        renderer.render(lvl, agents, generation=-1, previous_score=agent.fitness)

    level.run([agent], on_frame=on_frame)
    print(f"Fitness finale: {agent.fitness:.0f}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    network = load_network(args.path)
    if args.format == "dot":
        print(to_dot(network))
    else:
        print(to_ascii(network))
    print(f"[size={network.size()}]", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dash-genetique",
        description="Entraîne une IA par algorithme génétique à jouer à Dash-Genetique.",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("train", help="Lance l'entraînement.")
    t.add_argument("--generations", type=int)
    t.add_argument("--population", type=int)
    t.add_argument("--seed", type=int)
    t.add_argument("--level", default=None, choices=list(LEVELS) + ["random"])
    t.add_argument("--save", default=None, help="Chemin JSON de sauvegarde du meilleur")
    t.add_argument("--no-render", action="store_true", help="Mode headless (10x+ plus rapide)")
    t.add_argument("--render-every", type=int, help="Ne dessiner que 1 génération sur N")
    t.add_argument("--fps", type=int)
    t.add_argument("--workers", type=int, help="Parallélisation (headless uniquement)")
    t.add_argument("--size-penalty", type=float, help="Poids pénalité taille réseau")
    t.add_argument("--stats-csv", default=None)
    t.add_argument("--stats-plot", default=None)
    t.add_argument("--config", default=None, help="Chemin d'un fichier Config JSON")
    t.set_defaults(func=_cmd_train)

    w = sub.add_parser("watch", help="Rejoue un réseau JSON sauvegardé avec rendu.")
    w.add_argument("path")
    w.add_argument("--level", default="level_1", choices=list(LEVELS) + ["random"])
    w.add_argument("--seed", type=int, default=0)
    w.add_argument("--fps", type=int, default=60)
    w.set_defaults(func=_cmd_watch)

    s = sub.add_parser("show", help="Affiche un réseau JSON en ASCII ou en DOT graphviz.")
    s.add_argument("path")
    s.add_argument("--format", choices=("ascii", "dot"), default="ascii")
    s.set_defaults(func=_cmd_show)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
