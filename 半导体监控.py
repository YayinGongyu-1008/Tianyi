import time
import pandas as pd
import smtplib
import chinese_calendar as cc  # 引入中国节假日库
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os

# ================== 配置信息 ==================
CONFIG = {
    'stock_code': '881121',  # 半导体指数的同花顺代码
    'interval': 300,          # 监控间隔 (秒), 300秒 = 5分钟

    # 邮箱配置（请务必替换成你的真实信息）
    'smtp_server': 'smtp.qq.com',      # SMTP服务器地址
    'smtp_port': 465,                  # SSL端口
    'sender_email': '2707318267@qq.com',   # 你的邮箱
    'sender_password': 'cnmbniikkpbbddjc',     # 你的邮箱授权码或密码
    'receiver_email': '2707318267@qq.com', # 收件人邮箱
}

# ================== 核心功能函数 ==================
def is_trading_day():
    """判断今天是否为A股交易日，支持法定节假日"""
    today = datetime.now().date()
    # chinese_calendar.is_workday 会判断当天是否为工作日（包括补班）
    # 但A股在周末必然休市，即使补班也不开市。
    # 所以最终条件必须是：是工作日 并且 不是周六或周日。
    is_workday = cc.is_workday(today)
    is_weekend = today.weekday() >= 5  # Monday=0, Sunday=6
    return is_workday and not is_weekend

def is_trading_time():
    """判断当前时间是否在交易时段内 (9:30-11:30, 13:00-15:00)"""
    now = datetime.now()
    current_time = now.time()
    morning_start = datetime.strptime('09:30', '%H:%M').time()
    morning_end = datetime.strptime('11:30', '%H:%M').time()
    afternoon_start = datetime.strptime('13:00', '%H:%M').time()
    afternoon_end = datetime.strptime('15:00', '%H:%M').time()

    return (morning_start <= current_time <= morning_end) or (afternoon_start <= current_time <= afternoon_end)

def fetch_index_data(stock_code):
    """获取同花顺半导体指数成份股数据"""
    import akshare as ak
    try:
        # 使用 AKShare 获取同花顺板块成份股
        df = ak.stock_board_cons_ths(symbol=stock_code)
        if df.empty:
            return None
        # 添加数据获取时间戳
        df['数据时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return df
    except Exception as e:
        print(f"数据获取失败: {e}")
        return None

def send_email_with_excel(data, config):
    """发送带Excel附件的邮件"""
    if data is None or data.empty:
        print("没有数据，邮件未发送。")
        return
    filename = f"半导体指数_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    data.to_excel(filename, index=False)
    msg = MIMEMultipart()
    msg['From'] = config['sender_email']
    msg['To'] = config['receiver_email']
    msg['Subject'] = f"半导体指数成份股数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    msg.attach(MIMEText("请查收附件中的半导体指数成份股数据。", 'plain', 'utf-8'))
    with open(filename, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {filename}')
        msg.attach(part)
    try:
        with smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port']) as server:
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)
        print(f"邮件已发送至 {config['receiver_email']}")
    except Exception as e:
        print(f"邮件发送失败: {e}")
    if os.path.exists(filename):
        os.remove(filename)

# ================== 主循环 ==================
def main():
    print("监控脚本已启动...")
    while True:
        if not is_trading_day():
            print(f"{datetime.now()} 非交易日，休眠一小时后重试。")
            time.sleep(3600)
            continue
        if not is_trading_time():
            print(f"{datetime.now()} 非交易时间，休眠五分钟。")
            time.sleep(CONFIG['interval'])
            continue
        print(f"{datetime.now()} 获取数据...")
        data = fetch_index_data(CONFIG['stock_code'])
        if data is not None:
            send_email_with_excel(data, CONFIG)
        else:
            print("获取数据失败，本次跳过。")
        time.sleep(CONFIG['interval'])

if __name__ == "__main__":
    main()
