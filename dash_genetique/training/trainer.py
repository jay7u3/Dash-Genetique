"""Trainer: orchestration de l'algorithme génétique."""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from random import Random
from typing import Callable, List, Optional, Sequence

from ..ai.agent import Agent
from ..ai.crossover import crossover
from ..ai.mutation import mutate
from ..ai.neurons import Neuron
from ..ai.serialization import save_network
from ..config import Config, MutationConfig
from ..core.obstacle import Obstacle
from ..game.level import Level
from ..resources import Resources
from .hall_of_fame import HallOfFame
from .selection import tournament_pick
from .stats import Stats


log = logging.getLogger("dash_genetique.trainer")


LevelFactory = Callable[[], List[Obstacle]]


@dataclass
class _EvalResult:
    fitness: float
    alive: bool


def _simulate_headless(
    network_dicts: List[dict],
    obstacles_ser: List[tuple],
    level_args: dict,
    seed: int,
) -> List[_EvalResult]:
    """Worker ``multiprocessing``: recharge les objets puis simule.

    On passe des dicts/tuples pour éviter les problèmes de pickle sur pygame.
    """
    from ..ai.agent import Agent
    from ..ai.serialization import network_from_dict
    from ..core.obstacle import Obstacle
    from ..core.player import Player
    from ..game.level import Level as _Level

    obstacles = [Obstacle(*args) for args in obstacles_ser]
    networks = [network_from_dict(d) for d in network_dicts]

    largeur = level_args["largeur"]
    hauteur = level_args["hauteur"]
    hauteur_sol = level_args["hauteur_sol"]
    bob_w = level_args["bob_largeur"]
    bob_h = level_args["bob_hauteur"]

    agents: List[Agent] = []
    for net in networks:
        player = Player(
            x=largeur // 2 - 25,
            y=hauteur_sol - bob_h,
            width=bob_w,
            height=bob_h,
            ground_y=hauteur_sol - bob_h,
        )
        agents.append(Agent(network=net, player=player))

    level = _Level(
        obstacles,
        largeur=largeur,
        hauteur=hauteur,
        hauteur_sol=hauteur_sol,
        speed=level_args.get("speed", 2.5),
    )
    level.run(agents, max_frames=level_args.get("max_frames"))
    return [_EvalResult(a.fitness, a.alive) for a in agents]


class Trainer:
    def __init__(
        self,
        cfg: Config,
        resources: Resources,
        level_factory: LevelFactory,
        *,
        rng: Optional[Random] = None,
    ) -> None:
        self.cfg = cfg
        self.resources = resources
        self.level_factory = level_factory
        self.rng = rng or Random(cfg.training.seed)

        self.bounds = (resources.largeur, resources.hauteur)

        self.agents: List[Agent] = [
            Agent.new_random(
                self.rng,
                largeur=resources.largeur,
                hauteur=resources.hauteur,
                bob_largeur=resources.bob_largeur,
                bob_hauteur=resources.bob_hauteur,
                hauteur_sol=resources.hauteur_sol,
            )
            for _ in range(cfg.training.population)
        ]

        self.stats = Stats()
        self.hof = HallOfFame(capacity=10)

        self._stagnation = 0
        self._last_best = float("-inf")
        self._prev_score: float = 0.0

    # ------------------------------------------------------------------ API

    def run(self) -> None:
        tcfg = self.cfg.training
        for gen in range(tcfg.generations):
            self._evaluate(gen)
            for a in self.agents:
                a.size_cache = a.network.size()
            self.agents.sort(
                key=lambda a: (
                    a.adjusted_fitness(tcfg.size_penalty_weight),
                    int(a.alive),
                ),
                reverse=True,
            )
            rec = self.stats.record(gen, self.agents)
            self.hof.submit(self.agents[0], gen)
            save_network(
                self.cfg.save_path,
                self.agents[0].network,
                meta={"generation": gen, "fitness": self.agents[0].fitness},
            )
            self._prev_score = rec.mean
            self._update_stagnation(rec.best)
            self._next_generation()

        if self.cfg.stats_csv:
            self.stats.to_csv(self.cfg.stats_csv)
        if self.cfg.stats_plot:
            self.stats.plot(self.cfg.stats_plot)

    # -------------------------------------------------------- Evaluation

    def _evaluate(self, generation: int) -> None:
        tcfg = self.cfg.training
        do_render = (
            tcfg.render
            and tcfg.render_every > 0
            and (generation % tcfg.render_every == 0)
        )

        # On reset les joueurs (le réseau, lui, est conservé / muté à la génération suivante)
        for a in self.agents:
            a.reset_player(
                None,
                largeur=self.resources.largeur,
                hauteur=self.resources.hauteur,
                bob_largeur=self.resources.bob_largeur,
                bob_hauteur=self.resources.bob_hauteur,
                hauteur_sol=self.resources.hauteur_sol,
            )

        if do_render:
            self._evaluate_with_render(generation)
        elif tcfg.workers > 1:
            self._evaluate_parallel()
        else:
            self._evaluate_serial()

    def _make_level(self) -> Level:
        return Level(
            self.level_factory(),
            largeur=self.resources.largeur,
            hauteur=self.resources.hauteur,
            hauteur_sol=self.resources.hauteur_sol,
        )

    def _evaluate_serial(self) -> None:
        level = self._make_level()
        level.run(self.agents)

    def _evaluate_with_render(self, generation: int) -> None:
        from ..game.renderer import Renderer  # import tardif: pygame display

        level = self._make_level()
        renderer = Renderer(self.resources, fps=self.cfg.training.fps)

        def on_frame(lvl: Level, agents: Sequence[Agent]) -> None:
            renderer.render(
                lvl,
                agents,
                generation=generation,
                previous_score=self._prev_score,
            )

        level.run(self.agents, on_frame=on_frame)

    def _evaluate_parallel(self) -> None:
        """Parallélisation multiprocess (headless uniquement).

        Chaque worker re-simule sa part avec la même graine de niveau.
        """
        from multiprocessing import Pool
        from ..ai.serialization import network_to_dict

        tcfg = self.cfg.training
        obstacles = self.level_factory()
        obstacles_ser = [
            (o.x1, o.y1, o.x2, o.y2, o.type, o.sprite_key) for o in obstacles
        ]
        level_args = {
            "largeur": self.resources.largeur,
            "hauteur": self.resources.hauteur,
            "hauteur_sol": self.resources.hauteur_sol,
            "bob_largeur": self.resources.bob_largeur,
            "bob_hauteur": self.resources.bob_hauteur,
        }

        # On découpe la population en chunks égaux
        n = len(self.agents)
        w = max(1, tcfg.workers)
        chunk = (n + w - 1) // w
        chunks = [self.agents[i : i + chunk] for i in range(0, n, chunk)]

        def _pack(chunk_agents: List[Agent]):
            return [network_to_dict(a.network) for a in chunk_agents]

        tasks = [(_pack(ch), obstacles_ser, level_args, self.rng.randrange(2**31))
                 for ch in chunks]

        with Pool(processes=w) as pool:
            results = pool.starmap(_simulate_headless, tasks)

        flat: List[_EvalResult] = [r for chunk_res in results for r in chunk_res]
        for agent, res in zip(self.agents, flat):
            agent.fitness = res.fitness
            agent.player.alive = res.alive

    # -------------------------------------------------- GA: génération suivante

    def _effective_mutation_cfg(self) -> MutationConfig:
        """Si on stagne, on booste temporairement les taux de mutation."""
        tcfg = self.cfg.training
        mcfg = self.cfg.mutation
        if self._stagnation < tcfg.adaptive_stagnation:
            return mcfg
        boost = tcfg.adaptive_mutation_boost
        boosted = copy.deepcopy(mcfg)
        boosted.detector_coord_rate = min(1.0, mcfg.detector_coord_rate * boost)
        boosted.detector_type_rate = min(1.0, mcfg.detector_type_rate * boost)
        boosted.detector_to_gate_rate = min(1.0, mcfg.detector_to_gate_rate * boost)
        boosted.gate_operator_flip_rate = min(1.0, mcfg.gate_operator_flip_rate * boost)
        boosted.gate_negation_flip_rate = min(1.0, mcfg.gate_negation_flip_rate * boost)
        boosted.gate_add_child_rate = min(1.0, mcfg.gate_add_child_rate * boost)
        log.info("Stagnation %d gen -> mutation boostée x%.1f", self._stagnation, boost)
        return boosted

    def _update_stagnation(self, best: float) -> None:
        if best > self._last_best:
            self._last_best = best
            self._stagnation = 0
        else:
            self._stagnation += 1

    def _next_generation(self) -> None:
        tcfg = self.cfg.training
        mcfg = self._effective_mutation_cfg()
        n = len(self.agents)

        n_elite = max(1, int(n * tcfg.elite_pct))
        n_random = int(n * tcfg.random_pct)
        n_children = n - n_elite - n_random

        elites: List[Agent] = []
        for a in self.agents[:n_elite]:
            elite = a.clone()  # réseau conservé tel quel (non muté)
            elite.reset_player(
                self.rng,
                largeur=self.resources.largeur,
                hauteur=self.resources.hauteur,
                bob_largeur=self.resources.bob_largeur,
                bob_hauteur=self.resources.bob_hauteur,
                hauteur_sol=self.resources.hauteur_sol,
            )
            elites.append(elite)

        pool = self.agents[: max(n_elite * 3, tcfg.tournament_k * 2)]
        children: List[Agent] = []
        while len(children) < n_children:
            parent_a = tournament_pick(pool, tcfg.tournament_k, self.rng)
            if self.rng.random() < mcfg.crossover_rate:
                parent_b = tournament_pick(pool, tcfg.tournament_k, self.rng)
                net_a, net_b = crossover(parent_a.network, parent_b.network, self.rng)
                for net in (net_a, net_b):
                    if len(children) >= n_children:
                        break
                    net = mutate(net, self.rng, mcfg, self.bounds)
                    child = self._make_child(net)
                    children.append(child)
            else:
                net = mutate(parent_a.network.clone(), self.rng, mcfg, self.bounds)
                children.append(self._make_child(net))

        randoms: List[Agent] = [
            Agent.new_random(
                self.rng,
                largeur=self.resources.largeur,
                hauteur=self.resources.hauteur,
                bob_largeur=self.resources.bob_largeur,
                bob_hauteur=self.resources.bob_hauteur,
                hauteur_sol=self.resources.hauteur_sol,
            )
            for _ in range(n_random)
        ]

        self.agents = elites + children + randoms

    def _make_child(self, network: Neuron) -> Agent:
        r = self.resources
        child = Agent(
            network=network,
            player=None,  # type: ignore[arg-type]  # sera remplacé immédiatement
        )
        child.reset_player(
            self.rng,
            largeur=r.largeur,
            hauteur=r.hauteur,
            bob_largeur=r.bob_largeur,
            bob_hauteur=r.bob_hauteur,
            hauteur_sol=r.hauteur_sol,
        )
        return child
