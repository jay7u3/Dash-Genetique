# Dash-Genetique

Entraînement d’une IA par **algorithme génétique** pour jouer à un clone de *Geometry Dash* en **Python** et **Pygame**.

Contrairement à un réseau de neurones classique (type perceptron multicouche), le « cerveau » est un **arbre symbolique** : des **portes logiques** (`ET` / `OU`, avec négation optionnelle) combinent des **détecteurs d’obstacles** (zones relatives à la position du joueur). Ce modèle est compact, interprétable et évolutif par mutation / crossover.

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Ligne de commande](#ligne-de-commande)
- [Configuration avancée (JSON)](#configuration-avancée-json)
- [Niveaux et cartes aléatoires](#niveaux-et-cartes-aléatoires)
- [Fichiers de sortie](#fichiers-de-sortie)
- [Architecture du code](#architecture-du-code)
- [Algorithme génétique (résumé)](#algorithme-génétique-résumé)
- [Performance et parallélisation](#performance-et-parallélisation)
- [Dépannage](#dépannage)
- [Développement et tests](#développement-et-tests)
- [Auteurs](#auteurs)

---

## Fonctionnalités

- **Simulation** découplée du rendu : entraînement **headless** (sans fenêtre) beaucoup plus rapide.
- **Parallélisation** de l’évaluation des agents (`multiprocessing`) en mode headless.
- **GA** avec élitisme, tournoi, crossover d’arbres, mutation, injection d’individus aléatoires, **mutation adaptative** en cas de stagnation.
- **Fitness** basée sur la survie (frames) + bonus de fin de niveau pour les survivants.
- **Sauvegarde / chargement JSON** du meilleur réseau (reproductible, versionnable).
- **Statistiques** par génération (CSV + graphique matplotlib).
- **Visualisation** du réseau en ASCII ou en **DOT** (Graphviz).
- **Hall of fame** interne (meilleurs historiques pendant une session).
- **Suite de tests** (pytest) couvrant physique, collisions, mutation, sérialisation, niveaux aléatoires, etc.

---

## Prérequis

- **Python 3.10+**
- **Pygame 2.5+** (affichage et chargement des sprites)
- **matplotlib** (optionnel mais recommandé pour `--stats-plot`)
- **Graphviz** (optionnel, pour convertir le DOT en image : `dot -Tpng`)

Les sprites doivent se trouver dans le dossier `ressources/` (chemins relatifs au répertoire de lancement du programme).

---

## Installation

### Avec un environnement virtuel (recommandé)

```bash
git clone <url-du-depot> Dash-Genetique
cd Dash-Genetique

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Installation en mode éditable (optionnel)

Depuis la racine du dépôt :

```bash
pip install -e .
```

Cela installe la commande **`dash-genetique`** (voir `pyproject.toml`).

---

## Démarrage rapide

| Objectif | Commande |
|----------|----------|
| Entraînement avec fenêtre (défaut) | `python -m dash_genetique train` ou `python main.py` |
| Entraînement rapide sans affichage | `python -m dash_genetique train --no-render` |
| Carte aléatoire | `python -m dash_genetique train --no-render --level random` |
| Rejouer un réseau sauvegardé | `python -m dash_genetique watch saved.json` |
| Afficher la structure d’un réseau | `python -m dash_genetique show saved.json` |

Après `pip install -e .`, vous pouvez aussi utiliser :

```bash
dash-genetique train --no-render --seed 42
```

---

## Ligne de commande

Le programme expose trois sous-commandes : **`train`**, **`watch`**, **`show`**.

### Options globales

| Option | Description |
|--------|-------------|
| `-v`, `--verbose` | Logs détaillés (niveau DEBUG). |

### `train` — Entraînement

| Option | Défaut | Description |
|--------|--------|-------------|
| `--generations N` | `500` | Nombre de générations. |
| `--population N` | `200` | Taille de la population. |
| `--seed N` | aléatoire | Graine pour reproductibilité (RNG Python). |
| `--level NAME` | `level_1` | Niveau : `level_1`, `level_2`, `random`. |
| `--no-render` | off | Pas de fenêtre : simulation headless (souvent ×10 ou plus rapide). |
| `--render-every K` | `1` | Avec rendu : n’afficher qu’une génération sur `K` (`0` = jamais dessiner pendant l’entraînement). |
| `--fps N` | `160` | Images par seconde pendant le rendu. |
| `--workers N` | `1` | Si `N > 1` : évaluation parallèle (**uniquement** avec `--no-render`). |
| `--size-penalty λ` | `0` | Tri / sélection avec `fitness - λ × taille_réseau` (pénalise les arbres trop gros). |
| `--save PATH` | `./saved.json` | Fichier JSON du **meilleur** réseau à chaque génération. |
| `--stats-csv PATH` | — | Export CSV des stats par génération. |
| `--stats-plot PATH` | — | Image PNG (matplotlib) : courbes best / mean / median. |
| `--config PATH` | — | Charge une configuration JSON (voir section suivante). Les options CLI **écrasent** les champs correspondants du fichier. |

Exemples :

```bash
# Session longue, reproductible, avec traces
python -m dash_genetique train --no-render --generations 800 --population 300 \
  --seed 42 --stats-csv stats.csv --stats-plot fitness.png --save meilleur.json

# Rendu léger : une génération sur 10 affichée
python -m dash_genetique train --render-every 10 --fps 120

# Parallèle sur 4 cœurs (headless)
python -m dash_genetique train --no-render --workers 4 --population 400
```

### `watch` — Rejouer un réseau sauvegardé

Ouvre une fenêtre Pygame et fait jouer **un** agent avec le réseau chargé depuis un JSON produit par `train`.

| Argument / option | Description |
|-------------------|-------------|
| `path` | Fichier JSON (ex. `saved.json`). |
| `--level NAME` | `level_1` par défaut ; idem que pour `train`. |
| `--seed N` | Graine pour le niveau `random` (reproductibilité). |
| `--fps N` | Défaut `60`. |

```bash
python -m dash_genetique watch saved.json --level random --seed 7
```

### `show` — Inspecter un réseau (texte ou Graphviz)

| Argument / option | Description |
|-------------------|-------------|
| `path` | Fichier JSON du réseau. |
| `--format ascii` | Arbre indenté sur la sortie standard (défaut). |
| `--format dot` | Graphe au format DOT (à passer à `dot`). |

```bash
python -m dash_genetique show saved.json
python -m dash_genetique show saved.json --format dot | dot -Tpng -o reseau.png
```

La taille du réseau (nombre de nœuds) est affichée sur **stderr** en fin de commande.

---

## Configuration avancée (JSON)

Vous pouvez générer un fichier de configuration via `Config.to_json()` en Python, ou le rédiger à la main. Structure attendue (champs optionnels fusionnés avec les défauts) :

```json
{
  "mutation": {
    "detector_coord_rate": 0.5,
    "detector_type_rate": 0.2,
    "detector_to_gate_rate": 0.5,
    "coord_delta": 20,
    "gate_operator_flip_rate": 0.1,
    "gate_negation_flip_rate": 0.1,
    "gate_add_child_rate": 0.25,
    "gate_add_gate_vs_detector": 0.66,
    "child_mutate_rate": 0.5,
    "child_remove_rate": 0.142857,
    "crossover_rate": 0.2
  },
  "training": {
    "population": 200,
    "generations": 500,
    "elite_pct": 0.1,
    "children_pct": 0.7,
    "random_pct": 0.2,
    "tournament_k": 5,
    "size_penalty_weight": 0.0,
    "adaptive_stagnation": 10,
    "adaptive_mutation_boost": 2.0,
    "render": true,
    "render_every": 1,
    "fps": 160,
    "workers": 1,
    "seed": null
  },
  "level_name": "level_1",
  "save_path": "./saved.json",
  "stats_csv": null,
  "stats_plot": null
}
```

Utilisation :

```bash
python -m dash_genetique train --config ma_config.json --no-render --seed 1
```

Les pourcentages `elite_pct`, `children_pct` et `random_pct` doivent **sommer à 1.0** (sinon la taille de la génération suivante peut être incohérente).

---

## Niveaux et cartes aléatoires

### Niveaux fixes (`levels_data.py`)

| Nom | Description |
|-----|-------------|
| `level_1` | Parcours principal, obstacles variés (référence historique du projet). |
| `level_2` | Niveau court, utile pour des tests rapides. |

### Niveau `random` (`random_map.py`)

Assemble plusieurs **stages** (morceaux de niveau) choisis au hasard, espacés horizontalement. Les stages disponibles sont regroupés dans le dictionnaire `STAGES` (noms explicites : `couloir`, `long_parcours`, `court`, `trio_piques`, `escalier_montant`, `pyramide`, `ile_au_dessus_pique`, `tunnel_bas`, etc.).

Paramètres internes du factory CLI pour `random` : `start_x=1000`, `n_stages=5`, `spacing=400`.

---

## Fichiers de sortie

| Fichier | Produit par | Contenu |
|---------|-------------|---------|
| `saved.json` (ou `--save`) | `train` | Réseau du meilleur agent + métadonnées (`generation`, `fitness`, …). Format stable pour `watch` / `show`. |
| `stats.csv` | `train --stats-csv` | Une ligne par génération : best, mean, median, worst, taille moyenne du réseau, nombre d’agents encore vivants en fin de simulation. |
| `fitness.png` (ou autre chemin) | `train --stats-plot` | Courbes matplotlib. |

**Note :** d’anciennes sauvegardes texte du type `saved.txt` (repr `str()` du réseau) ne sont **pas** chargeables par le nouveau pipeline JSON.

---

## Architecture du code

```text
Dash-Genetique/
├── main.py                 # Point d’entrée minimal (équivalent à « train »)
├── pyproject.toml          # Métadonnées du paquet, script dash-genetique, ruff, pytest
├── requirements.txt
├── ressources/             # Images (fond, sol, Bob, piques, blocs, …)
├── dash_genetique/
│   ├── __main__.py         # python -m dash_genetique
│   ├── cli.py              # argparse : train | watch | show
│   ├── config.py           # MutationConfig, TrainingConfig, Config (+ JSON)
│   ├── resources.py        # Chargement des sprites (compatible headless)
│   ├── core/               # Logique métier sans pygame
│   │   ├── obstacle.py     # AABB, collision
│   │   └── player.py       # Physique (gravité, saut, surface)
│   ├── game/
│   │   ├── level.py        # Boucle de simulation pure
│   │   ├── levels_data.py  # level_1, level_2
│   │   ├── random_map.py   # Stages + random_level()
│   │   └── renderer.py     # Affichage pygame (optionnel)
│   ├── ai/
│   │   ├── neurons.py      # ObstacleDetector, LogicGate
│   │   ├── mutation.py     # Mutation d’arbre
│   │   ├── crossover.py    # Échange de sous-arbres
│   │   ├── agent.py        # Agent = réseau + joueur + fitness
│   │   ├── serialization.py
│   │   └── visualize.py    # ASCII / DOT
│   └── training/
│       ├── trainer.py      # Boucle GA, parallèle, adaptation
│       ├── selection.py    # Tournoi
│       ├── stats.py        # CSV + matplotlib
│       └── hall_of_fame.py
└── tests/                  # Tests pytest
```

**Principe directeur :** la simulation (`game/level.py`, `core/`) ne dépend pas de Pygame ; le rendu (`game/renderer.py`) est branché uniquement quand `training.render` est activé.

---

## Algorithme génétique (résumé)

1. **Évaluation** : chaque agent parcourt le niveau ; la fitness augmente avec le nombre de **frames** survécues ; un **bonus** est ajouté si l’agent est encore vivant à la fin du parcours.
2. **Tri** : les agents sont classés par `fitness - λ × taille(réseau)` si `λ > 0`.
3. **Nouvelle génération** :
   - **Élite** (~10 %) : clones **non mutés** (préservation du meilleur matériel génétique).
   - **Enfants** (~70 %) : parents tirés par **tournoi**, parfois **crossover** puis **mutation**.
   - **Aléatoires** (~20 %) : nouveaux arbres aléatoires (diversité).
4. **Stagnation** : si le meilleur score ne progresse pas pendant plusieurs générations, les taux de mutation augmentent temporairement.

Les détails (probabilités, tailles) sont dans `dash_genetique/config.py` et modifiables via JSON.

---

## Performance et parallélisation

| Mode | Remarque |
|------|----------|
| `--no-render` | Utilise un pilote vidéo SDL factice ; pas de `blit` ni de limite FPS → beaucoup plus rapide. |
| `--workers N` avec `N > 1` | Uniquement sans rendu. Chaque processus réévalue un sous-ensemble d’agents. |
| `--render-every K` | Réduit le coût graphique tout en gardant un aperçu périodique. |

Pour des sessions très longues, privilégiez `--no-render` avec `--stats-csv` pour suivre la progression sans ralentissement dû à l’interface.

---

## Dépannage

| Problème | Piste |
|----------|--------|
| `pygame.error: No video device` sur serveur SSH | Utiliser `train --no-render` (définit automatiquement un pilote SDL adapté). |
| Fenêtre qui ne répond pas / fermeture | Fermer la fenêtre : le renderer appelle `pygame.quit()` puis `sys.exit(0)`. |
| `FileNotFoundError` sur les images | Lancer les commandes depuis la **racine** du dépôt (là où se trouve `ressources/`). |
| `ModuleNotFoundError: pytest` | `pip install pytest` dans votre venv. |
| Graphviz : `dot: command not found` | Installer le paquet système `graphviz` (le format DOT est tout de même affichable en texte brut). |

---

## Développement et tests

```bash
# Toute la suite
pytest

# Un module précis
pytest tests/test_random_map.py -v

# Lint (si ruff est installé)
ruff check dash_genetique tests
```

Les tests couvrent notamment : collisions AABB, mutations (réassignation des enfants, pas de porte vide), sérialisation JSON idempotente, sélection par tournoi, crossover, simulation du niveau (fitness continue), stages de `random_map.py`, intégration minimale CLI.

---

## Auteurs

- **Real Quiet Kid** — [@CarryUrself](https://github.com/CarryUrself)
- **Stephane** — [@Stephane39](https://github.com/Stephane39)

---

## Licence

Aucune licence n’est indiquée dans ce dépôt : par défaut, les droits restent ceux des auteurs. Pour une réutilisation ou une distribution, contactez les auteurs ou ajoutez un fichier `LICENSE` explicite.
