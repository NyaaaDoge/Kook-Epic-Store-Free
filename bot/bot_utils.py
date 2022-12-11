import logging
import os
from logging import Logger
from khl import Message


class BotUtils(object):
    @staticmethod
    def get_item_free_status(item_json_raw: dict) -> dict:
        """
        传入item_json_raw商品，如果是免费商品则返回对应字典
        :param item_json_raw:
        :return free_info = {'is_free': False, ...}:
        """
        free_info = {'is_free': False}
        # 如果只可以用激活码激活就直接返回False
        if item_json_raw.get('isCodeRedemptionOnly'):
            return free_info

        promotions = item_json_raw.get('promotions')
        prices = item_json_raw.get('price')

        # 检查是否是折扣比设置为0的商品，在promotions里面判断
        if promotions is not None and any(promotions):
            promotional_offers = item_json_raw.get('promotions').get('promotionalOffers')
            upcoming_promotional_offers = item_json_raw.get('promotions').get('upcomingPromotionalOffers')
            # 现在的折扣
            if any(promotional_offers):
                for offers_info in promotional_offers:
                    promotions_infos = offers_info.get('promotionalOffers')
                    # 遍历详细的折扣信息
                    for promotions_info in promotions_infos:
                        discount_setting = promotions_info.get('discountSetting')
                        if discount_setting.get('discountType') == 'PERCENTAGE':
                            discount_percentage = discount_setting.get('discountPercentage')
                            # 如果折扣不为0，跳到下一个信息继续检查
                            if not discount_percentage == 0:
                                continue
                            else:
                                # 折扣有为0
                                free_info['startDate'] = promotions_info.get('startDate')
                                free_info['endDate'] = promotions_info.get('endDate')
                                free_info['is_free'] = True
                                return free_info

            # 将来的折扣信息
            if any(upcoming_promotional_offers):
                for offers_info in upcoming_promotional_offers:
                    promotions_infos = offers_info.get('promotionalOffers')
                    # 遍历详细的折扣信息
                    for promotions_info in promotions_infos:
                        discount_setting = promotions_info.get('discountSetting')
                        if discount_setting.get('discountType') == 'PERCENTAGE':
                            discount_percentage = discount_setting.get('discountPercentage')
                            # 如果折扣不为0，跳到下一个信息继续检查
                            if not discount_percentage == 0:
                                continue
                            else:
                                # 折扣有为0
                                free_info['startDate'] = promotions_info.get('startDate')
                                free_info['endDate'] = promotions_info.get('endDate')
                                free_info['is_free'] = True
                                return free_info

        # 检查当前价格是否为0
        if prices is not None and any(prices):
            total_price = prices.get('totalPrice')
            fmt_price = total_price.get('fmtPrice')
            if fmt_price.get('discountPrice') == '0':
                free_info['is_free'] = True
                free_info['discountPrice'] = '0'
                return free_info

        return free_info

    @staticmethod
    def logging_msg(logger: Logger, msg: Message):
        logger.info(f"Message: G_id({msg.ctx.guild.id})-C_id({msg.ctx.channel.id}) - "
                    f"Au({msg.author_id})-({msg.author.username}#{msg.author.identify_num}) = {msg.content}")

    @staticmethod
    def create_log_file(logger: Logger, filename: str):
        """
        将日志记录到日志文件
        :param logger:
        :param filename:
        :return:
        """
        filename = './logs/' + filename

        try:
            # 尝试创建 FileHandler
            fh = logging.FileHandler(filename=filename, encoding='utf-8', mode='a')

        except OSError:
            os.makedirs(os.path.dirname(filename))
            # 再次尝试创建 FileHandler
            fh = logging.FileHandler(filename=filename, encoding="utf-8", mode="a")

        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -%(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        return logger
