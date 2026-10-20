"""Kern: jede Einheit an von Hand gerechneten Mini-Netzen (DEMO-PLAYBOOK §1b)."""

import pytest

import mng_algorithm as A
import mng_constants as C

from conftest import MINI


def test_flownet_adds_arcs_in_pairs_and_maxflow_counts_augmentations():
    net = A.FlowNet(3)
    net.add_arc(0, 1, 2)
    net.add_arc(1, 2, 1)
    net.add_arc(0, 2, 1)
    assert len(net.to) == 6 and net.base == [2, 0, 1, 0, 1, 0]
    value, cap, reach, cost = net.maxflow(0, 2)
    assert value == 2 and cost.augmentations == 2 and cost.flows == 1
    assert cap[0] == 1 and cap[2] == 0 and cap[4] == 0            # 0->1 trägt 1, 1->2 und 0->2 sind gesättigt
    assert reach == {0, 1}                                         # nach dem Fluss bleibt von 0 aus nur der Standort 1 erreichbar (0->1 hat Rest 1)


def test_flownet_refuses_an_unbounded_flow_between_adjacent_locations():
    net = A.split_net(MINI["pfad4"][0])
    with pytest.raises(ValueError):
        net.maxflow(2 * 0 + 1, 2 * 1)                              # 0_aus -> 1_ein hat die Kapazität FLOW_BIG: ein Weg ohne Zwischenstandort


def test_split_net_has_one_unit_arc_per_location_and_two_big_arcs_per_link():
    adj = MINI["pfad4"][0]
    net = A.split_net(adj)
    assert len(net.out) == 8 and len(net.to) == 2 * (4 + 6)
    assert net.base.count(1) == 4 and net.base.count(C.FLOW_BIG) == 6


def test_edge_net_has_a_pair_of_unit_arcs_per_link():
    net = A.edge_net(MINI["pfad4"][0])
    assert len(net.to) == 6 and net.base == [1, 1, 1, 1, 1, 1]


def test_local_kappa_on_the_cycle_has_two_disjoint_paths():
    res = A.local_kappa(MINI["kreis5"][0], 0, 2)
    assert res.value == 2 and res.paths == ((0, 1, 2), (0, 4, 3, 2))
    assert A.is_vertex_separator(MINI["kreis5"][0], 0, 2, res.cut) and len(res.cut) == 2 and res.cost.flows == 1


def test_local_kappa_on_the_path_is_one_and_the_separator_is_the_first_location():
    res = A.local_kappa(MINI["pfad4"][0], 0, 3)
    assert res.value == 1 and res.paths == ((0, 1, 2, 3),) and res.cut == (1,) and res.side == (0,)


def test_local_kappa_in_the_two_works_is_the_connecting_location():
    adj = MINI["zwei_werke"][0]
    res = A.local_kappa(adj, 1, 6)                                  # B nach G
    assert res.value == 1 and res.cut == (0,) and res.paths == ((1, 0, 4, 6),)
    assert A.local_kappa(adj, 0, 6).value == 2                      # von A nach G gibt es A-E-G und A-F-G


def test_local_kappa_refuses_adjacent_and_equal_pairs():
    adj = MINI["kreis5"][0]
    with pytest.raises(ValueError):
        A.local_kappa(adj, 0, 1)
    with pytest.raises(ValueError):
        A.local_kappa(adj, 2, 2)


def test_local_lambda_between_the_two_works_cuts_the_two_links():
    adj = MINI["zwei_werke"][0]
    res = A.local_lambda(adj, 1, 6)
    assert res.value == 2 and res.cut == ((0, 4), (0, 5)) and res.side == (0, 1, 2, 3)
    assert A.valid_paths(adj, res.paths, 1, 6, "edge") and A.is_edge_cut(adj, 1, 6, res.cut)


def test_local_lambda_on_adjacent_locations_counts_the_direct_link_too():
    adj = MINI["vollstaendig4"][0]
    res = A.local_lambda(adj, 0, 1)
    assert res.value == 3 and len(res.paths) == 3 and A.valid_paths(adj, res.paths, 0, 1, "edge")


def test_global_values_of_every_mini_network():
    for name, (adj, kappa, lam, delta) in MINI.items():
        assert A.global_kappa_even(adj).value == kappa, name
        assert A.global_kappa_naive(adj).value == kappa, name
        assert A.global_lambda(adj).value == lam, name
        assert A.min_degree(adj) == delta, name
        assert A.whitney(adj) == (kappa, lam, delta), name


def test_even_counts_flows_by_hand_on_the_path_and_the_two_works():
    path6 = tuple(tuple(w for w in (v - 1, v + 1) if 0 <= w < 6) for v in range(6))
    even, naive = A.global_kappa_even(path6), A.global_kappa_naive(path6)
    assert even.cost.flows == 7 and naive.cost.flows == 10 and even.value == naive.value == 1       # Quellen 0 und 1: 4 + 3 Flüsse gegen 10 nicht benachbarte Paare
    adj = MINI["zwei_werke"][0]
    even = A.global_kappa_even(adj)
    assert even.cost.flows == 6 and even.pair == (1, 4) and even.cut == (0,)                       # Quelle A: 2 Flüsse (k sinkt auf 2), Quelle B: 4 Flüsse (k sinkt auf 1)
    assert A.global_kappa_naive(adj).cost.flows == 14


def test_even_on_the_cycle_needs_every_pair_and_naive_agrees():
    adj = MINI["kreis5"][0]
    assert A.global_kappa_even(adj).cost.flows == A.global_kappa_naive(adj).cost.flows == 5


def test_even_falls_back_to_the_neighbours_of_the_weakest_location():
    adj = MINI["k33"][0]
    res = A.global_kappa_even(adj)
    assert res.value == 3 and res.cut == (3, 4, 5) and res.pair == (0, 1)                          # Mindestgrad 3, kein Fluss unterbietet ihn: Standort 0 wird von seinen Nachbarn getrennt


def test_global_lambda_uses_n_minus_one_flows_and_names_the_cut():
    adj = MINI["zwei_werke"][0]
    res = A.global_lambda(adj)
    assert res.value == 2 and res.cost.flows == 7 and res.pair == (0, 4) and res.cut == ((0, 4), (0, 5))


def test_complete_network_has_kappa_n_minus_one_without_any_flow():
    res = A.global_kappa_even(MINI["vollstaendig4"][0])
    assert res.value == 3 and res.cost.flows == 0 and res.pair == () and res.cut == ()
    assert A.nonadjacent_pairs(MINI["vollstaendig4"][0]) == []


def test_nonadjacent_pairs_and_all_pairs_kappa_on_the_cycle():
    adj = MINI["kreis5"][0]
    assert A.nonadjacent_pairs(adj) == [(0, 2), (0, 3), (1, 3), (1, 4), (2, 4)]
    kap, cost = A.all_pairs_kappa(adj)
    assert kap == {p: 2 for p in A.nonadjacent_pairs(adj)} and cost.flows == 5


def test_bottleneck_pairs_by_hand_in_the_two_works():
    adj = MINI["zwei_werke"][0]
    kap, _ = A.all_pairs_kappa(adj)
    assert len(kap) == 14 and kap[(1, 4)] == 1 and kap[(0, 6)] == 2
    assert len(A.bottleneck_pairs(adj, kap)) == 14                 # jedes nicht benachbarte Paar läuft über A, also ist κ(s, t) immer kleiner als der kleinere Grad


def test_bottleneck_pairs_empty_when_connectivity_equals_the_degrees():
    adj = MINI["k33"][0]
    kap, _ = A.all_pairs_kappa(adj)
    assert A.bottleneck_pairs(adj, kap) == []


def test_bruteforce_values_of_the_mini_networks():
    for name, (adj, kappa, lam, _delta) in MINI.items():
        assert A.kappa_bruteforce(adj) == kappa, name
        assert A.lambda_bruteforce(adj) == lam, name
    assert A.kappa_local_bruteforce(MINI["zwei_werke"][0], 1, 6) == 1 and A.kappa_local_bruteforce(MINI["kreis5"][0], 0, 2) == 2


def test_checkers_accept_true_and_reject_false_certificates():
    adj = MINI["kreis5"][0]
    assert A.is_vertex_separator(adj, 0, 2, (1, 4)) and not A.is_vertex_separator(adj, 0, 2, (1,)) and not A.is_vertex_separator(adj, 0, 2, (0, 1))
    assert A.is_edge_cut(adj, 0, 2, ((0, 1), (0, 4))) and not A.is_edge_cut(adj, 0, 2, ((0, 1),))
    assert A.valid_paths(adj, ((0, 1, 2), (0, 4, 3, 2)), 0, 2, "vertex")
    assert not A.valid_paths(adj, ((0, 1, 2), (0, 1, 2)), 0, 2, "vertex")             # gemeinsamer Zwischenstandort
    assert not A.valid_paths(adj, ((0, 1, 2), (0, 1, 2)), 0, 2, "edge")               # gemeinsame Leitung
    assert not A.valid_paths(adj, ((0, 2),), 0, 2, "vertex")                            # keine Leitung 0-2
    assert not A.valid_paths(adj, ((0, 1, 0, 1, 2),), 0, 2, "vertex")                   # Standort doppelt
    bow = MINI["schleife"][0]
    assert A.valid_paths(bow, ((0, 2, 3), (0, 1, 2, 4, 3)), 0, 3, "edge") and not A.valid_paths(bow, ((0, 2, 3), (0, 1, 2, 4, 3)), 0, 3, "vertex")   # beide Wege laufen über den Standort 2


def test_cost_adds_componentwise():
    assert A.Cost(1, 2, 3) + A.Cost(10, 20, 30) == A.Cost(11, 22, 33)


def test_degrees_and_min_degree():
    adj = MINI["zwei_werke"][0]
    assert A.degrees(adj) == [5, 3, 3, 3, 4, 4, 3, 3] and A.min_degree(adj) == 3 and A.min_degree(()) == 0


def test_edge_disjoint_paths_come_out_shortest_first_in_the_order_of_the_neighbours():
    res = A.local_lambda(MINI["vollstaendig4"][0], 0, 1)
    assert res.paths == ((0, 1), (0, 2, 1), (0, 3, 1))                       # die direkte Leitung, dann über 2, dann über 3: der Fluss findet kurze Wege zuerst


def test_a_cut_that_contains_the_start_or_the_goal_is_never_a_separator():
    adj = MINI["kreis5"][0]
    assert not A.is_vertex_separator(adj, 0, 2, (0, 1, 4)) and not A.is_vertex_separator(adj, 0, 2, (2, 3, 1)) and A.is_vertex_separator(adj, 0, 2, (1, 4))
