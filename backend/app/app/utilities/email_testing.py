import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Данные для SMTP Mail.ru
SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 465  # Используем SSL
SMTP_USER = "ridgeside@mail.ru"  # Замени на свою почту
SMTP_PASSWORD = "4sRjByhbdWRsaKz291pW"  # Замени на пароль приложения

# Данные письма
recipient_email = "egordr0433@gmail.com"  # Кому отправляем
subject = "Тест"  # Тема письма
body = """
<h3>Привет!</h3>
<p>Это тестовое письмо, отправленное через SMTP Mail.ru.</p>
"""


def send_email():
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        # Подключаемся к SMTP-серверу с SSL
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipient_email, msg.as_string())

        print("✅ Письмо успешно отправлено!")

    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")


# Отправляем тестовое письмо
send_email()