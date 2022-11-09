from khl.card import CardMessage, Card, Types, Module, Element
from datetime import datetime, timedelta
from botutils import sqlite_epic_free


# ========================================卡片部分================================================


# 免费游戏卡片 按时间做分类
def freeGameCardMessage(item_free):
    db_item = sqlite_epic_free.DatabaseFreeItem(*item_free)
    card_message = CardMessage()

    now_time = datetime.now()
    fmt_release_time = datetime.fromisoformat(db_item.epic_release_date[:-1]).strftime("%Y-%m-%d")
    db_start_time_bj = datetime.fromisoformat(db_item.free_start_date[:-1]) + timedelta(hours=8)
    db_end_time_bj = datetime.fromisoformat(db_item.free_end_date[:-1]) + timedelta(hours=8)

    card = Card(theme=Types.Theme.INFO)
    card.append(
        Module.Section(text=Element.Text(f"**Epic 商店限时免费领取物品！**", type=Types.Text.KMD),
                       accessory=Element.Image('https://img.kookapp.cn/assets/2022-10/2BwJawa4NY0dz0e8.jpg',
                                               circle=False, size=Types.Size.SM)))
    card.append(Module.Divider())
    card.append(Module.Section(Element.Text(f"**[{db_item.title}]({db_item.store_url})**", type=Types.Text.KMD)))
    # 如果现在能领取
    if db_start_time_bj < now_time < db_end_time_bj:
        card.append(Module.Section(text=Element.Text(f"**`{db_end_time_bj}` 之前**", type=Types.Text.KMD),
                                   accessory=Element.Button(f"获取", f"{db_item.store_url}",
                                                            theme=Types.Theme.INFO, click=Types.Click.LINK)))
        card.append(Module.Context(Element.Text("离免费领取时间**结束**还有：", type=Types.Text.KMD)))
        card.append(Module.Countdown(end=db_end_time_bj, mode=Types.CountdownMode.DAY))
    # 现在不能领取
    elif now_time < db_start_time_bj:
        card.append(
            Module.Section(text=Element.Text(f"**`{db_start_time_bj}` 至\n`{db_end_time_bj}`**", type=Types.Text.KMD),
                           accessory=Element.Button(f"即将推出", f"{db_item.store_url}",
                                                    theme=Types.Theme.INFO, click=Types.Click.LINK)))
        card.append(Module.Context(Element.Text("离免费领取时间**开始**还有：", type=Types.Text.KMD)))
        card.append(Module.Countdown(end=db_start_time_bj, mode=Types.CountdownMode.DAY))
        card.append(Module.Context(Element.Text("离免费领取时间**结束**还有：", type=Types.Text.KMD)))
        card.append(Module.Countdown(end=db_end_time_bj, mode=Types.CountdownMode.DAY))

    card.append(Module.Container(Element.Image(f"{db_item.image_wide}")))
    card.append(Module.Context(f"登陆Epic商店日期：{fmt_release_time}\n发行商：{db_item.seller}"))
    card.append(Module.Section(text=Element.Text(f"> {db_item.description}", type=Types.Text.KMD)))
    card.append(Module.Context(Element.Text('[Bot Market](https://www.botmarket.cn/bots?id=108) | '
                                            '[交流服务器内有更多资讯](https://kook.top/nGr9DH) | '
                                            '[爱发电](https://afdian.net/a/NyaaaDoge)', type=Types.Text.KMD)))

    card_message.append(card)
    return card_message


# 帮助信息卡片
def helpInfoCardMessage():
    card_message = CardMessage()
    card = Card(theme=Types.Theme.INFO)
    card.append(Module.Header('Epic Store Free Bot 使用说明'))
    card.append(Module.Context(Element.Text(f"[在Github上查看使用文档](https://github.com/NyaaaDoge/Kook-Epic-Store-Free)",
                                            type=Types.Text.KMD)))
    card.append(Module.Divider())
    card.append(Module.Section(Element.Text("""指令说明：
`.epic free on`     在该频道开启Epic免费游戏推送。注意：一个服务器只能有一个频道能进行推送。
`.epic free off`    关闭Epic免费游戏推送，注意：该指令在服务器内任何频道都生效。
`.epic free now`    获取现在正在领取时间的Epic免费游戏资讯。
`.epic free coming`    获取预告能领取的Epic免费游戏资讯。
Bot需要拥有 角色管理权限，用于判断用户是否具有权限开关功能；用户开关功能需要拥有 服务器管理 或 频道管理 权限。
----
关于Bot：
> 建议在服务器单独开设一个频道接收Epic免费游戏资讯，将该文字频道的频道的Epic Store Free角色的可见和发送消息权限设置为开启。
Bot获取到的Epic Games Store的免费游戏的区域均为国区（CN）。
如果觉得Epic Store Free好用的话，欢迎来[Bot Market页面](https://www.botmarket.cn/)发表评价或[爱发电捐助我](https://afdian.net/a/NyaaaDoge)。
欢迎加入交流服务器**[Steam阀门社](https://kook.top/nGr9DH)**，服务器内有Steam限时免费游戏推送等游戏资讯。""", type=Types.Text.KMD)))
    card.append(Module.Divider())
    card.append(Module.Section('如有任何问题，欢迎加入交流服务器与开发者联系',
                               Element.Button('交流服务器', 'https://kook.top/nGr9DH', Types.Click.LINK)))

    card_message.append(card)
    return card_message
