"""Kern der Demo (nur Standardbibliothek): Zusammenhang eines Netzes über disjunkte Wege (Satz von Menger).

`adj[v]` sind die Nachbarn des Standorts v (einfacher, ungerichteter Graph). Alles läuft auf **einem** Fluss mit Einheitskapazitäten (Edmonds–Karp, ein Weg je Durchlauf):

* `local_kappa(adj, s, t)`: knotendisjunkte Wege zwischen zwei nicht benachbarten Standorten = kleinste Trennmenge von Standorten (Knotenspaltungsnetz: jeder Standort v wird zu v_ein -> v_aus mit Kapazität 1,
  jede Leitung bekommt eine Kapazität, die nie die engste Stelle ist);
* `local_lambda(adj, s, t)`: kantendisjunkte Wege = kleinster Schnitt aus Leitungen;
* `global_kappa_naive`, `global_kappa_even`, `global_lambda`: Zusammenhang des ganzen Netzes (alle Paare einzeln gegen den Algorithmus von Even; n - 1 Flüsse für lambda);
* Brute Force (`kappa_bruteforce`, `lambda_bruteforce`, `kappa_local_bruteforce`) für kleine Netze und die Prüfer (`is_vertex_separator`, `valid_paths`, `is_edge_cut`).

Aufwand wird in **Flüssen** (ein Fluss je Paar), **Erweiterungen** (gefundene Wege) und **Besuchen** (in einer Breitensuche abgearbeitete Knoten des Flussnetzes) gezählt, nie in Sekunden."""

from collections import deque
from dataclasses import dataclass
from itertools import combinations

import mng_constants as C


@dataclass(frozen=True)
class Cost:
    flows: int = 0
    augmentations: int = 0
    visits: int = 0

    def __add__(self, other):
        return Cost(self.flows + other.flows, self.augmentations + other.augmentations, self.visits + other.visits)


@dataclass(frozen=True)
class Local:
    value: int
    paths: tuple            # Wege als Standortlisten [s, ..., t]
    cut: tuple              # kappa: trennende Standorte (sortiert); lambda: Leitungen (u, v) mit u auf der Seite von s
    side: tuple             # Standorte, die von s aus noch erreichbar sind, wenn der Schnitt entfernt ist
    cost: Cost


# --- Fluss ---------------------------------------------------------------------------------------------------------------------------------------


class FlowNet:
    """Flussnetz als Pfeilfelder: Pfeil i hat den Rückpfeil i ^ 1; `base` sind die Anfangskapazitäten."""

    def __init__(self, nodes):
        self.out = [[] for _ in range(nodes)]
        self.to = []
        self.base = []

    def add_arc(self, u, v, cap, back_cap=0):
        i = len(self.to)
        self.to.extend((v, u))
        self.base.extend((cap, back_cap))
        self.out[u].append(i)
        self.out[v].append(i + 1)
        return i

    def maxflow(self, s, t):
        """Edmonds–Karp. Gibt (Wert, Restkapazitäten, von s im Restnetz erreichbare Knoten, Kosten) zurück."""
        cap = self.base[:]
        value = augment = visits = 0
        while True:
            parent = {s: -1}
            queue = deque([s])
            while queue and t not in parent:
                u = queue.popleft()
                visits += 1
                for i in self.out[u]:
                    v = self.to[i]
                    if cap[i] > 0 and v not in parent:
                        parent[v] = i
                        queue.append(v)
            if t not in parent:
                break
            bottleneck, v = None, t
            while v != s:
                i = parent[v]
                bottleneck = cap[i] if bottleneck is None else min(bottleneck, cap[i])
                v = self.to[i ^ 1]
            if bottleneck >= C.FLOW_BIG:
                raise ValueError("unbeschränkter Fluss: Start und Ziel sind benachbart")
            v = t
            while v != s:
                i = parent[v]
                cap[i] -= bottleneck
                cap[i ^ 1] += bottleneck
                v = self.to[i ^ 1]
            value += bottleneck
            augment += 1
        return value, cap, set(parent), Cost(1, augment, visits)


def split_net(adj):
    """Knotenspaltung: Standort v wird zu v_ein (2v) und v_aus (2v + 1) mit einem Pfeil der Kapazität 1; jede Leitung u-v wird zu u_aus -> v_ein und v_aus -> u_ein mit Kapazität `FLOW_BIG`."""
    net = FlowNet(2 * len(adj))
    for v in range(len(adj)):
        net.add_arc(2 * v, 2 * v + 1, 1)
    for u in range(len(adj)):
        for v in adj[u]:
            net.add_arc(2 * u + 1, 2 * v, C.FLOW_BIG)
    return net


def edge_net(adj):
    """Jede Leitung u-v ist ein Paar gegenläufiger Pfeile mit Kapazität 1."""
    net = FlowNet(len(adj))
    for u in range(len(adj)):
        for v in adj[u]:
            if u < v:
                net.add_arc(u, v, 1, 1)
    return net


def _decompose_vertex(net, cap, adj, s, t):
    """Wege aus dem Fluss: von s_aus den Pfeilen mit Fluss folgen (jeder Standort trägt höchstens einen Weg)."""
    nxt = {}
    for u in range(len(adj)):
        for i in net.out[2 * u + 1]:
            if i % 2 == 0 and net.base[i] >= C.FLOW_BIG and cap[i] < net.base[i]:
                nxt.setdefault(u, []).append(net.to[i] // 2)
    paths = []
    for first in sorted(nxt.get(s, [])):
        path, v = [s, first], first
        while v != t:
            v = nxt[v][0]
            path.append(v)
        paths.append(tuple(path))
    return tuple(paths)


def _decompose_edge(net, cap, adj, s, t):
    """Wege aus dem Fluss auf Leitungen: dem Fluss folgen (verbrauchen) und Schleifen herausnehmen."""
    flow = {}
    for u in range(len(adj)):
        for i in net.out[u]:
            if i % 2 == 0:
                f = net.base[i] - cap[i]
                if f > 0:
                    flow.setdefault(net.to[i ^ 1], []).append(net.to[i])
                elif f < 0:
                    flow.setdefault(net.to[i], []).append(net.to[i ^ 1])
    for u in flow:
        flow[u].sort()
    paths = []
    while flow.get(s):
        path, pos, v = [s], {s: 0}, s
        while v != t:
            w = flow[v].pop(0)
            if w in pos:                       # Schleife: zurück auf den früheren Stand
                for x in path[pos[w] + 1:]:
                    del pos[x]
                del path[pos[w] + 1:]
            else:
                pos[w] = len(path)
                path.append(w)
            v = w
        paths.append(tuple(path))
    return tuple(paths)


# --- Lokaler Zusammenhang ---------------------------------------------------------------------------------------------------------------------------


def local_kappa(adj, s, t, net=None):
    """Knotenzusammenhang zwischen s und t (nicht benachbart, s != t): Zahl knotendisjunkter Wege = kleinste Zahl von Standorten, die s und t trennt."""
    if s == t or t in adj[s]:
        raise ValueError("local_kappa braucht zwei verschiedene, nicht benachbarte Standorte")
    net = net or split_net(adj)
    value, cap, reach, cost = net.maxflow(2 * s + 1, 2 * t)
    cut = tuple(v for v in range(len(adj)) if v not in (s, t) and 2 * v in reach and 2 * v + 1 not in reach)
    side = tuple(sorted(v for v in range(len(adj)) if (2 * v in reach or 2 * v + 1 in reach) and v not in cut))
    return Local(value, _decompose_vertex(net, cap, adj, s, t), cut, side, cost)


def local_lambda(adj, s, t, net=None):
    """Kantenzusammenhang zwischen s und t (s != t): Zahl kantendisjunkter Wege = kleinster Schnitt aus Leitungen."""
    if s == t:
        raise ValueError("local_lambda braucht zwei verschiedene Standorte")
    net = net or edge_net(adj)
    value, cap, reach, cost = net.maxflow(s, t)
    cut = tuple((u, v) for u in sorted(reach) for v in adj[u] if v not in reach)
    return Local(value, _decompose_edge(net, cap, adj, s, t), cut, tuple(sorted(reach)), cost)


# --- Globaler Zusammenhang ---------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Global:
    value: int
    pair: tuple             # (s, t) mit dem Wert, sonst ()
    cut: tuple              # kleinste trennende Standortmenge (kappa) bzw. Leitungsmenge (lambda)
    cost: Cost


def degrees(adj):
    return [len(a) for a in adj]


def min_degree(adj):
    return min(degrees(adj)) if adj else 0


def nonadjacent_pairs(adj):
    return [(s, t) for s in range(len(adj)) for t in range(s + 1, len(adj)) if t not in adj[s]]


def global_kappa_naive(adj):
    """Alle nicht benachbarten Paare einzeln (ein Fluss je Paar); ein vollständiges Netz hat kappa = n - 1 ohne einen Fluss."""
    n = len(adj)
    pairs = nonadjacent_pairs(adj)
    if not pairs:
        return Global(max(n - 1, 0), (), (), Cost())
    net = split_net(adj)
    best, cost = None, Cost()
    for s, t in pairs:
        res = local_kappa(adj, s, t, net)
        cost += res.cost
        if best is None or res.value < best[0]:
            best = (res.value, (s, t), res.cut)
    return Global(best[0], best[1], best[2], cost)


def global_kappa_even(adj):
    """Algorithmus von Even: nur die ersten k + 1 Standorte dienen als Quellen (k ist der bisher beste Wert, anfangs der Mindestgrad), jede gegen alle späteren. Ein kleinstes
    Trennmengen-Stück mit höchstens k Standorten kann nicht alle k + 1 Quellen enthalten; eine Quelle liegt außerhalb und hat auf der anderen Seite einen Standort (oder war vorher schon Ziel)."""
    n = len(adj)
    if not nonadjacent_pairs(adj):
        return Global(max(n - 1, 0), (), (), Cost())
    degs = degrees(adj)
    v_min = min(range(n), key=lambda v: (degs[v], v))
    far = next(w for w in range(n) if w != v_min and w not in adj[v_min])
    k, pair, cut = degs[v_min], (v_min, far), tuple(adj[v_min])      # Rückfall: die Nachbarn des Standorts mit dem Mindestgrad trennen ihn vom Rest
    net = split_net(adj)
    cost = Cost()
    i = 0
    while i <= k and i < n:
        for j in range(i + 1, n):
            if j in adj[i]:
                continue
            res = local_kappa(adj, i, j, net)
            cost += res.cost
            if res.value < k:
                k, pair, cut = res.value, (i, j), res.cut
        i += 1
    return Global(k, pair, cut, cost)


def global_lambda(adj):
    """Kantenzusammenhang des Netzes: min über alle t von lambda(0, t), also n - 1 Flüsse."""
    n = len(adj)
    if n < 2:
        return Global(0, (), (), Cost())
    net = edge_net(adj)
    best, cost = None, Cost()
    for t in range(1, n):
        res = local_lambda(adj, 0, t, net)
        cost += res.cost
        if best is None or res.value < best[0]:
            best = (res.value, (0, t), res.cut)
    return Global(best[0], best[1], best[2], cost)


def all_pairs_kappa(adj):
    """{(s, t): kappa(s, t)} für alle nicht benachbarten Paare s < t, dazu die Kosten."""
    net = split_net(adj)
    out, cost = {}, Cost()
    for s, t in nonadjacent_pairs(adj):
        res = local_kappa(adj, s, t, net)
        out[(s, t)] = res.value
        cost += res.cost
    return out, cost


def bottleneck_pairs(adj, kappas):
    """Paare, deren Zusammenhang kleiner ist als der kleinere Grad der beiden Standorte: dort sitzt eine Engstelle (die Standorte selbst sind nicht der Engpass)."""
    degs = degrees(adj)
    return [p for p, k in kappas.items() if k < min(degs[p[0]], degs[p[1]])]


# --- Brute Force und Prüfer --------------------------------------------------------------------------------------------------------------------------


def _connected_without(adj, removed, start=None):
    """Bilden die Standorte ohne `removed` ein zusammenhängendes Netz? (Netze mit weniger als zwei Standorten gelten als zusammenhängend.)"""
    alive = [v for v in range(len(adj)) if v not in removed]
    if len(alive) < 2:
        return True
    seen, stack = {alive[0]}, [alive[0]]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in removed and v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(alive)


def kappa_bruteforce(adj):
    """Kleinste Standortmenge, nach deren Entfernen das Netz zerfällt (oder n - 1 beim vollständigen Netz); nur für kleine Netze."""
    n = len(adj)
    for size in range(0, n - 1):
        for subset in combinations(range(n), size):
            if not _connected_without(adj, set(subset)):
                return size
    return max(n - 1, 0)


def lambda_bruteforce(adj):
    """Kleinste Zahl von Leitungen, die man kappen muss, damit das Netz zerfällt: kleinster Schnitt über alle Zweiteilungen; nur für kleine Netze."""
    n = len(adj)
    if n < 2:
        return 0
    best = None
    for mask in range(1, 2 ** (n - 1)):
        side = {v for v in range(n) if (mask >> v) & 1}
        cross = sum(1 for u in side for v in adj[u] if v not in side)
        best = cross if best is None else min(best, cross)
    return best


def kappa_local_bruteforce(adj, s, t):
    """Kleinste Standortmenge ohne s und t, die s und t trennt (s, t nicht benachbart); nur für kleine Netze."""
    others = [v for v in range(len(adj)) if v not in (s, t)]
    for size in range(0, len(others) + 1):
        for subset in combinations(others, size):
            removed = set(subset)
            seen, stack = {s}, [s]
            while stack:
                u = stack.pop()
                for v in adj[u]:
                    if v not in removed and v not in seen:
                        seen.add(v)
                        stack.append(v)
            if t not in seen:
                return size
    return len(others)


def is_vertex_separator(adj, s, t, cut):
    """Trennt die Standortmenge `cut` (ohne s und t) die Standorte s und t?"""
    removed = set(cut)
    if s in removed or t in removed:
        return False
    seen, stack = {s}, [s]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in removed and v not in seen:
                seen.add(v)
                stack.append(v)
    return t not in seen


def is_edge_cut(adj, s, t, cut):
    """Trennen die Leitungen `cut` die Standorte s und t?"""
    removed = {(min(u, v), max(u, v)) for u, v in cut}
    seen, stack = {s}, [s]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if (min(u, v), max(u, v)) not in removed and v not in seen:
                seen.add(v)
                stack.append(v)
    return t not in seen


def valid_paths(adj, paths, s, t, kind):
    """Sind das einfache Wege von s nach t im Netz, paarweise knotendisjunkt (`kind` = "vertex": keine gemeinsamen Zwischenstandorte) bzw. kantendisjunkt (`kind` = "edge")?"""
    used_nodes, used_edges = set(), set()
    for path in paths:
        if path[0] != s or path[-1] != t or len(set(path)) != len(path):
            return False
        for u, v in zip(path, path[1:]):
            if v not in adj[u]:
                return False
            e = (min(u, v), max(u, v))
            if e in used_edges:
                return False
            used_edges.add(e)
        if kind == "vertex":
            inner = set(path[1:-1])
            if inner & used_nodes:
                return False
            used_nodes |= inner
    return True


def whitney(adj):
    """(kappa, lambda, Mindestgrad) nach den schnellen Verfahren; die Kette kappa <= lambda <= Mindestgrad gilt immer (Whitney 1932)."""
    return global_kappa_even(adj).value, global_lambda(adj).value, min_degree(adj)
