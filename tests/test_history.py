"""Undo/redo across every kind of mutation."""
import json


def norm(st):
    """State minus measurement caches, for comparing snapshots."""
    st = json.loads(json.dumps(st))
    for n in st["nodes"].values():
        for k in ("_w", "_h", "_dry"):
            n.pop(k, None)
    st["edges"] = sorted(st["edges"])
    return st


def check_roundtrip(app, action):
    before = norm(app.state())
    n0 = app.undo_len()
    action()
    app.settle(150)
    after = norm(app.state())
    assert after != before, "action did not change state"
    assert app.undo_len() == n0 + 1, "action must add exactly one undo step"
    app.page.click("#undo")
    assert norm(app.state()) == before
    app.page.click("#redo")
    assert norm(app.state()) == after
    assert not app.page.is_disabled("#undo")


def test_undo_redo_every_mutation(make_app):
    app = make_app().mock().open().build(seeds=["Alpha", "Beta", "Gamma"])
    p = app.page
    a, b, g = app.id_of("Alpha"), app.id_of("Beta"), app.id_of("Gamma")
    assert p.is_disabled("#undo") and p.is_disabled("#redo")

    def drag():
        x, y = app.center(a)
        app.drag(x, y, x + 90, y + 40)
    check_roundtrip(app, drag)

    def multidrag():
        app.select(a)
        app.select(b, shift=True)
        x, y = app.center(b)
        app.drag(x, y, x - 50, y + 70)
    check_roundtrip(app, multidrag)

    def edit():
        app.node(g).dblclick()
        p.keyboard.type("Gamma edited")
        p.keyboard.press("Enter")
    check_roundtrip(app, edit)

    def star():
        app.select(g)
        p.keyboard.press("s")
    check_roundtrip(app, star)

    def link_handle():
        hx, hy = app.handle(a)
        x, y = app.center(g)
        app.drag(hx, hy, x, y)
    check_roundtrip(app, link_handle)

    def unlink_edge():
        x, y = app.ev("(k)=>{const g=edgeGeom(k);return [g.mx*V.k+V.x,g.my*V.k+V.y]}", app.edges()[0])
        p.mouse.click(x, y)
        p.keyboard.press("Delete")
    check_roundtrip(app, unlink_edge)

    def delete():
        app.select(b)
        p.keyboard.press("Delete")
    check_roundtrip(app, delete)

    def add_child():
        app.select(a)
        p.keyboard.press("Tab")
        p.keyboard.type("Kid")
        p.keyboard.press("Enter")
    # adding a child + typing its text are two steps (create, then rename)
    before = norm(app.state())
    add_child()
    p.click("#undo")
    p.click("#undo")
    assert norm(app.state()) == before

    def tidy():
        p.click("#tidy")
        p.wait_for_function("!tidying")
    check_roundtrip(app, tidy)

    def ai_expand():
        app.select(a)
        p.locator('#ctx button[data-g="yes"]').click()
        p.wait_for_function("busy.size===0")
        app.settle(500)
    check_roundtrip(app, ai_expand)

    def combine():
        app.select(a)
        app.select(g, shift=True)
        p.locator('#ctx button[data-a="combine"]').click()
        p.wait_for_function("busy.size===0")
    # combine = hub (one step) + hybrids (second step)
    before = norm(app.state())
    n0 = app.undo_len()
    combine()
    assert app.undo_len() == n0 + 2
    p.click("#undo")
    p.click("#undo")
    assert norm(app.state()) == before

    def import_map():
        p.click("#export")
        p.click("#tJson")
        v = json.loads(p.input_value("#extext"))
        v["nodes"]["root"]["text"] = "Imported Q"
        p.fill("#extext", json.dumps(v))
        p.click("#exImp")
    check_roundtrip(app, import_map)


def test_new_action_clears_redo(app):
    app.open().build()
    a = app.id_of("Alpha")
    app.select(a)
    app.page.keyboard.press("s")
    app.page.keyboard.press("Control+z")
    assert not app.page.is_disabled("#redo")
    app.page.keyboard.press("s")
    assert app.page.is_disabled("#redo")


def test_undo_restores_selection_sanity(app):
    app.open().build()
    app.page.keyboard.press("Escape")
    a = app.id_of("Alpha")
    app.select(a)
    app.page.keyboard.press("Tab")
    p = app.page
    p.keyboard.press("Escape")
    child = app.ev("[...sel][0]")
    assert child != a
    p.keyboard.press("Control+z")
    assert app.ev("[...sel]") == []
    assert not p.is_visible("#ctx")
