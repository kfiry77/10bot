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
- macOS
```sh
brew install weasyprint
```
- linux / Ubuntu 
```sh
apt install weasyprint
```
- Windows : make sure to install GTK+, and add it to the PATH environment variable.

Execute script ``main``` initially, to acquire authentication tokens, you will get SMS with OTP, type it on the command line.

```sh
python3 main.py
```

Add the script to the system crontab, by typing ```crontab -e ``` and adding the following line to it.   
```
crontab -e
0 23 * * *  usr/bin/python3 /path/to/your/script/main.py  >> /path/to/your/log//10bot.log 2>&1 &
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
- [ ] Add report publisher, and make it generic to various kind for example: Google Drive share.
- [ ] Bug Fix : Pdf is cannot be generated on windows due to weasyprint dependency.

