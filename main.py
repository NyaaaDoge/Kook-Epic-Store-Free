import json
import logging
import aiohttp

from bot import sqlite_epic_free
from khl import Bot
from bot.bot_commands import register_cmds
from bot.bot_tasks import getFreeGames, pushFreeGames, freeGamesStatus

BOT_VERSION = 'v0.1.2 20221201'

logger = logging.getLogger("Main")

# 日志信息
logging.basicConfig(level='INFO', format='%(asctime)s - %(name)s - %(levelname)s -%(message)s')

# ========================================初始化================================================

logger.info(f"Bot Version: {BOT_VERSION}")

with open('config/bot-config.json', 'r', encoding='utf-8') as f:
    botConfig = json.load(f)

# 用读取来的 bot-config 初始化 bot
developers = botConfig['developers']
botToken = botConfig['token']
botMarketUUID = botConfig['bot_market_uuid']

bot = Bot(token=botToken)

# 给Bot注册需要用到的指令
register_cmds(bot, developers, BOT_VERSION)

# 向botmarket通信
if any(botMarketUUID):
    @bot.task.add_interval(minutes=30)
    async def botmarketOnline():
        botmarket_api = "http://bot.gekj.net/api/v1/online.bot"
        headers = {'uuid': botMarketUUID}
        async with aiohttp.ClientSession() as session:
            await session.get(botmarket_api, headers=headers)


#################################################################################################
#################################################################################################


# ========================================定时任务================================================


# 分钟数定时任务
@bot.task.add_interval(minutes=10)
async def interval_minutes_tasks():
    try:
        # 获取Epic免费商品，写入数据库中
        logger.info(f"Execute getFreeGames task...")
        await getFreeGames()

        epicFreeSQL = sqlite_epic_free.EpicFreeGamesSQL()
        # 查询没有没被推送过的免费商品  "0"代表没被推送过，"1"代表已被推送过
        items = epicFreeSQL.get_item_by_push_flag(0)
        if any(items):
            # 执行推送任务
            logger.info(f"Execute pushFreeGames task...")
            await pushFreeGames(bot)
        else:
            logger.info(f"No free item to be pushed to the channel.")

        # 更新Bot状态
        logger.info(f"Execute freeGamesStatus task...")
        await freeGamesStatus(bot)

    except Exception as e:
        logger.exception(e, exc_info=True)


#################################################################################################
#################################################################################################

if __name__ == "__main__":
    # 运行机器人
    bot.run()
