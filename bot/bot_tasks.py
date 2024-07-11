import logging
from datetime import datetime, timedelta

from khl import Bot, MessageTypes, HTTPRequester, PublicChannel

from bot import epic_store_core, sqlite_epic_free, sqlite_kook_channel
from bot.card_storage import free_game_card_message

logger = logging.getLogger(__name__)


def register_tasks(bot: Bot):
    # 分钟数定时任务
    @bot.task.add_interval(minutes=10)
    async def interval_minutes_tasks():
        try:
            # 获取Epic免费商品，写入数据库中
            logger.info(f"Execute get_free_games task...")
            await get_free_games()

            epicFreeSQL = sqlite_epic_free.EpicFreeGamesSQL()
            # 查询没有没被推送过的免费商品  "0"代表没被推送过，"1"代表已被推送过
            items = epicFreeSQL.get_item_by_push_flag(0)
            if any(items):
                # 执行推送任务
                logger.info(f"Execute push_free_items task...")
                await push_free_items(bot)
            else:
                logger.info(f"No free item to be pushed to the channel.")

            # 更新Bot状态
            logger.info(f"Execute update_music_status task...")
            await update_music_status(bot)

        except Exception as e:
            logger.exception(e, exc_info=True)


# ========================================定时任务================================================

# ----------------------------------------获取任务-----------------------------------------------


# 获取Epic免费商品，写入数据库中
async def get_free_games():
    try:
        logger.info(f"Getting free items...")
        # 获取免费商品
        free_items = await epic_store_core.get_epic_free_games()
        # 将免费商品写入数据库中，数据会有更新的说法，同时需要更新数据库的数据
        epicFreeSQL = sqlite_epic_free.EpicFreeGamesSQL()
        flag_insert = epicFreeSQL.insert_items(free_items)
        if flag_insert:
            logger.debug(f"Insert {len(free_items)} item(s) info into the table successfully.")
        else:
            logger.debug(f"The {len(free_items)} item(s) inserted info the table fail.")
        # 对于重复game_id的物品，更新数据
        for free_item in free_items:
            # if free_item.get('isCodeRedemptionOnly'):
            current_game_id = free_item['id']
            title = free_item.get('title', '').replace("'", "''")
            db_data = epicFreeSQL.get_item_by_game_id(current_game_id)
            # TODO 如果是以前已经存在于数据库的商品，重新修改了领取起止时间可以修改push flag?
            if any(db_data):
                # 执行更新操作
                epicFreeSQL.update_item_by_game_id(current_game_id, free_item)
                logger.info(f"Successfully update item({current_game_id}:{title})")

    except Exception as e:
        logger.exception(e, exc_info=True)

    finally:
        logger.info("Task get_free_games done.")


# ----------------------------------------推送任务-----------------------------------------------


# 推送数据库中未被推送过的商品信息
async def push_free_items(bot: Bot):
    try:
        logger.info(f"Pushing free items...")
        # 查询数据库中开启订阅功能的频道id-channel[4] "0"代表关闭，"1"代表开启
        channelSQL = sqlite_kook_channel.KookChannelSQL()
        sub_channels = channelSQL.get_channel_by_push_flag_free(1)
        epicFreeSQL = sqlite_epic_free.EpicFreeGamesSQL()
        items = epicFreeSQL.get_item_by_push_flag(0)
        # 遍历频道，给频道进行推送
        for channel in sub_channels:
            channel_id: str = channel[4]
            try:
                # 获取频道
                target_channel = await bot.client.fetch_public_channel(channel_id=channel_id)
                for item in items:
                    db_item = sqlite_epic_free.DatabaseFreeItem(*item)
                    # 按时间进行推送，有截止日期 同时需要折扣设置为0
                    if not db_item.free_end_date == '':
                        now_time = datetime.now() - timedelta(hours=8)
                        db_end_time = datetime.fromisoformat(db_item.free_end_date[:-1])
                        # 如果还未结束领取，进行推送
                        if db_end_time > now_time:
                            try:
                                await send_item_to_channel(bot, target_channel, item)
                            except Exception as e:
                                logger.exception(f"Free item({db_item.game_id}:{db_item.title}): {e}")

            except Exception as e:
                logger.exception(f"Channel{channel}: {e}")

        # 推送完毕需要更改数据库中flag信息
        for item in items:
            flag_push = epicFreeSQL.update_item_push_flag_by_game_id(item[1], 1)
            if flag_push:
                logger.info(
                    f"Item({item[1]}:{item[2]}) has been pushed to all channels and the push-flag updated to 1.")
            else:
                logger.info(f"Item({item[1]}) push flag update failed.")

    except Exception as e:
        logger.exception(e, exc_info=True)

    finally:
        logger.info("Task push_free_items done.")


async def send_item_to_channel(bot: Bot, target_channel: PublicChannel, item_free_tuple_raw):
    db_item = sqlite_epic_free.DatabaseFreeItem(*item_free_tuple_raw)
    try:
        # 进行推送
        await bot.client.send(target=target_channel, type=MessageTypes.CARD,
                              content=free_game_card_message(item_free_tuple_raw))
        # 推送完毕
        logger.info(
            f"Free item({db_item.game_id}:{db_item.title}) has been pushed to channel"
            f"(G_id-{target_channel.guild_id}, C_name-{target_channel.name}, "
            f"C_id-{target_channel.id})")

    # 如果遇到 40000 代码再创建不发送描述的任务
    except HTTPRequester.APIRequestFailed as failed:
        if failed.err_code == 40000:
            try:
                logger.exception(
                    f"Failed to send card message for {db_item.title}({db_item.game_id}), "
                    f"sending card message without descriptions...", exc_info=False)
                # 进行推送
                await bot.client.send(target=target_channel, type=MessageTypes.CARD,
                                      content=free_game_card_message(item_free_tuple_raw,
                                                                     desc=False, game_img=False))
                # 推送完毕
                logger.info(
                    f"Free item({db_item.game_id}:{db_item.title}) has been pushed to channel"
                    f"(G_id-{target_channel.guild_id}, C_name-{target_channel.name}, "
                    f"C_id-{target_channel.id}) without desc.")
            except Exception as e:
                logger.exception(f"Free item({db_item.game_id}:{db_item.title}): {e}")

    except Exception as e:
        logger.exception(f"Free item({db_item.game_id}:{db_item.title}): {e}")


# ----------------------------------------更新状态任务---------------------------------------------


# 更新Bot听音乐的状态
async def update_music_status(bot: Bot):
    try:
        logger.info(f"Updating bot status...")
        ongoing_free = 0
        upcoming_free = 0
        now_time = datetime.now() - timedelta(hours=8)
        epicFreeSQL = sqlite_epic_free.EpicFreeGamesSQL()
        free_items = epicFreeSQL.get_all_item()
        for item in free_items:
            db_item = sqlite_epic_free.DatabaseFreeItem(*item)
            # 有截止日期
            if not db_item.free_end_date == '':
                start_time = datetime.fromisoformat(db_item.free_start_date[:-1])
                end_time = datetime.fromisoformat(db_item.free_end_date[:-1])
                # 如果现在在领取期间中，给正在领取+1
                if start_time < now_time < end_time:
                    ongoing_free += 1
                # 如果现在不在领取期间，但是在预告之前
                if now_time < start_time:
                    upcoming_free += 1

        await bot.client.update_listening_music(f"🎁{ongoing_free}款能领取、{upcoming_free}款游戏预告中",
                                                f"Steam 阀门社 -🔎Code: nGr9DH")
        logger.info(f"Successfully update status ({ongoing_free}款能领取、{upcoming_free}款游戏预告中).")

    except Exception as e:
        logger.exception(e, exc_info=True)

    finally:
        logger.info("Task update_music_status done.")
