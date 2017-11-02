LIUKEN3
Coding Challenge #3

Installation
===================================================
This script was built using python v3.6.3

This script relies on the following additional modules installed via pip3:
    requests
    urllib
    pdfminer
    BeautifulSoup
    nltk
    

How to Use
===================================================
Script should be run in a python compatible IDE or other runtime

The script has been packaged with pyInstaller


About the Script
===================================================
The script works by making a request to http://ir.expediainc.com/annuals.cfm
and scraping the PDF links using the BeautifulSoup library. I target the anchor
tags with no descendents (because there are two links for each PDF and are duplicates).

After logging the PDF links, I noticed that when the links are clicked, there is actually a redirect to another website (shareholder.com) domain. This is where the PDFs reside.
My script determines the final redirect URL and uses it to download the PDF and parse through it collect the text data. I use pdfminer to extract the data and nltk to parse and tokenize the data. 

The last step in the process is to count the occurances of the word 'travel' in the documents. I use a regex function to find exact matches to the word 'travel' as per the specifications of the problem statement. Words hyphenated with travel or plural words are ignored in the final count.