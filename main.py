import json
import logging
import aiohttp

from khl import Bot
from bot.bot_commands import register_cmds
from bot.bot_tasks import register_tasks

BOT_VERSION = 'v0.1.3 20221216'

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
# 给Bot注册任务
register_tasks(bot)

# 向botmarket通信
if any(botMarketUUID):
    @bot.task.add_interval(minutes=30)
    async def botmarketOnline():
        botmarket_api = "http://bot.gekj.net/api/v1/online.bot"
        headers = {'uuid': botMarketUUID}
        async with aiohttp.ClientSession() as session:
            await session.get(botmarket_api, headers=headers)


if __name__ == "__main__":
    # 运行机器人
    bot.run()
