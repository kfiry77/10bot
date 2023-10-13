# 10bot

A bot to buy 10Bis coupons
This projects aims to run every day and to buy a [10bis](www.10bis.co.il) coupon, 
if there is a credit.  

## Installation and usage

download the repository an install requirements.

```sh
git clone https://github.com/kfiry77/10bot
cd 10bot
pip3 install -r requirements.txt
```

Execute the script ``main``` script initially, to acquire authentication tokens, you will get SMS with OTP, type it on the command line.

```sh
python3 main.py <<tenbis accountname>>
```

Add the script to the system crontab, by typing ```crontab -e ``` and adding the following line to it.   
```
crontab -e
0 23 * * *  usr/bin/python3 /path/to/your/script/main.py <<accountname>> >> /path/to/your/log//10bot.log 2>&1 &
```

## references:

The code is bases from these repositories by [Dvir Perets](https://github.com/Dvirus89)
- [Dvirus89/tenbisbarcodes](https://github.com/Dvirus89/tenbisbarcodes)
- [Dvirus89/tenbis-buy-coupons](https://github.com/Dvirus89/tenbis-buy-coupons)

## TODO:  
- [ ] Fix the holidays, to block only non-working day. 
- [ ] Add the deployment in Microsoft Azure using Azure function.  
- [ ] Add Report generation.
- [ ] Find a way to send it: website or message. 