"""Regenerate the README screenshots in docs/screenshots/ (replaces the old shot*.py scripts).

    python tests/screenshots.py            # writes docs/screenshots/*.png
    python tests/screenshots.py /tmp/out   # or somewhere else (extra review shots included)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playwright.sync_api import sync_playwright  # noqa: E402

from conftest import App  # noqa: E402

Q = "How might we make weekend mornings feel like a mini vacation?"
SEEDS = ["Breakfast picnic on the balcony", "Phone-free first two hours", "Neighbourhood walking tour",
         "Cook a dish from a random country", "Sunrise swim", "Board game brunch"]
IDEAS = """window.__ideas=['Hammock with a thermos of chai','Postcards to yourself','Rooftop yoga with neighbours',
 'A playlist only for Saturdays','Pretend-tourist map of your street','Try a bakery you have never noticed',
 'Swap breakfasts with the flat upstairs','Sunrise sketching club','Pack a picnic the night before',
 'Tiny souvenir from every walk','No-clock morning: cover every screen','Bring the plants outside too',
 'Pancakes shaped like the destination','Local guide for a day: kids lead','Window seat ritual with a novel',
 'Borrow a dog for a stroll','Market haul, then cook together','Write a one-line travel diary'];
 window.__mock.n=0; const orig=window.__mock;"""


def main(out, extra):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        tmp = pathlib.Path("/tmp/mm-shots")
        tmp.mkdir(exist_ok=True)

        a = App(b, tmp).mock().open()
        a.page.fill("#q", Q)
        for s in SEEDS[:4]:
            a.page.fill("#seedin", s)
            a.page.press("#seedin", "Enter")
        a.page.fill("#seedin", "Sunrise sw")
        a.page.screenshot(path=str(out / "1-setup.png"))
        a.page.fill("#seedin", "")
        for s in SEEDS[4:]:
            a.page.fill("#seedin", s)
            a.page.press("#seedin", "Enter")
        a.page.click("#goBtn")
        a.settle(900)
        a.select(a.id_of("Sunrise swim"))
        a.settle(300)
        a.page.screenshot(path=str(out / "2-seeded-map.png"))

        # grow with the mock, using nicer idea text
        a.ev("""()=>{const L=['Hammock with a thermos of chai','Postcards to yourself','Rooftop yoga with neighbours',
 'A playlist only for Saturdays','Pretend-tourist map of your street','Try a bakery you never noticed',
 'Swap breakfasts with the flat upstairs','Sunrise sketching club','Pack the picnic the night before',
 'Tiny souvenir from every walk','No-clock morning: cover every screen','Bring the plants outside too',
 'Pancakes shaped like the destination','Kids are tour guides for a day','Window seat ritual with a novel',
 'Borrow a dog for a stroll','Market haul, then cook together','One-line travel diary',
 'Cold-water swim then hot cocoa','Board game set in another country','Dress code: holiday shirts',
 'Ferry ride to nowhere in particular','Breakfast in a different room each week','Audio guide recorded by friends',
 'Postcard-sized photo walk','Learn one phrase from that cuisine','Brunch passport with stamps','Sunrise from a hill, not the beach'];
 let i=0;const s=async p=>{await new Promise(r=>setTimeout(r,30));return [L[i++%L.length],L[i++%L.length],L[i++%L.length]]};
 sample=async p=>({text:JSON.stringify(await s(p))});sample.json=s;ui()}""")
        a.page.keyboard.press("Escape")
        a.page.click("#grow")
        a.page.wait_for_function("Object.keys(S.nodes).length>=27", timeout=20000)
        a.page.click("#grow")
        a.page.wait_for_function("busy.size===0")
        star = a.ids_by_text("Rooftop yoga with neighbours")
        if star:
            a.ev("(id)=>{S.nodes[id].star=true;render()}", star[0])
        a.page.click("#tidy")
        a.page.wait_for_function("!tidying")
        a.settle(700)
        a.select(a.id_of("Phone-free first two hours"))
        a.settle(300)
        a.page.screenshot(path=str(out / "3-grown-map.png"))
        if extra:
            a.page.keyboard.press("l")
            a.settle(200)
            a.page.screenshot(path=str(out / "x-link-mode.png"))
            a.page.keyboard.press("Escape")
        a.ctx.close()

        m = App(b, tmp, viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True,
                device_scale_factor=2).mock().open()
        m.build(q="How might we make weekend mornings feel like a mini vacation?",
                seeds=["Balcony picnic", "Phone-free hours", "Walking tour", "Random-country dish"])
        nid = m.id_of("Walking tour")
        m.page.tap(f'.node[data-id="{nid}"]')
        m.settle(300)
        m.page.screenshot(path=str(out / "4-mobile.png"))
        if extra:
            m.ctx.close()
            d = App(b, tmp, color_scheme="dark").open()
            d.page.fill("#q", "Dark mode check")
            d.page.click("#ctxtog")
            d.page.fill("#sctx", "Context text")
            d.page.screenshot(path=str(out / "x-dark-setup.png"))
            d.ctx.close()
        b.close()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "docs" / "screenshots"
    main(target, extra=len(sys.argv) > 1)
