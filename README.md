# Fit4Less bot
Automatically get gym booking slots for Fit4Less.

This bot is written in Python using Selenium.

## Setup 

To run the bot, open the command line in the cloned repo directory and install the requirements using pip with the following command:
```bash
pip install -r requirements.txt
```

Next, you need to fill out the config.yaml file.

```yaml
email: email@domain.com
password: mypassword
bookingDay: 1 # how many days in advance, put 3 if you are running it the night before via a cronjob
bookingTime: 7:00 PM # Must be exact, in hh:MM AM/PM format
club:
  useClubName: False # Set to True to change to this club
  clubName: Waterloo Erb Street # Exact name of the club as on the club selection list
```


## Execute

To run the bot, run the following in the command line:
```
python3 main.py
```
