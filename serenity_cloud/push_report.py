"""
Serenity Daily - PushPlus Pusher (Cloud Version)
Pushes the HTML report via PushPlus API.
"""
import json
import urllib.request

PUSHPLUS_URL = "https://www.pushplus.plus/send"


def push_report(html_content: str, title: str, token: str) -> dict:
    """Push HTML report to PushPlus. Returns API response dict."""
    payload = json.dumps({
        "token": token,
        "title": title,
        "content": html_content,
        "template": "html",
    }).encode("utf-8")

    req = urllib.request.Request(PUSHPLUS_URL, data=payload, headers={
        "Content-Type": "application/json",
    })

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    import os
    token = os.environ.get("PUSHPLUS_TOKEN", "3d9d364039ab432ead44d9725e456f7a")
    result = push_report("<h1>Test</h1>", "Test Push", token)
    print(result)
