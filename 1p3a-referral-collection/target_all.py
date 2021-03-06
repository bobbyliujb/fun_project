#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re, gspread, time
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from oauth2client.service_account import ServiceAccountCredentials

def parseHtml(driver, link_count, MAX_LINK_PER_COMPANY, result, target_name):
    if (driver.page_source == None):
        return False
    soup = BS(driver.page_source, 'html.parser')
    section_main = soup.find(id='threadlisttableid')
    if (section_main == None):
        return False
    tbody_array = section_main.find_all('tbody', id = re.compile('^normalthread'))
    if (tbody_array == None or len(tbody_array) == 0):
        return False

    i = 0
    while i < len(tbody_array):
        if (tbody_array[i].tr.th.em != None 
            and tbody_array[i].tr.th.em.get_text() == "找工就业"
            and tbody_array[i].tr.th.span != None
            and tbody_array[i].tr.th.span.span != None
            and tbody_array[i].tr.th.find('a', class_ = 's xst') != None):
            span = tbody_array[i].tr.th.span.span
            if (span.u == None):
                i = i + 1
                continue
            company_name = span.u.find_all('b')[2].get_text().lower()
            a = tbody_array[i].tr.th.find('a', class_ = 's xst')
            if (target_name not in company_name
            and target_name not in a.get_text().lower()):
                i = i + 1
                continue
            
            if (company_name not in link_count):
                link_count[company_name] = 0

            if (link_count[company_name] < MAX_LINK_PER_COMPANY):
                link_count[company_name] = link_count[company_name] + 1
                metadata = [company_name]
                metadata.append(span.find('font', color = '#F60').b.get_text())   # major
                metadata.append(span.u.next_sibling)            # experience level
                clickable_url = 'http://www.1point3acres.com/bbs/' + a['href']                  # clickable url
                metadata.append(clickable_url)
                metadata.append(tbody_array[i].tr.find('td', class_ = 'by').em.span.get_text()) # date
                metadata.append(a.get_text())                   # thread title

                result.append(metadata)
                # temp = '{}\t{}\t{}\t{}\t{}\t{}'.format(company_name, metadata[1], metadata[2], metadata[3], metadata[4], metadata[5])
                # print(temp)
                print(clickable_url)

        i = i + 1

    return True

def main():
    url = 'https://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=28&sortid=192&%1=&sortid=192&page='
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

    if len(sys.argv) < 7:
        print('Usage: python3 target_all.py <max-page-count> <max-link-per-company> <path-to-credentials> <sheet-id> <path-to-chromedriver> <target-comapny-name>')
        return
    MAX_PAGE = int(sys.argv[1])
    MAX_LINK_PER_COMPANY = int(sys.argv[2])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(sys.argv[3], scope)
    gc = gspread.authorize(credentials)
    SPREADSHEET_ID = sys.argv[4]
    DRIVER_PATH = sys.argv[5]
    TARGET_NAME = (sys.argv[6])
    wks = gc.open_by_key(SPREADSHEET_ID).get_worksheet(4)

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
            try:
                time.sleep(2)
                driver.get(url + str(page))
            except:
                time.sleep(10)
                continue
            if (parseHtml(driver, link_count, MAX_LINK_PER_COMPANY, result, TARGET_NAME) == False):
                continue
            page = page + 1
            print("rows: " + str(len(result)))
        driver.quit()

        if (len(result) == 0):
            break
        row_count = len(result)
        col_count = len(result[0])
        cell_list = wks.range(2, 1, row_count + 1, col_count)
        for i in range(row_count):
            for j in range(col_count):
                cell_list[i * col_count + j].value = result[i][j]
        wks.update_cells(cell_list)

        # Free memory
        del cell_list
        del result
        del link_count

        # print('Start to sleep 3000 seconds...')
        # time.sleep(3000)
        break

if __name__ == "__main__":
    main()
