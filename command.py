# 添加数据
import telebot


def add_sub(message, **kwargs):
    c = kwargs.get('cursor', None)
    bot = kwargs.get('bot', None)
    conn = kwargs.get('conn', None)
    try:
        url_comment = message.text.split()[1:]
        url = url_comment[0]
        comment = url_comment[1]
        c.execute("SELECT * FROM My_sub WHERE URL=?", (url,))
        if c.fetchone():
            bot.reply_to(message, "😅订阅已存在！")
        else:
            c.execute("INSERT INTO My_sub VALUES(?,?)", (url, comment))
            conn.commit()
            bot.reply_to(message, "✅添加成功！")
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😵😵输入格式有误，请检查后重新输入")


# 删除数据
def delete_sub(message, **kwargs):
    c = kwargs.get('cursor', None)
    bot = kwargs.get('bot', None)
    conn = kwargs.get('conn', None)
    try:
        row_num = message.text.split()[1]
        c.execute("DELETE FROM My_sub WHERE rowid=?", (row_num,))
        conn.commit()
        bot.reply_to(message, "✅删除成功！")
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😵😵输入格式有误，请检查后重新输入")


# 查找数据
def search_sub(message, **kwargs):
    c = kwargs.get('cursor', None)
    bot = kwargs.get('bot', None)
    # conn = kwargs.get('conn', None)
    try:
        search_str = message.text.split()[1]
        c.execute("SELECT rowid,URL,comment FROM My_sub WHERE URL LIKE ? OR comment LIKE ?",
                  ('%' + search_str + '%', '%' + search_str + '%'))
        result = c.fetchall()
        if result:
            keyboard = []
            for i in range(0, len(result), 2):
                row = result[i:i + 2]
                keyboard_row = []
                for item in row:
                    button = telebot.types.InlineKeyboardButton(item[2], callback_data=item[0])
                    keyboard_row.append(button)
                keyboard.append(keyboard_row)
            total = len(result)
            keyboard.append([telebot.types.InlineKeyboardButton('❎结束搜索', callback_data='close')])
            reply_markup = telebot.types.InlineKeyboardMarkup(keyboard)
            bot.reply_to(message, f'卧槽，天降订阅！！！👮‍♂️发现了{str(total)}条订阅！！！快点击查看⏬', reply_markup=reply_markup)
        else:
            bot.reply_to(message, '😅没有查找到结果！')
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😵😵您输入的内容有误，请检查后重新输入")


# 更新数据
def update_sub(message, **kwargs):
    c = kwargs.get('cursor', None)
    bot = kwargs.get('bot', None)
    conn = kwargs.get('conn', None)
    try:
        row_num = message.text.split()[1]
        url_comment = message.text.split()[2:]
        url = url_comment[0]
        comment = url_comment[1]
        c.execute("UPDATE My_sub SET URL=?, comment=? WHERE rowid=?", (url, comment, row_num))
        conn.commit()
        bot.reply_to(message, "✅更新成功！")
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😵😵输入格式有误，请检查后重新输入")


# 使用帮助
def help_sub(message, **kwargs):
    bot = kwargs.get('bot', None)
    doc = '''
    时间有限暂未做太多异常处理，请遵循使用说明的格式规则，否则程序可能出错,如果出现异常情况，联系bot的主人处理
🌈使用说明：
    1. 添加数据：/add url 备注
    2. 删除数据：/del 行数
    3. 查找数据：/search 内容
    4. 修改数据：/update 行数 订阅链接 备注
    5. 导入xlsx表格：发送xlsx表格（注意文件格式！A列为订阅地址，B列为对应的备注）
    '''
    bot.send_message(message.chat.id, doc)
