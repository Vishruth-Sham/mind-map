"""Setup screen: validation, the one-seed-per-line box, building the map."""


def test_empty_question_and_no_seeds_are_rejected(app):
    app.open()
    p = app.page
    assert p.is_visible("#setup")
    p.click("#goBtn")
    assert "question" in p.text_content("#serr")
    p.fill("#q", "How might we X?")
    p.click("#goBtn")
    assert "seed" in p.text_content("#serr")
    assert p.is_visible("#setup")
    assert app.ev("S") is None


def test_whitespace_only_question_rejected(app):
    app.open()
    app.page.fill("#q", "   \n  ")
    app.page.fill("#seedin", "a")
    app.page.press("#seedin", "Enter")
    app.page.click("#goBtn")
    assert "question" in app.page.text_content("#serr")


def test_enter_in_question_moves_to_seed_input(app):
    app.open()
    app.page.fill("#q", "Q?")
    app.page.press("#q", "Enter")
    assert app.ev("document.activeElement.id") == "seedin"
    assert app.page.input_value("#q") == "Q?"


def test_seed_box_one_idea_per_line(app):
    app.open()
    p = app.page
    p.fill("#q", "Q?")
    p.click("#seedin")
    p.keyboard.type("Alpha")
    p.keyboard.press("Enter")          # Enter starts a new line, it doesn't submit
    p.keyboard.type("Beta")
    p.keyboard.press("Enter")
    p.keyboard.press("Enter")          # blank lines are ignored
    p.keyboard.type("Gamma")
    assert p.input_value("#seedin") == "Alpha\nBeta\n\nGamma"
    assert p.is_visible("#setup")
    p.click("#goBtn")
    p.wait_for_selector("#setup", state="hidden")
    seeds = sorted(n["text"] for k, n in app.nodes().items() if k != "root")
    assert seeds == ["Alpha", "Beta", "Gamma"]


def test_pasted_list_markers_and_semicolons_are_split(app):
    app.open()
    p = app.page
    p.fill("#q", "Q?")
    p.fill("#seedin", "- Alpha\n2. Beta\n* Gamma\n\n3D-printed lamp\n24-hour cafe; Delta")
    p.click("#goBtn")
    p.wait_for_selector("#setup", state="hidden")
    seeds = sorted(n["text"] for k, n in app.nodes().items() if k != "root")
    assert seeds == sorted(["Alpha", "Beta", "Gamma", "3D-printed lamp", "24-hour cafe", "Delta"])


def test_seed_box_grows_with_its_lines(app):
    app.open()
    p = app.page
    h0 = p.locator("#seedin").bounding_box()["height"]
    p.fill("#seedin", "\n".join(f"Seed {i}" for i in range(10)))
    p.dispatch_event("#seedin", "input")
    assert p.locator("#seedin").bounding_box()["height"] > h0 * 2


def test_pending_seed_text_is_added_on_map_it(app):
    app.open()
    p = app.page
    p.fill("#q", "Q?")
    p.fill("#seedin", "Typed but not entered")
    p.click("#goBtn")
    p.wait_for_selector("#setup", state="hidden")
    assert "Typed but not entered" in [n["text"] for n in app.nodes().values()]


def test_build_map_structure(app):
    app.open().build(q="How might we cook?", seeds=["A", "B", "C", "D"])
    st = app.state()
    assert st["nodes"]["root"]["text"] == "How might we cook?"
    assert st["q"] == "How might we cook?"
    assert len(st["nodes"]) == 5
    assert len(st["edges"]) == 4
    for k, n in st["nodes"].items():
        if k != "root":
            assert n["seed"] and app.has_edge("root", k)
    assert app.page.locator(".node").count() == 5
    assert app.page.text_content("#crumbq") == "How might we cook?"
    # every node is within the viewport after the initial fit
    vw, vh = 1360, 820
    for k in st["nodes"]:
        x, y = app.center(k)
        assert 0 < x < vw and 0 < y < vh


def test_context_toggle_and_ctx_saved(app):
    app.open()
    app.page.click("#ctxtog")
    assert app.page.is_visible("#sctx")
    app.page.fill("#sctx", "For kids")
    app.build()
    assert app.state()["ctx"] == "For kids"


def test_many_seeds_and_long_text(app):
    app.open()
    long = "A very long seed idea " * 30
    seeds = [f"Seed number {i}" for i in range(24)] + [long.strip()]
    app.build(seeds=seeds)
    assert len(app.nodes()) == 26
    # long node stays bounded in width and wraps
    nid = app.id_of(" ".join(long.split()))
    box = app.node(nid).bounding_box()
    assert box["width"] < 300


def test_home_reopens_setup_and_back_returns(app):
    app.open().build()
    p = app.page
    p.click("#home")
    assert p.is_visible("#setup")
    assert p.input_value("#q") == "How might we test this?"
    p.click("#backBtn")
    assert not p.is_visible("#setup")
    assert len(app.nodes()) == 4


def test_new_map_from_setup_is_undoable(app):
    app.open().build(seeds=["Old"])
    app.page.click("#home")
    app.build(q="New Q", seeds=["New"])
    assert app.state()["q"] == "New Q"
    app.page.keyboard.press("Control+z")
    assert app.state()["q"] == "How might we test this?"
