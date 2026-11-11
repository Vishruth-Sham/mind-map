"""Canvas interactions: drag, select, link, unlink, delete, edit, keyboard, view."""
import pytest


@pytest.fixture
def m(app):
    return app.open().build(seeds=["Alpha", "Beta", "Gamma", "Delta"])


def test_click_selects_and_shows_toolbar(m):
    a = m.id_of("Alpha")
    m.select(a)
    assert m.ev("[...sel]") == [a]
    assert m.page.is_visible("#ctx")
    m.page.keyboard.press("Escape")
    assert m.ev("sel.size") == 0
    assert not m.page.is_visible("#ctx")


def test_click_empty_canvas_clears_selection(m):
    m.select(m.id_of("Alpha"))
    x, y = m.empty_point()
    m.page.mouse.click(x, y)
    assert m.ev("sel.size") == 0


def test_drag_single_node(m):
    a = m.id_of("Alpha")
    before = m.nodes()[a]
    x, y = m.center(a)
    m.drag(x, y, x + 100, y + 60)
    after = m.nodes()[a]
    k = m.ev("V.k")
    assert abs(after["x"] - before["x"] - 100 / k) < 2
    assert abs(after["y"] - before["y"] - 60 / k) < 2
    assert m.undo_len() == 1
    # a drag is not a click: selection unchanged
    assert m.ev("sel.size") == 0


def test_tiny_move_is_a_click_not_a_drag(m):
    a = m.id_of("Alpha")
    x, y = m.center(a)
    m.drag(x, y, x + 2, y + 1, steps=2)
    assert m.undo_len() == 0
    assert m.ev("[...sel]") == [a]


def test_multi_select_with_shift_and_drag_together(m):
    a, b = m.id_of("Alpha"), m.id_of("Beta")
    m.select(a)
    m.select(b, shift=True)
    assert sorted(m.ev("[...sel]")) == sorted([a, b])
    n0 = m.nodes()
    x, y = m.center(a)
    m.drag(x, y, x + 80, y + 80)
    n1 = m.nodes()
    for i in (a, b):
        assert n1[i]["x"] - n0[i]["x"] > 30
    c = m.id_of("Gamma")
    assert n1[c]["x"] == n0[c]["x"]
    # shift-click again toggles off
    m.select(b, shift=True)
    assert m.ev("[...sel]") == [a]


def test_marquee_select(m):
    # Select everything by shift-dragging a box around the whole viewport content.
    m.drag(5, 70, 1355, 760, shift=True)
    assert m.ev("sel.size") == 5
    assert not m.page.is_visible("#marq")
    assert m.page.locator("#ctx").text_content().find("Combine 5") >= 0


def test_pan_by_dragging_canvas_and_wheel(m):
    v0 = m.ev("({...V})")
    x, y = m.empty_point()
    m.drag(x, y, x + 50, y + 30)
    v1 = m.ev("({...V})")
    assert abs(v1["x"] - v0["x"] - 50) < 1 and abs(v1["y"] - v0["y"] - 30) < 1
    m.page.mouse.move(x, y)
    m.page.mouse.wheel(0, 100)
    m.settle(50)
    assert abs(m.ev("V.y") - (v1["y"] - 100)) < 1
    m.page.keyboard.down("Control")
    m.page.mouse.wheel(0, -100)
    m.page.keyboard.up("Control")
    assert m.ev("V.k") > v1["k"]


def test_zoom_buttons_and_fit(m):
    k0 = m.ev("V.k")
    m.page.click("#zin")
    assert m.ev("V.k") > k0
    assert m.page.text_content("#zoomv") == f"{round(m.ev('V.k') * 100)}%"
    for _ in range(30):
        m.page.click("#zout")
    assert abs(m.ev("V.k") - 0.15) < 1e-6
    m.page.click("#fit")
    m.settle(500)
    for k in m.nodes():
        x, y = m.center(k)
        assert 0 < x < 1360 and 60 < y < 820


def test_link_via_handle(m):
    a, b = m.id_of("Alpha"), m.id_of("Gamma")
    assert not m.has_edge(a, b)
    hx, hy = m.handle(a)
    tx, ty = m.center(b)
    m.drag(hx, hy, tx, ty)
    assert m.has_edge(a, b)
    assert m.toast() == "Linked"
    assert m.ev("tmpPath") == ""


def test_duplicate_link_is_refused(m):
    a = m.id_of("Alpha")
    hx, hy = m.handle(a)
    tx, ty = m.center("root")
    n_edges = len(m.edges())
    m.drag(hx, hy, tx, ty)
    assert len(m.edges()) == n_edges
    assert m.toast() == "Already linked"
    assert m.undo_len() == 0


def test_self_link_is_ignored(m):
    a = m.id_of("Alpha")
    hx, hy = m.handle(a)
    x, y = m.center(a)
    n_edges = len(m.edges())
    m.drag(hx, hy, x, y)
    assert len(m.edges()) == n_edges
    assert m.undo_len() == 0


def test_drop_handle_on_empty_space_creates_connected_node(m):
    a = m.id_of("Alpha")
    hx, hy = m.handle(a)
    x, y = m.empty_point()
    m.drag(hx, hy, x, y)
    assert m.ev("editing") is not None
    m.page.keyboard.type("Spawned idea")
    m.page.keyboard.press("Enter")
    nid = m.id_of("Spawned idea")
    assert m.has_edge(a, nid)
    assert m.nodes()[nid]["c"] == m.nodes()[a]["c"]
    m.page.keyboard.press("Control+z")
    m.page.keyboard.press("Control+z")
    assert not m.ids_by_text("Spawned idea") and not m.ids_by_text("New idea")


def test_drop_handle_close_to_origin_does_nothing(m):
    a = m.id_of("Alpha")
    hx, hy = m.handle(a)
    n = len(m.nodes())
    m.drag(hx, hy, hx + 10, hy + 10)
    assert len(m.nodes()) == n and m.undo_len() == 0


def test_select_edge_and_unlink_with_button_and_delete_key(m):
    a = m.id_of("Alpha")
    k = "n1|root" if "n1|root" in m.edges() else m.edges()[0]
    def click_edge(key):
        x, y = m.ev("""(k)=>{const g=edgeGeom(k);return [g.mx*V.k+V.x,g.my*V.k+V.y]}""", key)
        m.page.mouse.click(x, y)
    click_edge(k)
    assert m.ev("selEdge") == k
    assert m.page.is_visible("#ex")
    assert m.page.locator("#edges .picked").count() == 1
    m.page.click("#ex")
    assert k not in m.edges()
    assert m.toast() == "Unlinked"
    k2 = m.edges()[0]
    click_edge(k2)
    m.page.keyboard.press("Delete")
    assert k2 not in m.edges()
    m.page.keyboard.press("Control+z")
    assert k2 in m.edges()
    assert a in m.nodes()


def test_delete_node_removes_its_edges(m):
    a = m.id_of("Alpha")
    m.select(a)
    m.page.keyboard.press("Delete")
    assert a not in m.nodes()
    assert all(a not in e.split("|") for e in m.edges())
    assert m.page.locator(f'.node[data-id="{a}"]').count() == 0


def test_delete_via_toolbar_and_multi(m):
    a, b = m.id_of("Alpha"), m.id_of("Beta")
    m.select(a)
    m.select(b, shift=True)
    m.select("root", shift=True)
    m.page.locator('#ctx button[data-a="del"]').click()
    assert a not in m.nodes() and b not in m.nodes()
    assert "root" in m.nodes()


def test_root_cannot_be_deleted(m):
    m.select("root")
    assert m.page.locator('#ctx button[data-a="del"]').count() == 0
    m.page.keyboard.press("Delete")
    m.page.keyboard.press("Backspace")
    assert "root" in m.nodes()
    assert m.undo_len() == 0


def test_edit_commit_with_enter(m):
    a = m.id_of("Alpha")
    m.node(a).dblclick()
    assert m.ev("editing") == a
    m.page.keyboard.type("Renamed")
    m.page.keyboard.press("Enter")
    assert m.nodes()[a]["text"] == "Renamed"
    assert m.ev("editing") is None
    assert m.undo_len() == 1


def test_edit_cancel_with_escape(m):
    a = m.id_of("Alpha")
    m.node(a).dblclick()
    m.page.keyboard.type("Nope")
    m.page.keyboard.press("Escape")
    assert m.nodes()[a]["text"] == "Alpha"
    assert m.undo_len() == 0
    assert m.ev("editing") is None


def test_edit_commit_on_blur_and_empty_keeps_old(m):
    a, b = m.id_of("Alpha"), m.id_of("Beta")
    m.node(a).dblclick()
    m.page.keyboard.type("Blurred")
    x, y = m.empty_point()
    m.page.mouse.click(x, y)
    assert m.nodes()[a]["text"] == "Blurred"
    m.node(b).dblclick()
    m.page.keyboard.press("Backspace")
    m.page.keyboard.press("Enter")
    assert m.nodes()[b]["text"] == "Beta"


def test_edit_root_updates_question(m):
    m.node("root").dblclick()
    m.page.keyboard.type("New question?")
    m.page.keyboard.press("Enter")
    assert m.state()["q"] == "New question?"
    assert m.page.text_content("#crumbq") == "New question?"


def test_edit_paste_is_plain_text_and_whitespace_collapsed(m):
    a = m.id_of("Alpha")
    m.node(a).dblclick()
    m.ev("""()=>{const dt=new DataTransfer();dt.setData('text/plain','Line one\\n\\nLine   two');dt.setData('text/html','<b>bold</b>');
      document.activeElement.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}))}""")
    assert m.ev("document.activeElement.querySelector('b')") is None
    m.page.keyboard.press("Enter")
    assert m.nodes()[a]["text"] == "Line one Line two"


def test_double_click_other_node_while_editing_switches_edit(m):
    a, b = m.id_of("Alpha"), m.id_of("Beta")
    m.node(a).dblclick()
    m.page.keyboard.type("First")
    m.ev("(id)=>startEdit(id)", b)  # what a dblclick on another node does
    assert m.nodes()[a]["text"] == "First"
    assert m.ev("editing") == b
    assert m.ev("document.activeElement.closest('.node').dataset.id") == b
    m.page.keyboard.type("Second")
    m.page.keyboard.press("Enter")
    assert m.nodes()[b]["text"] == "Second"


def test_tab_in_edit_commits_and_adds_child(m):
    a = m.id_of("Alpha")
    m.node(a).dblclick()
    m.page.keyboard.type("Parent")
    m.page.keyboard.press("Tab")
    assert m.nodes()[a]["text"] == "Parent"
    child = m.ev("editing")
    assert child and m.has_edge(a, child)


def test_keyboard_shortcuts(m):
    p = m.page
    a = m.id_of("Alpha")
    m.select(a)
    p.keyboard.press("Tab")            # child, opens editor
    p.keyboard.type("Child")
    p.keyboard.press("Enter")
    c = m.id_of("Child")
    assert m.has_edge(a, c)
    assert m.ev("[...sel]") == [c]
    p.keyboard.press("Enter")          # sibling of Child => another child of Alpha
    p.keyboard.type("Sibling")
    p.keyboard.press("Enter")
    s = m.id_of("Sibling")
    assert m.has_edge(a, s)
    p.keyboard.press("F2")
    p.keyboard.type("Sib2")
    p.keyboard.press("Enter")
    assert m.nodes()[s]["text"] == "Sib2"
    p.keyboard.press("e")
    p.keyboard.press("Escape")
    p.keyboard.press("s")
    assert m.nodes()[s]["star"] is True
    p.keyboard.press("Shift+S")
    assert m.nodes()[s]["star"] is False
    p.keyboard.press("Control+s")      # browser save shortcut must not toggle star
    assert m.nodes()[s]["star"] is False
    p.keyboard.press("Control+a")
    assert m.ev("sel.size") == len(m.nodes())
    p.keyboard.press("Escape")
    assert m.ev("sel.size") == 0
    m.select("root")
    p.keyboard.press("Enter")          # Enter on root adds a child
    p.keyboard.press("Escape")
    assert len(m.nodes()) == 8
    p.keyboard.press("Control+z")
    assert len(m.nodes()) == 7
    p.keyboard.press("Control+Shift+Z")
    assert len(m.nodes()) == 8
    p.keyboard.press("Control+z")
    p.keyboard.press("Control+y")
    assert len(m.nodes()) == 8


def test_double_click_canvas_adds_free_idea(m):
    x, y = m.empty_point()
    m.page.mouse.dblclick(x, y)
    nid = m.ev("editing")
    assert nid
    m.page.keyboard.type("Loose")
    m.page.keyboard.press("Enter")
    assert m.nodes()[nid]["text"] == "Loose"
    assert not any(nid in e.split("|") for e in m.edges())


def test_add_button(m):
    m.page.click("#add")
    nid = m.ev("editing")
    assert nid
    m.page.keyboard.press("Escape")
    a = m.id_of("Alpha")
    m.select(a)
    m.page.click("#add")
    child = m.ev("editing")
    m.page.keyboard.press("Escape")
    assert m.has_edge(a, child)


def test_star_via_toolbar_changes_grow_label(m):
    a = m.id_of("Alpha")
    m.select(a)
    m.page.locator('#ctx button[data-a="star"]').click()
    assert m.nodes()[a]["star"]
    assert m.node(a).locator(".stk").count() == 1
    m.page.keyboard.press("Escape")
    assert m.page.text_content("#growl") == "Grow starred"
    m.select(a)
    assert m.page.text_content("#growl") == "Grow selected"


def test_rapid_clicking_is_stable(m):
    p = m.page
    a = m.id_of("Alpha")
    x, y = m.center(a)
    for _ in range(25):
        p.mouse.click(x, y)
    for _ in range(10):
        p.click("#zin")
        p.click("#zout")
    for _ in range(5):
        p.click("#undo", force=True) if not p.is_disabled("#undo") else None
    assert m.ev("[...sel]") == [a]
    assert len(m.nodes()) == 5


def test_two_finger_pinch_zooms(make_app):
    m = make_app(has_touch=True).open().build()
    cdp = m.ctx.new_cdp_session(m.page)
    x, y = m.empty_point(margin=120)
    k0 = m.ev("V.k")

    def touch(kind, pts):
        cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [
            {"x": px, "y": py, "id": i} for i, (px, py) in enumerate(pts)]})
    touch("touchStart", [(x - 30, y)])
    touch("touchStart", [(x - 30, y), (x + 30, y)])
    for d in range(30, 90, 10):
        touch("touchMove", [(x - d, y), (x + d, y)])
    touch("touchEnd", [])
    m.settle(100)
    assert m.ev("V.k") > k0 * 2
    assert m.ev("sel.size") == 0
    assert not m.page.is_visible("#marq")
