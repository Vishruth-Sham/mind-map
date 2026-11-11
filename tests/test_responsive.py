"""Viewport sizes, dark-mode OS setting, reduced motion."""
import pytest

FITS = """(sel)=>{const r=document.querySelector(sel).getBoundingClientRect();
  return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight}"""
DOCK_BUTTONS_REACHABLE = """()=>[...document.querySelectorAll('#dock button')].filter(b=>getComputedStyle(b).display!=='none')
  .every(b=>{const r=b.getBoundingClientRect();if(!r.width)return false;
    const e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return e&&b.contains(e)})"""


@pytest.mark.parametrize("w,h", [(390, 844), (320, 640), (768, 1024), (1920, 1080)])
def test_dock_and_toolbar_fit_viewport(make_app, w, h):
    app = make_app(viewport={"width": w, "height": h}, has_touch=w < 800).mock().open().build()
    assert app.ev(FITS, "#dock")
    assert app.ev("(()=>{const d=document.getElementById('dock');return d.scrollWidth<=d.clientWidth})()")
    assert app.ev(DOCK_BUTTONS_REACHABLE)
    for nid in ["root", app.id_of("Alpha")]:
        app.ev("(id)=>{sel.clear();sel.add(id);updateSel()}", nid)
        assert app.ev(FITS, "#ctx"), nid
        # toolbar buttons are clickable (not covered by the dock / top bar)
        ok = app.ev("""()=>[...document.querySelectorAll('#ctx button')].every(b=>{const r=b.getBoundingClientRect();
            const e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return e&&b.contains(e)})""")
        assert ok, nid
    assert app.ev(FITS, "#top .mark")


def test_mobile_toolbar_actions_work(make_app):
    app = make_app(viewport={"width": 390, "height": 844}, has_touch=True).mock().open().build()
    a = app.id_of("Alpha")
    app.page.tap(f'.node[data-id="{a}"]')
    assert app.ev("[...sel]") == [a]
    app.page.locator('#ctx button[data-g="wild"]').tap()
    app.page.wait_for_function("busy.size===0")
    assert len(app.nodes()) == 8
    app.page.locator("#grow").tap()
    assert app.ev("growing")
    app.page.locator("#grow").tap()
    assert not app.ev("growing")


def test_viewport_resize_keeps_toolbar_on_screen(app):
    app.open().build()
    a = app.id_of("Alpha")
    app.select(a)
    for w, h in [(900, 700), (390, 700), (1360, 820)]:
        app.page.set_viewport_size({"width": w, "height": h})
        app.settle(100)
        assert app.ev(FITS, "#ctx")
        assert app.ev(FITS, "#dock")


def test_dark_mode_inputs_readable(make_app):
    app = make_app(color_scheme="dark").open()
    p = app.page
    p.fill("#q", "Readable?")
    p.click("#ctxtog")
    p.fill("#sctx", "ctx")
    p.fill("#seedin", "seed")

    def colors(sel):
        return app.ev("""(s)=>{const c=getComputedStyle(document.querySelector(s));
            return [c.color,c.webkitTextFillColor,c.backgroundColor,c.colorScheme]}""", sel)
    for sel in ["#q", "#sctx", "#seedin"]:
        fg, fill, bg, scheme = colors(sel)
        assert fg == "rgb(27, 26, 24)" and fill == "rgb(27, 26, 24)", (sel, fg, fill)
    p.press("#seedin", "Enter")
    p.click("#goBtn")
    app.settle(500)
    a = app.id_of("Seed") if app.ids_by_text("Seed") else app.id_of("seed")
    app.node(a).dblclick()
    fg, fill, bg, _ = colors(".tx[contenteditable=true]")
    assert fill == "rgb(27, 26, 24)" and bg == "rgb(255, 255, 255)"
    p.keyboard.press("Escape")
    p.click("#export")
    fg, fill, bg, _ = colors("#extext")
    assert fill == "rgb(27, 26, 24)" and bg == "rgb(255, 255, 255)"
    assert app.ev("getComputedStyle(document.body).backgroundColor") == "rgb(247, 244, 236)"


def test_reduced_motion(make_app):
    app = make_app(reduced_motion="reduce").mock().open().build()
    assert app.ev("reduce") is True
    a = app.id_of("Alpha")
    app.select(a)
    app.page.locator('#ctx button[data-g="yes"]').click()
    app.page.wait_for_function("busy.size===0")
    # no in-flight animation: drawn positions equal model positions immediately
    assert app.ev("Object.keys(AP).length") == 0
    app.page.keyboard.press("l")
    assert app.ev("getComputedStyle(document.querySelector('.node.linksrc')).animationName") == "none"
    app.page.keyboard.press("Escape")
    app.page.click("#fit")
    v = app.ev("({...V})")
    app.settle(50)
    assert app.ev("({...V})") == v  # fit is instant


def test_very_long_node_text(app):
    app.open().build(seeds=["x" * 3000, "word " * 400])
    for k, n in app.nodes().items():
        b = app.node(k).bounding_box()
        assert b["width"] <= 340
    app.page.click("#tidy")
    app.page.wait_for_function("!tidying")
    assert app.ev("Object.values(S.nodes).every(n=>Number.isFinite(n.x))")
