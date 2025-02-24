__author__ = 'Ashley'
__email__ = 'ddclare126@163.com'

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib


class emailSender:
    def __init__(self, smtp_server, smtp_port, sender, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port  # 通常为587
        self.sender = sender
        self.password = password

    def send_email(self, sender, receivers: list, subject: str, body: str):
        '''
        :param sender: 发送账号，需开通SMTP服务
        :param receivers: 接受邮件的账号
        :param subject: 邮件主题
        :return: 0
        '''

        message = MIMEMultipart()
        message['From'] = self.sender
        message['To'] = receivers
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain', 'utf-8'))    # 添加正文

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()   # 内容加密
            server.login(self.sender, self.password)
            server.sendmail(self.sender, receivers, message.as_string())
            print('邮件成功发送！')
            server.quit()
            return True
        except Exception as e:
            print(f'发送失败: {e}')
            return 0

