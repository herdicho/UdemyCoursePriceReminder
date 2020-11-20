import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
      driver.execute_script("arguments[0].scrollIntoView();", element)
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
   "LoginButtonLoginPage" : "submit-id-submit",
   "CourseSearchField" : "//input[@placeholder='Search for anything']",
}

data = {
   "Course" : "Go: The Complete Developer's Guide (Golang)",
   "MaxPrice" : 150000,
   "CoursePrice" : 0, # next will be overwritten with the course price
}

def sendEmail():
   msg = MIMEMultipart()
   msg['From'] = credential.get("EmailSender")
   msg['To'] = credential.get("EmailReceiver")
   msg['Subject'] = "UDEMY COURSE PRICE REMINDER"
 
   body = '''\
   Course "''' + data.get("Course") + '''" Regone : ''' + data.get("CoursePrice") + '''
   '''

   '''
   for key in credential:
      body = key + " : " + credential[key] + "\n"
      msg.attach(MIMEText(body, 'plain'))
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


def getUdemyCoursePrice():
   # open udemy webpage
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

   # search course
   courseSearchFieldElement = getElement(By.XPATH, element.get("CourseSearchField"), 10)
   courseSearchFieldElement.send_keys(data.get("Course"))
   courseSearchFieldElement.send_keys(Keys.RETURN)

   time.sleep(3)

   # search for first top 15 course according to the desired course and get course price then send email if price less than desired price
   for i in range (1, 15):
      try:
         title = getElement(By.XPATH, "/html/body/div[2]/div[3]/div/div/div[2]/div[1]/div[2]/div/div[2]/div[2]/div["+str(i)+"]/a/div/div[2]/div[1]", 5).text
         if (title == data.get("Course")):
            price = getElement(By.XPATH, "/html/body/div[2]/div[3]/div/div/div[2]/div[1]/div[2]/div/div[2]/div[2]/div["+str(i)+"]/a/div/div[2]/div[5]/div[1]/span[2]/span", 5).text
            priceInteger = int(price.replace("Rp", "").replace(",", ""))
            if (priceInteger < data.get("MaxPrice")):
               data["CoursePrice"] = price
               sendEmail()
            break
      except:
         continue
   
   driver.close()

#initiate browser for automation
driver = webdriver.Chrome()
getUdemyCoursePrice()

