import logging
import aiohttp

EPIC_FREE_GAMES_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN&allowCountries=CN"


async def getEpicFreeGames() -> list:
    headers = {
        "Referer": "https://www.epicgames.com/store/zh-CN/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }
    try:
        logging.info(f"Getting epic store free games from API...")
        async with aiohttp.ClientSession() as session:
            async with session.get(EPIC_FREE_GAMES_URL, headers=headers) as response:
                response_json = await response.json()
                if any(response_json):
                    free_games = response_json["data"]["Catalog"]["searchStore"]["elements"]
                    logging.info(f"Got {len(free_games)} item(s) from API.")
                    return free_games
                else:
                    logging.error(f"No Epic Free Games")
                    return []
    except Exception as e:
        logging.exception(f"Get Epic Free Games Exception: {e}")
        return []

