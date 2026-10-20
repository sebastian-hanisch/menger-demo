"""Netz-Erzeuger: einfach, zusammenhängend, deterministisch, dokumentierte Größen."""

import math

import pytest

import mng_algorithm as A
import mng_constants as C
import mng_scenario as S


class FixedRandom:
    """Liefert immer fast 1: die Fisher–Yates-Mischung lässt die Reihenfolge unverändert, `_below` gibt immer k - 1 zurück."""

    def random(self):
        return 0.999999


def _is_simple_and_symmetric(adj):
    for u, nbs in enumerate(adj):
        assert list(nbs) == sorted(set(nbs)) and u not in nbs
        for v in nbs:
            assert u in adj[v]
    return True


def test_below_stays_in_range_and_shuffle_with_a_fixed_source_is_the_identity():
    assert S._below(FixedRandom(), 5) == 4 and S._below(FixedRandom(), 1) == 0
    assert S._shuffle(range(6), FixedRandom()) == [0, 1, 2, 3, 4, 5]
    assert sorted(S._shuffle(range(10), S.make_rng(3, 1))) == list(range(10))


def test_random_connected_with_a_fixed_source_is_the_path():
    assert S.random_connected(5, 4, FixedRandom()) == [(0, 1), (1, 2), (2, 3), (3, 4)]


def test_random_connected_has_the_documented_number_of_edges():
    rng = S.make_rng(1, 1)
    assert len(S.random_connected(10, 3, rng)) == 9              # mindestens ein Baum
    assert len(S.random_connected(10, 20, S.make_rng(1, 2))) == 20
    assert len(S.random_connected(5, 999, S.make_rng(1, 3))) == 10   # höchstens alle Paare


def test_grid_pairs_and_the_grid_network():
    assert S.grid_pairs(2) == [(0, 1), (0, 2), (1, 3), (2, 3)]
    inst = S.make_instance("grid", 30, seed=1)
    assert inst.n == 25 and inst.m == 40 and sorted(A.degrees(inst.adj)) == [2] * 4 + [3] * 12 + [4] * 9


def test_scalefree_has_the_documented_number_of_links():
    for n in (6, 20, 50):
        inst = S.make_instance("scalefree", n, seed=4)
        assert inst.n == n and inst.m == 3 + 2 * (n - 3)


def test_ring_without_rewiring_is_four_regular():
    pairs = S.ring_pairs(12, FixedRandom(), rewire=0.0)
    adj = S._adj_from_pairs(12, pairs)
    assert set(A.degrees(adj)) == {4} and len(pairs) == 24


def test_verbund_has_the_given_number_of_links_between_every_two_regions():
    for links in (1, 3, 5):
        inst = S.make_instance("verbund", 36, 6.0, links, 2)
        sizes = S.region_sizes(36)
        bounds = [0, sizes[0], sizes[0] + sizes[1], 36]
        region = lambda v: next(i for i in range(3) if bounds[i] <= v < bounds[i + 1])   # noqa: E731
        between = {}
        for u, v in inst.edges:
            if region(u) != region(v):
                key = (region(u), region(v))
                between[key] = between.get(key, 0) + 1
        assert between == {(0, 1): links, (0, 2): links, (1, 2): links}


def test_region_sizes_split_the_network_evenly():
    assert S.region_sizes(10) == [4, 3, 3] and S.region_sizes(9) == [3, 3, 3] and sum(S.region_sizes(47)) == 47


def test_textbook_network_by_hand():
    inst = S.make_instance("textbook", 99)
    assert inst.n == 8 and inst.m == 14 and inst.labels == S.TEXTBOOK_LABELS and inst.name(0) == "A" and inst.name(7) == "H"
    assert A.whitney(inst.adj) == (1, 2, 3)


@pytest.mark.parametrize("kind", [k for k in C.KINDS])
def test_every_kind_gives_a_simple_connected_network_that_is_deterministic(kind):
    for seed in (1, 2, 3):
        inst = S.make_instance(kind, 30, 4.0, 2, seed)
        assert _is_simple_and_symmetric(inst.adj) and len(S._components(inst.adj)) == 1
        assert inst.xy.shape == (inst.n, 2) and abs(inst.xy).max() < 10
        again = S.make_instance(kind, 30, 4.0, 2, seed)
        assert again.adj == inst.adj and (again.xy == inst.xy).all()
    if kind not in ("textbook", "grid"):
        assert S.make_instance(kind, 30, 4.0, 2, 1).adj != S.make_instance(kind, 30, 4.0, 2, 2).adj


def test_the_network_size_follows_the_setting_except_for_the_grid_and_the_textbook():
    for kind in ("random", "ring", "scalefree", "verbund"):
        assert S.make_instance(kind, 37, 4.0, 2, 1).n == 37
    assert S.make_instance("grid", 37).n == 36 and S.make_instance("textbook", 37).n == 8


def test_random_network_has_the_requested_mean_degree():
    inst = S.make_instance("random", 40, 6.0, 2, 1)
    assert inst.m == 120 and sum(A.degrees(inst.adj)) / inst.n == 6.0


def test_unknown_kind_and_tiny_networks_are_rejected():
    with pytest.raises(ValueError):
        S.make_instance("sternfoermig", 10)
    with pytest.raises(ValueError):
        S.make_instance("random", 3)


def test_spring_layout_is_finite_scaled_and_deterministic():
    pairs = S.random_connected(15, 25, S.make_rng(1, 1))
    pos1 = S.spring_layout(15, pairs, S.make_rng(9, 9))
    pos2 = S.spring_layout(15, pairs, S.make_rng(9, 9))
    assert pos1.shape == (15, 2) and (pos1 == pos2).all() and math.isfinite(float(pos1.sum())) and abs(pos1).max() <= 1.0 + 1e-9
    assert S.spring_layout(1, [], S.make_rng(1, 1)).shape == (1, 2)


def test_ensure_connected_joins_every_component_to_location_zero():
    assert S._ensure_connected(6, [(1, 2), (3, 4)]) == [(0, 1), (0, 3), (0, 5), (1, 2), (3, 4)]
    assert S._ensure_connected(3, [(0, 1), (1, 2)]) == [(0, 1), (1, 2)]


def test_instance_properties_and_names():
    inst = S.make_instance("random", 12, 4.0, 2, 5)
    assert inst.n == 12 and inst.m == len(inst.edges) and inst.name(0) == "1" and inst.name(11) == "12"
    assert all(u < v for u, v in inst.edges)
