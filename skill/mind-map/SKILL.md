---
name: mind-map
description: Turn a question and a few seed ideas into a live, AI-growing mind map artifact. Use when the user types /mind-map or asks to mind-map or branch out ideas on a question.
---

# Mind map

Creates a fresh Mind Mapper artifact for a question, pre-seeded with ideas. The user then drags, links, unlinks, edits and auto-grows the map in the page itself.

The app's code ships with this skill: `app.js` and `app.css` sit next to this file, in the skill's base directory.

## 1. Get the question and seeds

Read them from the args or message. Typical forms: `/mind-map How might we X? | seed 1; seed 2; seed 3`, or a question followed by a list.

- **Question:** if there isn't one, ask a single short question for it. Otherwise phrase it as a "How might we…?" need, keeping the user's wording where you can.
- **Seeds:** use the user's own seeds as given. If they give fewer than 3, top up to 6 yourself, following the design-thinking rules below. Mark which seeds are yours when you reply.
- **Context:** optional. Include it only if the user gives some, such as who it's for or constraints.

Design-thinking rules for any ideas you write:
- defer judgment, with no feasibility talk
- go for quantity
- welcome wild ideas
- build on ideas ("Yes, and…")
- keep each idea a short, vivid phrase

## 2. Publish a small page plus the bundled app files

Each map is a new artifact: a ~15-line page holding the seed block, with `app.js` and `app.css` published beside it. Copy those two files with a shell command and never open, read or retype them; that keeps this step to a few seconds.

1. Make a fresh folder for this map in your scratchpad directory (if you have none, use a new folder under the working directory). Copy the two files into it with one shell command, e.g. `cp "<skill base directory>/app.js" "<skill base directory>/app.css" "<folder>/"`.
2. In the same folder, write `index.html` with this content. Change only the `<title>` and the seed block contents:

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
   <meta charset="utf-8">
   <meta name="viewport" content="width=device-width, initial-scale=1">
   <title>Mind map: QUESTION_SHORT</title>
   <link rel="preconnect" href="https://fonts.googleapis.com">
   <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,800;1,8..60,400&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet">
   <link rel="stylesheet" href="app.css">
   </head>
   <body>
   <script type="application/json" id="seed">SEED_JSON</script>
   <script src="app.js"></script>
   </body>
   </html>
   ```

   - `QUESTION_SHORT`: the question cut to about 6 words, HTML-escaped (`&` → `&amp;`, `<` → `&lt;`).
   - `SEED_JSON`: `{"id":"<random 8 chars>","q":"<question>","ctx":"<context or empty>","seeds":["…","…"]}` as valid JSON. Then replace every `<` with `\u003c` so the script tag can't close early. Seeds must be non-empty strings. If the block has a question but no usable seeds, the page opens its setup screen prefilled instead.
3. Publish it as a **new** artifact (no `url`) with the Artifact tool:
   - `file_path`: `<folder>/index.html`
   - `files`: `{"app.js": "<folder>/app.js", "app.css": "<folder>/app.css"}`
   - `icon`: `map`
   - `capabilities`: `{"sample": {}}` so the page can generate ideas

If publishing fails, tell the user why. They can still open `app/index.html` from the repo in a browser and type the question and seeds into its setup screen (idea generation is off outside claude.ai).

## 3. Reply

Keep it to one or two lines and don't repeat the link, because the artifact card already shows it. Say:
- the question and the seed count, marking any seeds you added
- the next move: select a node and pick Yes, and / Wilder / Concrete / Flip it, or hit **Keep growing**, then star the branches they want it to focus on

Stay in generation mode. Don't evaluate or rank ideas unless the user asks to move to evaluation.
