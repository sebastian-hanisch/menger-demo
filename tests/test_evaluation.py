"""Auswertung: Analyse des Lehrbeispiels von Hand, Prüfung vor der Anzeige, Paaransicht, Formate."""

import dataclasses

import mng_algorithm as A
import mng_constants as C
import mng_evaluation as ev


def _textbook():
    return ev.analyse(ev.Settings())


def test_analysis_of_the_two_works_by_hand():
    a = _textbook()
    assert (a.n, a.m, a.delta, a.kappa, a.lam_value) == (8, 14, 3, 1, 2)
    assert a.pairs == 14 and len(a.bottlenecks) == 14 and a.bottleneck_share == 1.0
    assert (a.flows_naive, a.flows_even) == (14, 6) and a.saving == 14 / 6
    assert a.even.pair == (1, 4) and a.even.cut == (0,) and a.naive.value == 1 and a.lam.pair == (0, 4)
    assert a.kappas[(1, 4)] == 1 and a.kappas[(0, 6)] == 2 and ev.validate(a) == []


def test_default_settings_are_the_constants_and_the_textbook():
    s = ev.Settings()
    assert (s.kind, s.n, s.deg, s.links, s.seed) == (C.DEFAULT_KIND, C.DEFAULT_N, C.DEFAULT_DEG, C.DEFAULT_LINKS, C.DEFAULT_SEED) and s.kind == "textbook"


def test_the_same_settings_give_the_same_analysis_and_the_seed_changes_the_network():
    s = ev.Settings("random", 20, 5.0, 2, 3)
    assert ev.analyse(s) == ev.analyse(s) and ev.analyse(s).inst.adj == ev.analyse(s).inst.adj
    assert ev.analyse(s).inst.adj != ev.analyse(dataclasses.replace(s, seed=4)).inst.adj


def test_analysis_of_a_network_with_unequal_chain_uses_the_first_minimal_pair_for_the_naive_cut():
    a = _textbook()
    assert a.naive.pair == (1, 4) and a.naive.cut == (0,)                       # kleinster Wert 1, kleinstes Paar (1, 4)


def test_validate_names_every_kind_of_error():
    a = _textbook()
    assert ev.validate(a) == []
    assert any("verschiedene Knotenzusammenhänge" in p for p in ev.validate(dataclasses.replace(a, naive=A.Global(2, a.naive.pair, a.naive.cut, a.naive.cost))))
    assert any("Kette" in p for p in ev.validate(dataclasses.replace(a, even=A.Global(4, a.even.pair, a.even.cut, a.even.cost), naive=A.Global(4, a.naive.pair, a.naive.cut, a.naive.cost))))
    assert any("Trennmenge" in p for p in ev.validate(dataclasses.replace(a, even=A.Global(1, (1, 4), (2,), a.even.cost))))
    assert any("Schnitt des Kantenzusammenhangs" in p for p in ev.validate(dataclasses.replace(a, lam=A.Global(2, (0, 4), ((0, 4),), a.lam.cost))))
    assert any("Zahl der Flüsse" in p for p in ev.validate(dataclasses.replace(a, naive=A.Global(1, a.naive.pair, a.naive.cut, A.Cost(3, 3, 3)))))
    wrong_value = dataclasses.replace(a, even=A.Global(2, a.even.pair, a.even.cut, a.even.cost), naive=A.Global(2, a.naive.pair, a.naive.cut, a.naive.cost))
    assert any("Aufzählung" in p for p in ev.validate(wrong_value))


def test_pair_view_of_the_textbook_by_hand():
    a = _textbook()
    v = ev.pair_view(a, 1, 6)                                                      # B nach G
    assert not v.adjacent and v.kappa.value == 1 and v.kappa.cut == (0,) and v.lam.value == 2 and (v.deg_s, v.deg_t) == (3, 3)
    assert ev.validate_pair(a, v) == []
    adjacent = ev.pair_view(a, 0, 1)                                               # A und B sind verbunden
    assert adjacent.adjacent and adjacent.kappa is None and adjacent.lam.value == 3 and ev.validate_pair(a, adjacent) == []


def test_validate_pair_names_every_kind_of_error():
    a = _textbook()
    v = ev.pair_view(a, 1, 6)
    bad_paths = dataclasses.replace(v, kappa=dataclasses.replace(v.kappa, paths=((1, 0, 4, 6), (1, 0, 5, 6))))
    assert any("nicht knotendisjunkt" in p for p in ev.validate_pair(a, bad_paths))
    bad_cut = dataclasses.replace(v, kappa=dataclasses.replace(v.kappa, cut=(2,)))
    assert any("trennende Standortmenge" in p for p in ev.validate_pair(a, bad_cut))
    bad_lam = dataclasses.replace(v, lam=dataclasses.replace(v.lam, cut=((0, 4),)))
    assert any("Leitungsschnitt" in p for p in ev.validate_pair(a, bad_lam))
    bad_edge_paths = dataclasses.replace(v, lam=dataclasses.replace(v.lam, paths=v.lam.paths[:1]))
    assert any("kantendisjunkt" in p for p in ev.validate_pair(a, bad_edge_paths))
    bad_chain = dataclasses.replace(v, deg_s=0)
    assert any("Kette" in p for p in ev.validate_pair(a, bad_chain))
    bad_brute = dataclasses.replace(v, kappa=dataclasses.replace(v.kappa, value=2, paths=((1, 0, 4, 6), (1, 2, 3, 0, 5, 7, 6))[:2], cut=(0, 4)))
    assert any("Aufzählung" in p or "nicht knotendisjunkt" in p for p in ev.validate_pair(a, bad_brute))


def test_number_formats():
    assert ev._i(1234567) == "1.234.567" and ev._dec(12.5) == "12,5" and ev._dec(12.0) == "12" and ev._dec(1.08333, 3) == "1,083" and ev._dec(1234.5) == "1.234,5"
    assert ev._pct(0.4567) == "46" and ev._pct(0.4567, 1) == "45,7" and ev._pct(1.0) == "100" and ev._pct(0.0) == "0"
