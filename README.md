# Menger: disjunkte Wege und Zusammenhang – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-menger-demo.streamlit.app/)**

Erstes Stück der Reihe **Schnitte und Zusammenhang** (Arbeitstitel der Linie `schnitte-zusammenhang`) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Bereich Graphentheorie. Vehikel: ein **Verbindungsnetz zwischen Standorten** (Depots, Umschlagpunkte, Werke), synthetisch und mit festem Zufalls-Seed. Die Demo fragt: **Wie viele voneinander unabhängige Verbindungen hat das Netz zwischen zwei Standorten, wie viele insgesamt, und wo ist die Engstelle?** Der Satz von Menger macht daraus eine Flussrechnung: Bei nicht benachbarten Standorten ist die Zahl knotendisjunkter Wege gleich der kleinsten Zahl von Standorten, deren Ausfall die beiden trennt; für Leitungen gilt es entsprechend auch bei benachbarten Standorten.

Nachbarn: Max-Flow gleich Min-Cut als Zertifikat zeigen `edmonds-karp-demo`, `dinic-demo` und `push-relabel-demo`; alle Paare auf einmal als Baum `gomory-hu-demo`; Brücken und Artikulationspunkte (Zusammenhang 1, Verstärkung nur gezählt) `bridges-demo`.

## Warum dieses Problem

Fällt ein Standort oder eine Leitung aus, soll das Netz zusammenhängen. Der **Mindestgrad** (die wenigsten Leitungen an einem Standort) ist die naheliegende Antwort und eine obere Schranke: Es gilt immer **κ ≤ λ ≤ Mindestgrad** (Whitney). Auf den dünnen Modellnetzen der Demo sagt er fast alles; interessant ist, wo er nicht reicht, nämlich dort, wo zwei dichte Regionen nur über wenige Leitungen oder einen einzelnen Standort zusammenhängen. Dort ist die **Engstelle** der Gegenstand: nicht der schwächste Standort, sondern die kleinste Menge von Standorten oder Leitungen, die das Netz trennt.

## Befunde und Korrekturen gegenüber dem Plan

- **Verbundnetz fest in drei Regionen:** Die Vormessung baute das Verbundnetz als Blockmodell mit zufälligen Verbindungen zwischen den Gruppen. Die Demo setzt drei Regionen fester Größe mit einem einstellbaren Regler „Leitungen zwischen je zwei Regionen“; mit mittlerem Grad 8 in den Regionen sind sie dicht genug, dass der Mindestgrad deutlich über der Engstelle liegt (Experiment 5).
- **Kein Delaunay-Netz:** Der Plan nannte es als Netztyp; die Demo lässt es weg (es bräuchte `scipy` zur Laufzeit). Stattdessen: Zufallsnetz, Gitter, Ring mit Abkürzungen, skalenfreies Netz, Verbundnetz und das handgebaute Lehrbeispiel.
- **Die Vormessungszahlen gelten nicht:** „κ = λ = Mindestgrad in 296 von 320“ stammt aus Zufallsnetzen anderer Bauart (größte Komponente eines Zufallsgraphen); die Demo baut Zufallsnetze als Zufallsbaum plus zufällige weitere Leitungen und misst andere Zahlen (Tabelle unten). Der Befund bleibt: Auf den dünnen Modellnetzen sagt der Mindestgrad fast alles; die Ausnahme ist das Verbundnetz mit wenigen Leitungen zwischen den Regionen.
- **κ nur für nicht benachbarte Standorte:** Der Satz von Menger gilt für nicht benachbarte Standorte (eine Leitung ist ein Weg ohne Zwischenstandort). Die Demo definiert κ des Netzes als kleinsten Wert über alle nicht benachbarten Paare, beim vollständigen Netz n − 1; für benachbarte Paare zeigt die Demo nur λ.
- **Zitat:** Genannt sind Menger (1927), Whitney (1932) und Even (1975) als Herkunft der Sätze und des Verfahrens (Fundstellen anhand der Quellenangaben geprüft); der Stand der Technik (Max-Flow und Knotenzusammenhang in fast linearer Zeit) steht nur als Einordnung ohne Zahlen der Originale in der App.

## Modell

Ein einfaches, **zusammenhängendes** Netz mit n Standorten (Zufallsnetz: Zufallsbaum plus Leitungen bis zum mittleren Grad; Gitter, Ring mit Abkürzungen, skalenfreies Netz nach bevorzugter Anbindung; Verbundnetz: drei Regionen mit dem mittleren Grad im Inneren und genau der gewählten Zahl von Leitungen zwischen je zwei Regionen) und ein handgebautes **Lehrbeispiel mit zwei Werken**: Werk 1 (A, B, C, D) und Werk 2 (E, F, G, H) sind je ein vollständiges Netz, dazu die Leitungen A–E und A–F. Von Hand: Mindestgrad **3**, kleinster Schnitt **2** (A–E und A–F), Knotenzusammenhang **1** (der Standort A trennt die Werke). Der Zufall kommt nur aus `random.Random(seed)` mit `random()` (plattformstabil). Details und Formeln: Expander „📐 Mathematische Formulierung“ in der App.

## Methodik

- **Fluss mit Einheitskapazitäten** (Edmonds–Karp, ein Weg je Durchlauf). **Knotendisjunkt:** Jeder Standort wird in einen Eingang und einen Ausgang gespalten (Pfeil mit Kapazität 1), jede Leitung wird zu zwei Pfeilen mit großer Kapazität; der Fluss von s_aus nach t_ein ist κ(s, t), die gesättigten Standortpfeile am Schnitt sind die **trennende Standortmenge**. **Kantendisjunkt:** jede Leitung ist ein Paar gegenläufiger Pfeile mit Kapazität 1.
- **Wege als Zeugen:** Die disjunkten Wege werden aus dem Fluss zerlegt, die trennende Menge aus dem Restnetz gelesen; beides prüft die App vor der Anzeige.
- **Zusammenhang des Netzes:** κ als Minimum von κ(s, t) über alle nicht benachbarten Paare; λ als Minimum von λ(s₀, t) über alle t (n − 1 Flüsse).
- **Algorithmus von Even:** Mit dem bisher besten Wert k (anfangs der Mindestgrad) dienen nur die ersten k + 1 Standorte als Start, jeder gegen alle späteren. Eine trennende Menge mit höchstens k Standorten enthält nicht alle k + 1 Starts; einer liegt außerhalb und hat auf der anderen Seite einen Standort (oder war vorher schon Ziel).
- **Aufwand:** in **Flüssen** (ein Fluss je Paar), Erweiterungen und Besuchen (abgearbeitete Knoten der Breitensuchen), nie in Sekunden.
- **Unabhängige Prüfer:** Die App prüft jedes Ergebnis vor der Anzeige (Even gleich alle Paare, die Kette κ ≤ λ ≤ Mindestgrad, jede trennende Menge trennt und hat die richtige Größe, jede Weg-Menge ist disjunkt und hat die richtige Zahl, bei höchstens 14 Standorten gleich der Aufzählung aller Teilmengen).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`; Zähler über feste Netze (je Netztyp zehn bzw. zwölf, feste Zufalls-Seeds), nie ein einzelner Zufalls-Seed. Netztypen: Zufallsnetz mit mittlerem Grad 3, 5, 8, Gitter, Ring mit Abkürzungen, skalenfreies Netz, Verbundnetz (mittlerer Grad 8, zwei Leitungen zwischen je zwei Regionen).

| Frage | Befund |
|---|---|
| Stimmen alle Verfahren mit der Aufzählung aller Trennmengen überein? | Auf **84** Netzen mit 12 Standorten (sieben Netztypen, je zwölf Netze) stimmen **6.540** Prüfungen überein: Zusammenhang des Netzes nach beiden Verfahren, Zeugen und jedes der **3.060** nicht benachbarten Standortpaare mit seinen disjunkten Wegen und der trennenden Menge. Abweichungen: **0**. |
| Sagt der Mindestgrad den Zusammenhang? (etwa 30 Standorte, je Netztyp zehn Netze) | κ = λ = Mindestgrad gilt in **59 von 70** Netzen (84 %); ohne das Verbundnetz in **59 von 60**, die einzige Ausnahme ist ein Ring mit Abkürzungen (κ < λ). Im Verbundnetz in **0 von 10**: κ < λ in 9, λ < Mindestgrad in 10; Mindestgrad im Mittel **6,2**, λ **4**, κ **3**. Die Kette κ ≤ λ ≤ Mindestgrad ist in **0** Netzen verletzt. |
| Wie viele Paare hängen an einer Engstelle? | Anteil der nicht benachbarten Paare mit κ(s, t) kleiner als der kleinere Grad: **0 %** (Gitter, Zufallsnetz Grad 8), 4 % (Zufallsnetz Grad 5), 15 % (Zufallsnetz Grad 3), 8 % (skalenfreies Netz), **28 %** (Ring mit Abkürzungen, in 10 von 10 Netzen mindestens ein Paar), **96 %** (Verbundnetz); gezählt über **23.870** Paare. |
| Wie viele Flüsse spart der Algorithmus von Even? | Im Mittel über die sieben Netztypen das **3,1-Fache** (20 Standorte), **6,6-Fache** (40) und **13,8-Fache** (80) der Flüsse gegenüber allen nicht benachbarten Paaren (auf diesen dünnen Modellnetzen mit kleinem Mindestgrad; Quotient der Summen, bei 80 Standorten nur 4 Netze je Typ); bei 80 Standorten je nach Netztyp das **9,5- bis 20-Fache** (Zufallsnetz Grad 5: 2.960 Flüsse gegen **148**). Bei 20, 40 und 80 Standorten braucht Even in allen Fällen weniger Flüsse. |
| Wie verschiebt sich die Engstelle mit der Verbundstärke? (45 Standorte, mittlerer Grad 8, zehn Netze je Zeile) | Bei 1 / 2 / 3 / 5 Leitungen zwischen je zwei Regionen: κ im Mittel **1,8 / 2,8 / 3,9 / 4,8**, λ **2 / 4 / 4,5 / 4,8**, Mindestgrad **4,4 / 4,4 / 4,5 / 4,8**. κ < λ in 2 / **10** / 4 / 0 von 10 Netzen; ab **5** Leitungen gilt κ = λ = Mindestgrad in allen 10 gemessenen Netzen (45 Standorte); auf 100 weiteren Zufalls-Seeds bei 5 Leitungen in 98. |
| Das Lehrbeispiel von Hand? | Zwei Werke, 8 Standorte, 14 Leitungen: Mindestgrad **3**, λ **2**, κ **1**; alle **14** nicht benachbarten Paare haben eine Engstelle; alle Paare einzeln brauchen **14** Flüsse, Even **6**. |
| Ist die Rechnung korrekt? | κ nach Even und nach allen Paaren gleich `networkx.node_connectivity`, λ gleich `networkx.edge_connectivity` auf **48** festen Netzen; jedes nicht benachbarte Paar gleich `local_node_connectivity`, `minimum_node_cut` und `node_disjoint_paths` (**18** Netze), kantendisjunkt entsprechend auf 40 Paaren je Netz; bei kleinen Netzen gleich der Aufzählung aller Trennmengen (**40** Netze); invariant gegen Umnummerieren; eine zusätzliche Leitung senkt den Zusammenhang nie. `tests/test_oracle_menger.py` |

## Ehrliche Grenzen

- **Die Zufallsnetze sind dünn.** Ein Zufallsbaum plus Zusatzleitungen hat einen kleinen Mindestgrad (bei mittlerem Grad 5 ist er 1 oder 2, in je fünf von zehn Netzen), und der begrenzt dann alles; dass der Mindestgrad „fast alles sagt“, gilt für diese Netze. Auf dichten, regelmäßigen Netzen mit hohem Mindestgrad wäre die Engstelle öfter die Ausnahme (nicht gemessen).
- **Das Verbundnetz ist gebaut, nicht gefunden.** Drei dichte Regionen mit wenigen Leitungen dazwischen sind absichtlich so gewählt, dass die Engstelle sichtbar wird; wie oft reale Netze so gebaut sind, zeigt die Demo nicht.
- **Alle Leitungen gleich.** Mit Kapazitäten und Kosten ist Max-Flow gleich Min-Cut die allgemeinere Rechnung (`edmonds-karp-demo`).
- **Ein Paar oder der kleinste Wert.** Alle Paare auf einmal als Baum zeigt `gomory-hu-demo`.
- **Gezählt, nicht verstärkt.** Die Engstelle wird benannt, nicht behoben; Brücken und die Zahl nötiger Straßen zählt `bridges-demo`.
- **Gezielter Ausfall, kein Zufall.** Die Demo fragt nach der kleinsten Trennmenge, nicht nach der Wahrscheinlichkeit zufälliger Ausfälle.
- **Ungerichtetes Netz.** In gerichteten Netzen gilt der Satz von Menger ebenfalls, die Kette κ ≤ λ ≤ Mindestgrad aber nur mit Ein- und Ausgrad.
- **Größe:** bis 80 Standorte (das Gitter bis 81); Aufwand in Flüssen und Besuchen gezählt, nicht in Sekunden.

## Tests

Das Verzeichnis `tests/` enthält zurzeit 139 Tests (Laufzeit etwa eine Minute auf dem Entwicklungsrechner):

- **Kern** (`test_algorithm.py`): jede Einheit an von Hand gerechneten Mini-Netzen (Pfad, Kreis, vollständiges Netz, zwei Dreiecke mit gemeinsamem Standort, K₃,₃, Stern, zwei Werke): Flussnetz, lokale Zusammenhänge mit Wegen und trennenden Mengen, Even-Flüsse von Hand (7 gegen 10 auf dem Pfad, 6 gegen 14 im Lehrbeispiel), Rückfall auf die Nachbarn des schwächsten Standorts, Aufzählung, Prüfer.
- **Szenarien** (`test_scenario.py`): einfach, symmetrisch, zusammenhängend, deterministisch für jeden Netztyp; Größen (Gitter, skalenfreies Netz, Regionen, Leitungen zwischen den Regionen, Lehrbeispiel).
- **Orakel** (`test_oracle_menger.py`): `networkx` (`node_connectivity`, `edge_connectivity`, `local_node_connectivity`, `local_edge_connectivity`, `minimum_node_cut`, `minimum_edge_cut`, `node_disjoint_paths`, `edge_disjoint_paths`) und die Aufzählung aller Trennmengen; Eigenschaften (Kette von Whitney, Umnummerieren, Leitung hinzufügen, Zahl der Flüsse gleich der Zahl der nicht benachbarten Paare).
- **Randfälle** (`test_edge_cases.py`): ein Standort, zwei Standorte mit und ohne Leitung, zwei Komponenten, vollständiges Netz, Stern, benachbarte und gleiche Standorte, kleinste und größte Netzgröße je Netztyp, Regler-Extreme des Verbundnetzes.
- **Zweige** (`test_branches.py`): jedes Preset löst seine Beschreibung ein (Mindestgrad genügt, Engstelle im Verbundnetz, κ < λ, Ring, Even spart Flüsse); **Auswertung und Verdikte** (`test_evaluation.py`, `test_verdicts.py`) an handgesetzten Werten; **Befunde** (`test_claims.py`) für jede Zahl dieses README.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), Layout (Schnellstart oben, aktives Preset hervorgehoben), Footer, Laufzeit-Importe.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: ein Paar, das ganze Netz, Aufwand, fünf Experimente |
| `requirements-dev.txt` | Laufzeit plus pytest und networkx (Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `mng_algorithm.py` | Kern: Fluss, Knotenspaltung, lokale Zusammenhänge, Even, Aufzählung, Prüfer |
| `mng_constants.py` | Regler-Grenzen, Netztypen, Raster der Experimente, Farben, Presets |
| `mng_evaluation.py` | Analyse, Prüfung vor der Anzeige, Paaransicht, Verdikte |
| `mng_experiments.py` | Experimente über feste Netze |
| `mng_layout.py` | Fester Kopf (Stylesheet) |
| `mng_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `mng_scenario.py` | Netze: Zufallsnetz, Gitter, Ring, skalenfreies Netz, Verbundnetz, Lehrbeispiel, Karte |
| `mng_visualization.py` | Plotly-Abbildungen (Karte mit Wegen und Engstelle, Verteilung, Experimente; Achsen gesperrt) |
| `tests/` | Mini-Netze, Orakel, Randfälle, Zweige, Verdikte, Befunde, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Globaler Min-Cut**, die Zahl aller Min-Cuts, mehrere Terminals, Verstärken und Partitionieren: nicht Thema dieses Stücks.
- **Gerichtete Netze, Kapazitäten, Kosten:** siehe `edmonds-karp-demo` und die Netzwerkfluss-Linie.
- **Echte Netze oder Dateiimport:** die Netze sind synthetisch.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
