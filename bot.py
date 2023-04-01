import asyncio
import json
import re
import time
from pathlib import Path

import feedparser
from mastodon import Mastodon
from telegram import Bot
import requests
import zlib

from argparse import ArgumentParser


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


def send_mastodon(the_message, creds):
    mastodon = Mastodon(
        client_id="pytooter_clientcred.secret",
    )
    mastodon.log_in(
        creds["mastodon"]["email"],
        creds["mastodon"]["password"],
        to_file=creds["mastodon"]["secret_file"],
    )
    mastodon.toot(the_message)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--dryrun", action="store_true")
    args = parser.parse_args()
    time_fmt = "%a, %d %b %Y %H:%M:%S +0000"
    creds_file = Path("creds.json")
    creds = json.loads(creds_file.read_text())
    token = creds["telegram"]["token"]
    channel = int(creds["telegram"]["channel"])
    date = time.strptime(creds["last_update"], time_fmt)
    bot = Bot(token)
    if "seen" in creds:
        seen_bytes = bytes.fromhex(creds["seen"])
        decomp = zlib.decompress(seen_bytes).decode()
        seen = json.loads(decomp)
    else:
        seen = []

    print("fetching feed")
    for item in reversed(feedparser.parse(creds["url"]).entries):
        if item["link"] not in seen:
            msg = re.sub(r"(.*from )(.*) \| (.*)", r"\1[\2](LINK) | \3", item["title"])
            for char in "-.()!":
                msg = msg.replace(char, f"\{char}")

            msg = msg.replace(
                "\(LINK\)",
                f"({item['link']}?utm_campaign=new_release&utm_source=telegram)",
            )
            msg = msg.replace("|", "\|")
            print(item["title"])
            print(msg)
            try:
                if not args.dryrun:
                    asyncio.run(message(bot, msg, channel))
                    plain_msg = f"{item['title']} - ({item['link']}?utm_campaign=new_release&utm_source=dischord)"
                    send_dischord(
                        plain_msg,
                        creds["dischord"]["token"],
                        creds["dischord"]["release_announce"],
                    )
                    plain_msg = f"{item['title']} - ({item['link']}?utm_campaign=new_release&utm_source=mastodon)"
                    send_mastodon(plain_msg, creds)
                seen.append(item["link"])
            except:
                pass

    creds["last_update"] = time.strftime(time_fmt, time.localtime())
    creds["seen"] = zlib.compress(json.dumps(seen).encode("utf-8")).hex()
    with creds_file.open("w", encoding="UTF-8") as target:
        json.dump(creds, target, indent=4)
