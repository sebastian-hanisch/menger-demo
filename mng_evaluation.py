"""Kennzahlen, Prüfung der Ergebnisse und Verdikte. Verdikte sind reine Funktionen (Art, Text): Zahlen kommen aus den Zeilen, nie aus dem Text.

Standorte sind in der Anzeige ab 1 nummeriert (`inst.name`), im Kern ab 0 (das Lehrbeispiel hat Buchstaben)."""

from dataclasses import dataclass, field

import mng_algorithm as A
import mng_constants as C
import mng_scenario as S


@dataclass(frozen=True)
class Settings:
    kind: str = C.DEFAULT_KIND
    n: int = C.DEFAULT_N
    deg: float = C.DEFAULT_DEG
    links: int = C.DEFAULT_LINKS
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    inst: S.Instance = field(compare=False, repr=False)
    even: A.Global = field(compare=False)
    naive: A.Global = field(compare=False)
    lam: A.Global = field(compare=False)
    kappas: dict = field(compare=False, repr=False)       # {(s, t): kappa(s, t)} für alle nicht benachbarten Paare s < t
    bottlenecks: tuple = field(compare=False, repr=False)  # Paare mit kappa(s, t) < kleinerer Grad

    @property
    def n(self):
        return self.inst.n

    @property
    def m(self):
        return self.inst.m

    @property
    def delta(self):
        return A.min_degree(self.inst.adj)

    @property
    def kappa(self):
        return self.even.value

    @property
    def lam_value(self):
        return self.lam.value

    @property
    def pairs(self):
        return len(self.kappas)

    @property
    def bottleneck_share(self):
        return len(self.bottlenecks) / self.pairs if self.pairs else 0.0

    @property
    def flows_naive(self):
        return self.naive.cost.flows

    @property
    def flows_even(self):
        return self.even.cost.flows

    @property
    def saving(self):
        return self.flows_naive / self.flows_even if self.flows_even else 0.0


def analyse(settings: Settings) -> Analysis:
    inst = S.make_instance(settings.kind, settings.n, settings.deg, settings.links, settings.seed)
    adj = inst.adj
    kappas, pair_cost = A.all_pairs_kappa(adj)
    if kappas:
        pair = min(kappas, key=lambda p: (kappas[p], p))
        naive = A.Global(kappas[pair], pair, A.local_kappa(adj, pair[0], pair[1]).cut, pair_cost)
    else:
        naive = A.Global(max(inst.n - 1, 0), (), (), pair_cost)
    return Analysis(settings, inst, A.global_kappa_even(adj), naive, A.global_lambda(adj), kappas, tuple(A.bottleneck_pairs(adj, kappas)))


def validate(a: Analysis) -> list:
    """Unabhängige Prüfung vor der Anzeige: gibt die Liste der Probleme zurück (leer = alles in Ordnung)."""
    problems = []
    adj = a.inst.adj
    if a.even.value != a.naive.value:
        problems.append(f"Even ({a.even.value}) und alle Paare einzeln ({a.naive.value}) liefern verschiedene Knotenzusammenhänge")
    if not (a.kappa <= a.lam.value <= a.delta):
        problems.append(f"Die Kette kappa <= lambda <= Mindestgrad ist verletzt ({a.kappa}, {a.lam.value}, {a.delta})")
    for name, res in (("Even", a.even), ("alle Paare", a.naive)):
        if res.pair and res.pair[1] not in adj[res.pair[0]]:
            if len(res.cut) != res.value or not A.is_vertex_separator(adj, res.pair[0], res.pair[1], res.cut):
                problems.append(f"Die Trennmenge von {name} trennt das Paar nicht oder hat die falsche Größe")
    if a.lam.pair and (len(a.lam.cut) != a.lam.value or not A.is_edge_cut(adj, a.lam.pair[0], a.lam.pair[1], a.lam.cut)):
        problems.append("Der Schnitt des Kantenzusammenhangs trennt das Paar nicht oder hat die falsche Größe")
    if a.n <= C.BRUTE_N:
        if A.kappa_bruteforce(adj) != a.kappa:
            problems.append("Knotenzusammenhang weicht von der Aufzählung ab")
        if A.lambda_bruteforce(adj) != a.lam.value:
            problems.append("Kantenzusammenhang weicht von der Aufzählung ab")
    if a.flows_naive != len(A.nonadjacent_pairs(adj)):
        problems.append("Die Zahl der Flüsse aller Paare stimmt nicht mit der Zahl der nicht benachbarten Paare überein")
    return problems


@dataclass(frozen=True)
class PairView:
    s: int
    t: int
    adjacent: bool
    kappa: A.Local | None
    lam: A.Local
    deg_s: int
    deg_t: int


def pair_view(a: Analysis, s: int, t: int) -> PairView:
    adj = a.inst.adj
    adjacent = t in adj[s]
    kap = None if adjacent else A.local_kappa(adj, s, t)
    return PairView(s, t, adjacent, kap, A.local_lambda(adj, s, t), len(adj[s]), len(adj[t]))


def validate_pair(a: Analysis, v: PairView) -> list:
    adj = a.inst.adj
    problems = []
    if v.kappa is not None:
        k = v.kappa
        if len(k.paths) != k.value or not A.valid_paths(adj, k.paths, v.s, v.t, "vertex"):
            problems.append("Die Wege zwischen den Standorten sind nicht knotendisjunkt oder ihre Zahl stimmt nicht")
        if len(k.cut) != k.value or not A.is_vertex_separator(adj, v.s, v.t, k.cut):
            problems.append("Die trennende Standortmenge trennt das Paar nicht oder hat die falsche Größe")
        if a.n <= C.BRUTE_N and A.kappa_local_bruteforce(adj, v.s, v.t) != k.value:
            problems.append("Der Knotenzusammenhang des Paares weicht von der Aufzählung ab")
    el = v.lam
    if len(el.paths) != el.value or not A.valid_paths(adj, el.paths, v.s, v.t, "edge"):
        problems.append("Die Wege zwischen den Standorten sind nicht kantendisjunkt oder ihre Zahl stimmt nicht")
    if len(el.cut) != el.value or not A.is_edge_cut(adj, v.s, v.t, el.cut):
        problems.append("Der Leitungsschnitt trennt das Paar nicht oder hat die falsche Größe")
    if v.kappa is not None and not (v.kappa.value <= el.value <= min(v.deg_s, v.deg_t)):
        problems.append("Die Kette kappa(s, t) <= lambda(s, t) <= kleinerer Grad ist für das Paar verletzt")
    return problems


# --- Formate ---------------------------------------------------------------------------------------------------------------------------------------


def _i(x) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner."""
    return f"{x:,.0f}".replace(",", ".")


def _dec(x, digits=1) -> str:
    """Zahl mit Komma; ganze Werte ohne Nachkommastelle."""
    x = float(x)
    if x == int(x):
        return _i(x)
    return f"{x:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(share, digits=0) -> str:
    return _dec(round(100.0 * share, digits), digits) if digits else _i(round(100.0 * share))


# --- Verdikte -------------------------------------------------------------------------------------------------------------------------------------


def verdict_question(a: Analysis):
    """Kernfrage: Zusammenhang des Netzes und was die Verfahren dafür aufwenden."""
    if a.n < 2:
        return "info", "Es gibt keine Standortpaare."
    names = ", ".join(a.inst.name(v) for v in a.even.cut)
    head = (f"**Bei {_i(a.n)} Standorten und {_i(a.m)} Leitungen ist der Mindestgrad {a.delta}, der Kantenzusammenhang λ = {a.lam.value} und der Knotenzusammenhang κ = {a.kappa}.**")
    if a.pairs == 0:
        return "info", head + " Das Netz ist vollständig: Jeder Standort ist mit jedem verbunden, es gibt kein nicht benachbartes Paar und keinen Fluss."
    if a.kappa == a.delta and a.lam.value == a.delta:
        chain = " Der Mindestgrad sagt hier alles: Es gibt keine Engstelle, die schlechter wäre als der am schwächsten angebundene Standort."
    else:
        fall = f"Fällt der Standort {names} aus" if a.kappa == 1 else f"Fallen die Standorte {names} aus"
        chain = f" Der Mindestgrad {a.delta} verrät den Zusammenhang nicht: {fall}, ist das Netz getrennt."
    cost = (f" Alle {_i(a.pairs)} nicht benachbarten Paare einzeln brauchen {_i(a.flows_naive)} Flüsse, der Algorithmus von Even {_i(a.flows_even)}; "
            f"{_pct(a.bottleneck_share)} % der Paare sind schlechter verbunden als ihr kleinerer Grad.")
    return "info", head + chain + cost


def verdict_exact(rows):
    nets, checks, wrong, pairs = (sum(r[k] for r in rows) for k in ("nets", "checks", "wrong", "pairs"))
    n = rows[0]["n"]
    text = (f"Auf {_i(nets)} Netzen mit {_i(n)} Standorten ({len(rows)} Netztypen) stimmen {_i(checks)} Prüfungen mit der Aufzählung aller Trennmengen überein: der Zusammenhang des Netzes "
            f"nach beiden Verfahren, die Zeugen (trennende Mengen) und jedes der {_i(pairs)} nicht benachbarten Standortpaare mit seinen disjunkten Wegen.")
    if wrong:
        return "warning", f"Auf {_i(nets)} Netzen weichen {_i(wrong)} von {_i(checks)} Prüfungen von der Aufzählung ab."
    return "info", text + " Abweichungen: 0."


def verdict_whitney(rows):
    nets = sum(r["nets"] for r in rows)
    eq, kl, ll, viol = (sum(r[k] for r in rows) for k in ("equal", "k_lt_l", "l_lt_d", "violations"))
    n = max(r["n"] for r in rows)
    rest = [r for r in rows if r["kind"] != "verbund"]
    verb = [r for r in rows if r["kind"] == "verbund"]
    eq_rest, nets_rest = sum(r["equal"] for r in rest), sum(r["nets"] for r in rest)
    text = (f"Auf {_i(nets)} Netzen ({len(rows)} Netztypen mit je {_i(rows[0]['nets'])}, bis {_i(n)} Standorte) gilt κ = λ = Mindestgrad in {_i(eq)} ({_pct(eq / nets)} %), κ < λ in {_i(kl)} und "
            f"λ < Mindestgrad in {_i(ll)}; die Kette κ ≤ λ ≤ Mindestgrad ist in {_i(viol)} Netzen verletzt.")
    if verb:
        v = verb[0]
        text += (f" Ohne das Verbundnetz gilt κ = λ = Mindestgrad in {_i(eq_rest)} von {_i(nets_rest)}; im Verbundnetz in {_i(v['equal'])} von {_i(v['nets'])}: dort liegt der Mindestgrad im Mittel bei "
                 f"{_dec(v['sum_d'] / v['nets'])}, der Kantenzusammenhang bei {_dec(v['sum_l'] / v['nets'])} und der Knotenzusammenhang bei {_dec(v['sum_k'] / v['nets'])}.")
    return ("warning" if viol else "info"), text


def verdict_bottleneck(rows):
    share = lambda r: r["bottleneck"] / r["pairs"] if r["pairs"] else 0.0   # noqa: E731
    lo, hi = min(rows, key=share), max(rows, key=share)
    pairs = sum(r["pairs"] for r in rows)
    text = (f"Der Anteil der nicht benachbarten Standortpaare, die schlechter verbunden sind als ihr kleinerer Grad, reicht von {_pct(share(lo))} % ({lo['label']}) bis {_pct(share(hi))} % ({hi['label']}); "
            f"gezählt über {_i(pairs)} Paare auf {_i(sum(r['nets'] for r in rows))} Netzen.")
    ring = [r for r in rows if r["kind"] == "ring"]
    if ring:
        text += f" Im Ring mit Abkürzungen sind es {_pct(share(ring[0]))} %, und in {_i(ring[0]['nets_with_bottleneck'])} von {_i(ring[0]['nets'])} Netzen gibt es mindestens ein solches Paar."
    return "info", text


def verdict_even(rows):
    sizes = sorted({r["n"] for r in rows})
    factors = []
    for n in sizes:
        part = [r for r in rows if r["n"] == n]
        factors.append(sum(r["naive_flows"] for r in part) / sum(r["even_flows"] for r in part))
    worst = max((r["even_flows"] / r["naive_flows"], r) for r in rows)[1]
    parts = ", ".join(f"{_dec(f)}-" for f in factors[:-1]) + (f" und {_dec(factors[-1])}-Fache" if len(factors) > 1 else f"{_dec(factors[0])}-Fache")
    big = [r for r in rows if r["n"] == sizes[-1]]
    lo, hi = min(r["naive_flows"] / r["even_flows"] for r in big), max(r["naive_flows"] / r["even_flows"] for r in big)
    text = (f"Der Algorithmus von Even braucht bei {', '.join(_i(n) for n in sizes[:-1])} und {_i(sizes[-1])} Standorten im Mittel über die Netztypen das {parts} weniger Flüsse als alle Paare einzeln; "
            f"bei {_i(sizes[-1])} Standorten je nach Netztyp das {_dec(lo)}- bis {_dec(hi)}-Fache.")
    if any(r["even_flows"] >= r["naive_flows"] for r in rows):
        return "warning", f"Even braucht nicht überall weniger Flüsse als alle Paare einzeln, zum Beispiel im Fall {worst['label']} bei {_i(worst['n'])} Standorten."
    return "info", text


def verdict_links(rows):
    first = next((r["links"] for r in rows if r["k_lt_l"] == 0 and r["l_lt_d"] == 0), None)
    pick = [r for r in rows if r["links"] in (1, 2, 3, 5)] or rows[:4]
    def seq(key):
        return " / ".join(_dec(r[key] / r["nets"]) for r in pick)
    names = " / ".join(_i(r["links"]) for r in pick)
    text = (f"Im Verbundnetz mit mittlerem Grad 8 steigt der Zusammenhang mit der Zahl der Leitungen zwischen je zwei Regionen: bei {names} Leitungen liegt der Knotenzusammenhang κ im Mittel bei {seq('sum_k')}, "
            f"der Kantenzusammenhang λ bei {seq('sum_l')} und der Mindestgrad bei {seq('sum_d')} (je {_i(rows[0]['nets'])} Netze).")
    if first is not None:
        text += f" Ab {_i(first)} Leitungen gilt κ = λ = Mindestgrad in allen Netzen."
    ks = [r["sum_k"] / r["nets"] for r in rows]
    return ("warning" if any(b < a for a, b in zip(ks, ks[1:])) else "info"), text
