from asyncio import run, sleep
from typing import List
from aiohttp import ClientSession
from aiofiles import open

BASE_URL = "https://api.mangadex.org"


def get_title(manga) -> str:
    title = manga["attributes"]["title"]

    if not title.get("en") is None:
        return title["en"]
    if not title.get("ja") is None:
        return title["ja"]

    print(title)
    raise Exception(title)


def find_tag_ids(tags, included_tag_names: List[str]):
    return [
        tag["id"]
        for tag in tags["data"]
        if tag["attributes"]["name"]["en"] in included_tag_names
    ]


async def fetch_tags(session: ClientSession):
    async with session.get(f"{BASE_URL}/manga/tag") as resp:
        return await resp.json()


async def fetch_total(session: ClientSession, included_tag_ids: List[str]) -> int:
    url = f"{BASE_URL}/manga"
    async with session.get(url, params={"includedTags[]": included_tag_ids}) as resp:
        data = await resp.json()
        return data["total"]


async def fetch_manga(sesseion: ClientSession, included_tag_ids, offset) -> List[str]:
    url = f"{BASE_URL}/manga"
    params = {"includedTags[]": included_tag_ids, "limit": 10, "offset": offset}
    async with sesseion.get(url, params=params) as resp:
        json_data = await resp.json()
        return [get_title(manga) for manga in json_data["data"]]


async def main():
    async with ClientSession() as session:
        tags = await fetch_tags(session)

        included_tag_names = ["Girls' Love", "Web Comic"]
        included_tag_ids = find_tag_ids(tags, included_tag_names)
        total = await fetch_total(session, included_tag_ids)


        print(total)
        titles: List[str] = []
        for offset in range(0, total, 10):
            chunk = await fetch_manga(session, included_tag_ids, offset)
            print("titles:", chunk)
            print("offset:" ,offset)
            titles.extend(chunk)
            await sleep(2)


    async with open("manga.txt", mode="wt", encoding="utf-8") as f:
        await f.write("\n".join(titles))


run(main())
