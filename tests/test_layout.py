"""Tidy (force layout) correctness and a ~200-node stress run."""
import time

import pytest

OVERLAPS = """()=>{const ns=Object.values(S.nodes);let c=0;
  for(let i=0;i<ns.length;i++)for(let j=i+1;j<ns.length;j++){const a=ns[i],b=ns[j];
    if(Math.abs(a.x-b.x)<(a._w+b._w)/2&&Math.abs(a.y-b.y)<(a._h+b._h)/2)c++}return c}"""
NAN = "()=>Object.values(S.nodes).filter(n=>!Number.isFinite(n.x)||!Number.isFinite(n.y)).length"


def tidy(app, timeout=20000):
    app.page.click("#tidy")
    app.page.wait_for_function("!tidying", timeout=timeout)
    app.settle(450)


def test_tidy_basic(app):
    app.open().build(seeds=[f"Seed {i}" for i in range(8)])
    # pile everything on top of the root, the worst case for a force layout
    app.ev("()=>{Object.values(S.nodes).forEach(n=>{if(n.id!=='root'){n.x=0;n.y=0}});render()}")
    root = app.nodes()["root"]
    tidy(app)
    assert app.ev(NAN) == 0
    assert app.ev(OVERLAPS) == 0
    st = app.nodes()
    assert (st["root"]["x"], st["root"]["y"]) == (root["x"], root["y"])
    for k in st:  # fit() after tidy shows everything
        x, y = app.center(k)
        assert -5 < x < 1365 and 40 < y < 825


def test_tidy_twice_rapidly_and_undo_mid_tidy(app):
    app.open().build(seeds=[f"S{i}" for i in range(6)])
    app.page.click("#tidy")
    app.page.click("#tidy")  # ignored while running
    app.page.wait_for_function("!tidying")
    assert app.undo_len() == 1
    before = app.state()
    app.page.click("#tidy")
    app.settle(60)
    app.page.keyboard.press("Control+z")  # undo while animating: tidy must abort, not keep mutating
    app.page.wait_for_function("!tidying")
    app.settle(300)
    after = app.state()
    for k, n in before["nodes"].items():
        assert abs(after["nodes"][k]["x"] - n["x"]) < 1e-6


def test_tidy_while_nodes_are_added(make_app):
    app = make_app().mock(delay=50).open().build()
    app.page.click("#tidy")
    app.select(app.id_of("Alpha"))
    app.page.keyboard.press("g")
    app.page.wait_for_function("!tidying&&busy.size===0", timeout=10000)
    assert app.ev(NAN) == 0
    assert len(app.nodes()) == 8


def test_tidy_with_disconnected_and_duplicate_positions(app):
    app.open().build()
    app.ev("()=>{for(let i=0;i<5;i++)mkNode('Loose '+i,40,40);render()}")
    tidy(app)
    assert app.ev(NAN) == 0
    assert app.ev(OVERLAPS) == 0


def test_tidy_reduced_motion_still_lays_out(make_app):
    app = make_app(reduced_motion="reduce").open().build(seeds=[f"Seed {i}" for i in range(10)])
    app.ev("()=>{Object.values(S.nodes).forEach((n,i)=>{if(n.id!=='root'){n.x=i;n.y=i}});render()}")
    app.page.click("#tidy")
    assert app.ev("tidying") is False  # synchronous under reduced motion
    assert app.ev(OVERLAPS) == 0
    assert app.ev(NAN) == 0


@pytest.mark.slow
def test_stress_200_nodes_keep_growing_and_tidy(make_app):
    app = make_app().mock(delay=5).open().build(seeds=[f"Seed {i}" for i in range(6)])
    p = app.page
    t0 = time.time()
    p.click("#grow")
    p.wait_for_function("!growing", timeout=120000)
    grow_s = time.time() - t0
    n = len(app.nodes())
    assert n == 220, n
    assert "220 ideas" in app.toast()
    # interaction latency on a full map
    lat = app.ev("""()=>{const t=performance.now();render();return performance.now()-t}""")
    assert lat < 250, f"render took {lat:.0f}ms"
    t0 = time.time()
    tidy(app, timeout=60000)
    tidy_s = time.time() - t0
    assert tidy_s < 15, tidy_s
    assert app.ev(NAN) == 0
    overlaps = app.ev(OVERLAPS)
    assert overlaps <= 3, overlaps
    # still responsive: a frame callback fires promptly
    frame = app.ev("()=>new Promise(r=>{const t=performance.now();requestAnimationFrame(()=>r(performance.now()-t))})")
    assert frame < 200
    # drag on the big map is undoable and fast
    a = app.id_of("Seed 0")
    x, y = app.center(a)
    t0 = time.time()
    app.drag(x, y, x + 60, y + 60, steps=20)
    drag_s = time.time() - t0
    assert drag_s < 5
    p.keyboard.press("Control+z")
    print(f"\n[stress] grow to {n}: {grow_s:.1f}s, render {lat:.0f}ms, tidy {tidy_s:.1f}s, "
          f"overlaps {overlaps}, 20-step drag {drag_s:.2f}s")
