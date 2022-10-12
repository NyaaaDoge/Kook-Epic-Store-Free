import logging
import sqlite3
from pathlib import Path

SQL = Path() / "data" / "epic.db"


class EpicFreeGamesSQL:

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
    free_start_date text,
    free_end_date   text,
    is_pushed integer default 0
);''')
        except sqlite3.OperationalError:
            pass
        except Exception as e:
            logging.error(e)

    def insert_item(self, items: list):
        try:
            conn = self.conn()
            for item in items:
                game_id = conn.execute(
                    f"SELECT game_id FROM EpicFreeGames WHERE game_id = '{item['id']}'").fetchone()
                # app已存在
                if game_id is not None:
                    continue
                # app不存在，插入数据，如果不是仅限激活码激活，插入数据
                if item.get('isCodeRedemptionOnly') == False:
                    title = item.get('title', '').replace("'", "''")
                    description = item.get('description').replace("'", "''")
                    store_url = "https://store.epicgames.com/zh-CN/p/" + item.get('catalogNs').get('mappings')[0].get('pageSlug', '')
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
                    # 获取免费领取开始时间
                    promotions = item.get('promotions', None)
                    free_start_date = ""
                    free_end_date = ""
                    # 如果没有promotions返回
                    if promotions is None:
                        pass
                    # 如果有promotions返回
                    else:
                        # 如果promotions中的promotionalOffers有内容，则代表现在时间段可以领取
                        if any(promotions['promotionalOffers']):
                            free_start_date = promotions['promotionalOffers'][0]['promotionalOffers'][0]['startDate']
                            free_end_date = promotions['promotionalOffers'][0]['promotionalOffers'][0]['endDate']
                        # 以后能领取
                        elif any(promotions['upcomingPromotionalOffers']):
                            free_start_date = promotions['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['startDate']
                            free_end_date = promotions['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['endDate']

                    conn.execute(f"""INSERT INTO EpicFreeGames VALUES (
                        NULL,
                        '{item['id']}',
                        '{title}',
                        '{description}',
                        '{store_url}',
                        '{epic_release_date}',
                        '{item['offerType']}',
                        '{image_wide}',
                        '{image_tall}',
                        '{image_thumbnail}',
                        '{item['seller']['name']}',
                        '{original_price}',
                        '{free_start_date}',
                        '{free_end_date}',
                        0)""")
                    conn.commit()
                    logging.debug(f"Item({item['id']} : {title}) has been inserted into table.")
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    def get_item_by_push_flag(self, flag: int) -> list:
        """
        根据是否推送的状态Flag来获取Epic商品信息
        :param flag:
        :return [(id, game_id, title, description, store_url, epic_release_date, offer_type, image_wide, image_tall, image_thumbnail, seller, original_price, free_start_date, free_end_date, is_pushed), ...]:
        """
        try:
            conn = self.conn()
            result = conn.execute(f"SELECT * FROM EpicFreeGames WHERE is_pushed = {flag}").fetchall()
            if not result:
                return []
            else:
                return result
        except Exception as e:
            logging.error(e)

    def get_all_item(self) -> list:
        """
        获取所有数据
        :return [(id, game_id, title, description, store_url, epic_release_date, offer_type, image_wide, image_tall, image_thumbnail, seller, original_price, free_start_date, free_end_date, is_pushed), ...]:
        """
        try:
            conn = self.conn()
            result = conn.execute(f"SELECT * FROM EpicFreeGames").fetchall()
            if not result:
                return []
            else:
                return result
        except Exception as e:
            logging.error(e)

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
            logging.error(e)
            return False
