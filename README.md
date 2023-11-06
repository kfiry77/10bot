# 10bot

A bot to buy 10Bis coupons
This projects aims to run every day, and to buy [10bis](www.10bis.co.il) coupon  
if there is a credit. It's also create an HTML report with all Coupons barcodes. 

## Installation and usage

download the repository and install requirements.

```sh
git clone https://github.com/kfiry77/10bot
cd 10bot
pip3 install -r requirements.txt
```

Install prerequisites for weasyprint (for PDF report generation), as describe  [here](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)
### macOS
```sh
brew install weasyprint
```
### linux / Ubuntu 
```sh
apt install weasyprint
```
### Windows
 install [gtk3](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) runtime and it's dependencies, and add the runtime to PATH environment variable
```sh
PATH=%PATH%;C:\Program Files\GTK3-Runtime Win64\bin
```

Execute script ```main```  to acquire authentication tokens, you will get SMS with OTP, type it on the command line.

note:purchase won't be submitted if -d is specified. 
```sh
python3 main.py -d 
```

Add the script to the system crontab, by typing ```crontab -e ``` and adding the following line to it.   
```
crontab -e
0 23 * * *  usr/bin/python3 /path/to/your/script/main.py [-v] [-d]  >> /path/to/your/log/10bot.log 2>&1 &
```

## references:

The code is bases from these repositories by [Dvir Perets](https://github.com/Dvirus89)
- [Dvirus89/tenbisbarcodes](https://github.com/Dvirus89/tenbisbarcodes)
- [Dvirus89/tenbis-buy-coupons](https://github.com/Dvirus89/tenbis-buy-coupons)

## TODO:  
- [x] Bug Fix: user-token header is not needed due to 10bis change of API, RefreshToken API should be used instead.  
- [ ] Fix the holidays, to block only non-working day. 
- [ ] Add scrips the deployment to cloud providers:
  - [ ] Azure 
  - [ ] GCP
- [x] Add Report generation.
  - [x] Make the report formatter generic, for various kinds of files.
  - [x] Make PDF report formatter. 
- [x] Add report publisher, and make it generic using [chain of responsibility](https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern)
       GOF design pattern. 
  - [x] whatsApp Publisher
  - [ ] Google Drive or Microsoft OneDrive Publisher. 
- and make it generic to various kind for example: Google Drive share.
- [x] Bug Fix : Pdf is cannot be generated on windows due to weasyprint dependency.
- [ ] describe software design with some plantuml class diagrams.
- [ ] Coupon images crop, for a nicer report formatting.
- [ ] Green API - send data to GroupChat, and delete previous report (if possible). 


