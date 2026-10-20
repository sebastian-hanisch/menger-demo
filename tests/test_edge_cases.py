"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): kleinste Netze, Grenzen inklusive, Start gleich Ziel, vollständige und unzusammenhängende Netze, Regler-Extreme."""

import pytest

import mng_algorithm as A
import mng_constants as C
import mng_evaluation as ev
import mng_scenario as S

from conftest import _adj


def test_a_single_location_has_no_connectivity_and_no_pairs():
    adj = ((),)
    assert A.global_kappa_even(adj).value == A.global_kappa_naive(adj).value == 0 and A.global_lambda(adj).value == 0
    assert A.min_degree(adj) == 0 and A.nonadjacent_pairs(adj) == []
    assert A.kappa_bruteforce(adj) == 0 and A.lambda_bruteforce(adj) == 0


def test_two_locations_with_a_link_are_a_complete_network():
    adj = _adj(2, [(0, 1)])
    assert A.global_kappa_even(adj).value == 1 and A.global_lambda(adj).value == 1 and A.global_kappa_even(adj).cost.flows == 0
    assert A.kappa_bruteforce(adj) == 1 and A.lambda_bruteforce(adj) == 1


def test_two_locations_without_a_link_have_connectivity_zero():
    adj = _adj(2, [])
    res = A.global_kappa_even(adj)
    assert res.value == 0 and A.global_kappa_naive(adj).value == 0 and A.global_lambda(adj).value == 0 and res.cut == ()
    assert A.local_kappa(adj, 0, 1).value == 0 and A.local_kappa(adj, 0, 1).paths == () and A.local_lambda(adj, 0, 1).cut == ()


def test_a_network_with_two_components_has_connectivity_zero_and_a_valid_empty_cut():
    adj = _adj(6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)])
    assert A.whitney(adj) == (0, 0, 2) and A.kappa_bruteforce(adj) == 0 and A.lambda_bruteforce(adj) == 0
    res = A.global_kappa_even(adj)
    assert res.value == 0 and A.is_vertex_separator(adj, res.pair[0], res.pair[1], res.cut)


def test_complete_network_of_five_has_kappa_four_and_no_flow():
    adj = tuple(tuple(w for w in range(5) if w != v) for v in range(5))
    assert A.whitney(adj) == (4, 4, 4) and A.global_kappa_naive(adj).cost.flows == 0 and A.kappa_bruteforce(adj) == 4


def test_star_has_connectivity_one_and_the_centre_is_the_cut():
    adj = _adj(6, [(0, v) for v in range(1, 6)])
    res = A.global_kappa_even(adj)
    assert res.value == 1 and res.cut == (0,) and A.global_lambda(adj).value == 1


def test_adjacent_locations_have_no_vertex_flow_but_an_edge_flow():
    adj = _adj(4, [(0, 1), (1, 2), (2, 3), (0, 3)])
    with pytest.raises(ValueError):
        A.local_kappa(adj, 0, 1)
    assert A.local_lambda(adj, 0, 1).value == 2                    # die Leitung selbst und der Umweg über 3 und 2


def test_start_equals_goal_is_rejected_everywhere():
    adj = _adj(4, [(0, 1), (1, 2), (2, 3)])
    for fn in (A.local_kappa, A.local_lambda):
        with pytest.raises(ValueError):
            fn(adj, 2, 2)


def test_flow_between_locations_in_different_components_is_empty():
    adj = _adj(4, [(0, 1), (2, 3)])
    res = A.local_lambda(adj, 0, 3)
    assert res.value == 0 and res.paths == () and res.cut == () and res.side == (0, 1)


def test_the_minimum_and_maximum_network_sizes_validate_for_every_kind():
    for kind in C.KINDS:
        for n in (C.N_MIN, 20):
            a = ev.analyse(ev.Settings(kind, n, 4.0, 2, 3))
            assert ev.validate(a) == [] and a.n >= 4
    big = ev.analyse(ev.Settings("grid", C.N_MAX, seed=1))
    assert big.n == 81 and ev.validate(big) == [] and big.flows_naive == 81 * 80 // 2 - big.m


def test_the_regler_extremes_of_the_verbund_validate():
    for links in (C.LINKS_MIN, C.LINKS_MAX):
        for deg in (C.DEG_MIN, C.DEG_MAX):
            a = ev.analyse(ev.Settings("verbund", 30, deg, links, 5))
            assert ev.validate(a) == [] and a.kappa <= a.lam_value <= a.delta


def test_a_network_without_nonadjacent_pairs_has_no_bottlenecks_and_no_saving():
    adj = tuple(tuple(w for w in range(5) if w != v) for v in range(5))
    inst = S.Instance(adj, S.np.zeros((5, 2)), "random")
    a = ev.Analysis(ev.Settings(), inst, A.global_kappa_even(adj), A.global_kappa_naive(adj), A.global_lambda(adj), {}, ())
    assert a.pairs == 0 and a.bottleneck_share == 0.0 and a.saving == 0.0 and ev.validate(a) == []
    assert "vollständig" in ev.verdict_question(a)[1]


def test_the_tree_plus_extra_edges_generator_survives_the_smallest_density():
    inst = S.make_instance("random", 8, C.DEG_MIN, 2, 1)
    assert inst.m >= 7 and A.global_kappa_even(inst.adj).value >= 1
