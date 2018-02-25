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

### Auto login(TODO...)
 * Auto login Leetcode every day to win Leetcode coin(= =).
 * Use debian crontab to run the py script daily.
 * Use requests to simulate post.
 * BUT! LeetCode's login has some other subsequent operations. I verified login unsuccess because my account was not forced to logout, let along getting the coin.
