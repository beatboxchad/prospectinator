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

# a piece of the dotfile search bit -- TODO make this more dynamic.
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


# grab the list of places
base_url  = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location=%s&keyword=*&&radius=5000&key=%s"
query_url = urllib.request.Request(base_url % (location, gmaps_apikey))
response  = json.loads(urllib.request.urlopen(query_url).read().decode('utf-8'))

# now we get the details of each place.
ids        = [result["place_id"] for result in response["results"]]
place_url  = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s"

def run_fingerprint(place_id):
    client = MongoClient(dbhost, dbport)
    db     = client.prospectinator
    places = db.places

    query_url = urllib.request.Request(place_url % (place_id, gmaps_apikey))

    # retrieve a record by the place id. If it is not present, create a new one.
    place_doc = places.find_one({'result.place_id' : place_id}) or json.loads(urllib.request.urlopen(query_url).read().decode('utf-8'))
    if 'website' in place_doc['result']:
        if 'fingerprint' not in place_doc:
            w = wig(url = place_doc['result']['website'])
            w.run()
            results = OutputJSON(w.options, w.data)
            results.add_results()
            place_doc['fingerprint'] = results.json_data
            places.save(place_doc)

    return 

pool = Pool()
pool.map(run_fingerprint, ids)
