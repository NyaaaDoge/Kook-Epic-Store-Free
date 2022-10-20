import json
import logging
import aiohttp

from datetime import datetime, timedelta
from botutils import sqlite_epic_free, sqlite_kook_channel, epic_store_core
from khl import Bot, Message, MessageTypes
from khl.card import CardMessage, Card, Module, Element, Types

BOT_VERSION = 'v0.0.1 20221020'

# 日志信息
logging.basicConfig(level='INFO', format='%(asctime)s - %(name)s - %(levelname)s -%(message)s')

# ========================================初始化================================================

with open('config/bot-config.json', 'r', encoding='utf-8') as f:
    botConfig = json.load(f)

# 用读取来的 bot-config 初始化 bot
developersID = botConfig['developers']
botToken = botConfig['token']
botMarketUUID = botConfig['bot_market_uuid']

bot = Bot(token=botToken)

# 创建SQL类，用于和数据库对接
channelSQL = sqlite_kook_channel.KookChannelSQL()
epicFreeSQL = sqlite_epic_free.EpicFreeGamesSQL()


# 日志
def msgLogging(msg: Message):
    logging.info(
        f" Message:{{ G_id:{msg.ctx.guild.id} - C_id:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content} }}")


# 向botmarket通信
@bot.task.add_interval(minutes=30)
async def botmarket():
    api = "http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid': botMarketUUID}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)


#################################################################################################
#################################################################################################

# ========================================基础指令================================================


@bot.command(name='helloepic')
async def hello(msg: Message):
    msgLogging(msg)
    await msg.reply('来Epic买点游戏？')


# ========================================EPIC指令================================================


# Epic指令
@bot.command(name='epic', prefixes=[".", "。"], case_sensitive=False)
async def epic(msg: Message, command: str = None, *args):
    msgLogging(msg)
    current_channel_guild_id = msg.ctx.guild.id
    current_guild = await bot.client.fetch_guild(current_channel_guild_id)

    current_user = await current_guild.fetch_user(msg.author.id)
    # 需要Bot拥有管理角色权限
    current_user_roles = await current_user.fetch_roles()
    if any(current_user_roles):
        # 遍历用户的角色构成
        for user_role in current_user_roles:
            # TODO 如果是服务器管理员才能执行操作，获取用户的permissions并判断是否有管理员(0) 频道管理(5)
            if user_role.has_permission(0) or user_role.has_permission(5):
                # 如果有一个角色满足条件就只执行一次
                try:
                    # 获取频道数据
                    current_channel_id = msg.ctx.channel.id
                    current_channel = await bot.client.fetch_public_channel(current_channel_id)
                    channel = {'guild_id': current_channel_guild_id, 'guild_name': current_guild.name,
                               'master_id': current_guild.master_id, 'channel_id': current_channel_id,
                               'channel_name': current_channel.name}

                    if command in ['free', '免费']:
                        if not any(args):
                            await msg.reply("""`.epic free on` 在该频道开启Epic免费游戏推送。注意：一个服务器只能有一个频道能进行推送。
`.epic free off`  关闭Epic免费游戏推送，注意：该指令在任何频道都生效。""", type=MessageTypes.KMD)

                        # 开启订阅
                        elif args[0] in ['on', '开']:
                            db_Channel = channelSQL.get_channel_by_channel_id(current_channel_id)
                            # 如果频道已经在数据库中不执行插入，执行修改推送flag_push_free
                            if any(db_Channel):
                                # 没开启推送，修改flag至开启
                                if db_Channel[6] == 0:
                                    channelSQL.update_channel_push_flag_free_by_channel_id(current_channel_id, 1)
                                    await msg.reply("订阅Epic商店限时免费商品推送功能 **[:green_square:开启]** 成功",
                                                    type=MessageTypes.KMD)
                                else:
                                    await msg.reply("订阅Epic商店限时免费商品推送功能 **[:yellow_square:开启]**，目前频道已开启推送功能！",
                                                    type=MessageTypes.KMD)
                            # 频道不在数据库中，执行插入操作
                            else:
                                # 验证是否为同一个服务器
                                db_Channel = channelSQL.get_channel_by_guild_id(current_guild.id)
                                # 如果不是同一个服务器
                                if not any(db_Channel):
                                    # 开启订阅功能，同时推送限时领取商品
                                    insert_flag = channelSQL.insert_channel_free_default(channel)
                                    if insert_flag:
                                        logging.debug(f"Channel{channel} subscribe successfully")
                                        await msg.reply("服务器新增推送频道成功！同时Epic商店限时免费商品推送功能 **[:green_square:开启]**。",
                                                        type=MessageTypes.KMD)
                                        now_time = datetime.now()
                                        free_items = epicFreeSQL.get_all_item()
                                        for item in free_items:
                                            # 有截止日期
                                            if not item[13] == '':
                                                db_end_time = datetime.fromisoformat(item[13][:-1])
                                                # 如果还未结束领取，先进行推送
                                                if db_end_time > now_time:
                                                    # 进行推送
                                                    await bot.client.send(target=current_channel,
                                                                          type=MessageTypes.CARD,
                                                                          content=freeGameCard(item))
                                                    # 推送完毕
                                                    logging.info(
                                                        f"Free item{{game_id-{item[1]}:{item[2]}}} has been pushed to channel{{G_id-{current_channel.guild_id}, C_name-{current_channel.name}, C_id-{current_channel.id}}}")
                                    else:
                                        await msg.reply(":yellow_square:服务器新增推送频道失败，因为目前频道已加入过推送功能！",
                                                        type=MessageTypes.KMD)
                                # 同一个服务器
                                else:
                                    await msg.reply(f""":red_square:服务器新增推送频道失败，一个服务器只能有一个频道进行推送！当前服务器已有频道加入过推送功能！
频道名称：**{db_Channel[5]}**
频道ID：**{db_Channel[4]}**""", type=MessageTypes.KMD)

                        elif args[0] in ['off', '关']:
                            # 根据服务器id删除数据库中的channel
                            unsub_flag = channelSQL.delete_channel_by_guild_id(current_guild.id)
                            if unsub_flag:
                                await msg.reply("订阅Epic商店限时免费商品推送功能 **[:black_large_square:关闭]** 成功",
                                                type=MessageTypes.KMD)
                            else:
                                await msg.reply("订阅Epic商店限时免费商品推送功能 **[:red_square:关闭]** 失败，请联系Bot管理员解决！",
                                                type=MessageTypes.KMD)

                    elif command is None:
                        await msg.reply("""用法帮助：
`.epic free on`     在该频道开启Epic免费游戏推送。注意：一个服务器只能有一个频道能进行推送。
`.epic free off`    关闭Epic免费游戏推送，注意：该指令在任何频道都生效。

> 建议在服务器单独开设一个频道接收Epic免费游戏资讯，将该文字频道的频道的Epic Store Free角色的可见和发送消息权限设置为开启。
如果觉得Epic Store Free好用的话，欢迎来 **[Bot Market页面](https://www.botmarket.cn/)** 发表评价。
欢迎加入交流服务器 **[Steam阀门社](https://kook.top/nGr9DH)**，内有Steam限时免费游戏推送。""", type=MessageTypes.KMD)

                except Exception as e:
                    logging.error(e, exc_info=True)
                    await msg.reply("发生了一些未知错误，请联系开发者解决。")

                finally:
                    break

            else:
                await msg.reply(f"您没有权限 管理员 或 频道管理，故无法进行操作！")


# 开发者指令
@bot.command(name='admin', case_sensitive=False)
async def admin(msg: Message, command: str = None, *args):
    msgLogging(msg)
    if msg.author.id in developersID:
        try:
            if command is None:
                await msg.reply("""`guilds` `here`""", type=MessageTypes.KMD)

            # 查看开启推送功能的频道，从数据库中查询
            elif command in ['guilds']:
                list_guild = await bot.client.fetch_guild_list()
                channels = channelSQL.get_all_channel()
                cm = CardMessage(Card(
                    Module.Section(Element.Text(f"""加入了 {len(list_guild)} 个服务器
{len(channels)} 个频道推送功能开启 """))
                ))
                await msg.reply(cm)

            elif command in ['here']:
                current_channel_guild_id = msg.ctx.guild.id
                current_guild = await bot.client.fetch_guild(current_channel_guild_id)
                current_channel_id = msg.ctx.channel.id
                current_channel = await bot.client.fetch_public_channel(current_channel_id)
                channel = {'guild_id': current_channel_guild_id, 'guild_name': current_guild.name,
                           'master_id': current_guild.master_id, 'channel_id': current_channel_id,
                           'channel_name': current_channel.name}
                await msg.reply(f"{channel}")

        except Exception as e:
            logging.error(e, exc_info=True)
            await msg.reply(f"{e}")


# ========================================定时任务================================================

# --------------------------------------定时获取任务-----------------------------------------------

# 定时获取Epic免费商品，写入数据库中
@bot.task.add_interval(minutes=3)
async def getFreeGames():
    logging.debug(f"Getting free items...")
    try:
        # 获取免费商品
        free_items = await epic_store_core.getEpicFreeGames()
        logging.debug(f"Got {len(free_items)} free item(s).")
        # 将免费商品写入数据库中
        flag_insert = epicFreeSQL.insert_item(free_items)
        if flag_insert:
            logging.debug(f"Insert {len(free_items)} item(s) info into the table successfully.")
        else:
            logging.debug(f"The {len(free_items)} item(s) inserted info the table fail, probably because of duplicate.")
    except Exception as e:
        logging.error(e, exc_info=True)

    # 查询没有没被推送过的免费商品  ”0“代表没被推送过，”1“代表已被推送过
    items = epicFreeSQL.get_item_by_push_flag(0)
    if any(items):
        # 执行推送任务
        logging.debug(f"Bot starting to push free items to channel(s)...")
        await pushFreeGames(items)
    else:
        logging.debug(f"No free item to be pushed to the channel")


# ----------------------------------------推送任务-----------------------------------------------


# 推送数据库中未被推送过的商品信息
async def pushFreeGames(items):
    try:
        # 查询数据库中开启订阅功能的频道id-channel[4] “0”代表关闭，“1”代表开启
        sub_channels = channelSQL.get_channel_by_push_flag_free(1)
        # 遍历频道，给频道进行推送
        for channel in sub_channels:
            channel_id: str = channel[4]
            try:
                # 获取频道
                target_channel = await bot.client.fetch_public_channel(channel_id=channel_id)
                for item in items:
                    # 按时间进行推送，有截止日期
                    if not item[13] == '':
                        now_time = datetime.now()
                        db_end_time = datetime.fromisoformat(item[13][:-1])
                        # 如果还未结束领取，进行推送
                        if db_end_time > now_time:
                            # 进行推送 TODO 一个频道一个频道发送效率是否不够高
                            await bot.client.send(target=target_channel, type=MessageTypes.CARD,
                                                  content=freeGameCard(item))
                            # 推送完毕
                            logging.info(
                                f"Free item{{game_id-{item[1]}:{item[2]}}} has been pushed to channel{{G_id-{target_channel.guild_id}, C_name-{target_channel.name}, C_id-{target_channel.id}}}")

            except Exception as e:
                logging.error(f"Channel{channel}: {e}")

        # 推送完毕需要更改数据库中flag信息
        for item in items:
            flag_push = epicFreeSQL.update_item_push_flag_by_game_id(item[1], 1)
            if flag_push:
                logging.info(
                    f"Item({item[1]}:{item[2]}) has been pushed to all channels and the push-flag updated to 1.")
            else:
                logging.info(f"Item({item[1]}) push flag update failed.")

    except Exception as e:
        logging.error(e, exc_info=True)


# ========================================卡片部分================================================

# 免费游戏卡片 按时间做分类
def freeGameCard(item_free):
    card_message = CardMessage()

    now_time = datetime.now()
    fmt_release_time = datetime.fromisoformat(item_free[5][:-1]).strftime("%Y-%m-%d")
    db_start_time_bj = datetime.fromisoformat(item_free[12][:-1]) + timedelta(hours=8)
    db_end_time_bj = datetime.fromisoformat(item_free[13][:-1]) + timedelta(hours=8)

    card = Card(theme=Types.Theme.INFO)
    card.append(
        Module.Section(text=Element.Text(f"**Epic 商店限时免费领取物品！**", type=Types.Text.KMD),
                       accessory=Element.Image('https://img.kookapp.cn/assets/2022-10/2BwJawa4NY0dz0e8.jpg',
                                               circle=False, size=Types.Size.SM)))
    card.append(Module.Divider())
    card.append(Module.Section(Element.Text(f"**[{item_free[2]}]({item_free[4]})**", type=Types.Text.KMD)))
    # 如果现在能领取
    if db_start_time_bj < now_time < db_end_time_bj:
        card.append(Module.Section(text=Element.Text(f"**`{db_end_time_bj}` 之前**", type=Types.Text.KMD),
                                   accessory=Element.Button(f"获取", f"{item_free[4]}",
                                                            theme=Types.Theme.INFO, click=Types.Click.LINK)))
        card.append(Module.Context(Element.Text("离免费领取时间**结束**还有：", type=Types.Text.KMD)))
        card.append(Module.Countdown(end=db_end_time_bj, mode=Types.CountdownMode.DAY))
    # 现在不能领取
    elif now_time < db_start_time_bj:
        card.append(
            Module.Section(text=Element.Text(f"**`{db_start_time_bj}` 至 `{db_end_time_bj}`**", type=Types.Text.KMD),
                           accessory=Element.Button(f"即将推出", f"{item_free[4]}",
                                                    theme=Types.Theme.INFO, click=Types.Click.LINK)))
        card.append(Module.Context(Element.Text("离免费领取时间**开始**还有：", type=Types.Text.KMD)))
        card.append(Module.Countdown(end=db_start_time_bj, mode=Types.CountdownMode.DAY))
        card.append(Module.Context(Element.Text("离免费领取时间**结束**还有：", type=Types.Text.KMD)))
        card.append(Module.Countdown(end=db_end_time_bj, mode=Types.CountdownMode.DAY))

    card.append(Module.Container(Element.Image(f"{item_free[7]}")))
    card.append(Module.Context(f"登陆Epic商店日期：{fmt_release_time}\n发行商：{item_free[10]}"))
    card.append(Module.Section(text=Element.Text(f"{item_free[3]}", type=Types.Text.KMD)))

    card_message.append(card)
    return card_message


#################################################################################################
#################################################################################################


# 运行机器人
bot.run()
