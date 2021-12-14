### Raspberry Pi Environment Setup
```bash
# python3 required. venv recommended.
sudo apt-get install python3-venv
python3 -m venv /home/pi/leetcode
source /home/pi/leetcode/bin/activate

# install dependencies
pip install selenium==3.14.0
sudo apt-get install chromium-chromedriver    # the driver path should be default in /usr/bin/chromedriver
```

### Usage
```bash
python3 -m venv /home/pi/leetcode && python3 /home/pi/fun_project/leetcode-autologin/lc_login.py <username> <password> /usr/bin/chromedriver > /home/pi/leetcode/lc_login_log
```