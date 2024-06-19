# The Beacon Bot

## 🤖 | Features:
- **Auto registration/login**
- **Auto completion of all quests**
- **Auto open all chests**


## 📝 | Description:
Login (Tweeter binding) works through the browser. 

After binding, the browser closes and work continues using requests.

Do not set too many threads, this may lead to unstable operation of the script.

The script completes all quests except discord.


## ⚙️ Config (config > settings.yaml):

```
Accounts: data > accounts.txt | Format:
- auth_token
- auth_token:wallet_mnemonic/pk

Proxies: data > proxies.txt | Format:

ACCEPTING ONLY HTTP 

- http://user:pass@ip:port
- http://user:pass:ip:port
- http://ip:port:user:pass
- http://ip:port@user:pass
```


| Name              | Description                                                       |
|-------------------|-------------------------------------------------------------------|
| threads           | Number of accounts that will work simultaneously                  |
| invisible_browser | run the browser in the background (only for login)                |
| max_timeout_for_login_account     | max timeout for login account in seconds (only for login)         |
| delay_between_quests       | delay between quests in seconds                                   |
| delay_between_quests_verification       | delay between quests verification and claiming rewards in seconds |
| delay_between_chests       | delay between open chests in seconds                              |



## 🚀 | How to start:
1. **Install python >= 3.11:**
```bash
https://www.python.org/downloads/
```
2. **Clone the repository:**
```bash
git clone this repo
```
3. **Create and activate a virtual environment:**
```bash
python -m venv venv
cd venv/Scripts
activate
cd ../..
```
3. **Install dependencies:**

**REQUIRED CHROME TO BE INSTALLED**
```bash
pip install -r requirements.txt
```
4. **Run the bot:**
```bash
python run.py
```
