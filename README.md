# Kook Epic Store Free

----

用于Kook语音上推送Epic商店限时免费领取游戏资讯的机器人。在指定的频道订阅后可以进行推送。

### 1. Bot指令使用说明

可以使用 "."(英文句号标点) 和 "。"(中文句号标点) 响应epic相关的指令。

| 指令               | 说明                                    |
|------------------|---------------------------------------|
| `.epic`          | 查看帮助说明。                               |
| `.epic free on`  | 在该文字频道开启Epic免费游戏推送。一个服务器只能有一个频道能进行推送。 |
| `.epic free off` | 关闭Epic免费游戏推送，该指令在服务器内任何频道都生效。         |

`.admin`开头的指令为开发者指令，使用前需要在config文件中填入开发者的kook id。

| 指令                   | 说明            |
|----------------------|---------------|
| `.admin info`        | 查看开启订阅服务的相关信息 |
| `.admin leave {gid}` | 退出指定服务器       |
| `.admin here`        | 查看当前频道的信息     |

### 2. 项目说明

项目依赖

+ 项目使用Kook社区TWT233提供的[Python SDK - khl.py(v0.3.8)](https://github.com/TWT233/khl.py)进行开发
+ 项目参考了Nonebot的[Epic 限免游戏资讯](https://github.com/monsterxcn/nonebot_plugin_epicfree)插件

### 3. 其他

本bot主要用于Kook服务器中推送相关资讯 [Steam阀门社](https://kook.top/nGr9DH)，欢迎加入Kook服务器，获取更多游戏资讯。