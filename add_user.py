import json
import uuid
import os
import logging
from datetime import date
import time
import subprocess
import qrcode

from telegram import Update, Bot, constants
from telegram.ext import ApplicationBuilder, ContextTypes, filters, MessageHandler

domain = "tj.itenshi.tk"
port = "443"
json_path = "/root/tj/data.json"
log_path = "/etc/logs/trojan-gfw/logs.log"
BOT_TOKEN = "5974659972:AAFVivpN6ijHQjvfLl1dFIrTUBCZABOv7cg"
data_channel = "-1001668299060"

owner = 1255875612
admins = [1255875612]

bot = Bot(token=BOT_TOKEN)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_json_data(path):
    data_dict = dict()
    with open(path,'r') as _json_file_:
        data_dict = json.load(_json_file_)
    return data_dict

def write_json_data(path,data):
    with open(path, "w") as outfile:
        json.dump(data, outfile)
    return True
    
async def add_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _td = update.message.text.replace("$add ","")  #add {name} {ip limit (default 1)} {duration of the vpn month (default 1)}
    _td = _td.split()

    if len(_td) == 0:
        await update.message.reply_html("Command is not valid")
        return False

    if len(_td) == 1:
        name = _td[0]
        user_limit = 1
        duration = 1
    elif len(_td) == 3:
        name = _td[0]
        user_limit = _td[1]
        duration = 1
    elif len(_td) == 3:
        name = _td[0]
        user_limit = _td[1]
        duration = _td[2]

    today = date.today()
    d = today.strftime("%b-%d-%Y")
    _password_ = str(uuid.uuid4())
    
    json_dict = get_json_data(json_path)
    json_dict[_password_] = {
        "name":name,
        "user_limit":user_limit,
        "duration":duration,
        "today":d,
        "exp":time.time()+(duration*30*24*60*60)
        }
    write_json_data(json_path,json_dict)

    subprocess.run(['trojan-go', '-api-addr', '127.0.0.1:10000', '-api', 'set', '-add-profile', '-target-password', _password_])
    subprocess.run(['trojan-go', '-api-addr', '127.0.0.1:10000', '-api', 'set', '-modify-profile', '-target-password', _password_, '-ip-limit', user_limit])

    link = f'trojan://{_password_}@{domain}:{port}#{name}'
    data_text = f"name: {name}\npassword: <code>{_password_}</code>\nDate: {d}\nDuration: {duration} month\nLimit user: {user_limit}"
    await update.message.reply_html(link)
    await update.message.reply_html(data_text)
    await bot.send_message(chat_id=data_channel,text=data_text,parse_mode=constants.ParseMode.HTML)
    qrcode.make(link).save('/root/tj/qrcode.png')
    await bot.send_photo(chat_id=update.message.chat.id,photo=open("/root/tj/qrcode.png","rb"))
    os.remove('/root/tj/qrcode.png')

async def renew_log_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot.send_document(chat_id=data_channel,document=open(log_path,"rb"))
    subprocess.run(['truncate', '-s', '0', log_path])

async def del_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _password = update.message.text.replace("$del ","")
    subprocess.run(['trojan-go', '-api-addr', '127.0.0.1:10000', '-api', 'set', '-delete-profile', '-target-password', _password])
    data_dict = get_json_data(json_path)
    del data_dict[_password]
    write_json_data(json_path,data_dict)
    await update.message.reply_html("Done")

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.User(user_id=owner) & ~filters.UpdateType.EDITED_MESSAGE & filters.Regex("^\$add "),add_profile))
    application.add_handler(MessageHandler(filters.User(user_id=owner) & ~filters.UpdateType.EDITED_MESSAGE & filters.Regex("^\$del "),del_profile))
    application.add_handler(MessageHandler(filters.User(user_id=owner) & ~filters.UpdateType.EDITED_MESSAGE & filters.Regex("^\$log"),renew_log_file))
    application.run_polling()

if __name__ == "__main__":
    main()
