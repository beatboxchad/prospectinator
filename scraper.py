#!/usr/bin/env python2
import json
import urllib2
import os

from pprint import pprint
from blindelephant.Fingerprinters import WebAppFingerprinter

# a piece of the dotfile search bit
CONFIG_PATH = os.path.expanduser("~/.config")

places = []
# load settings FIXME do the dotfile search, this shouldn't live in repo
# TODO also implement command-line args
with open('config.json') as defaults_file:    
    defaults = json.load(defaults_file)

apikey    = defaults["apikey"]
location  = defaults["location"]

# grab the list of places
base_url  = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location=%s&keyword=*&&radius=5000&key=%s"
query_url = base_url % (location, apikey)
query_response = json.loads(urllib2.urlopen(query_url).read())

#now we get the details of each place.

ids = [result["place_id"] for result in query_response["results"]]

base_url1 = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s"
for place_id in ids:
    my_query_url = base_url1 % (place_id, apikey)
    places.append(json.loads(urllib2.urlopen(my_query_url).read()))
