#------------------------------------------------------------------------#
# Program Name : market_notifications.py
# Author       : Mohammad Ozaslan
# Description  : currently searches Craigslist for motorcycle listings, and
#                notifies user of new listings (based on user preferences)
#------------------------------------------------------------------------#

#------------------------- LIBRARIES -------------------------#
from bs4 import BeautifulSoup # for parsing
import requests               # for web requests

# for setting up SMTP Client
import smtplib
import ssl
import getpass

# for email manipulation (MIME)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bisect
import math
import signal
import time

#------------------------- GLOBALS -------------------------#

# storage for listings
listings = []

# smtp client object
smtp_client = None
password = getpass.getpass("Type password and press enter: ")

# settings dictionary
settings = { 'max_price'      : 3500,
             'cities'         : ["denver", "cosprings", "fortcollins", "boulder", "rockies", "westslope"],
             'receiver_email' : "ADD_NUMBER@tmomail.net",           # T-Mobile phone number.
             'sender_email'   : "ADD_EMAIL@gmail.com",              # a Google Mail address
             'smtp_server'    : "smtp.gmail.com"                    # the SMPT server (if using different email service, update this)
            }

#------------------------- FUNCTION AND CLASS DEFINITIONS -------------------------#

class Listing:
    '''Represents a Craigslist listing.'''
    def __init__(self, _title, _link, _price) :
        self.title = _title
        self.link = _link
        self.price = int(_price.strip('$').replace(',', ''))
        self.price_text = _price

    # used by bisect module to determine ordering
    def __lt__(self, other):
        return self.title < other.title

    # returns a string of basic info
    def description(self) :
        return self.price_text + " - " + self.title + "\n" + self.link


def send_message(client, message_string) :
    ''' Takes an SMTP client object and message string,
        sends message via client, using MIMEText mimicking standard Google Mail,
        and using receiver and sender emails specified in the settings.
    '''
    msg  =  MIMEMultipart('alternative')
    receiver_email = settings['receiver_email']
    sender_email = settings['sender_email']

    # standard fields
    msg['Subject'] = ''
    msg['From'] = ''
    msg['To'] = receiver_email

    # to mimic standard Google Mail text, message contains both plain text and HTML
    html_string = "<div dir=\"ltr\">" + message_string + "<br></div>"

    plain_text = MIMEText(message_string, 'plain')
    html_text = MIMEText(html_string, 'html')

    msg.attach(plain_text)
    msg.attach(html_text)

    # send message with client
    try :
        client.sendmail(sender_email, receiver_email, msg.as_string())
        print("Message Sent: \'" + message_string + "\'")
    except :
        initialize_client()
        send_message(smtp_client, message_string)

def find_result_tags(url) :
    ''' Returns list of tag objects containing listing info,
        from Craigslist page linked to by the given URL.
    '''
    # setup of parsed html page
    r = requests.get(url)
    html = r.text
    parsed_html = BeautifulSoup(html, 'html.parser')

    results = parsed_html.find_all('li', class_ = 'result-row')
    return results


def update_data(new_listing) :
    ''' Updates listing array with new_listing, preserving order
        and avoiding duplicates based on title name
    '''
    i = bisect.bisect_left(listings, new_listing)

    if not (i < len(listings) and listings[i].title == new_listing.title) :
        # we have a new listing!
        listings.insert(i, new_listing)

        # if it's below the max price in settings, notify user
        if new_listing.price <= settings['max_price'] : # TODO: conditions for notifications should be queried at Craigslist!
            if __debug__ :                              #       gives user preferences for
                print(new_listing.description())
            else :
                send_message(smtp_client, new_listing.description())

def initialize_client() :
    global smtp_client

    port = 587
    smtp_server = settings['smtp_server']
    sender_email = settings['sender_email']

    smtp_client = smtplib.SMTP(smtp_server, port)
    context = ssl.create_default_context()

    smtp_client.starttls(context = context)
    smtp_client.login(sender_email, password)

def initialize_data() :
    all_results = []
    for city in settings['cities'] :
        url = "https://" + city.lower() + ".craigslist.org/search/mcy?"
        r = requests.get(url)
        html = r.text
        parsed_html = BeautifulSoup(html, 'html.parser')

        total_entries = float(parsed_html.find("span", class_="totalcount").get_text())
        total_pages = math.ceil(total_entries // 120)

        # collect result tags from initial/first page of given city
        city_results = find_result_tags(url)
        print(url)

        # collect result tags from all subsequent pages of given city
        for k in range(1, total_pages + 1) :
            time.sleep(2)

            page_num = str(k * 120)
            url = "https://" + city.lower() + ".craigslist.org/search/mcy?" + "s=" + page_num
            print(url)
            city_results = city_results + find_result_tags(url)

        all_results = all_results + city_results # collect result tags from each city

    for result in all_results :
        new_listing = to_listing(result)
        bisect.insort(listings, new_listing)

def initialize() :
    initialize_client()
    initialize_data()

    send_message(smtp_client, "Market Notifications On")

def to_listing(result) :
    ''' Convert tags containing listing info into listing object '''
    result_hyperlink = result.find('a', class_ = 'result-title hdrlnk')
    result_title     = result_hyperlink.get_text()
    result_link      = result_hyperlink.get('href')

    result_price = result.find('span', class_ = 'result-price').get_text()

    new_listing = Listing(result_title, result_link, result_price)

    return new_listing

def update() :
    ''' extract result tag objects from first page of every city in settings '''
    all_results = []
    for city in settings['cities'] :
        time.sleep(30)

        # access 1st motorcycle page of the given city
        url = "https://" + city.lower() + ".craigslist.org/search/mcy?"

        city_results = find_result_tags(url)
        all_results = all_results + city_results

    for result in all_results :
        new_listing = to_listing(result)
        update_data(new_listing)

def terminate() :
    send_message(smtp_client, "Market Notifications Off")
    smtp_client.quit()

def sigint_handler(signal, frame):
    ''' Custom handler, to notify user as part of interrupt '''
    global interrupted
    interrupted = True

    send_message(smtp_client, "Market Notifications Off")

#------------------------- APP CODE -------------------------#

signal.signal(signal.SIGINT, sigint_handler)

initialize()

if __debug__ :
    update()
else :
    interrupted = False
    while not interrupted :
        update()
        time.sleep(2*60)

terminate()