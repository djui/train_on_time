#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import dateutil.parser
import json
import sys
import urllib2


api_url = 'http://api.trafikinfo.trafikverket.se/v1/data.json'
api_key = '4f280ac6b173425a9aef811c3300a725'


def train_info(train_id, location):
  request = '''<REQUEST version="1.0">
                 <LOGIN authenticationkey="{}" />
                 <QUERY objecttype="TrainAnnouncement" orderby="AdvertisedTimeAtLocation">
                   <FILTER>
                     <AND>
                       <EQ name="AdvertisedTrainIdent" value="{}" />
                       <EQ name="LocationSignature" value="{}" />
                       <EQ name="ActivityType" value="Avgang" />
                     </AND>
                   </FILTER>
                 </QUERY>
               </REQUEST>'''
  payload = request.format(api_key, train_id, location)
  headers = {'Content-Type': 'text/xml'}
  req = urllib2.Request(api_url, payload, headers)
  res = urllib2.urlopen(req)
  j = json.load(res)
  return j['RESPONSE']['RESULT'][0]['TrainAnnouncement']


def main(train_id):
  trains = train_info(train_id)
  for train in trains:
    if          train['TypeOfTraffic']     == u'Tåg'   and \
                train['ActivityType']      == 'Avgang' and \
                train['LocationSignature'] == 'Cst'    and \
       'Cst' in train['FromLocation']                  and \
         'U' in train['ToLocation']:
      #departure_time = train['ScheduledDepartureDateTime']
      #arrival_time = train['AdvertisedTimeAtLocation']
      advertised_departure_time = dateutil.parser.parse(train['AdvertisedTimeAtLocation'])
      #estimated_departure_time = dateutil.parser.parse(train['EstimatedTimeAtLocation'])
      #is_preliminary = train['EstimatedTimeIsPreliminary']
      is_canceled = train['Canceled']
      track = train['TrackAtLocation']

      if is_canceled:
        print(';-( Jenny, your train {} is canceled!'.format(train_id))
      else:
        print(':-) Jenny, your train {} is leaving at {} from spår {}.'.format(train_id, advertised_departure_time, track))


if __name__ == '__main__':
  train_id = sys.argv[1] if len(sys.argv) > 1 else '810'
  train_id = sys.argv[2] if len(sys.argv) > 2 else 'Cst'
  main(train_id)
