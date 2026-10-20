"""Experimente über feste Netze (nie ein einzelner Zufalls-Seed als Befund). Jede Funktion gibt eine Liste von Zeilen (dict) zurück; Verdikte und Abbildungen lesen nur diese Zeilen.

1. `exactness_rows`: stimmen alle Verfahren mit der Aufzählung aller Trennmengen überein (kleine Netze)?
2. `whitney_rows`: Zusammenhang kappa, lambda und Mindestgrad je Netztyp (die Kette kappa <= lambda <= Mindestgrad).
3. `bottleneck_rows`: Anteil der nicht benachbarten Standortpaare, die schlechter verbunden sind als ihr Mindestgrad (Engstelle).
4. `even_rows`: Flüsse des Algorithmus von Even gegen alle Paare einzeln.
5. `link_rows`: Verbundnetz: Zusammenhang gegen die Zahl der Leitungen zwischen den Regionen."""

import mng_algorithm as A
import mng_constants as C
import mng_scenario as S


def kind_label(kind, deg):
    name = C.KIND_NAMES[kind]
    return f"{name}, Grad {deg:g}".replace(".", ",") if kind in ("random", "verbund") else name


def _net(kind, deg, n, seed, links=2):
    return S.make_instance(kind, n, deg, links, seed)


def exactness_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        checks = wrong = nets = pairs = 0
        for seed in C.EX_EXACT_SEEDS:
            inst = _net(kind, deg, C.EX_EXACT_N, seed)
            adj = inst.adj
            nets += 1
            even, naive, lam = A.global_kappa_even(adj), A.global_kappa_naive(adj), A.global_lambda(adj)
            kb, lb = A.kappa_bruteforce(adj), A.lambda_bruteforce(adj)
            results = [even.value == kb, naive.value == kb, lam.value == lb]
            if even.cut and even.pair:
                results.append(len(even.cut) == even.value and A.is_vertex_separator(adj, even.pair[0], even.pair[1], even.cut))
            if lam.pair:
                results.append(len(lam.cut) == lam.value and A.is_edge_cut(adj, lam.pair[0], lam.pair[1], lam.cut))
            net = A.split_net(adj)
            for s, t in A.nonadjacent_pairs(adj):
                loc = A.local_kappa(adj, s, t, net)
                pairs += 1
                results.append(loc.value == A.kappa_local_bruteforce(adj, s, t) and len(loc.cut) == loc.value and A.is_vertex_separator(adj, s, t, loc.cut)
                               and len(loc.paths) == loc.value and A.valid_paths(adj, loc.paths, s, t, "vertex"))
                el = A.local_lambda(adj, s, t)
                results.append(len(el.paths) == el.value == len(el.cut) and A.valid_paths(adj, el.paths, s, t, "edge") and A.is_edge_cut(adj, s, t, el.cut))
            checks += len(results)
            wrong += results.count(False)
        rows.append({"kind": kind, "deg": deg, "label": kind_label(kind, deg), "nets": nets, "pairs": pairs, "checks": checks, "wrong": wrong, "n": C.EX_EXACT_N})
    return rows


def pair_rows():
    """Experimente 2 und 3 teilen sich die Rechnung: je Netztyp alle Paare."""
    rows = []
    for kind, deg in C.EX_KINDS:
        row = {"kind": kind, "deg": deg, "label": kind_label(kind, deg), "nets": 0, "equal": 0, "k_lt_l": 0, "l_lt_d": 0, "violations": 0, "sum_k": 0, "sum_l": 0, "sum_d": 0,
               "pairs": 0, "bottleneck": 0, "nets_with_bottleneck": 0, "n": 0}
        for seed in C.SWEEP_SEEDS:
            inst = _net(kind, deg, C.EX_PAIR_N, seed)
            adj = inst.adj
            row["n"] = max(row["n"], inst.n)
            kap, cost = A.all_pairs_kappa(adj)
            k = min(kap.values()) if kap else max(inst.n - 1, 0)
            lam = A.global_lambda(adj).value
            d = A.min_degree(adj)
            row["nets"] += 1
            row["equal"] += k == lam == d
            row["k_lt_l"] += k < lam
            row["l_lt_d"] += lam < d
            row["violations"] += not (k <= lam <= d)
            row["sum_k"] += k
            row["sum_l"] += lam
            row["sum_d"] += d
            bp = len(A.bottleneck_pairs(adj, kap))
            row["pairs"] += len(kap)
            row["bottleneck"] += bp
            row["nets_with_bottleneck"] += bp > 0
        rows.append(row)
    return rows


def even_rows():
    rows = []
    for n, count in C.EX_EVEN:
        for kind, deg in C.EX_KINDS:
            naive = even = visits = 0
            for seed in C.SWEEP_SEEDS[:count]:
                inst = _net(kind, deg, n, seed)
                res = A.global_kappa_even(inst.adj)
                naive += len(A.nonadjacent_pairs(inst.adj))
                even += res.cost.flows
                visits += res.cost.visits
            rows.append({"kind": kind, "deg": deg, "label": kind_label(kind, deg), "n": n, "nets": count, "naive_flows": naive / count, "even_flows": even / count, "even_visits": visits / count})
    return rows


def link_rows():
    rows = []
    for links in C.EX_LINKS:
        row = {"links": links, "nets": 0, "sum_k": 0, "sum_l": 0, "sum_d": 0, "k_lt_l": 0, "l_lt_d": 0}
        for seed in C.SWEEP_SEEDS:
            inst = S.make_instance("verbund", C.EX_LINK_N, 8.0, links, seed)
            k, lam, d = A.whitney(inst.adj)
            row["nets"] += 1
            row["sum_k"] += k
            row["sum_l"] += lam
            row["sum_d"] += d
            row["k_lt_l"] += k < lam
            row["l_lt_d"] += lam < d
        rows.append(row)
    return rows
