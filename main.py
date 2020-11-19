import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def readCredentials():
    emailUdemy = passwordUdemy = ""
    with open("credentials.txt", "r") as f:
        file = f.readlines()
        emailUdemy = file[0].strip()
        passwordUdemy = file[1].strip()
        emailSender = file[2].strip()
        passwordSender = file[3].strip()
        emailReceiver = file[4].strip()

    return emailUdemy, passwordUdemy, emailSender, passwordSender, emailReceiver

def getElement(selector, elementSelector, waitTime):
   try:
      element = WebDriverWait(driver, waitTime).until(
         EC.presence_of_element_located((selector, elementSelector))
      )
   finally:
      return element

emailUdemy, passwordUdemy, emailSender, passwordSender, emailReceiver = readCredentials()

credential = {
   "EmailUdemy"   : emailUdemy,
   "PasswordUdemy" : passwordUdemy,
   "EmailSender" : emailSender, 
   "PasswordSender" : passwordSender,
   "EmailReceiver" : emailReceiver,
}

element = {
   "LoginButtonHomePage" : "/html/body/div[1]/div[1]/div[2]/div[5]",
   "EmailField" : "email--1",
   "PasswordField" : "id_password",
   "LoginButtonLoginPage" : "submit-id-submit"
}

# initiate browser & open udemy webpage
driver = webdriver.Chrome()
driver.get("http://udemy.com")

# login
loginButtonHomePageElement = getElement(By.XPATH, element.get("LoginButtonHomePage"), 10)
loginButtonHomePageElement.click()
emailFieldElement = getElement(By.ID, element.get("EmailField"), 10)
emailFieldElement.send_keys(credential.get("EmailUdemy"))
passwordFieldElement = getElement(By.ID, element.get("PasswordField"), 10)
passwordFieldElement.send_keys(credential.get("PasswordUdemy"))
loginButtonLoginPageElement = getElement(By.ID, element.get("LoginButtonLoginPage"), 10)
loginButtonLoginPageElement.click()

driver.close()

msg = MIMEMultipart()
msg['From'] = credential.get("EmailSender")
msg['To'] = credential.get("EmailReceiver")
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
   server.login(credential.get("EmailSender"), credential.get("PasswordSender"))
   server.sendmail(credential.get("EmailSender"), credential.get("EmailReceiver"), text)
   server.quit()
   print("Success send email")
except:
   print("Fail send email")
