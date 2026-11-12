"""Regenerate the README screenshots in docs/screenshots/.

    python tests/screenshots.py            # writes docs/screenshots/*.jpg
    python tests/screenshots.py /tmp/out   # or somewhere else (extra review shots included)

Set CHROME=/path/to/chrome if it isn't at /usr/bin/google-chrome. AI generation is mocked with
the hand-written IDEAS below, so the shots are reproducible and need no claude.ai session.
"""
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playwright.sync_api import sync_playwright  # noqa: E402

from conftest import App  # noqa: E402

Q = "How might we make Monday mornings fun?"
SEEDS = ["Coffee cart", "No-meeting hour", "Playlist swap"]
# Example ideas fed to the mocked `sample` capability, three per grow.
IDEAS = ["Barista rotates through every team", "Secret latte-art contest", "Pay-it-forward coffee board",
         "Quiet hour with lo-fi and candles", "Walk-and-talk instead of stand-up", "Monday maker hour: build anything",
         "Song of the week picked by the newest hire", "Karaoke elevator rides", "Shared playlist that DJs the office",
         "Pastry roulette from a new bakery", "Coffee cart doubles as a mood board", "Hot cocoa for the late risers",
         "Desk-swap Monday", "Ban email before 10", "Silent disco stand-up",
         "Vinyl corner with a turntable", "Theme songs for every meeting", "Guess-whose-playlist quiz"]
MOCK = """(L)=>{let i=0;const s=async p=>{await new Promise(r=>setTimeout(r,30));return [L[i++%L.length],L[i++%L.length],L[i++%L.length]]};
 sample=async p=>({text:JSON.stringify(await s(p))});sample.json=s;ui()}"""


def build(a):
    a.page.fill("#q", Q)
    a.page.fill("#seedin", "\n".join(SEEDS))


def main(out, extra):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="mm-shots-"))
    chrome = os.environ.get("CHROME", "/usr/bin/google-chrome")
    with sync_playwright() as p:
        kw = {"args": ["--no-sandbox"]}
        if os.path.exists(chrome):
            kw["executable_path"] = chrome
        b = p.chromium.launch(**kw)
        big = {"viewport": {"width": 1360, "height": 820}, "device_scale_factor": 2}

        # 1. setup screen, mid-typing
        a = App(b, tmp, **big).mock().open()
        build(a)
        a.page.fill("#seedin", "\n".join(SEEDS) + "\nDesk sw")
        a.settle(300)
        a.page.screenshot(path=str(out / "1-setup.jpg"), type="jpeg", quality=82)
        a.page.fill("#seedin", "\n".join(SEEDS))

        # 2. the fresh map, a seed selected so the AI toolbar shows
        a.page.click("#goBtn")
        a.settle(900)
        a.select(a.id_of("Playlist swap"))
        a.settle(300)
        a.page.screenshot(path=str(out / "2-seeded-map.jpg"), type="jpeg", quality=82)

        # 3. grown a few rounds, one starred, tidied
        a.ev(MOCK, IDEAS)
        a.page.keyboard.press("Escape")
        a.page.click("#grow")
        a.page.wait_for_function("Object.keys(S.nodes).length>=16", timeout=20000)
        a.page.click("#grow")
        a.page.wait_for_function("busy.size===0")
        star = a.ids_by_text("Secret latte-art contest")
        if star:
            a.ev("(id)=>{S.nodes[id].star=true;render()}", star[0])
        a.page.click("#tidy")
        a.page.wait_for_function("!tidying")
        a.settle(700)
        a.page.keyboard.press("Escape")   # nothing selected: the hero shot shows the whole map clean
        a.ev("document.activeElement&&document.activeElement.blur()")   # no focus ring on Tidy
        a.page.mouse.move(5, 400)
        a.settle(300)
        a.page.screenshot(path=str(out / "3-grown-map.jpg"), type="jpeg", quality=82)
        if extra:
            a.page.keyboard.press("l")
            a.settle(200)
            a.page.screenshot(path=str(out / "x-link-mode.jpg"), type="jpeg", quality=82)
            a.page.keyboard.press("Escape")
        a.ctx.close()

        # 4. phone
        m = App(b, tmp, viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True,
                device_scale_factor=2).mock().open()
        m.build(q=Q, seeds=SEEDS)
        nid = m.id_of("Coffee cart")
        m.page.tap(f'.node[data-id="{nid}"]')
        m.settle(300)
        m.page.screenshot(path=str(out / "4-mobile.jpg"), type="jpeg", quality=82)
        m.ctx.close()
        b.close()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "docs" / "screenshots"
    main(target, extra=len(sys.argv) > 1)
