"""Menger: disjunkte Wege und Zusammenhang - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Erstes Stück der Reihe „Schnitte und Zusammenhang“: Wie viele voneinander unabhängige Verbindungen hat ein Netz zwischen zwei Standorten, wie viele insgesamt, und wo ist die Engstelle?
Disjunkte Wege nach dem Satz von Menger über einen Fluss mit Knotenspaltung, der Algorithmus von Even gegen alle Paare, die Kette κ ≤ λ ≤ Mindestgrad.

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import mng_constants as C
import mng_evaluation as ev
import mng_experiments as ex
from mng_layout import dunkles_design, kopf_css
from mng_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from mng_visualization import (
    build_bottleneck,
    build_even,
    build_exact,
    build_flows,
    build_global_map,
    build_kappa_histogram,
    build_links,
    build_pair_map,
    build_whitney,
)

st.set_page_config(page_title="Menger: disjunkte Wege und Zusammenhang – Sebastian Hanisch", layout="wide")

_i, _dec = ev._i, ev._dec


def _show(verdict):
    kind, text = verdict
    {"success": st.success, "info": st.info, "warning": st.warning}[kind](text)


def _wege(k, adjektiv):
    """„1 knotendisjunkten Weg“ (nach „es gibt“), „2 knotendisjunkte Wege“."""
    return f"{_i(k)} {adjektiv}en Weg" if k == 1 else f"{_i(k)} {adjektiv}e Wege"


@st.cache_data(show_spinner=False, max_entries=8)
def _analysis(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _exactness():
    return ex.exactness_rows()


@st.cache_data(show_spinner=False)
def _pairs():
    return ex.pair_rows()


@st.cache_data(show_spinner=False)
def _even():
    return ex.even_rows()


@st.cache_data(show_spinner=False)
def _links():
    return ex.link_rows()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in mng_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔗 Menger: disjunkte Wege und Zusammenhang")
st.markdown(
    """
**Wie viele voneinander unabhängige Verbindungen hat ein Netz zwischen zwei Standorten, und wo ist die Engstelle?** Der **Satz von Menger** sagt: So viele **disjunkte Wege** es gibt (ohne gemeinsamen Zwischenstandort
oder ohne gemeinsame Leitung), so viele Standorte oder Leitungen muss man mindestens ausfallen lassen, um die beiden zu trennen (Standorte nur bei nicht benachbarten Standorten). Beides rechnet ein **Fluss** mit Einheitskapazitäten aus; die Demo zeigt die Wege, die trennende
Menge und den Zusammenhang des **ganzen Netzes** (der Algorithmus von **Even** spart gegenüber allen Paaren einzeln viele Flüsse).

Der **Mindestgrad** (die wenigsten Leitungen an einem Standort) ist eine obere Schranke: Es gilt immer **κ ≤ λ ≤ Mindestgrad**. Auf den dünnen Modellnetzen sagt er fast alles; interessant ist, wo er nicht reicht, nämlich an der **Engstelle**.

Das ist das erste Stück der Reihe **Schnitte und Zusammenhang**. Wer mehr zu Max-Flow = Min-Cut sucht, findet es in **edmonds-karp-demo** und **dinic-demo**; alle Paare auf einmal zeigt **gomory-hu-demo**; die Brücken und Artikulationspunkte (Zusammenhang 1) **bridges-demo**.
Weiter unten: die Experimente **🔬**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So rechnet man den Zusammenhang eines Netzes", expanded=True):
    st.markdown(
        """
1. **Disjunkte Wege:** Zwei Wege zwischen A und B sind **knotendisjunkt**, wenn sie außer A und B keinen Standort teilen, und **kantendisjunkt**, wenn sie keine Leitung teilen.
2. **Satz von Menger:** Bei nicht benachbarten Standorten ist die größte Zahl knotendisjunkter Wege gleich der kleinsten Zahl von Standorten, deren Ausfall A und B trennt; für Leitungen gilt es entsprechend auch bei benachbarten Standorten. Die trennende Menge ist die **Engstelle** zwischen den beiden.
3. **Fluss rechnen:** Jede Leitung bekommt Kapazität 1 (kantendisjunkt) bzw. jeder Standort wird in einen Eingang und einen Ausgang gespalten, verbunden durch eine Leitung mit Kapazität 1 (knotendisjunkt, **Knotenspaltung**). Wege, die der Fluss findet, sind die disjunkten Wege.
4. **Ganzes Netz:** κ ist das Minimum von κ(A, B) über alle nicht benachbarten Paare. **Even** prüft nur die ersten κ + 1 Standorte als Start gegen alle späteren, weil eine trennende Menge mit höchstens κ Standorten nicht alle enthalten kann. λ braucht n − 1 Flüsse von einem festen Standort.
5. **Warum der Mindestgrad nicht reicht:** κ ≤ λ ≤ Mindestgrad (Whitney), aber ein Netz mit hohem Mindestgrad kann an einer Engstelle hängen (zwei dichte Regionen, nur über wenige Leitungen verbunden).

| Begriff | Bedeutung |
|---|---|
| **Grad** | Zahl der Leitungen an einem Standort |
| **κ(A, B)** | Zahl knotendisjunkter Wege zwischen zwei nicht benachbarten Standorten = kleinste trennende Standortmenge |
| **λ(A, B)** | Zahl kantendisjunkter Wege = kleinster Schnitt aus Leitungen |
| **κ, λ des Netzes** | kleinster Wert über alle Paare (κ: nicht benachbarte Paare) |
| **Engstelle eines Paares** | κ(A, B) ist kleiner als der kleinere Grad der beiden: die trennende Menge liegt im Netz, nicht an den Standorten selbst |
| **Fluss** | ein Durchlauf mit Wegesuche für ein Paar; die Demo zählt Flüsse, Erweiterungen (gefundene Wege) und Besuche (abgearbeitete Knoten) |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Netz**")
    kind = st.selectbox("Art des Netzes", list(C.KINDS), format_func=C.KIND_NAMES.get, key="kind_select", help=C.KIND_HELP.get(st.session_state.get("kind_select", C.DEFAULT_KIND), ""))
    n = st.slider("Standorte n", *bounds("n_slider"), key="n_slider", help="Wie viele Standorte das Netz hat (das Gitter rundet auf ein Quadrat).")
    deg = st.slider("Mittlerer Grad", *bounds("deg_slider"), key="deg_slider", step=0.5, help="Leitungen je Standort im Mittel; wirkt beim Zufallsnetz und innerhalb der Regionen des Verbundnetzes.")
    links = st.slider("Leitungen zwischen je zwei Regionen", *bounds("links_slider"), key="links_slider", help="Wirkt nur beim Verbundnetz.")
    seed = st.number_input("Zufalls-Seed des Netzes", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neues Netz erzeugen", width="stretch", on_click=randomize_seed)
    st.caption(C.KIND_REGLER[kind])

sync_query_params({"kind_select": kind, "n_slider": int(n), "deg_slider": float(deg), "links_slider": int(links), "seed_input": int(seed)})

settings = ev.Settings(kind, int(n), float(deg), int(links), int(seed))
with st.spinner("Rechne den Zusammenhang aller Paare..."):
    a = _analysis(settings)
problems = ev.validate(a)
for p in problems:
    st.error(f"Prüfung fehlgeschlagen: {p}")
signature = f"{settings.kind}_{settings.n}_{settings.deg}_{settings.links}_{settings.seed}"
inst = a.inst

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
st.caption(f"{C.KIND_NAMES[kind]} mit {_i(a.n)} Standorten und {_i(a.m)} Leitungen. Standorte sind ab 1 nummeriert (das Lehrbeispiel hat Buchstaben). Ein Fluss ist die Rechnung für ein Paar.")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Mindestgrad", _i(a.delta), delta="wenigste Leitungen an einem Standort", delta_color="off")
m2.metric("Kantenzusammenhang λ", _i(a.lam_value), delta=f"{a.lam_value - a.delta:+d} gegen Mindestgrad" if a.lam_value != a.delta else "gleich dem Mindestgrad", delta_color="normal" if a.lam_value != a.delta else "off")
m3.metric("Knotenzusammenhang κ", _i(a.kappa), delta=f"{a.kappa - a.delta:+d} gegen Mindestgrad" if a.kappa != a.delta else "gleich dem Mindestgrad", delta_color="normal" if a.kappa != a.delta else "off")
m4.metric("Paare mit Engstelle", f"{ev._pct(a.bottleneck_share)} %", delta=f"{_i(len(a.bottlenecks))} von {_i(a.pairs)} Paaren", delta_color="off")

tab_pair, tab_net, tab_cost = st.tabs(["🔍 Ein Paar", "🕸️ Das ganze Netz", "💰 Aufwand"])

# --- Tab 1: Ein Paar -----------------------------------------------------------------------------------------------------------------------

with tab_pair:
    names = [inst.name(v) for v in range(a.n)]
    default_s, default_t = (1, 6) if kind == "textbook" else (0, a.n - 1)
    c1, c2, c3 = st.columns([1, 1, 2])
    s = c1.selectbox("Start", list(range(a.n)), index=default_s, format_func=lambda v: names[v], key=f"start_{signature}", help="Von diesem Standort aus werden die Wege gesucht.")
    t = c2.selectbox("Ziel", list(range(a.n)), index=default_t, format_func=lambda v: names[v], key=f"goal_{signature}", help="Dieser Standort soll erreicht werden.")
    mode = c3.radio("Was fällt aus?", ["vertex", "edge"], format_func={"vertex": "Standorte (knotendisjunkte Wege)", "edge": "Leitungen (kantendisjunkte Wege)"}.get, key=f"mode_{signature}", horizontal=True)
    if s == t:
        st.info("Start und Ziel sind derselbe Standort: Wählen Sie zwei verschiedene.")
    else:
        view = ev.pair_view(a, s, t)
        for p in ev.validate_pair(a, view):
            st.error(f"Prüfung fehlgeschlagen: {p}")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Grad des Starts", _i(view.deg_s))
        d2.metric("Grad des Ziels", _i(view.deg_t))
        d3.metric("κ(Start, Ziel)", _i(view.kappa.value) if view.kappa is not None else "–", delta="knotendisjunkte Wege" if view.kappa is not None else "benachbart: nicht definiert", delta_color="off")
        d4.metric("λ(Start, Ziel)", _i(view.lam.value), delta="kantendisjunkte Wege", delta_color="off")
        if mode == "vertex" and view.kappa is None:
            st.info(f"Die Standorte {names[s]} und {names[t]} sind direkt verbunden: Dann gibt es keine trennende Menge von Standorten (der Satz von Menger gilt für nicht benachbarte Standorte). Wählen Sie „Leitungen“ oder ein anderes Paar.")
            chosen = view.lam
            show_mode = "edge"
        else:
            chosen = view.kappa if mode == "vertex" else view.lam
            show_mode = mode
        if show_mode == "vertex":
            st.markdown(f"**Zwischen {names[s]} und {names[t]} gibt es {_wege(chosen.value, 'knotendisjunkt')}; der Ausfall von {', '.join(names[v] for v in chosen.cut)} trennt die beiden.**"
                        + (" Das ist weniger als der kleinere Grad: dort sitzt eine **Engstelle**." if chosen.value < min(view.deg_s, view.deg_t) else " Das entspricht dem kleineren Grad: keine Engstelle."))
        else:
            cut = ", ".join(f"{names[u]}–{names[w]}" for u, w in chosen.cut)
            st.markdown(f"**Zwischen {names[s]} und {names[t]} gibt es {_wege(chosen.value, 'kantendisjunkt')}; der Ausfall {'der Leitung' if chosen.value == 1 else 'der Leitungen'} {cut} trennt die beiden.**")
        st.plotly_chart(build_pair_map(inst, s, t, view, show_mode), width="stretch", key="chart_pair")
        st.caption("Jeder farbige Weg ist einer der disjunkten Wege; rote Rauten sind die trennenden Standorte, gepunktete rote Linien der kleinste Leitungsschnitt.")
        st.dataframe(pd.DataFrame([{"Weg": f"Weg {i + 1}", "Länge": len(p) - 1, "Verlauf": " → ".join(names[v] for v in p)} for i, p in enumerate(chosen.paths)]), hide_index=True, width="stretch")
        st.caption(f"Aufwand dieses Flusses: {_i(chosen.cost.augmentations)} Erweiterungen, {_i(chosen.cost.visits)} Besuche.")

# --- Tab 2: Das ganze Netz -----------------------------------------------------------------------------------------------------------------

with tab_net:
    if a.pairs == 0:
        st.info("Das Netz ist vollständig: Jeder Standort ist mit jedem verbunden, es gibt kein nicht benachbartes Paar. Dann gilt κ = n − 1, und λ ist ebenfalls n − 1.")
    else:
        st.plotly_chart(build_global_map(inst, a.even.pair, a.even.cut), width="stretch", key="chart_global")
        st.caption("Die Engstelle des Netzes: die kleinste trennende Standortmenge (rote Rauten) und die beiden Seiten, die sie trennt. Gibt es mehrere gleich kleine Mengen, zeigt die Demo die des zuerst gefundenen Paares.")
        w1, w2 = st.columns(2)
        w1.markdown("**Die Kette von Whitney:**")
        w1.dataframe(pd.DataFrame({"Größe": ["Mindestgrad", "Kantenzusammenhang λ", "Knotenzusammenhang κ"], "Wert": [a.delta, a.lam_value, a.kappa]}), hide_index=True, width="stretch")
        w2.markdown("**Wo die Engstellen sitzen:**")
        w2.plotly_chart(build_kappa_histogram(a.kappas, a.bottlenecks), width="stretch", key="chart_hist")
        st.caption("Jedes nicht benachbarte Paar hat einen Knotenzusammenhang. Rot: schlechter verbunden als der kleinere Grad der beiden Standorte; grau: so gut, wie die Grade es zulassen.")

# --- Tab 3: Aufwand ------------------------------------------------------------------------------------------------------------------------

with tab_cost:
    if a.pairs == 0:
        st.info("Ein vollständiges Netz braucht keinen Fluss.")
    else:
        f1, f2, f3 = st.columns(3)
        f1.metric("Alle Paare einzeln", f"{_i(a.flows_naive)} Flüsse", delta=f"{_i(a.pairs)} nicht benachbarte Paare", delta_color="off")
        f2.metric("Algorithmus von Even", f"{_i(a.flows_even)} Flüsse", delta=f"{_dec(a.saving)}-fach weniger", delta_color="off")
        f3.metric("Kantenzusammenhang λ", f"{_i(a.lam.cost.flows)} Flüsse", delta="n − 1 Flüsse von einem Standort", delta_color="off")
        st.plotly_chart(build_flows(a), width="stretch", key="chart_flows")
        st.caption(f"Even nutzt nur die ersten κ + 1 = {_i(a.kappa + 1)} Standorte als Start (anfangs den Mindestgrad + 1) und rechnet {_i(a.even.cost.visits)} Besuche; alle Paare einzeln rechnen {_i(a.naive.cost.visits)} Besuche.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie robust ist die Verbindung, und sagt der Mindestgrad genug?")
_show(ev.verdict_question(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

with st.spinner("Rechne die Experimente (einmalig, einige Sekunden)..."):
    rows_x, rows_p, rows_e, rows_l = _exactness(), _pairs(), _even(), _links()

st.subheader("🔬 Experiment 1: Stimmen die Verfahren mit der Aufzählung aller Trennmengen überein?")
st.caption(f"{len(rows_x)} Netztypen mit je {len(C.EX_EXACT_SEEDS)} festen Netzen mit {C.EX_EXACT_N} Standorten; Zusammenhang, jedes Paar mit seinen Wegen und der trennenden Menge, gegen die Aufzählung aller Mengen.")
st.plotly_chart(build_exact(rows_x), width="stretch", key="chart_exact")
_show(ev.verdict_exact(rows_x))

st.subheader("🔬 Experiment 2: Sagt der Mindestgrad den Zusammenhang?")
st.caption(f"Mittel über {len(C.SWEEP_SEEDS)} feste Netze je Typ mit etwa {C.EX_PAIR_N} Standorten: Mindestgrad, Kantenzusammenhang λ und Knotenzusammenhang κ.")
st.plotly_chart(build_whitney(rows_p), width="stretch", key="chart_whitney")
_show(ev.verdict_whitney(rows_p))

st.subheader("🔬 Experiment 3: Wie viele Paare hängen an einer Engstelle?")
st.caption("Anteil der nicht benachbarten Standortpaare, deren Knotenzusammenhang kleiner ist als der kleinere Grad der beiden Standorte.")
st.plotly_chart(build_bottleneck(rows_p), width="stretch", key="chart_bottleneck")
_show(ev.verdict_bottleneck(rows_p))

st.subheader("🔬 Experiment 4: Wie viele Flüsse spart der Algorithmus von Even?")
st.caption("Flüsse von Even in Prozent der Flüsse aller nicht benachbarten Paare (jedes Paar einzeln), bei 20, 40 und 80 Standorten.")
st.plotly_chart(build_even(rows_e), width="stretch", key="chart_even")
_show(ev.verdict_even(rows_e))

st.subheader("🔬 Experiment 5: Wie verschiebt sich die Engstelle mit der Verbundstärke?")
st.caption(f"Verbundnetz mit {C.EX_LINK_N} Standorten und mittlerem Grad 8 in drei Regionen; die Zahl der Leitungen zwischen je zwei Regionen steigt von {C.EX_LINKS[0]} auf {C.EX_LINKS[-1]}.")
st.plotly_chart(build_links(rows_l), width="stretch", key="chart_links")
_show(ev.verdict_links(rows_l))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Alle Leitungen gleich** | Jede Leitung zählt als eine Verbindung; mit Kapazitäten und Kosten ist Max-Flow = Min-Cut die allgemeinere Rechnung. | edmonds-karp-demo, dinic-demo |
| **Ein Paar oder der kleinste Wert** | Die Demo zeigt ein Paar und den Zusammenhang des ganzen Netzes; alle Paare auf einmal als Baum zeigt der Gomory–Hu-Baum. | gomory-hu-demo |
| **Zusammenhang 1 gezählt, nicht verstärkt** | Brücken und Artikulationspunkte zählt bridges-demo; hier wird die Engstelle benannt, nicht behoben. | bridges-demo |
| **Ausfälle gezielt, nicht zufällig** | Die Demo fragt nach der kleinsten Trennmenge, nicht nach der Wahrscheinlichkeit zufälliger Ausfälle. | random-spanning-tree-demo, robustheit-demo |
| **Ungerichtetes Netz** | In gerichteten Netzen gilt der Satz von Menger ebenfalls, aber die Kette κ ≤ λ ≤ Mindestgrad nur mit Ein- und Ausgrad. | - |
| **Synthetische Netze, bis 80 Standorte** | Reale Netze haben andere Strukturen; Aufwand in Flüssen und Besuchen gezählt, nicht in Sekunden. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein einfacher, ungerichteter Graph $G = (V, E)$ mit $n = |V|$ Standorten; $\delta(G)$ ist der Mindestgrad. Für nicht benachbarte $s, t$ ist $\kappa(s,t)$ die größte Zahl **innen knotendisjunkter** $s$-$t$-Wege, $\lambda(s,t)$ die größte Zahl **kantendisjunkter** Wege.

**Satz von Menger (Knotenversion).** Für nicht benachbarte $s, t$ gilt

$$\kappa(s,t) = \min \{\, |S| : S \subseteq V \setminus \{s,t\},\ S \text{ trennt } s \text{ von } t \,\}.$$

**Satz von Menger (Kantenversion).** Für alle $s \neq t$ gilt

$$\lambda(s,t) = \min \{\, |F| : F \subseteq E,\ F \text{ trennt } s \text{ von } t \,\}.$$

**Zusammenhang des Netzes.** Mit $\kappa(K_n) = n - 1$ für das vollständige Netz:

$$\kappa(G) = \min_{s,t \text{ nicht benachbart}} \kappa(s,t), \qquad \lambda(G) = \min_{t \neq s_0} \lambda(s_0, t).$$

**Kette von Whitney.** Es gilt immer

$$\kappa(G) \le \lambda(G) \le \delta(G).$$

**Rechnung.** Im Knotenspaltungsnetz wird jeder Standort $v$ zu $v_{\mathrm{ein}} \to v_{\mathrm{aus}}$ mit Kapazität 1, jede Leitung $\{u,v\}$ zu $u_{\mathrm{aus}} \to v_{\mathrm{ein}}$ und $v_{\mathrm{aus}} \to u_{\mathrm{ein}}$ mit großer Kapazität; der größte Fluss von $s_{\mathrm{aus}}$ nach $t_{\mathrm{ein}}$ ist $\kappa(s,t)$, die gesättigten Standortpfeile am Schnitt sind die trennende Menge. **Even:** Mit dem bisher besten Wert $k$ (anfangs $\delta$) genügen die ersten $k+1$ Standorte als Start, jeder gegen alle späteren: Eine trennende Menge mit höchstens $k$ Standorten enthält nicht alle $k+1$.

**Literatur.** K. Menger: *Zur allgemeinen Kurventheorie*, Fundamenta Mathematicae 10 (1927), S. 96–115. H. Whitney: *Congruent graphs and the connectivity of graphs*, American Journal of Mathematics 54 (1932), S. 150–168. S. Even: *An algorithm for determining whether the connectivity of a graph is at least k*, SIAM Journal on Computing 4 (1975), S. 393–396. Stand der Technik nur als Einordnung, ohne Zahlen der Originale: Max-Flow in Zeit $m^{1+o(1)}$ (L. Chen u. a., FOCS 2022) und, darauf aufbauend, der Knotenzusammenhang in fast linearer Zeit (J. Li u. a., Journal of the ACM 2025). Die Demo rechnet das klassische Verfahren mit Edmonds–Karp.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
