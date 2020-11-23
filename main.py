import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

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
   "LoginButtonHomePage" : "//a[@data-purpose='header-login']",
   "EmailField" : "//input[@name='email'][@type='email']",
   "PasswordField" : "//input[@name='password'][@type='password']",
   "LoginButtonLoginPage" : "/html/body/div[1]/div[2]/div[1]/div[3]/form/div[2]/div/input",
   "CourseSearchField" : "/html/body/div[2]/div[1]/div[3]/div[2]/form/input[2]",
}

data = {
   "Course" : "Go: The Complete Developer's Guide (Golang)",
   "MaxPrice" : 120000,
   "CoursePrice" : 0, # next will be overwritten with the course price
   "CourseLanguage" : "English",
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

def sendErrorEmail(error):
   subjectContent = "(Language Not Found)" if error == "languageNotFound" else "(Course Not Found)"
   bodyContent = "Language Not Found" if error == "languageNotFound" else "Course Not Found"

   msg = MIMEMultipart()
   msg['From'] = credential.get("EmailSender")
   msg['To'] = credential.get("EmailReceiver")
   msg['Subject'] = "UDEMY COURSE PRICE REMINDER ERROR "+ subjectContent + ""
 
   body = '''\
   ''' + bodyContent + '''   
   Please check the name of course or language
   '''

   msg.attach(MIMEText(body, 'plain'))
   text = msg.as_string()

   print("Try to send error email")
   try:
      server = smtplib.SMTP('smtp.gmail.com', 587)
      server.starttls()
      server.login(credential.get("EmailSender"), credential.get("PasswordSender"))
      server.sendmail(credential.get("EmailSender"), credential.get("EmailReceiver"), text)
      server.quit()
      print("Success send error email")
   except:
      print("Fail send error email")

def loginUdemyWebpage():
   loginButtonHomePageElement = getElement(By.XPATH, element.get("LoginButtonHomePage"), 30)
   time.sleep(7)
   driver.save_screenshot('captchagatel.png')
   driver.execute_script("arguments[0].click();", loginButtonHomePageElement)
   driver.save_screenshot('captchafuk.png')
   emailFieldElement = getElement(By.XPATH, element.get("EmailField"), 30)
   emailFieldElement.send_keys(credential.get("EmailUdemy"))
   passwordFieldElement = getElement(By.XPATH, element.get("PasswordField"), 30)
   passwordFieldElement.send_keys(credential.get("PasswordUdemy"))
   loginButtonLoginPageElement = getElement(By.XPATH, element.get("LoginButtonLoginPage"), 30)
   loginButtonLoginPageElement.click()

def searchCourse():
   courseSearchFieldElement = getElement(By.XPATH, element.get("CourseSearchField"), 30)
   courseSearchFieldElement.send_keys(data.get("Course"))
   courseSearchFieldElement.send_keys(Keys.RETURN)
   time.sleep(5)

def filterCourseLanguage():
   isLanguageFound = False

   # filter course by language of the course (if just input course name, sometimes we cant find the desired course)
   showMoreLanguage = driver.find_element_by_xpath("/html/body/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div[1]/form/div/div[2]/div[2]/div/div/button/span/span[1]")
   showMoreLanguage.click()
   listLanguage = driver.find_elements_by_xpath("/html/body/div[2]/div[3]/div/div/div[2]/div[1]/div[2]/div/div[1]/form/div/div[2]/div[2]/div/div/div/div/fieldset/label")
   
   indeks = 0
   langIndeks = -1
   for i in listLanguage:
      if (data.get("CourseLanguage").lower() in i.text.lower()):
         isLanguageFound = True
         langIndeks = indeks
         break

      indeks += 1

   if (isLanguageFound):
      languageFilter = driver.find_element_by_xpath("/html/body/div[2]/div[3]/div/div/div[2]/div[1]/div[2]/div/div[1]/form/div/div[2]/div[2]/div/div/div/div/fieldset/label["+str(langIndeks+1)+"]")
      languageFilter.click()
   else:
      sendErrorEmail("languageNotFound")
      sys.exit()
      
   time.sleep(3)

def getCoursePrice():
   isCourseFound = False
   
   # search for first top 15 course according to the desired course and get course price then send email if price less than desired price
   for i in range (1, 15):
      try:
         title = getElement(By.XPATH, "/html/body/div[2]/div[3]/div/div/div[2]/div[1]/div[2]/div/div[2]/div[2]/div["+str(i)+"]/a/div/div[2]/div[1]", 5).text
         if (title == data.get("Course")):
            isCourseFound = True
            price = getElement(By.XPATH, "/html/body/div[2]/div[3]/div/div/div[2]/div[1]/div[2]/div/div[2]/div[2]/div["+str(i)+"]/a/div/div[2]/div[5]/div[1]/span[2]/span", 5).text
            priceInteger = int(price.replace("Rp", "").replace(".","").replace(",",""))
            if (priceInteger < data.get("MaxPrice")):
               data["CoursePrice"] = price
               sendEmail()
            break
      except:
         continue
   
   if (not isCourseFound):
      sendErrorEmail("courseNotFound")
      sys.exit()

def getUdemyCoursePrice():
   # open udemy webpage
   driver.get("http://udemy.com")
   
   # loginUdemyWebpage() (Dont need login)
   searchCourse()
   filterCourseLanguage()
   getCoursePrice()

   driver.close()

#initiate browser for automation
options = Options()  
options.add_argument("--headless")
options.add_argument("--window-size=1280,800")
driver = webdriver.Chrome(options=options)

getUdemyCoursePrice()

