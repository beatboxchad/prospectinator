#!/usr/bin/env python2
import json
import urllib2
import os

from pprint import pprint
from blindelephant.Fingerprinters import WebAppFingerprinter

MAX_WP_VERSION = "4.7" #FIXME stop hardcoding

# a piece of the dotfile search bit -- TODO make this mroe dynamic.
# xdg-settings, whatever on mac. Also implement CL args
CONFIG_PATH    = os.path.expanduser("~/.config/prospectinator/")
if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)

CACHE = open(CONFIG_PATH + "cache.json", 'r')

with open(CONFIG_PATH + 'prospectinator.json', 'r') as defaults_file:    
    defaults = json.load(defaults_file)


try: 
    places = json.load(CACHE)
except:
    places = {}

gmaps_apikey = defaults["gmaps_apikey"]
location     = defaults["location"]

# grab the list of places
base_url  = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location=%s&keyword=*&&radius=5000&key=%s"
query_url = base_url % (location, gmaps_apikey)
response  = json.loads(urllib2.urlopen(query_url).read())

#now we get the details of each place.
ids        = [result["place_id"] for result in response["results"]]
place_url  = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s"

for place_id in ids:
    # FIXME gross name
    my_query_url = place_url % (place_id, gmaps_apikey)
    # FIXME better interrogation? Actually for this stage this is fine. We can
    # inspect the data for fingerprinted later
    if not place_id in places:
        places[place_id] = json.loads(urllib2.urlopen(my_query_url).read())

CACHE.close()

NEW_CACHE = open(CONFIG_PATH + "cache.json", 'w')
NEW_CACHE.write(json.dumps(places, indent=2, sort_keys=True))
NEW_CACHE.close()

# now we want to filter places based on whether the fingerprinter found an outdated WP

# Some fingerprinter subs are in order, which I can use as a filter fn.

# I have decided to save the data as JSON. Indeed, perhaps I'll build my own
# data structure and write it to disk between invocations. Yes!! Cache the
# place details. Like this:

#{ 
#        'some_place_id' : { 'all the data' : 'etc' },
#        'other_place_id' : { 'all the data' : 'etc' },
#        }

# Write that to a file, and don't ask the places API for information on places
# we already have. Brilliant. Write that next so that dev will be faster. Read
# it all at each invocation

# cache the fingerprint results too.
