import logging
import sqlite3

from bot.bot_utils import BotUtils
from dataclasses import dataclass
from pathlib import Path

SQL = Path() / "data" / "epic.db"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatabaseFreeItem(object):
    ID: int
    game_id: str
    title: str
    description: str
    store_url: str
    epic_release_date: str
    offer_type: str
    image_wide: str
    image_tall: str
    image_thumbnail: str
    seller: str
    original_price: str
    discount_price: str
    free_start_date: str
    free_end_date: str
    is_pushed: int

    def __str__(self):
        return f"{self.game_id}-{self.title}"


class EpicFreeGamesSQL(object):

    def __init__(self):
        if not SQL.exists():
            SQL.parent.mkdir(parents=True, exist_ok=True)
        self.make_epic_free_games_table()

    @staticmethod
    def conn():
        return sqlite3.connect(SQL)

    def make_epic_free_games_table(self):
        try:
            conn = self.conn()

            conn.execute(f'''create table EpicFreeGames(
    ID              integer not null
        constraint EpicFreeGames
            primary key autoincrement,
    game_id         text,
    title           text,
    description     text,
    store_url       text,
    epic_release_date    text,
    offer_type      text,
    image_wide      text,
    image_tall      text,
    image_thumbnail text,
    seller    text,
    original_price  text,
    discount_price text,
    free_start_date text,
    free_end_date   text,
    is_pushed integer default 0
);''')
        except sqlite3.OperationalError:
            pass
        except Exception as e:
            logger.error(e)

    def insert_items(self, items: list):
        try:
            conn = self.conn()
            for item in items:
                game_id = conn.execute(
                    f"SELECT game_id FROM EpicFreeGames WHERE game_id = '{item['id']}'").fetchone()
                # app已存在
                if game_id is not None:
                    continue
                # app不存在，插入数据，如果不是仅限激活码激活，插入数据
                if not item.get('isCodeRedemptionOnly'):
                    # 检查是否是折扣设置为0的商品，在promotions里面判断
                    free_info = BotUtils().get_item_free_status(item)
                    # 如果是可以免费领取的商品
                    if free_info.get('is_free'):
                        free_start_date = free_info.get('startDate', '')
                        free_end_date = free_info.get('endDate', '')
                    # 如果不是，跳过此条数据的插入
                    else:
                        continue

                    title = item.get('title', '')
                    description = item.get('description')
                    store_url = "https://store.epicgames.com/zh-CN/p/" + item.get('catalogNs').get('mappings')[0].get(
                        'pageSlug', '')
                    epic_release_date = item.get('effectiveDate', '')
                    # 获取图片地址
                    image_wide = ""
                    image_tall = ""
                    image_thumbnail = ""
                    for image in item.get('keyImages'):
                        if image.get('type') == 'OfferImageWide':
                            image_wide = image.get('url', '')
                        if image.get('type') == 'OfferImageTall':
                            image_tall = image.get('url', '')
                        if image.get('type') == 'Thumbnail':
                            image_thumbnail = image.get('url', '')
                    original_price = item.get('price').get('totalPrice').get('fmtPrice').get('originalPrice', '')
                    discount_price = item.get('price').get('totalPrice').get('fmtPrice').get('discountPrice', '')

                    insert_str = (item['id'],
                                  title,
                                  description,
                                  store_url,
                                  epic_release_date,
                                  item['offerType'],
                                  image_wide,
                                  image_tall,
                                  image_thumbnail,
                                  item['seller']['name'],
                                  original_price,
                                  discount_price,
                                  free_start_date,
                                  free_end_date,)

                    conn.execute(f"INSERT INTO EpicFreeGames VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)", insert_str)
                    conn.commit()
                    logger.info(f"Item({item['id']}:{title}) has been inserted into table.")
            return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            return False

    def get_item_by_push_flag(self, flag: int) -> list:
        """
        根据是否推送的状态Flag来获取Epic商品信息
        :param flag:
        """
        try:
            conn = self.conn()
            result = conn.execute(f"SELECT * FROM EpicFreeGames WHERE is_pushed = {flag}").fetchall()
            if not result:
                return []
            else:
                return result
        except Exception as e:
            logger.exception(e, exc_info=True)

    def get_all_item(self) -> list:
        """
        获取所有数据
        """
        try:
            conn = self.conn()
            result = conn.execute(f"SELECT * FROM EpicFreeGames").fetchall()
            if not result:
                return []
            else:
                return result
        except Exception as e:
            logger.exception(e, exc_info=True)

    def get_item_by_game_id(self, game_id):
        try:
            conn = self.conn()
            result = conn.execute(f"SELECT * FROM EpicFreeGames where game_id = '{game_id}'").fetchone()
            if not result:
                return ()
            else:
                return result
        except Exception as e:
            logger.exception(e, exc_info=True)

    def update_item_push_flag_by_game_id(self, game_id, flag: int):
        """
        更新商品推送Flag状态
        :param flag:
        :param game_id:
        :return:
        """
        try:
            conn = self.conn()
            conn.execute(f"UPDATE EpicFreeGames SET is_pushed = {flag} WHERE game_id = '{game_id}'")
            conn.commit()
            return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            return False

    def update_item_by_game_id(self, game_id, item):
        try:
            title = item.get('title', '')
            description = item.get('description')
            store_url = "https://store.epicgames.com/zh-CN/p/" + item.get('catalogNs').get('mappings')[0].get(
                'pageSlug', '')
            # 获取免费领取开始时间
            original_price = item.get('price').get('totalPrice').get('fmtPrice').get('originalPrice', '')
            discount_price = item.get('price').get('totalPrice').get('fmtPrice').get('discountPrice', '')
            free_info = BotUtils().get_item_free_status(item)
            # 如果是可以免费领取的商品
            if free_info.get('is_free'):
                free_start_date = free_info.get('startDate', '')
                free_end_date = free_info.get('endDate', '')
            # 如果不是，跳过此条数据的更新
            else:
                return

            insert_str = (title, description, store_url,
                          free_start_date, free_end_date,
                          original_price, discount_price, game_id)

            conn = self.conn()
            conn.execute(f"UPDATE EpicFreeGames "
                         f"SET title = ?, description = ?, store_url = ?, "
                         f"free_start_date = ?, free_end_date = ?,"
                         f"original_price = ?, discount_price = ?"
                         f"WHERE game_id = ?", insert_str)
            conn.commit()
            logger.debug(f"Item({game_id}-{title}) has been updated successfully.")
            return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            return False

    def delete_item_by_game_id(self, game_id):
        """
        根据game_id删除对应的数据
        :param game_id:
        :return:
        """
        try:
            logger.info(f"Deleting item by ({game_id})...")
            conn = self.conn()
            result = conn.execute(f"DELETE FROM EpicFreeGames where game_id = '{game_id}'")
            conn.commit()
            conn.execute(f"VACUUM")
            if not result:
                return False
            else:
                logger.info(f"Successfully delete {result.rowcount} item(s) by ({game_id}).")
                return result.rowcount
        except Exception as e:
            logger.exception(e, exc_info=True)
            return False
