from fhe_chatbot.classes.Singleton import Singleton
import smtplib
import traceback
from django.conf import settings

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService(metaclass=Singleton):
    def send_email(self, question, reply_to):
        msg = MIMEMultipart()
        msg['To'] = settings.MAIL_SETTINGS['recipient']
        msg['From'] = settings.MAIL_SETTINGS['sender']
        msg['Subject'] = "Anfrage von Studienintessierte"
        msg['Reply-To'] = reply_to
        msg.attach(MIMEText(question, 'plain'))
        try:
            server = smtplib.SMTP(settings.MAIL_SETTINGS['server'], settings.MAIL_SETTINGS['port'])
            server.ehlo()
            server.starttls()
            server.login(settings.MAIL_SETTINGS['username'], settings.MAIL_SETTINGS['password'])
            server.sendmail(settings.MAIL_SETTINGS['sender'], settings.MAIL_SETTINGS['recipient'], msg.as_string())
            return True
        except Exception:
            traceback.print_exc()
            return False
