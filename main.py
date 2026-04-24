"""Compat: permet de lancer ``python main.py`` comme avant.

Équivalent à ``python -m dash_genetique train`` (avec les valeurs par défaut).
Pour plus d'options: ``python -m dash_genetique --help``.
"""

from dash_genetique.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["train"]))
