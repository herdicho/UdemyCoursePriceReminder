import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Credentials
sender = "reminderemail09@gmail.com"
senderPass = "reminder09*"
receiver = "reminderemail09@gmail.com"

msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = receiver
msg['Subject'] = "JUDUL PESAN"
 
body = '''\
ISI PESAN

Mantapp
'''

msg.attach(MIMEText(body, 'plain'))
text = msg.as_string()

print("Try to send email")
try:
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login(sender, senderPass)
   server.sendmail(sender, receiver, text)
   server.quit()
   print("Success send email")
except:
   print("Fail send email")
