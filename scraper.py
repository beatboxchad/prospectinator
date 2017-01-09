#!/usr/bin/env python
import json
import urllib.request
import os
import re

from pprint import pprint
from wig.wig import wig
from wig.classes.output import OutputJSON
from pymongo import MongoClient
from multiprocessing import Pool
pool = Pool()

# a piece of the dotfile search bit -- TODO make this mroe dynamic.
# xdg-settings, whatever on mac. Also implement CL args
CONFIG_PATH    = os.path.expanduser("~/.config/prospectinator/")
if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)

with open(CONFIG_PATH + 'prospectinator.json', 'r') as defaults_file:    
    defaults = json.load(defaults_file)

gmaps_apikey  =  defaults["gmaps_apikey"]
location      =  defaults["location"]
dbhost        =  defaults["dbhost"]
dbport        =  defaults["dbport"]

client  =  MongoClient(dbhost, dbport)
DB      =  client.prospectinator

coll    = DB.places

# grab the list of places
base_url  = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location=%s&keyword=*&&radius=5000&key=%s"
query_url = urllib.request.Request(base_url % (location, gmaps_apikey))
response  = json.loads(urllib.request.urlopen(query_url).read().decode('utf-8'))

# now we get the details of each place.
ids        = [result["place_id"] for result in response["results"]]
place_url  = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s"
    
def run_fingerprint(place_id):
    # FIXME gross name
    print(place_id)
    my_query_url = urllib.request.Request(place_url % (place_id, gmaps_apikey))
    # FIXME better interrogation? Actually for this stage this is fine. We can
    # inspect the data for fingerprinted later
    if not place_id in places:
        places[place_id] = json.loads(urllib.request.urlopen(my_query_url).read().decode('utf-8'))

    if 'website' in places[place_id]['result']:
        if 'fingerprint' not in places[place_id]:
            places[place_id]['fingerprint'] = []
            w = wig(url = places[place_id]['result']['website'])
            w.run()
            results = OutputJSON(w.options, w.results)
            try:
                results.add_results()
            except KeyError:
                pass

            places[place_id]['fingerprint'].append(results.json_data)
    return

pool.map(run_fingerprint, ids)


#cleanup and write
CACHE.close()
NEW_CACHE = open(CONFIG_PATH + "cache.json", 'w')
NEW_CACHE.write(json.dumps(places, indent=2, sort_keys=True))
NEW_CACHE.close()
