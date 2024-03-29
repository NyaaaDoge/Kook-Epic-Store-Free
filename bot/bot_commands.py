import logging
from datetime import datetime, timedelta

from khl import Message, Bot, MessageTypes
from khl.card import CardMessage, Card, Module, Element

from . import sqlite_epic_free, sqlite_kook_channel, bot_tasks
from .bot_tasks import get_free_games, push_free_items, update_music_status
from .bot_utils import BotUtils
from .card_storage import help_card_message

logger = logging.getLogger(__name__)
BotUtils.create_log_file(logger, 'commands_log.log')


async def has_admin_and_manage(bot: Bot, user_id, guild_id):
    try:
        guild = await bot.client.fetch_guild(guild_id)
        user_roles = (await guild.fetch_user(user_id)).roles
        guild_roles = await (await bot.client.fetch_guild(guild_id)).fetch_roles()
        # 遍历服务器身分组
        for role in guild_roles:
            # 查看当前遍历到的身分组是否在用户身分组内且是否有管理员权限
            if role.id in user_roles and role.has_permission(0) or role.has_permission(5):
                return True
        # 由于腐竹可能没给自己上身分组，但是依旧拥有管理员权限
        if user_id == guild.master_id:
            return True
        return False
    except Exception as e:
        logger.exception(f"Failed to get permissions (U:{user_id},G:{guild_id}). {e}", exc_info=False)
        return False


def register_cmds(bot: Bot, developers: list, BOT_VERSION: str = 'v???'):
    # ========================================基础指令================================================
    @bot.command(name="helloepic", case_sensitive=False)
    async def cmd_hello(msg: Message):
        BotUtils.logging_msg(logger, msg)
        await msg.reply('来Epic买点游戏？')

    # ========================================EPIC指令================================================

    @bot.command(name="epic", prefixes=[".", "。"], case_sensitive=False)
    async def cmd_epic(msg: Message, command: str = None, *args):
        BotUtils.logging_msg(logger, msg)
        channelSQL = sqlite_kook_channel.KookChannelSQL()
        epicFreeSQL = sqlite_epic_free.EpicFreeGamesSQL()
        current_channel_guild_id = msg.ctx.guild.id
        current_guild = await bot.client.fetch_guild(current_channel_guild_id)

        current_user = await current_guild.fetch_user(msg.author.id)

        if command is None:
            await msg.reply(content=help_card_message(BOT_VERSION), type=MessageTypes.CARD)

        try:
            async def exec_mods_commands():
                # 获取频道数据
                current_channel_id = msg.ctx.channel.id
                current_channel = await bot.client.fetch_public_channel(current_channel_id)
                channel = {'guild_id': current_channel_guild_id, 'guild_name': current_guild.name,
                           'master_id': current_guild.master_id, 'channel_id': current_channel_id,
                           'channel_name': current_channel.name}

                if command in ['free']:
                    if not any(args):
                        await msg.reply(content=help_card_message(BOT_VERSION), type=MessageTypes.CARD)

                    # 开启订阅
                    elif args[0] in ['on']:
                        query_channel = channelSQL.get_channel_by_channel_id(current_channel_id)
                        # 如果频道已经在数据库中不执行插入，执行修改推送flag_push_free
                        if any(query_channel):
                            db_channel = sqlite_kook_channel.DatabaseKookChannel(*query_channel)
                            # 没开启推送，修改flag至开启
                            if db_channel.flag_push_free == 0:
                                channelSQL.update_channel_push_flag_free_by_channel_id(current_channel_id, 1)
                                await msg.reply("订阅Epic商店限时免费商品推送功能 **[:green_square:开启]** 成功",
                                                type=MessageTypes.KMD)
                            else:
                                await msg.reply("订阅Epic商店限时免费商品推送功能 **[:yellow_square:开启]**，目前频道已开启推送功能！",
                                                type=MessageTypes.KMD)
                        # 频道不在数据库中，执行插入操作
                        else:
                            # 验证是否为同一个服务器
                            query_channel = channelSQL.get_channel_by_guild_id(current_guild.id)
                            # 如果不是同一个服务器
                            if not any(query_channel):
                                # 开启订阅功能，同时推送限时领取商品
                                insert_flag = channelSQL.insert_channel_free_default(channel)
                                if insert_flag:
                                    logger.info(f"Channel{channel} subscribe successfully")
                                    await msg.reply("服务器新增推送频道成功！同时Epic商店限时免费商品推送功能 **[:green_square:开启]**。",
                                                    type=MessageTypes.KMD)
                                    now_time = datetime.now() - timedelta(hours=8)
                                    free_items = epicFreeSQL.get_all_item()
                                    for item in free_items:
                                        # 有截止日期且
                                        db_item = sqlite_epic_free.DatabaseFreeItem(*item)
                                        if not db_item.free_end_date == '':
                                            db_end_time = datetime.fromisoformat(db_item.free_end_date[:-1])
                                            # 如果还未结束领取，先进行推送
                                            if db_end_time > now_time:
                                                # 进行推送
                                                await bot_tasks.send_item_to_channel(bot, current_channel, item)

                                else:
                                    await msg.reply(":yellow_square:服务器新增推送频道失败，因为目前频道已加入过推送功能！",
                                                    type=MessageTypes.KMD)
                            # 同一个服务器
                            else:
                                db_channel = sqlite_kook_channel.DatabaseKookChannel(*query_channel)
                                await msg.reply(f":red_square:服务器新增推送频道失败，一个服务器只能有一个频道进行推送！当前服务器已有频道加入过推送功能！\n"
                                                f"频道名称：**{db_channel.channel_name}**\n"
                                                f"频道ID：**{db_channel.channel_id}**\n"
                                                f"(chn){db_channel.channel_id}(chn)", type=MessageTypes.KMD)

                    # 关闭订阅
                    elif args[0] in ['off']:
                        # 根据服务器id删除数据库中的channel
                        unsub_flag = channelSQL.delete_channel_by_guild_id(current_guild.id)
                        if unsub_flag:
                            await msg.reply("订阅Epic商店限时免费商品推送功能 **[:black_large_square:关闭]** 成功",
                                            type=MessageTypes.KMD)
                        else:
                            await msg.reply("订阅Epic商店限时免费商品推送功能 **[:red_square:关闭]** 失败，请联系Bot管理员解决！",
                                            type=MessageTypes.KMD)

                    # 获取现在能领取的游戏
                    elif args[0] in ['now']:
                        now_time = datetime.now() - timedelta(hours=8)
                        free_items = epicFreeSQL.get_all_item()
                        for item in free_items:
                            db_item = sqlite_epic_free.DatabaseFreeItem(*item)
                            # 有截止日期
                            if not db_item.free_end_date == '':
                                start_time = datetime.fromisoformat(db_item.free_start_date[:-1])
                                end_time = datetime.fromisoformat(db_item.free_end_date[:-1])
                                # 在领取区间内
                                if start_time < now_time < end_time:
                                    await bot_tasks.send_item_to_channel(bot, current_channel, item)

                    # 获取预告领取的游戏
                    elif args[0] in ['coming']:
                        now_time = datetime.now() - timedelta(hours=8)
                        free_items = epicFreeSQL.get_all_item()
                        for item in free_items:
                            db_item = sqlite_epic_free.DatabaseFreeItem(*item)
                            # 有截止日期
                            if not db_item.free_end_date == '':
                                start_time = datetime.fromisoformat(db_item.free_start_date[:-1])
                                # 在预告区间内
                                if now_time < start_time:
                                    await bot_tasks.send_item_to_channel(bot, current_channel, item)

            if await has_admin_and_manage(bot, current_user.id, current_guild.id):
                await exec_mods_commands()
            else:
                await msg.reply(f":red_square:**Bot没有管理角色权限！请在`服务器设置`中打开Bot角色的`管理角色权限`！**:red_square:")

        except Exception as e:
            logger.exception(e, exc_info=True)
            await msg.reply(f"出现了一些未知问题，请稍后再试，或者联系Bot开发者解决。")

            # 开发者指令

    # ========================================ADMIN指令================================================

    @bot.command(name="admin", prefixes=[".", "。"], case_sensitive=False)
    async def cmd_admin(msg: Message, command: str = None, *args):
        BotUtils.logging_msg(logger, msg)
        # 创建SQL类，用于和数据库对接
        channelSQL = sqlite_kook_channel.KookChannelSQL()
        epicFreeSQL = sqlite_epic_free.EpicFreeGamesSQL()
        if msg.author.id in developers:
            try:
                if command is None:
                    await msg.reply("[README.md on Github](https://github.com/NyaaaDoge/Kook-Epic-Store-Free)",
                                    type=MessageTypes.KMD)

                elif command in ['update']:
                    await get_free_games()
                    await msg.reply("执行获取Epic免费商品成功！", type=MessageTypes.KMD)

                elif command in ['push']:
                    logger.info(f"Execute push_free_items task...")
                    await push_free_items(bot)
                    await msg.reply("执行推送Epic免费商品成功！", type=MessageTypes.KMD)

                elif command in ['delete']:
                    if not any(args):
                        await msg.reply("用法 `.admin delete {game_id}`", type=MessageTypes.KMD)

                    elif len(args) == 1:
                        target_data = epicFreeSQL.get_item_by_game_id(args[0])
                        item = sqlite_epic_free.DatabaseFreeItem(*target_data)
                        await msg.reply(f"获取到数据库中有此数据。数据信息如下：\n"
                                        f"game_id: {item.game_id}\n"
                                        f"title: {item.title}\n"
                                        f"store_url: [商店地址]({item.store_url})\n"
                                        f"start: {item.free_start_date}\n"
                                        f"end: {item.free_end_date}\n"
                                        f"您确定要删除该数据吗？\n"
                                        f"确定请输入 `.admin delete {args[0]} confirm`", type=MessageTypes.KMD)

                    elif any(args[0]) and args[1] == "confirm":
                        target_data = epicFreeSQL.get_item_by_game_id(args[0])
                        result = epicFreeSQL.delete_item_by_game_id(args[0])
                        await msg.reply(f"成功删除此条数据！影响行数：{result}\n({target_data})", type=MessageTypes.KMD)

                elif command in ['info']:
                    # 查看开启推送功能的频道，从数据库中查询
                    list_guild = await bot.client.fetch_guild_list()
                    channels = channelSQL.get_all_channel()
                    free_items = epicFreeSQL.get_all_item()
                    cm = CardMessage(Card(
                        Module.Section(Element.Text(f"加入了 {len(list_guild)} 个服务器\n"
                                                    f"{len(channels)} 个频道推送功能开启\n"
                                                    f"免费游戏数据库中有 {len(free_items)} 行数据"))))
                    await msg.reply(cm)
                    if any(args) and 'detail' in args[0]:
                        guild_lists = []
                        for guild in list_guild:
                            user_list = await guild.fetch_user_list(guild.welcome_channel_id)
                            master = await guild.fetch_user(guild.master_id)
                            guild_lists.append(f"Guild: **{guild.name}** - *{len(user_list)} members*, "
                                               f"Master: {master.nickname}#{master.identify_num}")
                        await msg.reply("\n".join(guild_lists), type=MessageTypes.KMD)

                elif command in ['here']:
                    current_channel_guild_id = msg.ctx.guild.id
                    current_guild = await bot.client.fetch_guild(current_channel_guild_id)
                    current_channel_id = msg.ctx.channel.id
                    current_channel = await bot.client.fetch_public_channel(current_channel_id)
                    channel = {'guild_id': current_channel_guild_id, 'guild_name': current_guild.name,
                               'master_id': current_guild.master_id, 'channel_id': current_channel_id,
                               'channel_name': current_channel.name}
                    await msg.reply(f"{channel}")

                elif command in ['leave']:
                    if not any(args):
                        await msg.reply("用法 `.admin leave {gid}`", type=MessageTypes.KMD)

                    elif len(args) == 1:
                        try:
                            target_guild = await bot.client.fetch_guild(args[0])
                            await msg.reply(f"获取到Bot加入了此服务器。服务器信息如下：\n"
                                            f"服务器id: {target_guild.id}\n"
                                            f"服务器name: {target_guild.name}\n"
                                            f"服务器master_id: {target_guild.master_id}\n"
                                            f"您确定要退出该服务器吗？\n"
                                            f"确定请输入 `.admin leave {target_guild.id} confirm`", type=MessageTypes.KMD)

                        except Exception as e:
                            logger.exception(e, exc_info=True)
                            await msg.reply("获取服务器失败，请检查服务器id是否正确。", type=MessageTypes.KMD)

                    elif any(args[0]) and args[1] == "confirm":
                        target_guild = await bot.client.fetch_guild(args[0])
                        await target_guild.leave()
                        await msg.reply("Bot成功退出此服务器！", type=MessageTypes.KMD)

                elif command in ['status']:
                    if not any(args):
                        await msg.reply("用法：\n"
                                        "`.admin status update` 更新状态\n"
                                        "`.admin status stop` 停止目前状态", type=MessageTypes.KMD)

                    elif args[0] in ['update']:
                        await update_music_status(bot)
                        await msg.reply("Bot更新状态成功！", type=MessageTypes.KMD)

                    elif args[0] in ['stop']:
                        await bot.client.stop_listening_music()
                        await msg.reply("Bot停止听音乐状态成功！", type=MessageTypes.KMD)

            except Exception as e:
                logger.exception(e, exc_info=True)
                await msg.reply(f"{e}")

    # 注册完毕更改所有指令前缀
    bot.command.update_prefixes(".", "。")
