"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import mng_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _lines(inst, pairs):
    xs, ys = [], []
    for u, v in pairs:
        xs += [float(inst.xy[u, 0]), float(inst.xy[v, 0]), None]
        ys += [float(inst.xy[u, 1]), float(inst.xy[v, 1]), None]
    return xs, ys


def _nodes(inst, nodes, color, size, symbol="circle", name=None, show_text=False, line_color="white", line_width=1):
    nodes = list(nodes)
    degs = [len(inst.adj[v]) for v in nodes]
    return go.Scatter(
        x=[float(inst.xy[v, 0]) for v in nodes], y=[float(inst.xy[v, 1]) for v in nodes], mode="markers+text" if show_text else "markers",
        marker=dict(size=size, color=color, symbol=symbol, line=dict(color=line_color, width=line_width)),
        text=[inst.name(v) for v in nodes] if show_text else None, textfont=dict(size=10, color="#ffffff"), textposition="middle center",
        hovertext=[f"Standort {inst.name(v)}, Grad {d}" for v, d in zip(nodes, degs)], hoverinfo="text", name=name, showlegend=name is not None)


def _map_layout(fig, inst, height=470):
    xs, ys = inst.xy[:, 0], inst.xy[:, 1]
    pad = 0.25 * max(float(xs.max() - xs.min()), float(ys.max() - ys.min()), 1.0)
    fig.update_xaxes(visible=False, range=[float(xs.min()) - pad, float(xs.max()) + pad])
    fig.update_yaxes(visible=False, range=[float(ys.min()) - pad, float(ys.max()) + pad], scaleanchor="x", scaleratio=1)
    return _base(fig, height)


def build_pair_map(inst, s, t, view, kind):
    """Karte mit den disjunkten Wegen zwischen s und t. `kind` = "vertex": knotendisjunkte Wege und trennende Standorte; "edge": kantendisjunkte Wege und der kleinste Leitungsschnitt."""
    fig = go.Figure()
    show_text = inst.n <= 60
    base = list(inst.edges)
    on_paths = set()
    paths = view.kappa.paths if kind == "vertex" and view.kappa is not None else view.lam.paths
    for path in paths:
        on_paths.update(zip(path, path[1:]))
        on_paths.update(zip(path[1:], path))
    rest = [e for e in base if e not in on_paths]
    xs, ys = _lines(inst, rest)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_EDGE, width=1.2), hoverinfo="skip", showlegend=False))
    for i, path in enumerate(paths):
        xs, ys = _lines(inst, list(zip(path, path[1:])))
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_PATHS[i % len(C.COLOR_PATHS)], width=4), hoverinfo="skip", name=f"Weg {i + 1}", showlegend=len(paths) <= 8))
    if kind == "edge" and view.lam.cut:
        xs, ys = _lines(inst, view.lam.cut)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_SEP, width=3, dash="dot"), hoverinfo="skip", name="Leitungsschnitt"))
    special = {s, t}
    sep = set(view.kappa.cut) if kind == "vertex" and view.kappa is not None else set()
    others = [v for v in range(inst.n) if v not in special and v not in sep]
    fig.add_trace(_nodes(inst, others, C.COLOR_NODE, 20 if show_text else 10, show_text=False, line_color="#8a9a9c"))
    if sep:
        fig.add_trace(_nodes(inst, sorted(sep), C.COLOR_SEP, 26 if show_text else 15, "diamond", "trennende Standorte", show_text))
    fig.add_trace(_nodes(inst, [s], C.COLOR_S, 28 if show_text else 17, name="Start", show_text=show_text))
    fig.add_trace(_nodes(inst, [t], "#14233B", 28 if show_text else 17, name="Ziel", show_text=show_text))
    if show_text:
        for v in others:
            fig.add_annotation(x=float(inst.xy[v, 0]), y=float(inst.xy[v, 1]), text=inst.name(v), showarrow=False, font=dict(size=9, color="#14233B"))
    return _map_layout(fig, inst)


def build_global_map(inst, pair, cut):
    """Karte des ganzen Netzes mit der Engstelle: die trennenden Standorte (rot) und die beiden Seiten, die sie trennen (Seite des Startstandorts grün, der Rest hellblau)."""
    fig = go.Figure()
    removed = set(cut)
    side, stack = {pair[0]} if pair else set(), [pair[0]] if pair else []
    while stack:
        u = stack.pop()
        for v in inst.adj[u]:
            if v not in removed and v not in side:
                side.add(v)
                stack.append(v)
    xs, ys = _lines(inst, list(inst.edges))
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_EDGE, width=1.2), hoverinfo="skip", showlegend=False))
    show_text = inst.n <= 60
    a_side = [v for v in range(inst.n) if v in side]
    b_side = [v for v in range(inst.n) if v not in side and v not in removed]
    size = 20 if show_text else 10
    fig.add_trace(_nodes(inst, a_side, C.COLOR_S, size, name="eine Seite", show_text=show_text))
    fig.add_trace(_nodes(inst, b_side, C.COLOR_BAR, size, name="die andere Seite", show_text=show_text))
    if removed:
        fig.add_trace(_nodes(inst, sorted(removed), C.COLOR_SEP, size + 6, "diamond", "Engstelle (trennende Standorte)", show_text))
    return _map_layout(fig, inst)


def build_kappa_histogram(kappas, bottlenecks):
    """Wie viele nicht benachbarte Paare haben welchen Knotenzusammenhang? Paare mit Engstelle (kleiner als der kleinere Grad) sind farbig."""
    bn = set(bottlenecks)
    values = sorted(set(kappas.values()))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[str(v) for v in values], y=[sum(1 for p, k in kappas.items() if k == v and p not in bn) for v in values], name="so gut wie der kleinere Grad", marker_color=C.COLOR_NODE))
    fig.add_trace(go.Bar(x=[str(v) for v in values], y=[sum(1 for p, k in kappas.items() if k == v and p in bn) for v in values], name="Engstelle", marker_color=C.COLOR_SEP))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title_text="Knotenzusammenhang κ(s, t) des Paares")
    fig.update_yaxes(title_text="Zahl der Standortpaare")
    return _base(fig)


def build_flows(a):
    """Aufwand in Flüssen: alle Paare einzeln gegen den Algorithmus von Even."""
    fig = go.Figure(go.Bar(x=["alle Paare einzeln", "Even"], y=[a.flows_naive, a.flows_even], marker_color=[C.COLOR_BAR2, C.COLOR_BAR3],
                           text=[f"{a.flows_naive:,}".replace(",", "."), f"{a.flows_even:,}".replace(",", ".")], textposition="outside", cliponaxis=False))
    fig.update_yaxes(title_text="Flüsse")
    return _base(fig, 320)


# --- Experimente ---------------------------------------------------------------------------------------------------------------------------------


def build_exact(rows):
    labels = [r["label"] for r in rows]
    ys = [round(100 * (r["checks"] - r["wrong"]) / r["checks"]) if r["checks"] else 0 for r in rows]
    fig = go.Figure(go.Bar(x=labels, y=ys, marker_color=C.COLOR_BAR, text=[f"{y} %" for y in ys], textposition="outside", cliponaxis=False, showlegend=False))
    fig.update_yaxes(title_text="Prüfungen ohne Abweichung (%)", range=[0, 118])
    return _base(fig)


def build_whitney(rows):
    labels = [r["label"] for r in rows]
    fig = go.Figure()
    for key, name, color in (("sum_d", "Mindestgrad", C.COLOR_NODE), ("sum_l", "λ (Leitungen)", C.COLOR_BAR2), ("sum_k", "κ (Standorte)", C.COLOR_BAR3)):
        fig.add_trace(go.Bar(x=labels, y=[r[key] / r["nets"] for r in rows], name=name, marker_color=color, hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Mittel über die Netze")
    return _base(fig)


def build_bottleneck(rows):
    labels = [r["label"] for r in rows]
    ys = [round(100 * r["bottleneck"] / r["pairs"], 1) if r["pairs"] else 0 for r in rows]
    fig = go.Figure(go.Bar(x=labels, y=ys, marker_color=C.COLOR_SEP, text=[f"{y:.1f} %".replace(".", ",") for y in ys], textposition="outside", cliponaxis=False, showlegend=False))
    fig.update_yaxes(title_text="Paare mit Engstelle (%)", range=[0, max(ys + [1]) * 1.2 + 2])
    return _base(fig)


def build_even(rows):
    sizes = sorted({r["n"] for r in rows})
    labels = []
    for r in rows:
        if r["label"] not in labels:
            labels.append(r["label"])
    fig = go.Figure()
    colors = (C.COLOR_BAR2, C.COLOR_BAR, C.COLOR_BAR3)
    for n, color in zip(sizes, colors):
        part = {r["label"]: r for r in rows if r["n"] == n}
        fig.add_trace(go.Bar(x=labels, y=[round(100 * part[l]["even_flows"] / part[l]["naive_flows"], 1) for l in labels], name=f"{n} Standorte", marker_color=color,
                             hovertemplate="%{x}: %{y:.1f} %<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Flüsse von Even (% aller Paare)")
    return _base(fig)


def build_links(rows):
    xs = [r["links"] for r in rows]
    fig = go.Figure()
    for key, name, color in (("sum_d", "Mindestgrad", C.COLOR_NODE), ("sum_l", "λ (Leitungen)", C.COLOR_BAR2), ("sum_k", "κ (Standorte)", C.COLOR_BAR3)):
        fig.add_trace(go.Scatter(x=xs, y=[r[key] / r["nets"] for r in rows], mode="lines+markers", name=name, line=dict(color=color, width=3),
                                 hovertemplate="%{x} Leitungen: %{y:.2f}<extra></extra>"))
    fig.update_xaxes(title_text="Leitungen zwischen je zwei Regionen", dtick=1)
    fig.update_yaxes(title_text="Mittel über die Netze")
    return _base(fig)
