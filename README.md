# Mind Mapper

A single-file, no-build mind-map brainstorming tool (`app/index.html`). Enter a question and a few seed ideas. The question becomes the root and each seed becomes a branch. Then grow the map by hand or with AI.

## Features
- Drag nodes. Shift-click or shift-drag a marquee to select several and drag them together. Pan with the wheel or by dragging the canvas, zoom with Ctrl/⌘+wheel or a two-finger pinch, and use Fit.
- **Linking:** select a node, choose **Link** (or press `L`), then click another idea to link it. Clicking an idea that's already linked unlinks it. Clicking empty canvas creates a new connected idea. Esc cancels. You can also drag the corner link handle onto an idea, or onto empty space to create one. With 2 nodes selected you get **Link these / Unlink these**; with 3 or more you get chain Link / Unlink. Click an edge to select it, then use the red ✕ or Delete to unlink.
- Inline editing, star, delete, undo/redo for every change (including drags, tidy, AI expansions and import), Tidy (force layout), export as an outline or a JSON map file, import, and saving to localStorage.
- AI modes for each node (Yes-and / Wilder / Concrete / Flip it), Combine for a multi-selection, and **Keep growing**. Keep growing expands leaves breadth-first, scoped to the selection, then to starred nodes, then to the whole map. It stops at 220 nodes.

## Keyboard
| Key | Action |
|---|---|
| Tab | new child (also commits an edit in progress) |
| Enter | new sibling |
| F2 / E, double-click | edit (Enter commits, Shift+Enter is a soft break, Esc cancels, blur commits) |
| L | link mode from the selected node |
| G | grow the selected node (Yes, and) |
| S | star / unstar |
| Delete / Backspace | delete the selection or the selected edge (the root can't be deleted) |
| Ctrl/⌘+Z, Ctrl/⌘+Shift+Z or Ctrl/⌘+Y | undo / redo |
| Ctrl/⌘+A, Esc | select all / clear |

## AI: the `sample` capability
The page calls `const sample = await window.claude.use('sample')`. `sample.json(prompt)` should return an array of strings; objects with `idea`/`text` fields are also accepted. If `.json` is missing or fails, the page uses `sample(prompt)` → `{text}` and pulls a JSON array out of the text instead. Outside the claude.ai host, or if `use` fails, `sample` is null: the grow controls are disabled, the top bar says "generation off", and everything else still works. Error codes are handled: `rate_limited` shows a toast, and `not_granted` turns generation off.

## The /mind-map skill
`skill/mind-map/SKILL.md` copies the template artifact, fills `<script type="application/json" id="seed"></script>` with `{"id","q","ctx","seeds"}` (escaping `</`), publishes it as a new artifact and declares the `sample` capability. The `id` namespaces the localStorage key, so each map keeps its own state. To install it, copy `skill/mind-map/` into your Claude skills directory (or upload it as a skill in claude.ai), then type `/mind-map How might we …? | seed; seed; seed`.

## Tests
```
pip install -r requirements.txt   # needs Chrome/Chromium; set CHROME=/path if not /usr/bin/google-chrome
pytest                            # full suite (~4 min); -m "not slow" skips the 220-node stress test
python tests/screenshots.py       # regenerate docs/screenshots/
```
The tests load `app/index.html` over `file://` and mock `window.claude` (see `tests/conftest.py`). They fail on any JS error in the console.

## License
MIT (see LICENSE).
