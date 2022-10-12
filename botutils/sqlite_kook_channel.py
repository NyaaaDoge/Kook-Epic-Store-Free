import logging
import sqlite3
from pathlib import Path

SQL = Path() / "data" / "epic.db"


# KOOK频道
# class KookChannel:
#
#     def __init__(self, channel_id):
#         if channel_id is not None:
#             query_result = KookChannelSQL.get_channel_by_channel_id(channel_id)
#             self._guild_id = query_result[1]
#             self._guild_name = query_result[2]
#             self._master_id = query_result[3]
#             self._channel_id = query_result[4]
#             self._channel_name = query_result[5]
#             self._flag_push_free = query_result[6]
#
#         else:
#             raise ValueError("'channel_id' argument must be supplied.")
#
#     def __repr__(self):
#         return f'{self._guild_id} : {self._channel_id} - {self._channel_name}'
#
#     @property
#     def guild_id(self) -> str:
#         return self._guild_id
#
#     @property
#     def guild_name(self) -> str:
#         return self._guild_name
#
#     @property
#     def master_id(self) -> str:
#         return self._master_id
#
#     @property
#     def channel_id(self) -> str:
#         return self._channel_id
#
#     @property
#     def channel_name(self) -> str:
#         return self._channel_name
#
#     @property
#     def flag_push_free(self) -> str:
#         return self._flag_push_free


class KookChannelSQL:

    def __init__(self):
        if not SQL.exists():
            SQL.parent.mkdir(parents=True, exist_ok=True)
        self.make_kook_channel_table()

    @staticmethod
    def conn():
        return sqlite3.connect(SQL)

    def make_kook_channel_table(self):
        try:
            conn = self.conn()

            conn.execute('''create table KookChannel(
    ID             integer not null
        constraint KookChannel
            primary key autoincrement,
    guild_id text not null,
    guild_name text,
    master_id text,
    channel_id text not null,
    channel_name text,
    flag_push_free integer default 0)''')
        except sqlite3.OperationalError:
            pass
        except Exception as e:
            logging.error(e, exc_info=True)

    def update_sqlite(self):
        try:
            conn = self.conn()
            result = conn.execute(f"")
            return result
        except Exception as e:
            logging.error(e, exc_info=True)
            return e

    def insert_channel_free_default(self, channel):
        """
        插入频道，默认开启FREE推送服务
        :param channel:
        :return:
        """
        try:
            conn = self.conn()
            dbChannel = conn.execute(
                f"SELECT channel_id FROM KookChannel WHERE channel_id = {channel['channel_id']}").fetchone()
            # channel已存在
            if dbChannel is not None:
                return False
            # channel不存在，插入数据
            conn.execute(f"""INSERT INTO KookChannel VALUES (
                NULL,
                '{channel['guild_id']}',
                '{channel['guild_name']}',
                '{channel['master_id']}',
                '{channel['channel_id']}',
                '{channel['channel_name']}',
                1)""")
            conn.commit()
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    def get_channel_by_push_flag_free(self, flag: int) -> list:
        """
        根据是否开启Free推送的状态Flag来获取channel
        :param flag:
        :return [(id, guild_id, guild_name, master_id, channel_id, channel_name, is_pushed), ...]:
        """
        try:
            conn = self.conn()
            result = conn.execute(f"SELECT * FROM KookChannel WHERE flag_push_free = {flag}").fetchall()
            if not result:
                return []
            else:
                return result
        except Exception as e:
            logging.error(e, exc_info=True)

    def update_channel_push_flag_free_by_channel_id(self, channel_id, flag: int):
        """
        更新频道信息
        :param flag:
        :param channel_id:
        :return:
        """
        try:
            conn = self.conn()
            conn.execute(f"UPDATE KookChannel SET flag_push_free = {flag} WHERE channel_id = {channel_id}")
            conn.commit()
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    def delete_channel_by_channel_id(self, channel_id):
        try:
            conn = self.conn()
            conn.execute(f"DELETE FROM KookChannel WHERE channel_id = {channel_id}")
            conn.commit()
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    def delete_channel_by_guild_id(self, guild_id):
        try:
            conn = self.conn()
            conn.execute(f"DELETE FROM KookChannel WHERE guild_id = {guild_id}")
            conn.commit()
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    def get_channel_by_channel_id(self, channel_id):
        try:
            conn = self.conn()
            result = conn.execute(f"SELECT * FROM KookChannel WHERE channel_id = {channel_id}").fetchone()
            if not result:
                return []
            else:
                return result
        except Exception as e:
            logging.error(e, exc_info=True)
            return []

    def get_channel_by_guild_id(self, guild_id):
        try:
            conn = self.conn()
            result = conn.execute(f"SELECT * FROM KookChannel WHERE guild_id = {guild_id}").fetchone()
            if not result:
                return []
            else:
                return result
        except Exception as e:
            logging.error(e, exc_info=True)
            return []

    def get_all_channel(self):
        try:
            conn = self.conn()
            result = conn.execute(f"SELECT * FROM KookChannel").fetchall()
            if not result:
                return []
            else:
                return result
        except Exception as e:
            logging.error(e, exc_info=True)
            return []
