import urllib.parse
import urllib.request
import os
import shutil
from PIL import Image
import img2pdf

def createPDF(bookInfo, startPage, endPage):

  def directoryPath():
    return f"{bookInfo['Title']}"

  def filePath(i):
    return directoryPath() + f"/{i}.{bookInfo['Image Format']}"

  def makeDirectory(name):
    print("Creating directory...")
    try:
      currentPath = os.getcwd()
      os.mkdir(f"{currentPath}/{name}")
      print("Created directory.")
    except:
      print("Directory is already present.")

  def showProgress(blockNum, blockSize, totalSize):
    percent = blockNum * blockSize / totalSize
    ending = " "
    if percent > 1:
      percent = 1
      ending = "\n"
    print("{:.0%}".format(percent), end=ending)

  def downloadPage(i, key):
    URL = bookInfo["Key"] + str(key) + "." + bookInfo["Image Format"]
    # print(f"Downloading page #{i+1} from: " + URL + "\n")
    print(f"Downloading page #{i+1}...")
    tries = 0
    maxTries = 10
    while tries < maxTries:
      try:
        # print(" Connection attempt #" + str(tries + 1))
        urllib.request.urlretrieve(urllib.parse.quote(URL).replace("%3A", ":"), filePath(i + 1))
        break
      except:
        tries += 1

  def makeBlankPageBackground(i):
    path = filePath(i + 1)
    page = Image.open(path).convert('RGBA')
    background = Image.new('RGBA', page.size, (255,255,255))
    alphaComposite = Image.alpha_composite(background, page)
    alphaComposite.convert('RGB').save(path, "PNG")

  def manipulatePages():
    print("Beginning to download all pages...\n")
    for i in range(startPage - 1, endPage):
      if i == 0:
        k = ''
      else:
        k = i
      downloadPage(i, k)
      makeBlankPageBackground(i)
    print("")

  def makePDF():
    print("Making PDF File...")
    makeDirectory("Books")
    PDFPath = f"Books/{bookInfo['Title']}.pdf"
    with open(PDFPath, "wb") as PDFFile:
      pages = []
      for i in range(startPage - 1, endPage):
        pages.append(filePath(i + 1))
      PDFFile.write(img2pdf.convert(pages))

  makeDirectory(bookInfo['Title'])
  manipulatePages()
  makePDF()
  print("Finished! Your book is in the 'Books' folder")
  shutil.rmtree(directoryPath(), ignore_errors=True)
  
