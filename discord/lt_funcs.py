import aiohttp

from db_funcs import handle_your_score

LT_URL = "http://languagetool:8010/v2/check"


async def check_lt(session, content, your_only=False):
    params = {"text": content, "language": "en-US"}
    if your_only:
        params["enabledRules"] = "YOUR"
        params["enabledOnly"] = "true"

    try:
        r = await session.post(LT_URL, params=params)
        res = await r.json()
        return res["matches"]
    except aiohttp.ClientConnectionError as e:
        print(f"aiohttp error: {e}")
        return None


def correct_your_message(matches):
    fixed_msgs = []
    for match in matches:
        context = match["context"]
        text, offset, length = context["text"], context["offset"], context["length"]
        replacement = match["replacements"][0]["value"]
        fixed = f"> {text[:offset]}*__{replacement}__{text[offset+length:]}"
        fixed_msgs.append(fixed)

    return "\n".join(fixed_msgs)


async def check_your_messsage(session, db, msg):
    matches = await check_lt(session, msg.content, your_only=True)
    if matches:
        fixed_msgs = correct_your_message(matches)
        score = await handle_your_score(db, msg, matches)
        if score:
            return "\n".join([fixed_msgs, score])


async def check_all_errors(session, content):
    matches = await check_lt(session, content)
    if matches:
        fixes = []
        for idx, match in enumerate(matches):
            context = match["context"]
            text, offset, length = context["text"], context["offset"], context["length"]
            resp_context = f"{text[0:offset]}__{text[offset:offset+length]}__{text[offset+length:]}"
            sug_fix = match["message"]
            resp = f"> {idx+1}) '{resp_context}'\n`Fix: {sug_fix}`"
            fixes.append(resp)
        return "\n".join(fixes)
    else:
        context = content if len(content) <= 40 else f"{content[:40]}..."
        return f"> {context}\nI didn't find anything I could fix"
