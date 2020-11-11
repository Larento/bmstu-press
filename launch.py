import json
import argparse
from getBookInfo import getBookInfo
from createPDF import createPDF

dbPath = "booksInfo.json"
loginFile = open("login.json")
user = json.load(loginFile)
loginFile.close()

parser = argparse.ArgumentParser(description='Script so useful.')
parser.add_argument("-b", action="store", dest="bookID", type=int, required=True)
parser.add_argument("-s", action="store", dest="startPage", type=int, default=1)
parser.add_argument("-e", action="store", dest="endPage", type=int, default=argparse.SUPPRESS)
args = parser.parse_args()

if (args.bookID <= 0) or (args.bookID > 9999):
  args.bookID = 6846

bookInfo = getBookInfo(args.bookID, user["login"], user["password"], dbPath)

if (not ("endPage" in args)) or (args.endPage > bookInfo["Pages"]) or (args.endPage <= 0):
  args.endPage = bookInfo["Pages"]

if (args.startPage >= args.endPage) or (args.startPage <= 0):
  args.startPage = 1

print(f"\n{bookInfo['Title']}, {bookInfo['Pages']} pages\n")
createPDF(bookInfo, args.startPage, args.endPage)