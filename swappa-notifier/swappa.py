import requests, json, os, time, sendgrid, sys
from bs4 import BeautifulSoup as BS
from sendgrid.helpers.mail import *

def getResponse(url):
    try:
        print('in getResponse: ' + url)
        r = requests.get(url)
        return r
    except Exception:
        return None

def getText(arr):
    text = ''
    for s in arr:
        text = text + '\n\n' + s
    return text

'''
def sendEmail(TO, SUBJECT, TEXT):
    # Gmail Sign In
    gmail_sender = os.environ['GOOGLE_ACCOUNT']
    gmail_passwd = os.environ['GOOGLE_PASSWORD']
    
    server = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)

    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', TEXT])

    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print ('email sent')
    except:
        print ('error sending mail')
    server.quit()
'''

def sendEmail(FROM, TO, subject, emailContent):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(FROM)
    to_email = Email(TO)
    content = Content("text/plain", emailContent)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code

def parseHtml(r, url, price, listingIdSet):
    soup = BS(r.text, 'html.parser')
    listing = soup.find_all('div', class_='listing_preview')
    i = 0
    arr = []
    while i < len(listing) - 5:         # exclude last five sold ones
        temp = '${}\t{}\t{}\t{}{}'.format(listing[i]['data-price'], listing[i]['data-condition'], listing[i].div.div.find(class_='headline').a.text, url, listing[i]['data-url'])
        # print(temp)
        if int(listing[i]['data-price']) <= price and not listing[i]['data-date'] in listingIdSet:
            listingIdSet.add(listing[i]['data-date'])
            arr.append(temp)
        i = i + 1
    return getText(arr)

def main():
    url = 'https://swappa.com/buy/samsung-galaxy-s7-edge-att'
    FROM = os.environ['GOOGLE_ACCOUNT']
    TO = os.environ.get('TARGET_GOOGLE_ACCOUNT')
    SUBJECT = 'Swappa new listing!'
    listingIdSet = set()

    while True:
        r = getResponse(url)
        emailContent = parseHtml(r, url, 250, listingIdSet)
        if not emailContent == '':
            print(emailContent)
            if int(sendEmail(FROM, TO, SUBJECT, emailContent)) == 202:
                print('Email sent successfully!')
            else:
                print('Error when sending email...')
        time.sleep(600)     # sleep for 600s

if __name__ == "__main__":
    main()
