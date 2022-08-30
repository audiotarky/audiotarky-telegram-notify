import time
import re
import asyncio
import json
import logging
from pathlib import Path
import feedparser
from telegram import Bot
from telegram.helpers import escape_markdown

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def message(bot, message="hello world", channel=0):
    print(message)
    async with bot:
        await bot.send_message(text=message, chat_id=channel, parse_mode="MarkdownV2")


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
            msg = re.sub(r"(.*from )(.*)", r"\1[\2]", item["title"])
            msg = msg.replace("-", "\-")
            msg = msg.replace(".", "\.")
            msg += f"({item['link']})"
            asyncio.run(message(bot, msg, channel))
    creds["last_update"] = time.strftime(time_fmt, time.localtime())

    with creds_file.open("w", encoding="UTF-8") as target:
        json.dump(creds, target)
