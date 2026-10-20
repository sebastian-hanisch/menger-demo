"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen; Permalink-Grenzen."""

import mng_constants as C
import mng_evaluation as ev
import mng_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["kind"] in C.KINDS and C.N_MIN <= preset["n"] <= C.N_MAX and C.DEG_MIN <= preset["deg"] <= C.DEG_MAX, name
        assert C.LINKS_MIN <= preset["links"] <= C.LINKS_MAX and 0 <= preset["seed"] <= C.SEED_MAX, name


def test_the_first_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[next(iter(C.PRESETS))]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert {spec.url_param for spec in P.SETTING_SPECS.values()} == {"kind", "n", "deg", "links", "seed"}


def test_every_kind_has_a_name_and_a_help_text():
    assert set(C.KIND_NAMES) == set(C.KIND_HELP) == set(C.KIND_REGLER) == set(C.KINDS)


def test_the_experiment_grid_uses_only_known_kinds_and_sizes_inside_the_regler_range():
    assert all(kind in C.KINDS and kind != "textbook" for kind, _deg in C.EX_KINDS)
    assert C.N_MIN <= C.EX_PAIR_N <= C.N_MAX and all(C.N_MIN <= n <= C.N_MAX for n, _count in C.EX_EVEN) and C.EX_EXACT_N <= C.BRUTE_N
    assert all(count <= len(C.SWEEP_SEEDS) for _n, count in C.EX_EVEN)
