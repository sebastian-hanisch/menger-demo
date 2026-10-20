"""Orakel-Test menger-demo: Zusammenhang, disjunkte Wege und trennende Mengen gegen networkx und die Aufzählung aller Trennmengen (DEMO-PLAYBOOK §12).

Unabhängige Rechenwege: `networkx.node_connectivity`, `edge_connectivity`, `local_node_connectivity`, `local_edge_connectivity`, `minimum_node_cut`, `minimum_edge_cut`, `node_disjoint_paths`,
`edge_disjoint_paths`; dazu die Aufzählung aller Teilmengen (kleine Netze). Feste Netze (Seeds), nie ein einzelner Zufalls-Seed."""

import random

import pytest

import mng_algorithm as A
import mng_scenario as S

nx = pytest.importorskip("networkx")

from conftest import MINI  # noqa: E402


def _nets(count=48, base=500):
    kinds = ("random", "grid", "ring", "scalefree", "verbund")
    for k in range(count):
        kind = kinds[k % len(kinds)]
        n = 10 + (k * 7) % 22
        yield S.make_instance(kind, n, (3.0, 4.5, 6.0, 8.0)[k % 4], 1 + k % 3, base + k)


def _graph(inst):
    g = nx.Graph()
    g.add_nodes_from(range(inst.n))
    g.add_edges_from(inst.edges)
    return g


def test_global_connectivity_equals_networkx_for_every_method():
    for inst in _nets():
        g = _graph(inst)
        assert A.global_kappa_even(inst.adj).value == A.global_kappa_naive(inst.adj).value == nx.node_connectivity(g), (inst.kind, inst.n)
        assert A.global_lambda(inst.adj).value == nx.edge_connectivity(g), (inst.kind, inst.n)


def test_every_nonadjacent_pair_equals_networkx_local_node_connectivity_and_the_cut_separates():
    for inst in list(_nets(18, 700)):
        g = _graph(inst)
        net = A.split_net(inst.adj)
        for s, t in A.nonadjacent_pairs(inst.adj):
            res = A.local_kappa(inst.adj, s, t, net)
            assert res.value == nx.algorithms.connectivity.local_node_connectivity(g, s, t), (inst.kind, s, t)
            assert len(res.cut) == res.value and A.is_vertex_separator(inst.adj, s, t, res.cut)
            assert len(res.paths) == res.value and A.valid_paths(inst.adj, res.paths, s, t, "vertex")
            assert len(nx.minimum_node_cut(g, s, t)) == res.value
            assert len(list(nx.node_disjoint_paths(g, s, t))) == res.value


def test_every_pair_equals_networkx_local_edge_connectivity_and_the_cut_separates():
    for inst in list(_nets(18, 900)):
        g = _graph(inst)
        net = A.edge_net(inst.adj)
        rng = random.Random(inst.n * 31 + inst.m)
        pairs = [(s, t) for s in range(inst.n) for t in range(s + 1, inst.n)]
        for s, t in rng.sample(pairs, min(40, len(pairs))):
            res = A.local_lambda(inst.adj, s, t, net)
            assert res.value == nx.algorithms.connectivity.local_edge_connectivity(g, s, t), (inst.kind, s, t)
            assert len(res.cut) == res.value and A.is_edge_cut(inst.adj, s, t, res.cut)
            assert len(res.paths) == res.value and A.valid_paths(inst.adj, res.paths, s, t, "edge")
            assert len(nx.minimum_edge_cut(g, s, t)) == res.value
            assert len(list(nx.edge_disjoint_paths(g, s, t))) == res.value


def test_small_networks_equal_the_enumeration_of_all_separating_sets():
    for k in range(40):
        inst = S.make_instance(("random", "ring", "scalefree", "verbund")[k % 4], 8 + k % 6, 3.0 + k % 4, 1 + k % 2, 300 + k)
        assert A.global_kappa_even(inst.adj).value == A.kappa_bruteforce(inst.adj), (inst.kind, inst.n, k)
        assert A.global_lambda(inst.adj).value == A.lambda_bruteforce(inst.adj), (inst.kind, inst.n, k)
        for s, t in A.nonadjacent_pairs(inst.adj)[:12]:
            assert A.local_kappa(inst.adj, s, t).value == A.kappa_local_bruteforce(inst.adj, s, t)


def test_whitney_chain_holds_on_every_network():
    for inst in _nets():
        kappa, lam, delta = A.whitney(inst.adj)
        assert kappa <= lam <= delta, (inst.kind, inst.n)


def test_the_whitney_chain_is_strict_somewhere():
    """Beide Ungleichungen können echt sein (Lehrbeispiel: κ = 1 < λ = 2 < Mindestgrad = 3) und sind es auf Verbundnetzen häufig."""
    assert A.whitney(MINI["zwei_werke"][0]) == (1, 2, 3)
    strict = [A.whitney(S.make_instance("verbund", 45, 8.0, 2, 1000 + k).adj) for k in range(12)]
    assert any(k < la < d for k, la, d in strict)


def test_connectivity_does_not_depend_on_the_numbering_of_the_locations():
    rng = random.Random(7)
    for inst in list(_nets(20, 1100)):
        perm = list(range(inst.n))
        rng.shuffle(perm)
        pairs = [(perm[u], perm[v]) for u, v in inst.edges]
        adj2 = S._adj_from_pairs(inst.n, pairs)
        assert A.whitney(adj2) == A.whitney(inst.adj), (inst.kind, inst.n)


def test_adding_a_link_never_lowers_the_connectivity():
    for inst in list(_nets(20, 1300)):
        adj = inst.adj
        pairs = A.nonadjacent_pairs(adj)
        if not pairs:
            continue
        s, t = pairs[len(pairs) // 2]
        adj2 = S._adj_from_pairs(inst.n, list(inst.edges) + [(s, t)])
        k1, l1, d1 = A.whitney(adj)
        k2, l2, d2 = A.whitney(adj2)
        assert k2 >= k1 and l2 >= l1 and d2 >= d1, (inst.kind, inst.n)


def test_the_number_of_flows_of_the_naive_method_is_the_number_of_nonadjacent_pairs():
    for inst in list(_nets(12, 1500)):
        assert A.global_kappa_naive(inst.adj).cost.flows == len(A.nonadjacent_pairs(inst.adj)) == inst.n * (inst.n - 1) // 2 - inst.m


def test_even_never_needs_more_flows_than_all_pairs():
    for inst in _nets():
        assert A.global_kappa_even(inst.adj).cost.flows <= len(A.nonadjacent_pairs(inst.adj)), (inst.kind, inst.n)


def test_menger_equals_flow_equals_cut_on_the_hand_networks():
    for name, (adj, kappa, lam, _d) in MINI.items():
        g = nx.Graph()
        g.add_nodes_from(range(len(adj)))
        g.add_edges_from((u, v) for u in range(len(adj)) for v in adj[u] if u < v)
        assert nx.node_connectivity(g) == kappa and nx.edge_connectivity(g) == lam, name
