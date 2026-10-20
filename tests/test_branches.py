"""Zweige der Hauptansicht (Nullspalte-Lehre): Jeder Weg, den die App zeigt, kommt in mindestens einem Preset oder einem festen Netz vor.

Ein Preset, das seine Beschreibung nicht einlöst (z. B. „Der Mindestgrad sagt fast alles“ mit einer Engstelle im Netz), fällt hier auf."""

import dataclasses

import pytest

import mng_constants as C
import mng_evaluation as ev


def _a(name, **over):
    return ev.analyse(ev.Settings(**{**C.PRESETS[name], **over}))


def test_lehrbeispiel_has_a_strict_chain_and_every_pair_is_a_bottleneck():
    a = _a("Lehrbeispiel (zwei Werke)")
    assert (a.delta, a.lam_value, a.kappa) == (3, 2, 1) and a.bottleneck_share == 1.0 and ev.verdict_question(a)[0] == "info"


def test_the_minimum_degree_says_it_all_in_its_preset():
    a = _a("Der Mindestgrad sagt fast alles")
    assert a.kappa == a.lam_value == a.delta and a.bottleneck_share < 0.1 and "Der Mindestgrad sagt hier alles" in ev.verdict_question(a)[1]


def test_the_bottleneck_hangs_at_one_link_in_the_verbund_preset():
    a = _a("Die Engstelle im Verbundnetz")
    assert a.kappa == a.lam_value == 2 and a.delta == 5 and a.bottleneck_share > 0.5 and len(a.even.cut) == 2


def test_two_links_put_the_vertex_connectivity_below_the_edge_connectivity_in_its_preset():
    a = _a("Standorte vor Leitungen: κ < λ")
    assert (a.kappa, a.lam_value, a.delta) == (3, 4, 5) and len(a.even.cut) == 3


def test_the_ring_has_many_pairs_with_a_bottleneck_in_its_preset():
    a = _a("Ring: viele kleine Engstellen")
    assert a.bottleneck_share > 0.3 and a.kappa == a.lam_value == a.delta == 2


def test_even_saves_many_flows_in_its_preset():
    a = _a("Even spart Flüsse")
    assert a.n == 80 and a.flows_naive > 2500 and a.saving > 10 and a.flows_even == a.even.cost.flows


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_passes_the_validation(name):
    a = _a(name)
    assert ev.validate(a) == []
    view = ev.pair_view(a, 0, a.n - 1)
    assert ev.validate_pair(a, view) == []


def test_the_pair_view_covers_adjacent_and_nonadjacent_pairs_in_one_network():
    a = _a("Der Mindestgrad sagt fast alles")
    adj = a.inst.adj
    s, t_adjacent = 0, adj[0][0]
    t_far = next(v for v in range(1, a.n) if v not in adj[0])
    assert ev.pair_view(a, s, t_adjacent).kappa is None and ev.pair_view(a, s, t_far).kappa is not None


def test_the_settings_are_immutable_and_hashable_for_the_cache():
    s = ev.Settings()
    assert hash(s) == hash(ev.Settings()) and dataclasses.replace(s, links=3) != s
