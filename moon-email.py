#!/usr/bin/python
import time
import smtplib
import requests
import dominate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup as bs
from datetime import datetime
from turtle import *
from dominate.tags import *

EMAIL  = ""
PWD    = ""
SMTP_SERVER = ""
SMTP_PORT   = ""


DAY_OF_MONTH = datetime.now().day
CURRENT_DATE = datetime.now()

def get_date():
	return CURRENT_DATE.strftime("%d/%m/%Y")

def get_date_y_m_d():
	return CURRENT_DATE.strftime("%Y-%m-%d")

def get_soup(url):
    page = requests.get(url)
    html = page.text
    return bs(html, 'html.parser')

def get_moon_data():
	soup = get_soup('https://www.timeanddate.com/moon/uk/derby')
	table = soup.find('table', attrs={'id': 'tb-7dmn'}).find('tbody')
	for row in table:
		if (DAY_OF_MONTH == int(row.find('th').text.strip())):
			try:
				if str(row.find_all('td')[5].text) == 'Moon does not pass the meridian on this day.':
					return 'Moon does not pass the meridian on this day.'
			except:
				pass
			return row.find_all('td')[7]['title']

def get_weather_data():
	date = str(get_date_y_m_d())
	soup = get_soup('https://www.metoffice.gov.uk/weather/forecast/gcqvn6pq4#?date=' + date)
	data_tab = soup.find('li', attrs={'data-tab-id': date})
	return {
		'sunrise': data_tab.find_all('div', attrs={'class': 'weather-text'})[0].find('time').text,
		'sunset': data_tab.find_all('div', attrs={'class': 'weather-text'})[1].find('time').text,
		'temp-high': data_tab.find('span', attrs={'title': 'Maximum daytime temperature'}).text[:-1]+"C",
		'temp-low': data_tab.find('span', attrs={'title': 'Minimum nighttime temperature'}).text[:-1]+"C",
		'weather-description': data_tab.find('span', attrs={'id': 'tabSummaryText' + date}).text
	}

def create_html():
	weather_data = get_weather_data()
	doc = dominate.document(title='Biggest Trades Today')
	with doc:
		with div(id='moon-summary'):
			caption(h3('Moon Phase Tonight: ' + get_date()))
			p(get_moon_data())
			p(weather_data['weather-description'])
		with table(id='weather-summary'):
			with thead():
				with tr():
					th('Sunrise')
					th('Sunset')
					th('Temperature High')
					th('Temperature Low')
			with tbody():
				with tr():
					td(weather_data['sunrise'])
					td(weather_data['sunset'])
					td(weather_data['temp-high'])
					td(weather_data['temp-low'])
	return doc


def send_moon_phase_email():
    fromaddr = EMAIL
    toaddrs = 'me@shanel.ee'
    msg = MIMEMultipart('alternative')
    msg['To'] = toaddrs
    msg['From'] = EMAIL
    msg['Subject'] = 'Moon Phase Tonight: ' + get_date()
    text = ""

    html = str(create_html()).encode('utf-8').strip()

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, PWD)

    server.sendmail(fromaddr, toaddrs, str(msg))
    server.quit()

send_moon_phase_email()


