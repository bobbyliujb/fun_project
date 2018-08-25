#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re, gspread, time
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from oauth2client.service_account import ServiceAccountCredentials

def parseHtml(driver, link_count, MAX_LINK_PER_COMPANY, result):
    soup = BS(driver.page_source, 'html.parser')
    section_main = soup.find(id='threadlisttableid')
    tbody_array = section_main.find_all('tbody', id = re.compile('^normalthread'))

    i = 0
    while i < len(tbody_array):
        if (tbody_array[i].tr.th.em != None 
            and tbody_array[i].tr.th.em.get_text() == "我这里要招人"
            and tbody_array[i].tr.th.span != None
            and tbody_array[i].tr.th.span.span != None):
            span = tbody_array[i].tr.th.span.span
            company_name = span.u.find_all('b')[2].get_text().lower()
            if (company_name not in link_count):
                link_count[company_name] = 0

            if (link_count[company_name] < MAX_LINK_PER_COMPANY):
                link_count[company_name] = link_count[company_name] + 1
                metadata = [company_name]
                a = tbody_array[i].tr.th.find('a', class_ = 's xst')
                metadata.append(span.find('font', color = '#F60').b.get_text())   # major
                metadata.append(span.u.next_sibling)            # experience level
                metadata.append(a['href'])                      # clickable url
                metadata.append(tbody_array[i].tr.find('td', class_ = 'by').em.span.get_text()) # date
                metadata.append(a.get_text())                   # thread title

                result.append(metadata)
                # temp = '{}\t{}\t{}\t{}\t{}\t{}'.format(company_name, metadata[1], metadata[2], metadata[3], metadata[4], metadata[5])
                # print(temp)

        i = i + 1

def main():
    url = 'http://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=198&sortid=192&%1=&sortid=192&page='
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

    if len(sys.argv) < 6:
        print('Usage: python3 referral.py <max-page-count> <max-link-per-company> <path-to-credentials> <sheet-id> <path-to-chromedriver>')
        return
    MAX_PAGE = int(sys.argv[1])
    MAX_LINK_PER_COMPANY = int(sys.argv[2])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(sys.argv[3], scope)
    gc = gspread.authorize(credentials)
    SPREADSHEET_ID = sys.argv[4]
    DRIVER_PATH = sys.argv[5]
    wks = gc.open_by_key(SPREADSHEET_ID).sheet1

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    while True:
        link_count = dict()
        result = []
        page = 1

        driver = webdriver.Chrome(DRIVER_PATH, chrome_options=options)
        while page <= MAX_PAGE:
            print("Get webpage for " + url + str(page))
            driver.get(url + str(page))
            parseHtml(driver, link_count, MAX_LINK_PER_COMPANY, result)
            page = page + 1
            print("rows: " + str(len(result)))
        driver.close()
        
        row_count = len(result)
        col_count = len(result[0])
        cell_list = wks.range(2, 1, row_count + 1, col_count)
        for i in range(row_count):
            for j in range(col_count):
                cell_list[i * col_count + j].value = result[i][j]
        wks.update_cells(cell_list)

        time.sleep(3000)

if __name__ == "__main__":
    main()
