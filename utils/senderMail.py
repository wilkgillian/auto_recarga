import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

fromaddr = os.environ['FROM_EMAIL_ADDRESS']
toaddr = os.environ['TO_EMAIL_ADDRESS']
ccaddr = os.environ['CC_EMAIL_ADDRESS']


async def send_mail(date, directory):
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ccaddr
    msg['Cc'] = ccaddr
    msg['Subject'] = "🤖 SENAC BOT [AUTO RECARGA]"
    body = "Olá, solicitação de recargas concluídas. Segue em anexo o boleto."
    msg.attach(MIMEText(body, 'plain'))
    filename = "boleto"+date+".png"
    attachment = open(
        directory, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', 'attachment; filename= %s' % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.office365.com', 587)
    s.starttls()
    s.login(fromaddr, os.environ['PASSWORD_EMAIL'])
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()


pass
