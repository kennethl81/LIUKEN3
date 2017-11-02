#Kenneth Liu, 11/1/17

import requests
import urllib.request
import urllib.error
import unittest
import sys
import io
import re
import logging
import pdfminer

from bs4 import BeautifulSoup
from time import sleep
from nltk.tokenize import word_tokenize

#libs to scrape PDF
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

#prevents the warnings from flooding the console from pdfminer from improperly formatted PDFs
logging.propagate = False
logging.getLogger().setLevel(logging.ERROR)

class TestingMethods(unittest.TestCase):

    #test ability to get a completed url request
    def test_response(self):
        url = 'http://ir.expediainc.com/'
        response = requests.get(url, stream=True)
        testResponse = 0
        if response.status_code is not None:
            testResponse = response.status_code
        
        self.assertEqual(testResponse, 200)

    #tests the ability to count the number of words matching 'travel'
    def test_wordCount(self):
        input = ["travel", "travelled", "test", "hello", "travel"]
        count = countNumberofWords(input)

        self.assertEqual(count, 2)


#main method to initialize the script
def main(argv):
    print("Trying to get list of PDF urls")
    pdfLinks = getListOfPDFUrls()

    #with the resolved URLs, we parse them for content
    for index in range(len(pdfLinks)):
        tokenizedPDF = parsePDFByURLandTokenize_PDFMiner(pdfLinks[index])
        count = countNumberofWords(tokenizedPDF)
        print("Number of times 'travel' appeared in " + getFileName(pdfLinks[index]) + ": " + str(count))

    print("Execution complete!")


#counts the number of times a tokenized PDF collection contains the word to match
def countNumberofWords(tokens):
    count = 0
    for index in range(len(tokens)):

            #need a function to determine if any other words that contain travel is there
            #if tokens[index] == "travel":
                #count += 1
                #print(tokens[index])
            regex = re.compile(r"\btravel\b") #look for this exact word. if the word is a part partly hyphenated or plural, it will not match
            match = re.findall(regex, tokens[index])
            if len(match) > 0:
                count += len(match)
    return count


#retrieves a list of PDF URLs from the Expedia IR site
def getListOfPDFUrls():
    baseURL = 'http://ir.expediainc.com'
    url = 'http://ir.expediainc.com/annuals.cfm'
    #response = requests.get(url, stream=True)

    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')

    urlList = [];
    for link in soup.find_all('a', attrs={'class' : 'docList'}):
        #there are two links per PDF doc, one with an image tag as a child and one without
        #we try and get the one without.  no children == 1, one child == 2
        if len(list(link.descendants)) == 1:
            urlList.append(baseURL + link['href'])

    if len(urlList) == 0:
        print("No PDF URLs were found")
        return None

    print("Attempting to resolve final URLs of each document link. This will take a while as there are a couple of redirects to other pages to get each document. Please wait...")
    #get final urls after redirects
    for index in range(len(urlList)):
        urlList[index] = getFinalURL(urlList[index])

    print("Done resolving final URLs")

    return urlList


#due to redirects when trying to access the PDFs
#we have to use a function to get the final url
def getFinalURL(url):
    response = requests.get(url, stream=True)
    if response.history:
        for resp in response.history:
            if response.status_code == 200:
                print("PDF link resolved to = " + response.url)
                return response.url
            sleep(2) #sleep so we don't overload the server with requests
    else:
        print("Request was not redirected")


#returns the file name from a given URL
#returns an empty string when no file name is found (likely to happen if URL format is invalid)
def getFileName(url):
    if len(url) > 0:
        indexOfLastSlash = url.rfind('/') + 1
        return url[indexOfLastSlash:len(url)]

    return ""


#uses a URL to retrieve a PDF file and scrapes it for data
def parsePDFByURLandTokenize_PDFMiner(url):
    file = urllib.request.urlopen(url).read()

    if file is not None:

        memory = io.BytesIO(file)
        parser = PDFParser(memory)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
        laparams = pdfminer.layout.LAParams()

        #sets the layout analyzer params so we can extract the text with whitespaces
        for param in ("all_texts", "detect_vertical", "word_margin", "char_margin", "line_margin", "boxes_flow"):
            paramv = locals().get(param, None)
            if paramv is not None:
                setattr(laparams, param, paramv)

        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        extracted_text = ''

        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    extracted_text += lt_obj.get_text()

        return word_tokenize(extracted_text)

    return None


#uncomment below to run tests in TestMethods class
#if __name__ == '__main__':
    #unittest.main()

if __name__ == "__main__":
    main(sys.argv)