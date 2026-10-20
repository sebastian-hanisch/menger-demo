"""Konstanten: Regler-Grenzen, feste Annahmen, Experiment-Raster, Farben und Presets."""

KINDS = ("textbook", "random", "grid", "ring", "scalefree", "verbund")
KIND_NAMES = {"textbook": "Lehrbeispiel (zwei Werke)", "random": "Zufallsnetz", "grid": "Gitter", "ring": "Ring mit Abkürzungen", "scalefree": "Skalenfreies Netz", "verbund": "Verbundnetz"}
KIND_HELP = {
    "textbook": "Acht Standorte in zwei Werken, von Hand zu rechnen; die übrigen Regler wirken nicht.",
    "random": "Verbindungen zwischen beliebigen Standortpaaren; der mittlere Grad ist einstellbar.",
    "grid": "Standorte auf einem Raster, Verbindungen zu den vier Nachbarn.",
    "ring": "Jeder Standort ist mit seinen vier nächsten Nachbarn auf einem Ring verbunden, ein Zehntel der Verbindungen führt zu einem zufälligen Standort.",
    "scalefree": "Neue Standorte hängen sich bevorzugt an gut vernetzte an (jeder bringt zwei Verbindungen mit): wenige Knotenpunkte, viele Randstandorte.",
    "verbund": "Drei Regionen mit dichten inneren Verbindungen; zwischen je zwei Regionen führen nur wenige Leitungen (einstellbar).",
}

KIND_REGLER = {
    "textbook": "Das Lehrbeispiel ist fest: Größe, Grad, Leitungen und Zufalls-Seed wirken hier nicht.",
    "random": "Wirksam: Standorte, mittlerer Grad, Zufalls-Seed. Die Leitungen zwischen den Regionen wirken nicht.",
    "grid": "Wirksam: Standorte (gerundet auf ein Quadrat). Grad, Leitungen und Zufalls-Seed wirken nicht.",
    "ring": "Wirksam: Standorte, Zufalls-Seed (die Abkürzungen). Grad und Leitungen zwischen den Regionen wirken nicht.",
    "scalefree": "Wirksam: Standorte, Zufalls-Seed. Grad und Leitungen zwischen den Regionen wirken nicht.",
    "verbund": "Wirksam: Standorte, mittlerer Grad (in den Regionen), Leitungen zwischen den Regionen, Zufalls-Seed.",
}

N_MIN, N_MAX, DEFAULT_N = 8, 80, 24
DEG_MIN, DEG_MAX, DEFAULT_DEG = 2.0, 10.0, 5.0
LINKS_MIN, LINKS_MAX, DEFAULT_LINKS = 1, 8, 2
SEED_MAX, DEFAULT_SEED = 999999, 7
DEFAULT_KIND = "textbook"
REGIONS = 3
RING_NEIGHBOURS, RING_REWIRE = 4, 0.1
SCALEFREE_M = 2
FLOW_BIG = 10 ** 6                       # Kapazität der Verbindungen im Knotenspaltungsnetz: nie die engste Stelle

PAIR_LIMIT = 80                          # größte Netzgröße für „alle Paare“ in der App (ein Fluss je nicht benachbartes Paar)
BRUTE_N = 14                             # größte Netzgröße für die Aufzählung aller Trennmengen (Test und Experiment 1)

SWEEP_SEEDS = tuple(range(100000, 100010))   # feste Netze für alle Experimente: nie ein einzelner Zufalls-Seed als Befund
EX_PAIR_N = 30                               # Experimente 2 und 3 (ein Fluss je nicht benachbartes Paar)
EX_EVEN = ((20, 10), (40, 10), (80, 4))      # Experiment 4: (Größe, Zahl der Netze je Typ)
EX_LINKS = tuple(range(1, 9))                # Experiment 5: Leitungen zwischen je zwei Regionen
EX_LINK_N = 45
EX_EXACT_N = 12                              # Experiment 1: Aufzählung aller Trennmengen
EX_EXACT_SEEDS = tuple(range(100000, 100012))
EX_KINDS = (("random", 3.0), ("random", 5.0), ("random", 8.0), ("grid", 0.0), ("ring", 0.0), ("scalefree", 0.0), ("verbund", 8.0))

COLOR_PATHS = ("#2F6B65", "#4c78a8", "#e8a33d", "#8d6cab", "#d1495b", "#6a994e", "#bc6c25", "#457b9d")
COLOR_SEP = "#d1495b"
COLOR_S, COLOR_T = "#2F6B65", "#d1495b"
COLOR_NODE = "#c9d1d3"
COLOR_EDGE = "rgba(150,150,150,0.45)"
COLOR_BAR = "#4c78a8"
COLOR_BAR2 = "#e8a33d"
COLOR_BAR3 = "#2F6B65"

PRESETS = {
    "Lehrbeispiel (zwei Werke)": {"kind": "textbook", "n": DEFAULT_N, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": DEFAULT_SEED},
    "Der Mindestgrad sagt fast alles": {"kind": "random", "n": 40, "deg": 5.0, "links": DEFAULT_LINKS, "seed": 3},
    "Die Engstelle im Verbundnetz": {"kind": "verbund", "n": 45, "deg": 8.0, "links": 1, "seed": 1},
    "Standorte vor Leitungen: κ < λ": {"kind": "verbund", "n": 45, "deg": 8.0, "links": 2, "seed": 1},
    "Ring: viele kleine Engstellen": {"kind": "ring", "n": 40, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 2},
    "Even spart Flüsse": {"kind": "random", "n": 80, "deg": 6.0, "links": DEFAULT_LINKS, "seed": 5},
}
PRESET_HELP = {
    "Lehrbeispiel (zwei Werke)": "Zwei Werke mit je vier Standorten, nur über den Standort A verbunden: Fällt A aus, sind die Werke getrennt; zwei Leitungen müssten fallen (von Hand zu prüfen).",
    "Der Mindestgrad sagt fast alles": "40 Standorte, mittlerer Grad 5: Der am schwächsten angebundene Standort entscheidet allein, Engstellen im Netz gibt es kaum.",
    "Die Engstelle im Verbundnetz": "Drei dichte Regionen mit nur einer Leitung zwischen je zwei Regionen: Der Zusammenhang hängt an dieser Engstelle, der Mindestgrad ist viel größer.",
    "Standorte vor Leitungen: κ < λ": "Mit zwei Leitungen zwischen je zwei Regionen laufen manche Leitungen über denselben Standort: Der Knotenzusammenhang liegt unter dem Kantenzusammenhang, und der unter dem Mindestgrad.",
    "Ring: viele kleine Engstellen": "Der Ring mit Abkürzungen hat viele Standortpaare, die nur über wenige Zwischenstandorte verbunden sind.",
    "Even spart Flüsse": "80 Standorte: Alle Paare einzeln zu prüfen kostet ein Vielfaches der Flüsse, die der Algorithmus von Even braucht.",
}
