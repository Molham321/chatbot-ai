from fhe_chatbot.classes.Singleton import Singleton
import smtplib
import traceback
from django.conf import settings
from chatbot_logic.models import ChatMessage, Chat, EmailSupport

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.template.loader import render_to_string


class EmailService(metaclass=Singleton):
    def send_email(self, chat_session, reply_to):
        self.create_email_support(chat_session, reply_to)

        msg = MIMEMultipart()
        msg['To'] = settings.MAIL_SETTINGS['recipient']
        msg['From'] = settings.MAIL_SETTINGS['sender']
        msg['Subject'] = "Neue Anfrage über Chatbot von Gast"
        msg['Reply-To'] = reply_to

        chat = Chat.objects.filter(chat_session_id=chat_session.id).first()
        messages = ChatMessage.objects.filter(chat_id=chat.id).all()

        content = render_to_string("email_template.html", {
            "session": chat_session,
            "chat": chat,
            "messages": messages,
            "reply_to": reply_to
        })

        msg.attach(MIMEText(content, 'html'))
        try:
            server = smtplib.SMTP(settings.MAIL_SETTINGS['server'], settings.MAIL_SETTINGS['port'])
            server.ehlo()
            server.starttls()
            server.login(settings.MAIL_SETTINGS['username'], settings.MAIL_SETTINGS['password'])
            server.sendmail(settings.MAIL_SETTINGS['sender'], settings.MAIL_SETTINGS['recipient'], msg.as_string())

            print("Mail sent")

            return True
        except Exception:
            traceback.print_exc()
            return False

    def create_email_support(self, chat_session, email):
        email_support = EmailSupport()

        email_support.email = email
        email_support.chat_session = chat_session

        email_support.save()