"""Gemeinsame Fixtures: die Mini-Netze, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Teure Experimente laufen einmal je Testlauf (`lru_cache`) und werden von Claims-, Verdikt- und Mutationstests gemeinsam genutzt."""

import sys
from functools import lru_cache
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _adj(n, pairs):
    nb = [set() for _ in range(n)]
    for u, v in pairs:
        nb[u].add(v)
        nb[v].add(u)
    return tuple(tuple(sorted(s)) for s in nb)


# Von Hand gerechnete Mini-Netze: Name -> (Adjazenz, Knotenzusammenhang kappa, Kantenzusammenhang lambda, Mindestgrad)
MINI = {
    "pfad4": (_adj(4, [(0, 1), (1, 2), (2, 3)]), 1, 1, 1),
    "kreis5": (_adj(5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]), 2, 2, 2),
    "vollstaendig4": (_adj(4, [(a, b) for a in range(4) for b in range(a + 1, 4)]), 3, 3, 3),
    "schleife": (_adj(5, [(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4)]), 1, 2, 2),                    # zwei Dreiecke teilen den Standort 2
    "k33": (_adj(6, [(a, b) for a in range(3) for b in range(3, 6)]), 3, 3, 3),
    "stern4": (_adj(4, [(0, 1), (0, 2), (0, 3)]), 1, 1, 1),
    "zwei_werke": (_adj(8, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (4, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7), (0, 4), (0, 5)]), 1, 2, 3),
}


@pytest.fixture
def mini():
    return MINI


@lru_cache(maxsize=None)
def cached(name):
    """Einmal je Testlauf berechnete Experimente (Name der Funktion in mng_experiments)."""
    import mng_experiments as ex
    return getattr(ex, name)()
