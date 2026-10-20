"""Jede Zahl im README (Abschnitt „Befunde“) wird hier über dieselben Experimentfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Zähler über feste Netze (je Netztyp zehn bzw. zwölf Netze, feste Zufalls-Seeds), nie ein einzelner Zufalls-Seed. Aufwand in Flüssen und Besuchen, nicht in Sekunden. Die Zahlen der Vormessung im Einzelplan
stammen aus Wegwerfskripten mit anderen Netzen und anderen Parametern (Verbundnetz dort ohne feste Regionsgröße); maßgeblich sind diese hier."""

import pytest

import mng_constants as C
import mng_evaluation as ev

from conftest import cached


def test_all_methods_agree_with_the_enumeration_on_every_small_network():
    rows = cached("exactness_rows")
    assert [r["label"] for r in rows] == ["Zufallsnetz, Grad 3", "Zufallsnetz, Grad 5", "Zufallsnetz, Grad 8", "Gitter", "Ring mit Abkürzungen", "Skalenfreies Netz", "Verbundnetz, Grad 8"]
    assert sum(r["nets"] for r in rows) == 84 and sum(r["checks"] for r in rows) == 6540 and sum(r["pairs"] for r in rows) == 3060 and sum(r["wrong"] for r in rows) == 0
    assert [r["checks"] for r in rows] == [1212, 924, 492, 636, 1068, 1140, 1068] and all(r["n"] == 12 for r in rows)


def test_the_minimum_degree_decides_everything_except_in_the_verbund_and_once_in_the_ring():
    rows = cached("pair_rows")
    assert [r["nets"] for r in rows] == [10] * 7 and all(r["violations"] == 0 for r in rows)
    assert [r["equal"] for r in rows] == [10, 10, 10, 10, 9, 10, 0] and sum(r["equal"] for r in rows) == 59
    assert [r["k_lt_l"] for r in rows] == [0, 0, 0, 0, 1, 0, 9] and [r["l_lt_d"] for r in rows] == [0, 0, 0, 0, 0, 0, 10]
    assert [r["n"] for r in rows] == [30, 30, 30, 25, 30, 30, 30]


def test_the_connectivity_means_per_network_type():
    rows = cached("pair_rows")
    assert [r["sum_d"] for r in rows] == [10, 15, 35, 20, 29, 20, 62] and [r["sum_l"] for r in rows] == [10, 15, 35, 20, 29, 20, 40] and [r["sum_k"] for r in rows] == [10, 15, 35, 20, 28, 20, 30]
    verbund = rows[-1]
    assert (verbund["sum_d"] / 10, verbund["sum_l"] / 10, verbund["sum_k"] / 10) == (6.2, 4.0, 3.0)


def test_the_share_of_pairs_with_a_bottleneck_per_network_type():
    rows = cached("pair_rows")
    assert [r["pairs"] for r in rows] == [3900, 3600, 3150, 2600, 3750, 3780, 3090] and sum(r["pairs"] for r in rows) == 23870
    assert [r["bottleneck"] for r in rows] == [581, 135, 0, 0, 1064, 317, 2960]
    assert [round(100 * r["bottleneck"] / r["pairs"], 1) for r in rows] == [14.9, 3.8, 0.0, 0.0, 28.4, 8.4, 95.8]
    assert [r["nets_with_bottleneck"] for r in rows] == [10, 8, 0, 0, 10, 10, 10]


def test_even_needs_a_fraction_of_the_flows_and_the_fraction_shrinks_with_the_size():
    rows = cached("even_rows")
    assert [(r["n"], r["nets"]) for r in rows[::7]] == [(20, 10), (40, 10), (80, 4)]
    factors = []
    for n in (20, 40, 80):
        part = [r for r in rows if r["n"] == n]
        factors.append(round(sum(r["naive_flows"] for r in part) / sum(r["even_flows"] for r in part), 1))
    assert factors == [3.1, 6.6, 13.8]
    big = [r for r in rows if r["n"] == 80]
    ratios = [r["naive_flows"] / r["even_flows"] for r in big]
    assert round(min(ratios), 1) == 9.5 and round(max(ratios), 1) == 20.0
    by_label = {(r["label"], r["n"]): r for r in rows}
    assert by_label[("Zufallsnetz, Grad 5", 80)]["naive_flows"] == 2960.0 and by_label[("Zufallsnetz, Grad 5", 80)]["even_flows"] == 148.0
    assert by_label[("Gitter", 40)]["naive_flows"] == 570.0 and by_label[("Gitter", 40)]["even_flows"] == 96.0
    assert all(r["even_flows"] < r["naive_flows"] for r in rows)


def test_the_verbund_connectivity_rises_with_the_number_of_links_between_the_regions():
    rows = cached("link_rows")
    assert [r["links"] for r in rows] == list(range(1, 9)) and all(r["nets"] == 10 for r in rows)
    assert [r["sum_k"] / 10 for r in rows] == [1.8, 2.8, 3.9, 4.5, 4.8, 4.8, 4.8, 4.8]
    assert [r["sum_l"] / 10 for r in rows] == [2.0, 4.0, 4.5, 4.7, 4.8, 4.8, 4.8, 4.8]
    assert [r["sum_d"] / 10 for r in rows] == [4.4, 4.4, 4.5, 4.7, 4.8, 4.8, 4.8, 4.8]
    assert [r["k_lt_l"] for r in rows] == [2, 10, 4, 2, 0, 0, 0, 0] and [r["l_lt_d"] for r in rows] == [10, 4, 0, 0, 0, 0, 0, 0]


def test_the_two_works_by_hand_and_in_the_app():
    a = ev.analyse(ev.Settings())
    assert (a.n, a.m, a.delta, a.lam_value, a.kappa) == (8, 14, 3, 2, 1) and (a.pairs, a.flows_naive, a.flows_even) == (14, 14, 6)


def test_the_presets_reproduce_the_readme_numbers():
    def a(name):
        return ev.analyse(ev.Settings(**C.PRESETS[name]))
    verbund = a("Die Engstelle im Verbundnetz")
    assert (verbund.delta, verbund.lam_value, verbund.kappa) == (5, 2, 2) and round(100 * verbund.bottleneck_share) == 84
    two = a("Standorte vor Leitungen: κ < λ")
    assert (two.delta, two.lam_value, two.kappa) == (5, 4, 3)
    ring = a("Ring: viele kleine Engstellen")
    assert round(100 * ring.bottleneck_share) == 45 and (ring.delta, ring.lam_value, ring.kappa) == (2, 2, 2)
    even = a("Even spart Flüsse")
    assert even.n == 80 and even.flows_naive > 2500 and even.flows_even < 300


def test_verdict_texts_quote_the_readme_numbers():
    x, p, e, link = cached("exactness_rows"), cached("pair_rows"), cached("even_rows"), cached("link_rows")
    assert "Auf 84 Netzen mit 12 Standorten (7 Netztypen) stimmen 6.540 Prüfungen" in ev.verdict_exact(x)[1] and "3.060 nicht benachbarten Standortpaare" in ev.verdict_exact(x)[1]
    assert "gilt κ = λ = Mindestgrad in 59 (84 %), κ < λ in 10 und λ < Mindestgrad in 10" in ev.verdict_whitney(p)[1]
    assert "in 59 von 60; im Verbundnetz in 0 von 10" in ev.verdict_whitney(p)[1] and "bei 6,2, der Kantenzusammenhang bei 4 und der Knotenzusammenhang bei 3" in ev.verdict_whitney(p)[1]
    assert "reicht von 0 % (Zufallsnetz, Grad 8) bis 96 % (Verbundnetz, Grad 8); gezählt über 23.870 Paare" in ev.verdict_bottleneck(p)[1]
    assert "Im Ring mit Abkürzungen sind es 28 %" in ev.verdict_bottleneck(p)[1]
    assert "das 3,1-, 6,6- und 13,8-Fache" in ev.verdict_even(e)[1] and "das 9,5- bis 20-Fache" in ev.verdict_even(e)[1]
    assert "bei 1 / 2 / 3 / 5 Leitungen liegt der Knotenzusammenhang κ im Mittel bei 1,8 / 2,8 / 3,9 / 4,8" in ev.verdict_links(link)[1]
    assert "Ab 5 Leitungen gilt κ = λ = Mindestgrad in allen Netzen." in ev.verdict_links(link)[1]


def test_the_experiment_grid_is_the_documented_one():
    assert C.EX_PAIR_N == 30 and C.EX_LINK_N == 45 and C.EX_EXACT_N == 12 and C.EX_EVEN == ((20, 10), (40, 10), (80, 4)) and len(C.SWEEP_SEEDS) == 10
    assert pytest.approx(C.DEFAULT_DEG) == 5.0
