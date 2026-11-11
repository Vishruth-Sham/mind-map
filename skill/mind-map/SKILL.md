---
name: mind-map
description: Turn a question and a few seed ideas into a live, AI-growing mind map artifact. Use when the user types /mind-map or asks to mind-map or branch out ideas on a question.
---

# Mind map

Creates a fresh Mind Mapper artifact for a question, pre-seeded with ideas. The user then drags, links, unlinks, edits and auto-grows the map in the page itself.

Template artifact slug: `e7581db2-a56c-4c5e-9ff7-8de45db41393` ("Mind Mapper", https://claude.ai/artifact/VZudQ7tZMfkftxLBEWf3eA).

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

## 2. Build the page from the template

1. Load the artifact tools with ToolSearch if they're deferred: `select:mcp__claude-artifacts__read_artifact,mcp__claude-artifacts__publish_version,mcp__claude-artifacts__declare_capabilities`.
2. Call `read_artifact` on the template slug to get its HTML.
3. Find the exact string `<script type="application/json" id="seed"></script>`. Put JSON inside it:
   `{"id":"<random 8 chars>","q":"<question>","ctx":"<context or empty>","seeds":["…","…"]}`
   Escape it as valid JSON, and replace every `</` with `<\/` so the script tag can't close early. Change nothing else in the page.
4. Publish it as a **new** artifact with `publish_version`:
   - omit the slug
   - title: `Mind map: <question shortened to about 6 words>`
   - icon: `map`
   - content: the full edited HTML
5. Call `declare_capabilities` on the new slug. Use the version returned by the publish, and pass `{"sample": {}}` so the page can generate ideas.

If the template can't be read, tell the user and give them the template link. They can type the question and seeds into its setup screen themselves.

## 3. Reply

Keep it to one or two lines and don't repeat the link, because the artifact card already shows it. Say:
- the question and the seed count, marking any seeds you added
- the next move: select a node and pick Yes, and / Wilder / Concrete / Flip it, or hit **Keep growing**, then star the branches they want it to focus on

Stay in generation mode. Don't evaluate or rank ideas unless the user asks to move to evaluation.
