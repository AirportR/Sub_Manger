import sqlite3
import pandas as pd
from loguru import logger
from command import *

# 定义数据库
conn = sqlite3.connect('My_sub.db', check_same_thread=False)
c = conn.cursor()

# 创建表
c.execute('''CREATE TABLE IF NOT EXISTS My_sub(URL text, comment text)''')


def loader(bot: telebot.TeleBot, **kwargs):
    command_loader(bot, **kwargs)
    callback_loader(bot, **kwargs)


def command_loader(bot: telebot.TeleBot, **kwargs):
    admin_id = kwargs.get('admin_id', [])

    # 接收用户输入的指令
    @bot.message_handler(commands=['add', 'del', 'search', 'update', 'help'])
    def handle_command(message):
        if str(message.from_user.id) in admin_id:
            command = message.text.split()[0]
            logger.debug(f"用户{message.from_user.id}使用了{command}功能")
            if command == '/add':
                add_sub(message, cursor=c, conn=conn, bot=bot)
            elif command == '/del':
                delete_sub(message, cursor=c, conn=conn, bot=bot)
            elif command == '/search':
                search_sub(message, cursor=c, conn=conn, bot=bot)
            elif command == '/update':
                update_sub(message, cursor=c, conn=conn, bot=bot)
            elif command == '/help':
                help_sub(message, bot=bot)
        else:
            # bot.send_message(message.chat.id, "你没有权限操作，别瞎搞！")
            bot.reply_to(message, "❌你没有操作权限，别瞎搞！")

    # 接收xlsx表格
    @logger.catch()
    @bot.message_handler(content_types=['document'], chat_types=['private'])
    def handle_document(message):
        if str(message.from_user.id) in admin_id:
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            try:
                file = bot.download_file(file_info.file_path)
                with open('sub.xlsx', 'wb') as f:
                    f.write(file)
                if file_analyze.filetype('sub.xlsx') in ['EXT_ZIP/XLSX/DOCX', 'XLS/DOC']:
                    df = pd.read_excel('sub.xlsx')
                    for i in range(len(df)):
                        c.execute("SELECT * FROM My_sub WHERE URL=?", (df.iloc[i, 0],))
                        if not c.fetchone():
                            c.execute("INSERT INTO My_sub VALUES(?,?)", (df.iloc[i, 0], df.iloc[i, 1]))
                            conn.commit()
                    bot.reply_to(message, "✅导入成功！")
                else:
                    bot.send_message(message.chat.id, "😵😵导入的文件格式错误，请检查文件后缀是否为xlsx后重新导入")
            except Exception as e:
                print(e)

        else:
            bot.reply_to(message, "😡😡😡你不是管理员，禁止操作！")


def callback_loader(bot: telebot.TeleBot, **kwargs):
    admin_id = kwargs.get('admin_id', [])

    # 按钮点击事件
    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        if str(call.from_user.id) in admin_id:
            if call.data == 'close':
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                try:
                    row_num = call.data
                    c.execute("SELECT rowid,URL,comment FROM My_sub WHERE rowid=?", (row_num,))
                    result = c.fetchone()
                    bot.send_message(call.message.chat.id,
                                     '行号：{}\n订阅地址：{}\n说明： {}'.format(result[0], result[1], result[2]))
                    logger.debug(f"用户{call.from_user.id}从BOT获取了{result}")
                except Exception as e:
                    print(e)
                    bot.send_message(call.message.chat.id, "😵😵这个订阅刚刚被别的管理员删了，请尝试其他操作")
        else:
            if call.from_user.username is not None:
                now_user = f" @{call.from_user.username} "
            else:
                now_user = f" tg://user?id={call.from_user.id} "
            bot.send_message(call.message.chat.id, now_user + "天地三清，道法无敌，邪魔退让！退！退！退！👮‍♂️")
