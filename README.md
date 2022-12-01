# Kook Epic Store Free

----

用于Kook语音上推送Epic商店（国区）限时免费领取游戏资讯的机器人。在指定的频道订阅后可以进行推送。需要Bot拥有`管理角色`权限，此权限用于判断用户是否具有权限开关功能。用户使用需要拥有`管理员`或者`管理频道`权限。

### 1. Bot指令使用说明

可以使用 "."(英文句号标点) 和 "。"(中文句号标点) 响应epic相关的指令。

| 指令                  | 说明                                        |
|---------------------|-------------------------------------------|
| `.helloepic`        | 测试bot是否在线，以及是否有权限在该频道发送消息。                |
| `.epic`             | 查看帮助说明。                                   |
| `.epic free on`     | 在该文字频道开启Epic免费游戏（国区）推送。一个服务器只能有一个频道能进行推送。 |
| `.epic free off`    | 关闭Epic免费游戏推送，该指令在服务器内任何频道都生效。             |
| `.epic free now`    | 获取现在正在领取时间的Epic免费游戏资讯。                    |
| `.epic free coming` | 获取预告能领取的Epic免费游戏资讯。                       |

`.admin`开头的指令为开发者指令，使用前需要在config文件中填入开发者的kook id。

| 指令                        | 说明                 |
|---------------------------|--------------------|
| `.admin info`             | 查看开启订阅服务的相关信息      |
| `.admin delete {game_id}` | 删除数据库中对应game_id的数据 |
| `.admin leave {gid}`      | 退出指定服务器            |
| `.admin here`             | 查看当前频道的信息          |
| `.admin status update`    | 立刻更新Bot的音乐状态       |
| `.admin status stop`      | 立刻停止Bot的音乐状态       |

### 2. 项目说明

项目依赖

+ 项目使用Kook社区TWT233提供的 [Python SDK - khl.py(v0.3.8)](https://github.com/TWT233/khl.py) 进行开发
+ 项目参考了Nonebot的 [Epic 限免游戏资讯](https://github.com/monsterxcn/nonebot_plugin_epicfree) 插件

### 3. 其他

bot每十分钟更新一次音乐状态（n个能领取、m个预告中的游戏）。 本bot主要用于Kook服务器中推送相关资讯 [Steam阀门社](https://kook.top/nGr9DH) ，欢迎加入Kook服务器，获取更多游戏资讯。
Bot现已开放邀请，如果觉得好用的话，欢迎点个 Star 或者来 [Bot Market页面](https://www.botmarket.cn/bots?id=108)
发表意见。也可以来我的 [爱发电页面](https://afdian.net/a/NyaaaDoge) 捐助我 .