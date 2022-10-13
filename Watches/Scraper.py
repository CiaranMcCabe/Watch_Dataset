from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

url = "https://watchbase.com/omega/speedmaster/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
        AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/105.0.0.0 Safari/537.36'
}
dataf = pd.DataFrame()
start = 0

def watch_ids(url, headers):
    cat_page = requests.get(url, headers = headers)
    doc = BeautifulSoup(cat_page.text, "html.parser")
    tags = doc.find_all("strong")
    strongs = [tag.get_text() for tag in tags]
    ids = [strong.replace('.','-').replace(' ','-') for strong in strongs]
    array_ids = np.array(ids)
    #print(array_ids)
    return array_ids

def get_watch_page(array_ids):
    watch_page = requests.get(url + str(array_ids),headers = headers)
    Soup = BeautifulSoup(watch_page.text, "html.parser")
    table_html = Soup.find_all('table',{'class':"info-table"})
    return table_html

def headers_values(table_html):
    row_values = []
    for values in table_html:
        for value in values.find_all('td'):
            value = (value.text).replace("\n"," ")
            row_values.append(value)
    
    row_headers = []
    for headers in table_html:
        for header in headers.find_all('th'):
            row_headers.append(header.text)

    watchdf = pd.DataFrame([row_values],columns=row_headers)
    return(watchdf)
    

ids = watch_ids(url, headers)
for i in range(3):
    id = ids[i]
    table = get_watch_page(id)
    watch = headers_values(table)
    dataf = pd.concat([watch,dataf])
print(dataf)
dataf.to_csv('out.csv',index=False)