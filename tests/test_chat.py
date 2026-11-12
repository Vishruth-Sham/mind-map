"""Chatting about one idea, and growing new ideas from that chat."""
import json


def chat_map(make_app, **mock):
    return make_app().mock(**mock).open().build(seeds=["Alpha", "Beta", "Gamma"])


def open_chat(app, nid):
    app.select(nid)
    app.page.locator('#ctx button[data-a="chat"]').click()
    app.page.wait_for_selector("#chat", state="visible")


def send(app, text):
    app.page.fill("#chatMsg", text)
    app.page.press("#chatMsg", "Enter")
    app.page.wait_for_function("chatBusy===null")
    app.settle(50)


def msgs(app):
    return app.page.locator("#chatLog .msg").all_text_contents()


def test_chat_button_opens_panel_for_that_idea(make_app):
    app = chat_map(make_app)
    a = app.id_of("Alpha")
    open_chat(app, a)
    assert app.page.text_content("#chatT") == "Alpha"
    assert app.ev("document.activeElement.id") == "chatMsg"
    assert app.page.is_disabled("#chatGrow")       # nothing said yet
    app.page.click("#chatX")
    assert app.page.is_hidden("#chat")


def test_send_gets_a_reply_and_marks_the_idea(make_app):
    app = chat_map(make_app)
    a = app.id_of("Alpha")
    open_chat(app, a)
    send(app, "What if it ran on Fridays too?")
    m = msgs(app)
    assert m[0] == "What if it ran on Fridays too?" and len(m) == 2
    assert app.node(a).locator(".cbdg").count() == 1
    prompt = app.ev("window.__calls[0].prompt")
    assert "How might we test this? → Alpha" in prompt
    assert "User: What if it ran on Fridays too?" in prompt
    assert "Beta" not in prompt and "Gamma" not in prompt
    assert app.ev("undoS.length") == 0             # chatting isn't an undo step
    assert not app.errors, app.errors


def test_shift_enter_is_a_new_line_not_send(make_app):
    app = chat_map(make_app)
    open_chat(app, app.id_of("Alpha"))
    app.page.click("#chatMsg")
    app.page.keyboard.type("line one")
    app.page.keyboard.press("Shift+Enter")
    app.page.keyboard.type("line two")
    assert app.page.input_value("#chatMsg") == "line one\nline two"
    assert msgs(app) == []


def test_grow_from_chat_uses_path_and_chat(make_app):
    app = chat_map(make_app)
    a = app.id_of("Alpha")
    open_chat(app, a)
    send(app, "Make it about music")
    before = len(app.nodes())
    app.page.click("#chatGrow")
    app.page.wait_for_function("busy.size===0")
    app.settle(200)
    kids = [k for k, n in app.nodes().items() if n["ai"] and app.has_edge(a, k)]
    assert len(app.nodes()) == before + 4 and len(kids) == 4
    prompt = app.ev("window.__calls[window.__calls.length-1].prompt")
    assert "Make it about music" in prompt and "How might we test this? → Alpha" in prompt
    assert "Beta" not in prompt
    assert "JSON array" in prompt
    app.page.keyboard.press("Control+z")            # the grow itself is undoable…
    assert len(app.nodes()) == before
    assert len(app.ev("CH")[a]) == 2                # …and undo keeps the chat


def test_chat_persists_and_exports(make_app):
    app = chat_map(make_app)
    a = app.id_of("Alpha")
    open_chat(app, a)
    send(app, "Remember me")
    app.page.reload()
    app.settle(300)
    assert app.ev("CH")[a][0]["t"] == "Remember me"
    app.page.click("#export")
    app.page.click("#tJson")
    data = json.loads(app.page.input_value("#extext"))
    assert data["chats"][a][0] == {"r": "u", "t": "Remember me"}
    # importing the file brings the chat back
    app.ev("CH={};save()")
    app.page.click("#exImp")
    assert app.ev("CH")[a][0]["t"] == "Remember me"


def test_deleting_the_idea_closes_its_chat(make_app):
    app = chat_map(make_app)
    a = app.id_of("Alpha")
    open_chat(app, a)
    app.page.click("#chatLog")
    app.select(a)
    app.page.keyboard.press("Delete")
    assert app.page.is_hidden("#chat")


def test_chat_off_without_generation(make_app):
    app = make_app().open().build(seeds=["Alpha"])
    open_chat(app, app.id_of("Alpha"))
    assert app.page.is_disabled("#chatSend") and app.page.is_disabled("#chatGrow")
    assert "only on inside claude.ai" in app.page.text_content("#chatLog")


def test_chat_error_keeps_message_and_toasts(make_app):
    app = chat_map(make_app, mode="rate")
    open_chat(app, app.id_of("Alpha"))
    send(app, "hello")
    assert msgs(app) == ["hello"]
    assert "too fast" in app.toast()


def test_c_key_opens_chat(make_app):
    app = chat_map(make_app)
    app.select(app.id_of("Beta"))
    app.page.keyboard.press("c")
    assert app.page.is_visible("#chat") and app.page.text_content("#chatT") == "Beta"


def test_chat_panel_fits_on_a_phone(make_app):
    app = make_app(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True).mock().open()
    app.build(seeds=["Alpha"])
    app.ev("(id)=>openChat(id)", app.id_of("Alpha"))
    b = app.page.locator("#chat").bounding_box()
    assert b["x"] >= 0 and b["x"] + b["width"] <= 390 and b["y"] + b["height"] <= 844


# ---------- web search through the Parallel Search connector ----------

def web_chat(make_app, **mock):
    app = chat_map(make_app, web=True, **mock)
    open_chat(app, app.id_of("Alpha"))
    return app


def test_search_toggle_hidden_without_connector(make_app):
    app = chat_map(make_app)
    open_chat(app, app.id_of("Alpha"))
    assert app.page.is_hidden("#chatWebRow")


def test_search_off_by_default_and_never_calls_connector(make_app):
    app = web_chat(make_app, tools=True)
    assert app.page.is_visible("#chatWebRow") and not app.page.is_checked("#chatWeb")
    send(app, "hello")
    assert app.ev("window.__mcpCalls.length") == 0
    assert app.page.locator("#chatLog .srcs").count() == 0


def test_search_with_tools_lists_sources(make_app):
    app = web_chat(make_app, tools=True)
    app.page.click("#chatWebRow")
    send(app, "What do real offices do?")
    call = app.ev("window.__mcpCalls[0]")
    assert call["server"] == "Parallel Search" and call["tool"] == "web_search"
    assert call["input"]["search_queries"] == ["monday office ideas"] and len(call["input"]["session_id"]) == 32
    assert app.ev("window.__calls[window.__calls.length-1].tools") == ["web_search"]
    out = app.ev("window.__toolOut")
    assert [r["url"] for r in out] == ["https://example.com/a", "https://example.org/b"]   # unsafe link dropped
    links = app.page.locator("#chatLog .srcs a")
    assert links.all_text_contents() == ["Fun Mondays", "Huddle ideas"]
    assert links.first.get_attribute("target") == "_blank"
    a = app.id_of("Alpha")
    assert app.ev("CH")[a][1]["src"][0] == {"t": "Fun Mondays", "u": "https://example.com/a"}
    # the toggle is remembered, and sources survive a reload
    app.page.reload()
    app.settle(300)
    app.ev("(id)=>openChat(id)", a)
    app.settle(100)
    assert app.page.is_checked("#chatWeb")
    assert app.page.locator("#chatLog .srcs a").count() == 2
    assert not app.errors, app.errors


def test_search_without_tools_searches_first(make_app):
    app = web_chat(make_app)
    app.page.click("#chatWebRow")
    send(app, "coffee carts in offices")
    q = app.ev("window.__mcpCalls[0].input.search_queries")
    assert q == ["Alpha", "coffee carts in offices"]
    prompt = app.ev("window.__calls[window.__calls.length-1].prompt")
    assert "Spin a wheel of perks." in prompt and "example.com/a" in prompt
    assert app.page.locator("#chatLog .srcs a").count() == 2


def test_missing_connector_turns_search_off(make_app):
    app = web_chat(make_app, webErr="server_not_connected")
    app.page.click("#chatWebRow")
    send(app, "hi")
    assert "Add it in claude.ai Settings" in app.toast()
    assert len(msgs(app)) == 2                     # still answered, just without search
    assert app.page.is_hidden("#chatWebRow")
