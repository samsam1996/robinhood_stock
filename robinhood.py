import robin_stocks as r
import os
import datetime
import time as t
import smtplib
import getpass

'''
Constants

'''
SLEEP_TIME = 1000  # in seconds
PRINT_TRACKING_OPTIONS = False #Set to True to print your current tracking options 
ENABLE_ALERT = False # Set to True to enable email alert service
PRINT_INFORMATION = False #Set to True to print stock information
USER = '*** Your robinhood username ***'  # Username is needed to obtain option information
EMAIL_SERVICE = "smtp.gmail.com"
EMAIL = "*** Your email ****"
APP_PASSWORD = "*** Your app id ***"

'''
Initialize Current Watchlist from watchlist.txt,
Append new line in .txt file to add options in your watchlist

'''
class watchlist(object):
    def __init__(self):
        self.list = []
    
    def input_option(self,info):
        self.list.append(info)
    

    def log_in(self):
        username = USER #Change to your robinhood username
        password = '' #Can be empty

        login = r.login(username,password) #Login is required to accesss market_data
        return login
    def read_from_txt(self):
        
        with open("./watchlist.txt",'r') as f:
            next(f)
            while True:
                line = f.readline()
                if not line:
                    break
                
                self.list.append(tuple([x.strip() for x in line.split(',')]))
    def print_list(self):
        for info in self.list:
            print(info)
            
'''
Setting up email service 

'''           
class send_email(object):
    def __init__(self,email_service,email_user,email_app_password):
        self.domain = email_service
        self.email_user = email_user
        self.email_pass = email_app_password
    def get_smtp_obj(self,sender=None,receiver=None):
        try:
            smtp_obj = smtplib.SMTP(self.domain,587)
            print("STMP connection established")
        except  smtplib.SMTPConnectError:
            print("No Connection")
        smtp_obj.ehlo()
        smtp_obj.starttls()
        smtp_obj.login(self.email_user,self.email_pass)
        if not sender:
            sender = self.email_user
        if not receiver:
            receiver = self.email_user
        return smtp_obj

'''
Functions
'''
def print_info(instrument_data,market_data):
    print("{} Instrument Data {}".format("="*30,"="*30))
    for key, value in instrument_data.items():
        print("key: {:<25} value: {}".format(key,value))
    print("{} Market Data {}".format("="*30,"="*30))
    
    for key, value in market_data[0].items():
        print("key: {:<25} value: {}".format(key,value))
                    
'''
Run option price alert

'''
def run():     
    w = watchlist() #Initilize watchlist
    w.read_from_txt() #Read watching options from list
    login = w.log_in() #Login to your robinhood account, password not needed
    
    if ENABLE_ALERT: #If set to True, send email alert to your email
        smtp = send_email(EMAIL_SERVICE,EMAIL,) #service, your email, your password
        sender = EMAIL #Send from 
        receiver = EMAIL #Send to
        smtp_obj = smtp.get_smtp_obj(sender,receiver)
        
    if PRINT_TRACKING_OPTIONS: #Print your current tracking options to console
        w.print_list()
        
    while t.time() < t.time()+10: #Runs until Ctrl+C
        #Print current timestamp
        time = str(datetime.datetime.now())
        print("Current time is: {}".format(time))
        
        #For each tracking options
        for strike, date, stock, optionType,cost,percent_sell, email_send in w.list:
            instrument_data = r.get_option_instrument_data(stock,date,strike,optionType) #Option general information
            market_data = r.get_option_market_data(stock,date,strike,optionType) #Option market information
            if PRINT_INFORMATION:
                print_info(instrument_data,market_data)
                
            for key, value in market_data[0].items():
                if key == "bid_price": #Get bid_price
                    cur_price = value
                    
            #If current price < your cost * loss factor
            if float(cur_price) < float(cost) * float(percent_sell):
                subject = "SELL {}".format(stock)
                message = "You need to Sell {} Option at {} expiring {}, current loss is {:.2f}%".format(stock,strike,date,float(cur_price)/float(cost)*100)
                msg = "Subject: " + subject + '\n' + message
                print(msg)
                #Send email alert only when alert is enable
                if ENABLE_ALERT and email_send != "send":
                    print("Email Alert Enabled, Alert send for {}!".format(stock))
                    smtp_obj.sendmail(sender,receiver,msg)

        t.sleep(SLEEP_TIME)
        
if __name__ == "__main__":
    run()