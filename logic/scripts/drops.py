from contextlib import closing
import json
import webbrowser
import re

from bs4 import BeautifulSoup

import requests
from requests.exceptions import RequestException
from tools import db_utils
from util import tasks
from config import constants
from types import SimpleNamespace
from datetime import date, datetime, timezone
from dateutil import parser



headers = {
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}

def sort_drops(drops):
    sorted_drops = sorted(drops, key=lambda x: x.startDate, reverse=True)
    return sorted_drops

def parse_date(date):
    return parser.parse(date)

def filter_upcoming_drops(drops):
    upcomingDrops = []
    for drop in drops:
        if not drop.startDate or not drop.endDate:
            continue
        if (parse_date(drop.startDate) > datetime.now(timezone.utc) or parse_date(drop.endDate) > datetime.now(timezone.utc)):
            drop.countdown = parse_date(drop.startDate).strftime('%A %B %m')
            upcomingDrops.append(drop)
    upcomingDrops = sort_drops(upcomingDrops) 
    
    return upcomingDrops      

def filter_past_drops(drops, allPast):
    pastDrops = []
    for drop in drops:
        if not drop.endDate:
            continue
        if parse_date(drop.endDate) < datetime.now(timezone.utc):
            pastDrops.append(drop) 
    pastDrops = sort_drops(pastDrops)

    print(allPast)
    print(len(pastDrops))

    if allPast == 'true':
        return pastDrops
    else:    
        return pastDrops[slice(0, 3)]  
               

def get_drops(allPast):

    headers = {
    "Content-Type": "application/json",
    }
    url = "{0}/site-marketing".format(constants.LAUNCHPAD_API)

    drops = []
    try:
        with closing(requests.get(url, headers=headers)) as resp:
            if resp.status_code == 200:
                drops =json.loads(resp.content, object_hook=lambda d: SimpleNamespace(**d))
            else:
                return None

    except RequestException as e:
        print("Error during requests to {0} : {1}".format(url, str(e)))
        return None 

    upcomingDrops = filter_upcoming_drops(drops)
    pastDrops = filter_past_drops(drops, allPast)  

    return [upcomingDrops, pastDrops, allPast]
