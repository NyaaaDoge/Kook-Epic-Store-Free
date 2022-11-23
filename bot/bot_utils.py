class BotUtils:
    @staticmethod
    def isItemAvailableFree(item_json_raw: dict):
        """
        检查传入是item是否为免费商品，跳过仅限激活码的商品
        :param item_json_raw:
        :return:
        """
        item_free_flag = False
        # 如果只可以用激活码激活就直接返回False
        if item_json_raw.get('isCodeRedemptionOnly'):
            return item_free_flag

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
                                item_free_flag = True
                                return item_free_flag

            # 将来的折扣信息
            elif any(upcoming_promotional_offers):
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
                                item_free_flag = True
                                return item_free_flag

        # 检查当前价格是否为0
        if prices is not None and any(prices):
            total_price = prices.get('totalPrice')
            fmt_price = total_price.get('fmtPrice')
            if fmt_price.get('discountPrice') == '0':
                item_free_flag = True
                return item_free_flag

        return item_free_flag
