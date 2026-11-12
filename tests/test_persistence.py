"""Export / import, localStorage persistence, and booting from the seed block."""
import json

import pytest


def open_export(app, mode="out"):
    app.page.click("#export")
    if mode == "json":
        app.page.click("#tJson")
    return app.page.input_value("#extext")


def test_export_outline(app):
    app.open().build(q="Q?", seeds=["Alpha", "Beta"])
    a = app.id_of("Alpha")
    app.select(a)
    app.page.keyboard.press("Tab")
    app.page.keyboard.type("Child of alpha")
    app.page.keyboard.press("Enter")
    app.select(a)
    app.page.keyboard.press("s")
    app.ev("()=>{mkNode('Floating',900,900);render()}")
    out = open_export(app)
    assert out.splitlines()[:4] == ["# Q?", "- Alpha ★", "  - Child of alpha", "- Beta"]
    assert "Unlinked ideas\n- Floating" in out
    app.page.keyboard.press("Escape")
    assert app.page.is_hidden("#exp")


def test_json_roundtrip_import(app):
    app.open().build(seeds=["Alpha", "Beta", "Gamma"])
    app.ev("()=>{mkNode('Extra',10,10);render()}")
    original = app.state()
    dump = open_export(app, "json")
    v = json.loads(dump)
    assert set(v) >= {"q", "ctx", "seq", "edges", "nodes"}
    app.page.click("#exClose")
    # wreck the map, then import the dump
    app.select(app.id_of("Alpha"))
    app.page.keyboard.press("Delete")
    app.page.click("#export")
    app.page.fill("#extext", dump)
    app.page.click("#exImp")
    assert app.page.is_hidden("#exp")
    assert app.toast() == "Imported"
    st = app.state()
    assert sorted(st["edges"]) == sorted(original["edges"])
    assert {k: n["text"] for k, n in st["nodes"].items()} == {k: n["text"] for k, n in original["nodes"].items()}
    assert st["seq"] == original["seq"]
    # new ids never collide with imported ones
    app.select("root")
    app.page.keyboard.press("Tab")
    app.page.keyboard.press("Escape")
    assert len(app.nodes()) == len(original["nodes"]) + 1


@pytest.mark.parametrize("payload", [
    "", "not json", "null", "[]", '{"nodes":{}}', '{"nodes":{"root":{}}}',
    '{"nodes":{"n1":{"text":"x"}},"edges":[]}', '{"nodes":[{"id":"root"}],"edges":[]}',
])
def test_invalid_import_is_rejected(app, payload):
    app.open().build()
    before = app.state()
    app.page.click("#export")
    app.page.fill("#extext", payload)
    app.page.click("#exImp")
    assert not app.page.is_hidden("#exp")
    assert "map file" in app.toast()
    assert app.state() == before
    assert app.undo_len() == 0


def test_import_sanitises_hostile_and_sloppy_files(app):
    app.open().build()
    evil = {
        "q": "ignored",
        "nodes": {
            "root": {"text": "Imported <b>Q</b>", "x": "nope"},
            "n2": {"text": "Two", "x": 10, "y": None, "c": "pink", "star": 1},
            "n9": {"text": "  spaced \n out  ", "x": 300, "y": 40, "c": 2},
            'x"><img src=x onerror=window.__pwned=1>': {"text": "evil"},
            "n3": "not an object",
        },
        "edges": ["root|n2", "n2|root", "n9|n9", "root|ghost", 'root|x"><img src=x onerror=window.__pwned=1>', 5, "root|n9"],
    }  # no seq at all
    app.page.click("#export")
    app.page.fill("#extext", json.dumps(evil))
    app.page.click("#exImp")
    app.settle(200)
    st = app.state()
    assert set(st["nodes"]) == {"root", "n2", "n9"}
    assert sorted(st["edges"]) == ["n2|root", "n9|root"]
    assert st["seq"] == 9
    assert st["q"] == "Imported <b>Q</b>"
    assert st["nodes"]["root"]["x"] == 0 and st["nodes"]["n2"]["y"] == 0
    assert st["nodes"]["n2"]["c"] is None and st["nodes"]["n2"]["star"] is True
    assert st["nodes"]["n9"]["text"] == "spaced out"
    assert app.ev("window.__pwned") is None
    assert app.page.locator("#nodes b, #nodes img").count() == 0
    # new nodes get fresh ids
    app.select("root")
    app.page.keyboard.press("Tab")
    assert app.ev("editing") == "n10"
    app.page.keyboard.press("Escape")


def test_persistence_across_reload(app):
    app.open().build(seeds=["Alpha", "Beta"])
    a = app.id_of("Alpha")
    x, y = app.center(a)
    app.drag(x, y, x + 70, y + 20)
    app.select(a)
    app.page.keyboard.press("s")
    app.page.click("#zin")
    st, v = app.state(), app.ev("({...V})")
    app.page.reload()
    app.page.wait_for_function("document.readyState==='complete'")
    assert app.page.is_hidden("#setup")
    st2 = app.state()
    assert st2["edges"] == st["edges"]
    for k, n in st["nodes"].items():
        assert st2["nodes"][k]["text"] == n["text"]
        assert abs(st2["nodes"][k]["x"] - n["x"]) < 1e-6
    assert st2["nodes"][a]["star"]
    assert abs(app.ev("V.k") - v["k"]) < 1e-9


def test_saved_positions_are_final_not_mid_animation(app):
    app.open().build(seeds=["Alpha", "Beta", "Gamma"])
    # buildMap animates seeds out from the root; what's stored must be the final layout
    saved = app.ev("JSON.parse(localStorage.getItem(KEY)).S.nodes")
    for k, n in app.nodes().items():
        assert abs(saved[k]["x"] - n["x"]) < 1e-6
    assert any(abs(n["x"]) > 50 for k, n in saved.items() if k != "root")


def test_corrupt_storage_falls_back_to_setup(app):
    app.open()
    app.ev("localStorage.setItem(KEY,'{\"S\":{\"nodes\":5}}')")
    app.page.reload()
    assert app.page.is_visible("#setup")
    app.ev("localStorage.setItem(KEY,'not json')")
    app.page.reload()
    assert app.page.is_visible("#setup")


def test_seed_block_boots_into_map(app):
    app.seeded({"id": "abc123", "q": "How might we seed?", "ctx": "Ctx here", "seeds": ["One", "Two", "Three"]}).open()
    app.settle(600)
    assert app.page.is_hidden("#setup")
    st = app.state()
    assert st["q"] == "How might we seed?" and st["ctx"] == "Ctx here"
    assert sorted(n["text"] for n in st["nodes"].values()) == ["How might we seed?", "One", "Three", "Two"]
    assert app.ev("KEY") == "mindmapper-v2:abc123"
    # edits persist under the namespaced key and survive reload (no rebuild from seed)
    app.select(app.id_of("One"))
    app.page.keyboard.press("Delete")
    app.page.reload()
    app.settle(300)
    assert len(app.nodes()) == 3


def test_seed_block_special_characters(app):
    long = "Very long seed " * 60
    seed = {"id": "sp1", "q": 'How might we handle "quotes", </script> & <!-- comments -->?',
            "ctx": "Emoji 🚀🌱 and \\backslashes\\ and 'single' quotes",
            "seeds": ["Plain", "</script><script>window.__pwned=1</script>", "Emoji 🎉 seed", "Ünïcödé — dashes", long, "Line\nbreak"]}
    app.seeded(seed).open()
    app.settle(600)
    assert app.ev("window.__pwned") is None
    st = app.state()
    assert st["q"] == seed["q"]
    assert st["ctx"] == seed["ctx"]
    texts = {n["text"] for n in st["nodes"].values()}
    assert "</script><script>window.__pwned=1</script>" in texts
    assert "Emoji 🎉 seed" in texts and "Ünïcödé — dashes" in texts and "Line break" in texts
    assert long.strip() in texts
    assert app.page.text_content("#crumbq") == seed["q"]


def test_seed_block_fully_unicode_escaped(app):
    raw = json.dumps({"id": "u1", "q": "Q <!--<script>", "seeds": ["a</script>b"]}).replace("<", "\\u003c")
    app.seeded(None, raw=raw).open()
    app.settle(400)
    assert app.state()["q"] == "Q <!--<script>"
    assert "a</script>b" in [n["text"] for n in app.nodes().values()]


@pytest.mark.parametrize("seed,expect_q,expect_chips", [
    ({"id": "s1", "q": "Only a question", "seeds": []}, "Only a question", []),
    ({"id": "s2", "q": "Q", "seeds": ["", "  ", None, {"x": 1}]}, "Q", []),
    ({"id": "s3", "seeds": ["Orphan seed"]}, "", ["Orphan seed"]),
    ({"id": "blank1"}, "", []),   # a bare /mind-map: blank map on the setup screen
])
def test_incomplete_seed_block_prefills_setup(app, seed, expect_q, expect_chips):
    app.seeded(seed).open()
    assert app.page.is_visible("#setup")
    assert app.page.input_value("#q") == expect_q
    assert app.page.locator(".chip > span").all_text_contents() == expect_chips


def test_malformed_seed_json_shows_setup(app):
    app.seeded(None, raw='{"q": "broken",').open()
    assert app.page.is_visible("#setup")


def test_template_keeps_exact_empty_seed_tag():
    from conftest import APP, SEED_TAG
    assert APP.read_text(encoding="utf-8").count(SEED_TAG) == 1


@pytest.mark.parametrize("name", ["app.js", "app.css"])
def test_skill_bundles_current_app_files(name):
    """The /mind-map skill ships its own copy of the app; it must match app/."""
    from conftest import APP
    bundled = APP.parent.parent / "skill" / "mind-map" / name
    assert bundled.read_bytes() == (APP.parent / name).read_bytes(), \
        f"skill/mind-map/{name} is stale: run  cp app/app.js app/app.css skill/mind-map/"
