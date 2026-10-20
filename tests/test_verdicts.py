"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds; ohne diese Datei überleben fast alle Mutanten der Verdikt-Arithmetik."""

import dataclasses

import mng_algorithm as A
import mng_evaluation as ev


# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

def _analysis(**over):
    a = ev.analyse(ev.Settings())                                                   # Lehrbeispiel: 8 Standorte, 14 Leitungen, Mindestgrad 3, λ = 2, κ = 1
    return dataclasses.replace(a, **over)


def test_question_names_the_chain_the_separator_and_the_costs():
    kind, text = ev.verdict_question(_analysis())
    assert kind == "info"
    assert "**Bei 8 Standorten und 14 Leitungen ist der Mindestgrad 3, der Kantenzusammenhang λ = 2 und der Knotenzusammenhang κ = 1.**" in text
    assert "Der Mindestgrad 3 verrät den Zusammenhang nicht: Fällt der Standort A aus, ist das Netz getrennt." in text
    assert "Alle 14 nicht benachbarten Paare einzeln brauchen 14 Flüsse, der Algorithmus von Even 6; 100 % der Paare sind schlechter verbunden als ihr kleinerer Grad." in text


def test_question_with_several_separating_locations_uses_the_plural():
    a = _analysis()
    kind, text = ev.verdict_question(dataclasses.replace(a, even=A.Global(2, (0, 6), (4, 5), a.even.cost)))
    assert "Fallen die Standorte E, F aus, ist das Netz getrennt." in text


def test_question_says_the_minimum_degree_is_enough_when_all_three_are_equal():
    a = ev.analyse(ev.Settings("random", 40, 5.0, 2, 3))
    kind, text = ev.verdict_question(a)
    assert a.kappa == a.lam_value == a.delta and "Der Mindestgrad sagt hier alles" in text and "verrät den Zusammenhang nicht" not in text


def test_question_of_a_complete_network_has_no_flow_and_no_pair():
    adj = tuple(tuple(w for w in range(4) if w != v) for v in range(4))
    a = ev.Analysis(ev.Settings(), _analysis().inst.__class__(adj, _analysis().inst.xy[:4], "random"), A.global_kappa_even(adj), A.global_kappa_naive(adj), A.global_lambda(adj), {}, ())
    text = ev.verdict_question(a)[1]
    assert text.startswith("**Bei 4 Standorten und 6 Leitungen ist der Mindestgrad 3,") and "Das Netz ist vollständig" in text


# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

def _x_row(label="Zufallsnetz, Grad 3", nets=12, pairs=576, checks=1212, wrong=0, n=12):
    return {"label": label, "nets": nets, "pairs": pairs, "checks": checks, "wrong": wrong, "n": n}


def test_exact_counts_nets_checks_and_pairs_and_warns_on_any_deviation():
    kind, text = ev.verdict_exact([_x_row(), _x_row("Gitter", pairs=288, checks=636)])
    assert kind == "info"
    assert ("Auf 24 Netzen mit 12 Standorten (2 Netztypen) stimmen 1.848 Prüfungen mit der Aufzählung aller Trennmengen überein: der Zusammenhang des Netzes nach beiden Verfahren, die Zeugen "
            "(trennende Mengen) und jedes der 864 nicht benachbarten Standortpaare mit seinen disjunkten Wegen. Abweichungen: 0.") == text
    kind2, text2 = ev.verdict_exact([_x_row(), _x_row("Gitter", pairs=288, checks=636, wrong=3)])
    assert kind2 == "warning" and text2 == "Auf 24 Netzen weichen 3 von 1.848 Prüfungen von der Aufzählung ab."


# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

def _p_row(kind="random", label="Zufallsnetz, Grad 5", nets=10, equal=10, k_lt_l=0, l_lt_d=0, violations=0, sum_k=20, sum_l=20, sum_d=20, pairs=3600, bottleneck=135, with_bn=8, n=30):
    return {"kind": kind, "label": label, "nets": nets, "equal": equal, "k_lt_l": k_lt_l, "l_lt_d": l_lt_d, "violations": violations, "sum_k": sum_k, "sum_l": sum_l, "sum_d": sum_d,
            "pairs": pairs, "bottleneck": bottleneck, "nets_with_bottleneck": with_bn, "n": n}


def test_whitney_counts_the_cases_and_compares_the_verbund_with_the_rest():
    rows = [_p_row(), _p_row("ring", "Ring mit Abkürzungen", equal=9, k_lt_l=1, sum_k=28, sum_l=29, sum_d=29),
            _p_row("verbund", "Verbundnetz, Grad 8", equal=0, k_lt_l=9, l_lt_d=10, sum_k=30, sum_l=40, sum_d=62)]
    kind, text = ev.verdict_whitney(rows)
    assert kind == "info"
    assert ("Auf 30 Netzen (3 Netztypen mit je 10, bis 30 Standorte) gilt κ = λ = Mindestgrad in 19 (63 %), κ < λ in 10 und λ < Mindestgrad in 10; die Kette κ ≤ λ ≤ Mindestgrad ist in 0 Netzen verletzt. "
            "Ohne das Verbundnetz gilt κ = λ = Mindestgrad in 19 von 20; im Verbundnetz in 0 von 10: dort liegt der Mindestgrad im Mittel bei 6,2, der Kantenzusammenhang bei 4 und der "
            "Knotenzusammenhang bei 3.") == text
    assert ev.verdict_whitney([_p_row(violations=1)])[0] == "warning"
    assert "Ohne das Verbundnetz" not in ev.verdict_whitney([_p_row()])[1]


# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

def test_bottleneck_names_the_smallest_and_largest_share_and_the_ring():
    rows = [_p_row(label="Gitter", kind="grid", pairs=2600, bottleneck=0, with_bn=0), _p_row(kind="ring", label="Ring mit Abkürzungen", pairs=3750, bottleneck=1064, with_bn=10),
            _p_row(kind="verbund", label="Verbundnetz, Grad 8", pairs=3090, bottleneck=2960, with_bn=10)]
    kind, text = ev.verdict_bottleneck(rows)
    assert kind == "info"
    assert ("Der Anteil der nicht benachbarten Standortpaare, die schlechter verbunden sind als ihr kleinerer Grad, reicht von 0 % (Gitter) bis 96 % (Verbundnetz, Grad 8); gezählt über 9.440 Paare auf "
            "30 Netzen. Im Ring mit Abkürzungen sind es 28 %, und in 10 von 10 Netzen gibt es mindestens ein solches Paar.") == text
    assert "Im Ring" not in ev.verdict_bottleneck(rows[:1] + rows[2:])[1]


# --- Experiment 4 --------------------------------------------------------------------------------------------------------------------------

def _e_row(label="Zufallsnetz, Grad 5", n=20, naive=140.0, even=41.3):
    return {"label": label, "n": n, "naive_flows": naive, "even_flows": even}


def test_even_names_the_factors_per_size_and_the_range_at_the_largest_size():
    rows = [_e_row(n=20, naive=100.0, even=50.0), _e_row("Gitter", n=20, naive=100.0, even=25.0), _e_row(n=40, naive=700.0, even=70.0), _e_row("Gitter", n=40, naive=500.0, even=50.0),
            _e_row(n=80, naive=3000.0, even=150.0), _e_row("Gitter", n=80, naive=3000.0, even=300.0)]
    kind, text = ev.verdict_even(rows)
    assert kind == "info"
    assert ("Der Algorithmus von Even braucht bei 20, 40 und 80 Standorten im Mittel über die Netztypen das 2,7-, 10- und 13,3-Fache weniger Flüsse als alle Paare einzeln; bei 80 Standorten "
            "je nach Netztyp das 10- bis 20-Fache.") == text
    kind2, text2 = ev.verdict_even(rows[:2] + [_e_row(n=40, naive=50.0, even=60.0)])
    assert kind2 == "warning" and "nicht überall weniger Flüsse" in text2 and "bei 40 Standorten" in text2


# --- Experiment 5 --------------------------------------------------------------------------------------------------------------------------

def _l_row(links, k, la, d, k_lt_l=0, l_lt_d=0, nets=10):
    return {"links": links, "nets": nets, "sum_k": k * nets, "sum_l": la * nets, "sum_d": d * nets, "k_lt_l": k_lt_l, "l_lt_d": l_lt_d}


def test_links_names_the_means_for_one_two_three_and_five_links_and_the_first_equal_case():
    rows = [_l_row(1, 1.8, 2.0, 4.4, 2, 10), _l_row(2, 2.8, 4.0, 4.4, 10, 4), _l_row(3, 3.9, 4.5, 4.5, 4, 0), _l_row(4, 4.5, 4.7, 4.7, 2, 0), _l_row(5, 4.8, 4.8, 4.8), _l_row(6, 4.8, 4.8, 4.8)]
    kind, text = ev.verdict_links(rows)
    assert kind == "info"
    assert ("Im Verbundnetz mit mittlerem Grad 8 steigt der Zusammenhang mit der Zahl der Leitungen zwischen je zwei Regionen: bei 1 / 2 / 3 / 5 Leitungen liegt der Knotenzusammenhang κ im Mittel "
            "bei 1,8 / 2,8 / 3,9 / 4,8, der Kantenzusammenhang λ bei 2 / 4 / 4,5 / 4,8 und der Mindestgrad bei 4,4 / 4,4 / 4,5 / 4,8 (je 10 Netze). Ab 5 Leitungen gilt κ = λ = Mindestgrad in allen Netzen.") == text


def test_links_warns_when_kappa_falls_and_omits_the_equal_sentence_without_such_a_case():
    rows = [_l_row(1, 3.0, 3.0, 4.0, 0, 10), _l_row(2, 2.0, 3.0, 4.0, 5, 10)]
    kind, text = ev.verdict_links(rows)
    assert kind == "warning" and "Ab " not in text
