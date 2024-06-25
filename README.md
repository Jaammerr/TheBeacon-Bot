# The Beacon Bot

## 🔗 Links

🔔 CHANNEL: https://t.me/JamBitPY

💬 CHAT: https://t.me/JamBitChat

💰 DONATION EVM ADDRESS: 0xe23380ae575D990BebB3b81DB2F90Ce7eDbB6dDa

## 🤖 | Features:
- **Auto registration/login**
- **Auto completion of all quests**
- **Auto open all chests**


## 📝 | Description:
This version supports automatic completion of discord quests

Before starting, you need to join the discord server (thebeacon) yourself, or you can purchase software (discord joiner) - https://t.me/JamBitPY/64


## ⚙️ Config (config > settings.yaml):

```
Accounts: data > accounts.txt | Format:
- auth_token
- auth_token:wallet_mnemonic/pk
- auth_token:wallet_mnemonic/pk:discord_token

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

```bash
pip install -r requirements.txt
```
4. **Run the bot:**
```bash
python run.py
```
