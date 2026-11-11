"""Click-to-link mode (toolbar Link button / L key) and pair link/unlink."""
import pytest


@pytest.fixture
def m(app):
    return app.open().build(seeds=["Alpha", "Beta", "Gamma"])


def enter_via_button(m, nid):
    m.select(nid)
    m.page.locator('#ctx button[data-a="linkmode"]').click()
    assert m.ev("linkFrom") == nid


def test_link_button_enters_mode_with_feedback(m):
    a = m.id_of("Alpha")
    enter_via_button(m, a)
    assert m.page.is_visible("#lbanner")
    assert "Click another idea to link it" in m.page.text_content("#lbanner")
    assert "linksrc" in m.node(a).get_attribute("class")
    assert m.ev("getComputedStyle(document.getElementById('stage')).cursor") == "crosshair"
    btn = m.page.locator('#ctx button[data-a="linkmode"]')
    assert "on" in btn.get_attribute("class") and "Cancel" in btn.text_content()


def test_click_node_links_then_toggle_unlinks(m):
    a, g = m.id_of("Alpha"), m.id_of("Gamma")
    enter_via_button(m, a)
    m.select(g)
    assert m.has_edge(a, g)
    assert m.toast() == "Linked"
    assert m.ev("linkFrom") is None
    assert not m.page.is_visible("#lbanner")
    assert m.ev("[...sel]") == [a]  # source stays selected for chaining
    # again: clicking an already-linked node unlinks it
    enter_via_button(m, a)
    m.select(g)
    assert not m.has_edge(a, g)
    assert m.toast() == "Unlinked"


def test_link_mode_undo_redo(m):
    a, g = m.id_of("Alpha"), m.id_of("Gamma")
    enter_via_button(m, a)
    m.select(g)
    assert m.has_edge(a, g)
    m.page.keyboard.press("Control+z")
    assert not m.has_edge(a, g)
    m.page.keyboard.press("Control+Shift+Z")
    assert m.has_edge(a, g)


def test_l_key_and_click_empty_canvas_creates_connected_idea(m):
    a = m.id_of("Alpha")
    m.select(a)
    m.page.keyboard.press("l")
    assert m.ev("linkFrom") == a
    x, y = m.empty_point()
    m.page.mouse.click(x, y)
    nid = m.ev("editing")
    assert nid and m.has_edge(a, nid)
    m.page.keyboard.type("From link mode")
    m.page.keyboard.press("Enter")
    assert m.nodes()[nid]["text"] == "From link mode"
    # created where clicked
    wx, wy = m.ev("([x,y])=>{const p=toWorld(x,y);return [p.x,p.y]}", [x, y])
    assert abs(m.nodes()[nid]["x"] - wx) < 1 and abs(m.nodes()[nid]["y"] - wy) < 1


def test_escape_cancels(m):
    a = m.id_of("Alpha")
    m.select(a)
    m.page.keyboard.press("L")
    m.page.keyboard.press("Escape")
    assert m.ev("linkFrom") is None
    assert not m.page.is_visible("#lbanner")
    assert "linksrc" not in m.node(a).get_attribute("class")
    m.select(m.id_of("Beta"))
    assert not m.has_edge(a, m.id_of("Beta"))
    assert m.undo_len() == 0


def test_button_again_and_banner_x_cancel(m):
    a = m.id_of("Alpha")
    enter_via_button(m, a)
    m.page.locator('#ctx button[data-a="linkmode"]').click()
    assert m.ev("linkFrom") is None
    enter_via_button(m, a)
    m.page.click("#lcancel")
    assert m.ev("linkFrom") is None
    assert m.undo_len() == 0


def test_click_source_itself_cancels(m):
    a = m.id_of("Alpha")
    enter_via_button(m, a)
    m.select(a)
    assert m.ev("linkFrom") is None
    assert m.undo_len() == 0


def test_link_mode_ends_if_source_deleted(m):
    a = m.id_of("Alpha")
    m.select(a)
    m.page.keyboard.press("l")
    m.ev("(id)=>{commit();delete S.nodes[id];S.edges=S.edges.filter(k=>!k.split('|').includes(id));render()}", a)
    assert m.ev("linkFrom") is None
    assert not m.page.is_visible("#lbanner")


def test_pair_toolbar_link_these_and_unlink_these(m):
    a, g = m.id_of("Alpha"), m.id_of("Gamma")
    m.select(a)
    m.select(g, shift=True)
    ctx = m.page.locator("#ctx")
    assert "Link these" in ctx.text_content()
    ctx.locator('button[data-a="link"]').click()
    assert m.has_edge(a, g)
    assert "Unlink these" in ctx.text_content()
    ctx.locator('button[data-a="unlink"]').click()
    assert not m.has_edge(a, g)
    assert "Link these" in ctx.text_content()
    m.page.keyboard.press("Control+z")
    assert m.has_edge(a, g)


def test_three_selected_shows_chain_link_and_unlink(m):
    ids = [m.id_of(t) for t in ("Alpha", "Beta", "Gamma")]
    m.select(ids[0])
    for i in ids[1:]:
        m.select(i, shift=True)
    ctx = m.page.locator("#ctx")
    ctx.locator('button[data-a="link"]').click()
    assert m.has_edge(ids[0], ids[1]) and m.has_edge(ids[1], ids[2])
    ctx.locator('button[data-a="unlink"]').click()
    assert not m.has_edge(ids[0], ids[1]) and not m.has_edge(ids[1], ids[2])


def test_handle_is_big_and_visible_on_selected(m):
    a, b = m.id_of("Alpha"), m.id_of("Beta")
    m.select(a)
    m.settle(250)  # opacity transition
    hd = m.node(a).locator(".hd")
    box = hd.bounding_box()
    assert 20 <= box["width"] <= 26
    assert hd.locator("svg").count() == 1
    assert m.ev("(id)=>getComputedStyle(document.querySelector(`.node[data-id='${id}'] .hd`)).opacity", a) == "1"
    m.page.mouse.move(5, 300)
    m.settle(200)
    assert m.ev("(id)=>getComputedStyle(document.querySelector(`.node[data-id='${id}'] .hd`)).opacity", b) == "0"


def test_handle_visible_on_touch_devices(make_app):
    m = make_app(has_touch=True, is_mobile=True, viewport={"width": 390, "height": 800}).open().build()
    b = m.id_of("Beta")
    assert m.ev("(id)=>getComputedStyle(document.querySelector(`.node[data-id='${id}'] .hd`)).opacity", b) == "1"
