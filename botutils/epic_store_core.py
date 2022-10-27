import logging
import aiohttp

EPIC_FREE_GAMES_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN&allowCountries=CN"


async def getEpicFreeGames() -> list:
    headers = {
        "Referer": "https://www.epicgames.com/store/zh-CN/",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Language": "q=0.9,zh;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6,zh-HK;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(EPIC_FREE_GAMES_URL, headers=headers) as response:
                response_json = await response.json()
                if any(response_json):
                    free_games = response_json["data"]["Catalog"]["searchStore"]["elements"]
                    return free_games
                else:
                    logging.error(f"No Epic Free Games")
                    return []
    except Exception as e:
        logging.exception(f"Get Epic Free Games Exception: {e}")
        return []

