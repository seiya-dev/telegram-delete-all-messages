# telegram-delete-all-messages
Delete all your messages in supergroups with python script.

Full rewrite of https://github.com/gurland/telegram-delete-all-messages

## Installation
To install this script you have to download project and install requirements:

### Linux
```
git clone https://github.com/seiya-dev/telegram-delete-all-messages
cd telegram-delete-all-messages
pip install -r requirements.txt
python app-auth.py
python app-cleaner.py
```

### Windows
- Download zip file from this repo and unpack it
- Install latest [Python 3](https://www.python.org) version
- python app-auth.py
- python app-cleaner.py

## Obtain standalone telegram app API credentials
- Login to https://my.telegram.org/
- Select `API development tools` link
- Create standalone application
- Copy app_id and app_hash

## Usage
> You need both App api_id and App api_hash to use script.

#### Start
After starting script you will be prompted:
- To enter your Telegram APP credentials (if no environment variables found)
- Your account phone and then code sent to you by Telegram
```
$ python app-auth.py

Enter your Telegram API id: 123456
Enter your Telegram API hash: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Enter phone number: +123456789012
Is "+123456789012" correct? (y/n): y
Enter phone code: 00000
Logged in successfully as ...
```

#### Choosing supergroup
```
$ python app-cleaner.py
```
- After providing needed information you will get your supergroup dialogs
- Enter number found near desired supergroup title
```
1. Python community
2. Rust Beginners
3. IDE & Editors

Insert group number:
```

#### Message removal process
- After choosing supergroup you would get informed about messages removal process
```
Insert group number: 2
Selected Rust Beginners

Searching messages. OFFSET: 0
Found 4 your messages in selected supergroup
```

## Contribution
To make any changes in our codebase, please do the following:
1. Create or find an Issue describing what needs to be done.
2. Discuss all changes needed.
3. Fork repository, clone it, create branch with briefly descriptive name of feature/bufix you are adding, e.g. `git checkout -b fix-sleep-treshold`.
4. Create Pull Request. Please, test all changes before creating PR and explicitly declare whether testing was successful or not.
5. Wait until available contributors review changes.
6. If everything is OK your contribution gets approved.

Note: it's very important to keep PRs brief and clear. Resolve single issue by a single PR.
