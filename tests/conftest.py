"""Shared Playwright fixtures for the Mind Mapper test suite.

The app is loaded straight from disk via file://. AI generation is mocked by
injecting a fake `window.claude` before any page script runs; tests steer the
mock at runtime through `window.__mock` (see MOCK_JS).
"""
import json
import os
import pathlib
import re
import shutil

import pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP = ROOT / "app" / "index.html"
SEED_TAG = '<script type="application/json" id="seed"></script>'
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")

# Configurable fake for the host `sample` capability.
#   window.__mock.mode : ok | objects | empty | text | garbage | rate | denied | throw | null
#   window.__mock.delay: ms before answering
#   window.__mock.json : false to drop the .json helper (exercises the text fallback)
# Every call is recorded in window.__calls.
MOCK_JS = r"""
(() => {
  window.__mock = Object.assign({mode: 'ok', delay: 0, json: true, n: 0}, window.__mockInit || {});
  window.__calls = []; window.__inflight = 0; window.__maxInflight = 0;
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const ideas = () => { const m = window.__mock; const out = [];
    for (let i = 0; i < 4; i++) out.push('Idea ' + (++m.n)); return out; };
  async function answer(prompt, asJson) {
    window.__calls.push({prompt, asJson});
    const m = window.__mock;
    window.__inflight++; window.__maxInflight = Math.max(window.__maxInflight, window.__inflight);
    try { if (m.delay) await wait(m.delay); } finally { window.__inflight--; }
    if (m.mode === 'rate') throw {code: 'rate_limited'};
    if (m.mode === 'denied') throw {code: 'not_granted'};
    if (m.mode === 'throw') throw new Error('boom');
    let v;
    if (m.mode === 'empty') v = [];
    else if (m.mode === 'objects') v = ideas().map((t, i) => i % 2 ? {text: t} : {idea: t});
    else if (m.mode === 'null') v = [null, 'Real idea ' + (++m.n), '', 42];
    else if (m.mode === 'text') return asJson ? (() => { throw new SyntaxError('not json'); })()
                                              : {text: 'Sure! Here are some thoughts, no list though.'};
    else if (m.mode === 'garbage') return asJson ? (() => { throw new SyntaxError('bad'); })()
                                                 : {text: 'Here: [not, valid json'};
    else v = ideas();
    return asJson ? v : {text: 'Here you go:\n' + JSON.stringify(v)};
  }
  // Chat with page tools: run the first tool once, like Claude deciding to search.
  async function withTools(p, opts) {
    if (opts && opts.tools) {
      window.__toolOut = await opts.tools[0].execute({objective: 'find examples', queries: ['monday office ideas']}, {signal: new AbortController().signal});
      window.__calls.push({prompt: p, asJson: false, tools: opts.tools.map(t => t.name)});
      return {text: 'Teams like rotating perks.'};
    }
    return answer(p, false);
  }
  const sample = (p, o) => withTools(p, o);
  sample.json = p => answer(p, true);
  sample.limits = async () => window.__mock.tools ? {maxPromptBytes: 262144, tools: {maxCount: 8}} : {maxPromptBytes: 262144};
  //   window.__mock.web   : expose a Parallel Search connector through use('mcp')
  //   window.__mock.webErr: make its web_search reject with that code
  window.__mcpCalls = [];
  const mcp = {
    listTools: async () => ({servers: [{server: 'Parallel Search', authStatus: 'connected', tools: [{name: 'web_search', description: ''}]}]}),
    callTool: async (server, tool, input) => {
      window.__mcpCalls.push({server, tool, input});
      if (window.__mock.webErr) throw {code: window.__mock.webErr, message: 'x'};
      return {content: [], payload: {results: [
        {url: 'https://example.com/a', title: 'Fun Mondays', excerpts: ['Spin a wheel of perks.']},
        {url: 'javascript:alert(1)', title: 'Bad link', excerpts: ['nope']},
        {url: 'https://example.org/b', title: 'Huddle ideas', excerpts: ['Office playlist.', 'Breakfast bar.']}]}};
    }};
  window.claude = {use: async name => {
    if (name === 'mcp') return window.__mock.web ? mcp : null;
    if (name !== 'sample') return null;
    if (!window.__mock.json) { const s = p => answer(p, false); return s; }
    return sample;
  }};
})();
"""

IGNORED_CONSOLE = re.compile(r"fonts\.(googleapis|gstatic)|net::ERR_|Failed to load resource", re.I)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        kw = {"args": ["--no-sandbox"]}
        if os.path.exists(CHROME):
            kw["executable_path"] = CHROME
        b = p.chromium.launch(**kw)
        yield b
        b.close()


class App:
    """Thin wrapper around a page running Mind Mapper."""

    def __init__(self, browser, tmp_path, **ctx):
        self.browser = browser
        self.tmp_path = tmp_path
        self.errors = []
        ctx.setdefault("viewport", {"width": 1360, "height": 820})
        self.ctx = browser.new_context(**ctx)
        self.page = self.ctx.new_page()
        self.page.on("pageerror", lambda e: self.errors.append("pageerror: " + str(e)))
        self.page.on("console", lambda m: self.errors.append("console: " + m.text)
                     if m.type == "error" and not IGNORED_CONSOLE.search(m.text) else None)
        # Fonts are optional; never wait on the network for them.
        self.page.route(re.compile(r"https?://fonts\..*"), lambda r: r.abort())
        self.url = APP.as_uri()

    # ---------- loading ----------
    def mock(self, **init):
        self.page.add_init_script("window.__mockInit=" + json.dumps(init) + ";" + MOCK_JS)
        return self

    def seeded(self, seed, raw=None):
        """Write a copy of the template with the seed block filled, like the skill does."""
        html = APP.read_text(encoding="utf-8")
        assert html.count(SEED_TAG) == 1
        body = raw if raw is not None else json.dumps(seed, ensure_ascii=False).replace("</", "<\\/")
        for asset in ("app.js", "app.css"):   # the shell loads these from beside itself
            shutil.copyfile(APP.parent / asset, self.tmp_path / asset)
        out = self.tmp_path / "seeded.html"
        out.write_text(html.replace(SEED_TAG, '<script type="application/json" id="seed">' + body + "</script>"),
                       encoding="utf-8")
        self.url = out.as_uri()
        return self

    def open(self):
        self.page.goto(self.url)
        self.page.wait_for_function("document.readyState==='complete'")
        self.page.wait_for_timeout(50)
        return self

    def build(self, q="How might we test this?", seeds=("Alpha", "Beta", "Gamma")):
        p = self.page
        p.fill("#q", q)
        p.fill("#seedin", "\n".join(seeds))   # one seed per line
        p.click("#goBtn")
        try:
            p.wait_for_selector("#setup", state="hidden", timeout=5000)
        except Exception:
            info = self.ev("[document.getElementById('serr').textContent, document.getElementById('q').value,"
                           " seeds, document.activeElement.id]")
            raise AssertionError(f"map not built: {info}")
        self.settle()
        return self

    def settle(self, ms=600):
        self.page.wait_for_timeout(ms)

    # ---------- state ----------
    def ev(self, js, arg=None):
        return self.page.evaluate(js, arg)

    def state(self):
        return self.ev("JSON.parse(JSON.stringify(S))")

    def nodes(self):
        return self.state()["nodes"]

    def edges(self):
        return self.state()["edges"]

    def ids_by_text(self, text):
        return [k for k, n in self.nodes().items() if n["text"] == text]

    def id_of(self, text):
        ids = self.ids_by_text(text)
        assert len(ids) == 1, (text, ids)
        return ids[0]

    def has_edge(self, a, b):
        k = a + "|" + b if a < b else b + "|" + a
        return k in self.edges()

    def node(self, nid):
        return self.page.locator(f'.node[data-id="{nid}"]')

    def center(self, nid):
        b = self.node(nid).bounding_box()
        return b["x"] + b["width"] / 2, b["y"] + b["height"] / 2

    def select(self, nid, shift=False):
        x, y = self.center(nid)
        if shift:
            self.page.keyboard.down("Shift")
        self.page.mouse.click(x, y)
        if shift:
            self.page.keyboard.up("Shift")

    def drag(self, x0, y0, x1, y1, steps=12, shift=False):
        m = self.page.mouse
        if shift:
            self.page.keyboard.down("Shift")
        m.move(x0, y0)
        m.down()
        m.move(x1, y1, steps=steps)
        m.up()
        if shift:
            self.page.keyboard.up("Shift")

    def handle(self, nid):
        self.node(nid).hover()
        b = self.node(nid).locator(".hd").bounding_box()
        return b["x"] + b["width"] / 2, b["y"] + b["height"] / 2

    def empty_point(self, margin=60):
        """A viewport point that is not covered by any node or chrome."""
        return self.ev("""(m)=>{const occ=(x,y)=>{const e=document.elementFromPoint(x,y);return !e||e.id!=='stage'&&!e.closest('#edges')};
          for(let y=120;y<innerHeight-120;y+=37)for(let x=m;x<innerWidth-m;x+=41){
            let ok=true;for(const dx of [-m,0,m])for(const dy of [-m,0,m])if(occ(x+dx,y+dy))ok=false;
            if(ok)return [x,y]}return null}""", margin)

    def toast(self):
        return self.ev("document.getElementById('toast').textContent")

    def undo_len(self):
        return self.ev("undoS.length")

    def close(self):
        self.ctx.close()


@pytest.fixture
def make_app(browser, tmp_path):
    apps = []

    def factory(**ctx):
        a = App(browser, tmp_path, **ctx)
        apps.append(a)
        return a

    yield factory
    errors = [e for a in apps for e in a.errors]
    for a in apps:
        a.close()
    assert not errors, "JS errors during test:\n" + "\n".join(errors)


@pytest.fixture
def app(make_app):
    return make_app()
