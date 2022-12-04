from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import random
from time import sleep

url = "https://watchbase.com/patek-philippe/twenty-4"
headers = {
    'Authority': 'watchbase.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
        AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/105.0.0.0 Safari/537.36'
}
dataf = pd.DataFrame()
start = 0

str_split = url.split('/', 4)
brand = str_split[3]
family = str_split[4]

def watch_ids(url, headers):
    cat_page = requests.get(url + '?sort=ref', headers = headers)
    doc = BeautifulSoup(cat_page.text, "html.parser")
    tags = doc.find_all("strong")
    strongs = [tag.get_text() for tag in tags]
    print(strongs)
    ids = [strong.replace('.','-').replace(' ','-').replace('/','-') for strong in strongs]
    array_ids = np.array(ids)
    print(array_ids)
    return array_ids

def get_page_html(array_ids):
    flag = 404
    while flag == 404:
        watch_page = requests.get(url + '/' + str(array_ids),headers=headers,timeout=2)
        flag = watch_page.status_code 
    soup = BeautifulSoup(watch_page.text, "html.parser")
    table_html = soup.find_all("table",{"class":"info-table"})
    return table_html

def watch_data(table_html):
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

def get_prices(id):
    id = id.replace(".", "-")
    flag = 404
    while flag == 404:
        raw_data = requests.get(url + '/' + id + "/prices",headers=headers,timeout=2)
        flag = raw_data.status_code
    object = raw_data.json()
    #print(len(object['labels']))
    if len(object['labels']) != 0:
        data = object["datasets"][0]["data"]
        pricelist = list(filter(lambda item: item is not None, data))
        prices = (pricelist[0],pricelist[-1])
    else:
        prices = (None, None)
    flag=0
    return(prices, flag)

def create_dataframe(ids,dataf):
    length = len(ids)
    count = 0
    while count !=length:
        sleep(random.uniform(1,3))
        table = get_page_html(ids[count])
        raw = watch_data(table)
        watch = raw.loc[:,~raw.columns.duplicated()]
        #print(watch)
        #prices, flag = get_prices(ids[count])
        #watch['Initial'] = prices[0]
        #watch['Current'] = prices[1]
        dataf = pd.concat([watch,dataf])
        count+=1
        print(f"\r{count}/{length}",end="")
    return(dataf)

ids = watch_ids(url, headers)
df1 = create_dataframe(ids,dataf)
with pd.ExcelWriter("{}.xlsx".format(brand), engine='openpyxl', mode='a') as writer:
    df1.to_excel(writer,sheet_name = family, index=False,merge_cells=False) 
 