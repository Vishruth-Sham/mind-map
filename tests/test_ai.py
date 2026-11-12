"""AI generation through the (mocked) `sample` capability, including failure modes,
interacting mid-generation, Keep growing, scoping, the cap and combine."""
import pytest


def ai_map(make_app, **mock):
    return make_app().mock(**mock).open().build(seeds=["Alpha", "Beta", "Gamma"])


def grow_btn(app, nid, mode="yes"):
    app.select(nid)
    app.page.locator(f'#ctx button[data-g="{mode}"]').click()


def wait_idle(app):
    app.page.wait_for_function("busy.size===0")
    app.settle(550)


def dblclick_xy(app, nid):
    """Double-click by coordinates: a busy node wobbles, and Playwright's locator.dblclick
    would wait for it to stop moving (i.e. until generation finished)."""
    app.page.mouse.dblclick(*app.center(nid))


def dom_matches_model(app):
    return app.ev("document.querySelectorAll('#nodes .node').length===Object.keys(S.nodes).length")


def test_without_capability_generation_is_off(app):
    app.open().build()
    p = app.page
    assert p.is_disabled("#grow")
    assert "generation off" in p.text_content("#meta")
    app.select(app.id_of("Alpha"))
    assert p.locator('#ctx button[data-g="yes"]').is_disabled()
    p.keyboard.press("g")
    assert "off" in app.toast()
    p.click("#grow", force=True)
    assert app.ev("growing") is False


@pytest.mark.parametrize("mode,phrase", [("yes", "Yes, and"), ("wild", "wild"), ("real", "concrete"), ("flip", "Flip it")])
def test_grow_modes(make_app, mode, phrase):
    app = ai_map(make_app)
    a = app.id_of("Alpha")
    grow_btn(app, a, mode)
    wait_idle(app)
    kids = [k for k, n in app.nodes().items() if n["ai"]]
    assert len(kids) == 4
    for k in kids:
        assert app.has_edge(a, k)
        assert app.nodes()[k]["c"] == app.nodes()[a]["c"]
    prompt = app.ev("window.__calls[0].prompt")
    assert phrase in prompt
    assert "How might we test this?" in prompt and '"Alpha"' in prompt
    assert dom_matches_model(app)
    assert app.page.locator(".node.ai").count() == 4
    assert "4 generated" in app.page.text_content("#meta")


def test_grow_prompt_uses_only_the_path_from_the_root(make_app):
    app = ai_map(make_app)
    grow_btn(app, app.id_of("Alpha"))
    wait_idle(app)
    child = app.id_of("Idea 1")
    app.ev("(id)=>grow(id,'yes',4)", child)
    wait_idle(app)
    prompt = app.ev("window.__calls[window.__calls.length-1].prompt")
    assert "How might we test this? → Alpha → Idea 1" in prompt
    # siblings, other branches and the idea's own neighbours stay out of it
    for other in ("Beta", "Gamma", "Idea 2", "Idea 3", "Idea 4"):
        assert other not in prompt, other


def test_grow_root_makes_new_seed_branches(make_app):
    app = ai_map(make_app)
    grow_btn(app, "root")
    wait_idle(app)
    new = [n for n in app.nodes().values() if n["ai"]]
    assert len(new) == 4 and all(n["seed"] for n in new)
    assert len({n["c"] for n in app.nodes().values() if n["seed"]}) == 7


def test_g_key_grows(make_app):
    app = ai_map(make_app)
    app.select(app.id_of("Beta"))
    app.page.keyboard.press("G")
    wait_idle(app)
    assert len(app.nodes()) == 8


def test_objects_and_junk_entries(make_app):
    app = ai_map(make_app, mode="objects")
    grow_btn(app, app.id_of("Alpha"))
    wait_idle(app)
    texts = sorted(n["text"] for n in app.nodes().values() if n["ai"])
    assert texts == ["Idea 1", "Idea 2", "Idea 3", "Idea 4"]


def test_null_entries_are_dropped(make_app):
    app = ai_map(make_app, mode="null")
    grow_btn(app, app.id_of("Alpha"))
    wait_idle(app)
    texts = [n["text"] for n in app.nodes().values() if n["ai"]]
    assert "null" not in texts and "" not in texts
    assert "Real idea 1" in texts


def test_text_fallback_without_json_helper(make_app):
    app = ai_map(make_app, json=False)
    grow_btn(app, app.id_of("Alpha"))
    wait_idle(app)
    assert len([n for n in app.nodes().values() if n["ai"]]) == 4
    assert app.ev("window.__calls.every(c=>!c.asJson)")


@pytest.mark.parametrize("mode", ["empty", "text", "garbage"])
def test_nothing_usable_back(make_app, mode):
    app = ai_map(make_app, mode=mode)
    a = app.id_of("Alpha")
    grow_btn(app, a)
    wait_idle(app)
    assert len(app.nodes()) == 4
    assert "Nothing came back" in app.toast()
    assert app.undo_len() == 0
    assert app.ev("(id)=>S.nodes[id]._dry", a) == 1


def test_rate_limited(make_app):
    app = ai_map(make_app, mode="rate")
    grow_btn(app, app.id_of("Alpha"))
    wait_idle(app)
    assert "too fast" in app.toast()
    assert app.ev("sample!==null")
    app.page.keyboard.press("Escape")
    app.page.click("#grow")
    app.page.wait_for_function("!growing")
    assert "too fast" in app.toast()


def test_not_granted_disables_generation(make_app):
    app = ai_map(make_app, mode="denied")
    app.page.click("#grow")
    app.page.wait_for_function("!growing")
    assert "not allowed" in app.toast()
    assert app.page.is_disabled("#grow")
    assert "generation off" in app.page.text_content("#meta")


def test_generic_error(make_app):
    app = ai_map(make_app, mode="throw")
    grow_btn(app, app.id_of("Alpha"))
    wait_idle(app)
    assert app.toast() == "Could not generate ideas: boom"


def test_busy_node_wobbles_and_buttons_disable(make_app):
    app = ai_map(make_app, delay=800)
    a = app.id_of("Alpha")
    grow_btn(app, a)
    app.settle(100)
    assert "busy" in app.node(a).get_attribute("class")
    assert app.page.locator('#ctx button[data-g="yes"]').is_disabled()
    app.page.keyboard.press("g")  # second request for same node is ignored
    wait_idle(app)
    assert app.ev("window.__calls.length") == 1
    assert "busy" not in app.node(a).get_attribute("class")


def test_edit_node_during_generation(make_app):
    app = ai_map(make_app, delay=700)
    a = app.id_of("Alpha")
    grow_btn(app, a)
    dblclick_xy(app, a)
    app.page.keyboard.type("Edited mid-gen")
    app.settle(900)  # results land while the editor is open: render is deferred
    assert app.ev("editing") == a
    assert len(app.nodes()) == 8
    assert not dom_matches_model(app)
    app.page.keyboard.press("Enter")
    app.settle(100)
    assert dom_matches_model(app)
    assert app.nodes()[a]["text"] == "Edited mid-gen"
    assert app.ev("dirty") is False
    assert "busy" not in app.node(a).get_attribute("class")
    assert app.page.text_content("#meta").startswith("7 ideas")


def test_delete_node_being_expanded(make_app):
    app = ai_map(make_app, delay=600)
    a = app.id_of("Alpha")
    grow_btn(app, a)
    app.page.keyboard.press("Delete")
    wait_idle(app)
    assert a not in app.nodes()
    assert len(app.nodes()) == 3
    # undo brings it back, results were not attached to a ghost
    app.page.keyboard.press("Control+z")
    assert a in app.nodes() and len(app.nodes()) == 4


def test_undo_during_generation_keeps_results_consistent(make_app):
    app = ai_map(make_app, delay=600)
    a, b = app.id_of("Alpha"), app.id_of("Beta")
    app.select(b)
    app.page.keyboard.press("s")
    grow_btn(app, a)
    app.page.keyboard.press("Control+z")  # undo the star while generating
    wait_idle(app)
    st = app.nodes()
    assert not st[b]["star"]
    kids = [k for k, n in st.items() if n["ai"]]
    assert len(kids) == 4 and all(app.has_edge(a, k) for k in kids)
    app.page.keyboard.press("Control+z")
    assert len(app.nodes()) == 4


def test_new_map_during_generation_discards_results(make_app):
    app = ai_map(make_app, delay=600)
    grow_btn(app, app.id_of("Alpha"))
    app.page.click("#home")
    app.build(q="Fresh", seeds=["One", "Two", "Three"])
    app.settle(800)
    assert sorted(n["text"] for n in app.nodes().values()) == ["Fresh", "One", "Three", "Two"]
    assert app.ev("busy.size") == 0


def test_keep_growing_start_stop(make_app):
    app = ai_map(make_app, delay=150)
    p = app.page
    p.click("#grow")
    assert app.ev("growing") and p.text_content("#growl") == "Stop growing"
    p.wait_for_function("Object.keys(S.nodes).length>=16", timeout=10000)
    p.click("#grow")
    assert not app.ev("growing")
    wait_idle(app)
    n = len(app.nodes())
    app.settle(800)
    assert len(app.nodes()) == n, "nothing should be added after Stop settles"
    assert p.text_content("#growl") == "Keep growing"
    # breadth first: every seed got expanded before any grandchild
    for s in ("Alpha", "Beta", "Gamma"):
        assert len([e for e in app.edges() if app.id_of(s) in e.split("|")]) > 1


def test_keep_growing_rapid_toggle_never_runs_two_loops(make_app):
    app = ai_map(make_app, delay=300)
    for _ in range(7):
        app.page.click("#grow")
        app.settle(40)
    assert app.ev("growing")
    app.settle(1500)
    assert app.ev("window.__maxInflight") == 1
    app.page.click("#grow")
    wait_idle(app)
    assert not app.ev("growing")


def test_keep_growing_scoped_to_selection(make_app):
    app = ai_map(make_app)
    a = app.id_of("Alpha")
    app.select(a)
    assert app.page.text_content("#growl") == "Grow selected"
    app.page.click("#grow")
    app.page.wait_for_function("Object.keys(S.nodes).length>=14", timeout=10000)
    app.page.click("#grow")
    wait_idle(app)
    b, g = app.id_of("Beta"), app.id_of("Gamma")
    assert [e for e in app.edges() if b in e.split("|")] == [e for e in app.edges() if b in e.split("|") and "root" in e]
    assert len([e for e in app.edges() if g in e.split("|")]) == 1
    prompts = app.ev("window.__calls.map(c=>c.prompt)")
    assert all("Alpha" in pr for pr in prompts)


def test_keep_growing_scoped_to_starred(make_app):
    app = ai_map(make_app)
    g = app.id_of("Gamma")
    app.select(g)
    app.page.keyboard.press("s")
    app.page.keyboard.press("Escape")
    assert app.page.text_content("#growl") == "Grow starred"
    app.page.click("#grow")
    app.page.wait_for_function("Object.keys(S.nodes).length>=12", timeout=10000)
    app.page.click("#grow")
    wait_idle(app)
    for s in ("Alpha", "Beta"):
        assert len([e for e in app.edges() if app.id_of(s) in e.split("|")]) == 1


def test_keep_growing_stops_when_everything_dry(make_app):
    app = ai_map(make_app, mode="empty")
    app.page.click("#grow")
    app.page.wait_for_function("!growing", timeout=15000)
    assert "Every branch" in app.toast()
    assert app.ev("window.__calls.length") == 6  # 3 leaves x 2 tries


def test_keep_growing_cap(make_app):
    app = ai_map(make_app)
    # pad the map to just under the cap with loose ideas far away
    app.ev("""()=>{for(let i=0;i<208;i++){const id=mkNode('Filler '+i,5000+(i%20)*260,(i/20|0)*120);S.nodes[id]._dry=9}render()}""")
    assert len(app.nodes()) == 212
    app.page.click("#grow")
    app.page.wait_for_function("!growing", timeout=15000)
    assert len(app.nodes()) == 220
    assert "220 ideas" in app.toast()
    app.page.click("#grow")
    app.page.wait_for_function("!growing", timeout=5000)
    assert len(app.nodes()) == 220


def test_editing_while_keep_growing_flushes_render(make_app):
    app = ai_map(make_app, delay=120)
    app.page.click("#grow")
    app.settle(200)
    a = app.id_of("Alpha")
    dblclick_xy(app, a)
    app.page.keyboard.type("While growing")
    app.settle(1200)
    assert app.ev("editing") == a
    app.page.keyboard.press("Enter")
    app.page.click("#grow")
    wait_idle(app)
    assert dom_matches_model(app)
    assert app.nodes()[a]["text"] == "While growing"
    assert not app.ev("dirty")
    # every node is drawn where the model says it is
    bad = app.ev("""()=>Object.values(S.nodes).filter(n=>{const el=els[n.id];return !el||Math.abs(parseFloat(el.style.left)-n.x)>.5||Math.abs(parseFloat(el.style.top)-n.y)>.5}).length""")
    assert bad == 0


def test_drag_while_keep_growing_rerenders(make_app):
    app = ai_map(make_app, delay=100)
    b = app.id_of("Beta")
    app.page.click("#grow")
    x, y = app.center(b)
    m = app.page.mouse
    m.move(x, y)
    m.down()
    for i in range(30):
        m.move(x + i * 4, y + i * 3)
        app.settle(30)
    m.up()
    app.page.click("#grow")
    wait_idle(app)
    assert app.ev("dragSet.size") == 0
    assert app.page.locator(".node.dragging").count() == 0
    k = app.ev("V.k")
    assert app.nodes()[b]["x"] != 0


def test_combine(make_app):
    app = ai_map(make_app)
    a, b = app.id_of("Alpha"), app.id_of("Beta")
    app.select(a)
    app.select(b, shift=True)
    app.page.locator('#ctx button[data-a="combine"]').click()
    wait_idle(app)
    hub = app.id_of("Alpha + Beta")
    assert app.has_edge(a, hub) and app.has_edge(b, hub)
    hybrids = [k for k, n in app.nodes().items() if n["ai"]]
    assert len(hybrids) == 4 and all(app.has_edge(hub, h) for h in hybrids)
    assert "Combine these ideas" in app.ev("window.__calls[0].prompt")


def test_combine_hub_deleted_mid_generation(make_app):
    app = ai_map(make_app, delay=600)
    a, b = app.id_of("Alpha"), app.id_of("Beta")
    app.select(a)
    app.select(b, shift=True)
    app.page.locator('#ctx button[data-a="combine"]').click()
    app.page.keyboard.press("Delete")  # hub is selected after combine starts
    wait_idle(app)
    assert len(app.nodes()) == 4
    assert "Could not" not in app.toast()


def test_combine_failure_message(make_app):
    app = ai_map(make_app, mode="rate")
    app.select(app.id_of("Alpha"))
    app.select(app.id_of("Beta"), shift=True)
    app.page.locator('#ctx button[data-a="combine"]').click()
    wait_idle(app)
    assert "too fast" in app.toast()


def test_duplicate_ideas_are_skipped(make_app):
    app = ai_map(make_app)
    app.ev("window.__mock.mode='ok';window.__mock.n=0")
    a = app.id_of("Alpha")
    grow_btn(app, a)
    wait_idle(app)
    app.ev("window.__mock.n=0")  # same 4 ideas again
    grow_btn(app, a)
    wait_idle(app)
    assert len([n for n in app.nodes().values() if n["ai"]]) == 4


def test_keep_growing_never_uses_wilder(make_app):
    app = ai_map(make_app, delay=20)
    app.page.click("#grow")
    app.page.wait_for_function("window.__calls.length>=8", timeout=15000)
    app.page.click("#grow")
    wait_idle(app)
    prompts = app.ev("window.__calls.map(c=>c.prompt)")
    assert not any("Push it wild" in pr for pr in prompts)
