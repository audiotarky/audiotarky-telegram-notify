import asyncio
import json
import re
import time
from pathlib import Path

import feedparser
from telegram import Bot
import requests


async def message(bot, message="hello world", channel=0):
    async with bot:
        await bot.send_message(text=message, chat_id=channel, parse_mode="MarkdownV2")


def send_dischord(the_message, token, channel):
    the_url = f"https://discord.com/api/v9/channels/{channel}/messages"
    header = {
        "authorization": f"Bot {token}",
    }

    payload = {"content": f"{the_message}", "author": {"pinned": True}}
    requests.post(the_url, data=payload, headers=header)


if __name__ == "__main__":
    time_fmt = "%a, %d %b %Y %H:%M:%S +0000"
    creds_file = Path("creds.json")
    creds = json.loads(creds_file.read_text())
    token = creds["telegram"]["token"]
    channel = int(creds["telegram"]["channel"])
    date = time.strptime(creds["last_update"], time_fmt)
    bot = Bot(token)

    for item in reversed(feedparser.parse(creds["url"]).entries):
        if item["published_parsed"] > date:
            msg = re.sub(r"(.*from )(.*) \| (.*)", r"\1[\2](LINK) | \3", item["title"])
            msg = msg.replace("-", "\-")
            msg = msg.replace(".", "\.")
            msg = msg.replace("(LINK)", f"({item['link']})")
            print(item["title"])
            print(msg)
            asyncio.run(message(bot, msg, channel))
            send_dischord(
                f"{item['title']} - ({item['link']})",
                creds["dischord"]["token"],
                creds["dischord"]["release_announce"],
            )
    creds["last_update"] = time.strftime(time_fmt, time.localtime())
    with creds_file.open("w", encoding="UTF-8") as target:
        json.dump(creds, target)
