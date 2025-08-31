import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from io import BytesIO
from typing import List
import pandas as pd
from datetime import datetime


def send_dataframe_email(sender: str, password: str, to_addrs: List[str], subject: str,
                         dataframes: List[pd.DataFrame], max_table_width: int = 800):
    """
    发送 DataFrame 邮件：
    - 邮件正文显示 HTML 表格（自适应列宽，最大宽度 max_table_width）
    - 每个 DataFrame 生成 Excel 附件，文件名带时间戳
    """
    html_content = ""
    attachments = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for idx, df in enumerate(dataframes):
        # HTML 表格
        html_table = df.to_html(index=False, border=0, justify="center", escape=False)
        html_table = html_table.replace(
            "<table",
            f'<table style="border-collapse:collapse; border-spacing:0; '
            f'table-layout:auto; width:auto; max-width:{max_table_width}px; margin:0 auto;"'
        ).replace(
            "<th>",
            '<th style="border:1px solid black; padding:4px; margin:0; '
            'word-wrap:break-word; white-space:normal;">'
        ).replace(
            "<td>",
            '<td style="border:1px solid black; padding:4px; margin:0; '
            'word-wrap:break-word; white-space:normal; max-width:200px;">'
        )

        html_content += f"<h2>数据表 {idx + 1}</h2>{html_table}<br>"

        # Excel 附件
        buf_excel = BytesIO()
        df.to_excel(buf_excel, index=False)
        buf_excel.seek(0)
        filename = f"data_{idx + 1}_{timestamp}.xlsx"
        part_excel = MIMEApplication(buf_excel.read(), _subtype='xlsx')
        part_excel.add_header('Content-Disposition', 'attachment', filename=filename)
        attachments.append(part_excel)

    # 构造邮件
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(to_addrs)

    # HTML 正文
    msg.attach(MIMEText(f"<html><body>{html_content}</body></html>", "html", "utf-8"))

    # 添加 Excel 附件
    for att in attachments:
        msg.attach(att)

    # 发送邮件
    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(sender, password)
            server.sendmail(from_addr=sender, to_addrs=to_addrs, msg=msg.as_string())
            try:
                server.quit()
            except smtplib.SMTPResponseException as e:
                print("⚠️ QUIT 异常，但邮件已发送：", e)
        print("📧 邮件已发送成功 ✅")
    except smtplib.SMTPException as e:
        print("❌ 邮件发送失败：", e)


# ================= 使用示例 =================
if __name__ == "__main__":
    df1 = pd.DataFrame(
        {"姓名": ["张三", "李四"],
         "年龄": [25, 30],
         'diff': [{'aa'}, {'bb'}]
         })
    df2 = pd.DataFrame({"城市": ["北京", "上海"], "人口": [2154, 2415]})

    send_dataframe_email(
        sender="matt17@qq.com",
        password="cxruxjqaetkoeiid",
        to_addrs=["dumingxuancn@163.com"],
        subject="自适应表格 + Excel 附件示例",
        dataframes=[df1, df2],
        max_table_width=800  # 可根据需要调整最大宽度
    )
