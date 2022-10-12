## 1. bot-config.json

### 1.1 bot-config.json 咋填？

> 本段引用自 [TWT233/khl.py/example/ex02](https://github.com/TWT233/khl.py/tree/main/example/ex02_config_file)

我们只需要填「Token」即可，记得打引号哦。还有，json 中字符串只能用双引号括起来，注意一下

Q: 还有两项「verify_token」「encrypt_key」是啥？

A: 「verify_token」「encrypt_key」这两项是为 webhook 准备的，我们现在留空即可

### 怎么在代码中读取 `config.json`？

看 `ex02.py` 第 5 ~ 11 行：

```python
# 用 json 读取 bot-config.json，装载到 config 里
# 注意文件路径，要是提示找不到文件的话，就 cd 一下工作目录/改一下这里
with open('bot-config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])
```

是不是很简单？而且以后要换 bot 也不用打开代码来改了，修改一下 json 就行，安全性也得到了保障

----

### 其他的项是啥玩意？

Q1: bot_market_uuid是？

A1: 给kook的非官方bot-market提供在线凭证的token，配置好机器人并且通过审核之后会得到UUID，点击“在线验证”将UUID填入其中即可

Q2: developers是？

A2: 用来给开发者管理或者查看机器人使用的，列表里面填写开发者的KookID，在Kook客户端打开开发者模式然后点击头像复制即可。