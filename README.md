# Projects for Fun
### Swappa Notifier
#### v1.1
 * Read Swappa link and user email from command line. Read specification from command line. 
 * Usage: `nohup python3 swappa.py <swappa-link> <target-email> <price(integer)> <time-interval(seconds)> (test) > myout.out 2>&1`. The last `test` argv is for test only, which will not actually send the email.
 * Might be treated as spam email. Need to check the first email from my email and add to whitelist by [setting filter](https://c-command.com/spamsieve/help/turning-off-the-gmail-s).
 * TODO: Add DB to support email to multiple subscription and unsubscription.
#### v1.0
 * Python 3.6 with sendgrid. Hardcoded time interval, email addresses, target url, etc. Get HTML page and analyze some key information. Filter by price and send to target email.
 * Usage: `nohup python3 swappa.py > myout.out 2>&1`. Need to export environment variables like `export SENDGRID_API_KEY=SG.xxx` and `export FROM_EMAIL=xxx@xxx.com`. GCloud compute engines seems to clear environment variables regularly.
 * ~~TODO: Support custom specification for filtering(price, check-interval)~~

***
### Auto login(TODO...)
 * Auto login Leetcode every day to win Leetcode coin(= =).
 * Use debian crontab to run the py script daily.
 * Use requests to simulate post.
 * BUT! LeetCode's login has some other subsequent operations. I verified login unsuccess because my account was not forced to logout, let along getting the coin.

***
### Referral Scraping
 * Get referral information from [1p3a](http://www.1point3acres.com/bbs).
 * Libraries for python3:
   ```
     pip3 install bs4 selenium oauth2client gspread
   ```
 * Use Google [spreadsheet API](https://developers.google.com/sheets/api/quickstart/python?authuser=2) to write content onto personnal spreadsheet.
 * Need chromedriver to run. [Install on Ubuntu](https://askubuntu.com/questions/1004947/how-do-i-use-the-chrome-driver-in-ubuntu-16-04). Set [headless options](https://stackoverflow.com/questions/47596402/selenium-chrome-failed-to-start-exited-abnormally-error) in code.
 * Deployed on GCP, ~~with [tmux](https://tmuxcheatsheet.com/) to run without interruption.~~ with crontab to schedule run.
   ```
     gcloud config set project project-name
     gcloud config set zone zone-xxx
     gcloud compute --project "project-anme" ssh --zone "zone-xxx" "instance-name"
     crontab -e
      0 0,6,12,15,18,21 * * * /usr/bin/python3 /home/bobby/referral.py 40 20 /home/bobby/token.json xxx /usr/lib/chromium-browser/chromedriver > /home/bobby/py.log 2>&1
      0 1 * * * /usr/bin/python3 /home/bobby/mianjing_onsite.py 300 500 /home/bobby/token.json xxx /usr/lib/chromium-browser/chromedriver > /home/bobby/py_onsite.log 2>&1
      0 3 * * * /usr/bin/python3 /home/bobby/mianjing_oa.py 300 50 /home/bobby/token.json xxx /usr/lib/chromium-browser/chromedriver > /home/bobby/py_oa.log 2>&1
   ```
 * For personal study only. Never use the data for any kind of business activities!
