import re
import time
import logging
import sys
import urllib.parse as urlparse
from tinydb import TinyDB, Query
sys.tracebacklimit=0
logging.basicConfig(level=logging.CRITICAL)

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def writeDB(ID, title, pagesCount, imgRequestKey, imgFormat, db):
  db.insert({
    "ID": ID,
    "Title": title,
    "Pages": pagesCount,
    "Key": imgRequestKey,
    "Image Format": imgFormat
  })

def readDB(ID, db):
  book = Query()
  result = db.search(book.ID == ID)
  if len(result) == 0:
    return False
  return result[0]

def getBookInfo(bookID, userLogin, userPassword, dbPath):
  def login(login, password):
    loginButton = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".login")))
    loginButton.click()
    completeForm(login, password)
    print("Login successful!")

  def completeForm(login, password):
    form = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form")))
    loginField = form.find_element_by_css_selector("input[name='login']")
    passwordField = form.find_element_by_css_selector("input[name='password']")
    loginField.send_keys(login)
    passwordField.send_keys(password)
    time.sleep(0.5)
    submit = form.find_element_by_css_selector("button[type='submit']")
    submit.click()

  def getNumberOfPages():
    pagesProperty = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@data-state-content='online']" + "//ul" + "/li[text()[contains(., 'стр')]]")))
    pagesCountString = pagesProperty.get_attribute('textContent')
    return list(map(int, re.findall(r'\d+', pagesCountString)))[0]

  def getBookTitle():
    title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-title h1")))
    return title.get_attribute('textContent').rstrip()

  def openReader():
    URL = driver.current_url
    driver.get(URL + "/reader")
    print("Opened reader.")

  def findRequestKey():
    for request in driver.requests:
      if request.response:
        link = urlparse.unquote(request.url)
        if (("image" in request.response.headers['Content-Type']) and ("OEBPS" in link)):
          splitLink = link.rsplit(".", 1)
          return splitLink[0], splitLink[1]
    return False

  rootURL = "https://bmstu.press"
  homeURL = rootURL + "/catalog/item/" + str(bookID).zfill(4)
  db = TinyDB(dbPath)

  if readDB(bookID, db) != False:
    print("Book found in database. No need to connect to server.")
  else:
    print("Book not found in database. Connecting to server...")
    try:
      swireOptions = {
      'suppress_connection_errors': True,
      'connection_timeout': 50,
      }
      selOptions = Options()
      selOptions.headless = True
      selOptions.capabilities["pageLoadStartegy"] = "eager"

      driver = webdriver.Firefox(options=selOptions, seleniumwire_options=swireOptions) # pylint: disable=unexpected-keyword-arg
      driver.get(homeURL)
      print("Connected to server.")
      login(userLogin, userPassword)
      endPage = getNumberOfPages()
      title = getBookTitle()
      openReader()
      time.sleep(10)
      if findRequestKey() == False:
        raise ValueError("Did not find the right request.")
      key, imgFormat = findRequestKey()
      writeDB(bookID, title, endPage, key, imgFormat, db)
    except:
      print("Could not receive response from server or this book ID might not exist. Please try again or change ID.")
    finally:
      driver.close()
      driver.quit()
  return readDB(bookID, db)