#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import dateutil.parser
import json
import pagerduty
import sys
import urllib2


trafiklab_api_url = 'http://api.trafikinfo.trafikverket.se/v1/data.json'
trafiklab_api_key = '{{YOUR_API_KEY_HERE}}'
pagerduty_api_key = '{{YOUR_API_KEY_HERE}}'


def train_info(train_id, location):
  request = '''<REQUEST version="1.0">
                 <LOGIN authenticationkey="{}" />
                 <QUERY objecttype="TrainAnnouncement" orderby="AdvertisedTimeAtLocation">
                   <FILTER>
                     <AND>
                       <GT name="AdvertisedTimeAtLocation" value="07:41:00" />
                       <EQ name="AdvertisedTrainIdent" value="{}" />
                       <EQ name="LocationSignature" value="{}" />
                       <EQ name="ActivityType" value="Avgang" />
                     </AND>
                   </FILTER>
                 </QUERY>
               </REQUEST>'''
  payload = request.format(trafiklab_api_key, train_id, location)
  headers = {'Content-Type': 'text/xml'}
  req = urllib2.Request(trafiklab_api_url, payload, headers)
  res = urllib2.urlopen(req)
  j = json.load(res)
  return j['RESPONSE']['RESULT'][0].get('TrainAnnouncement', None)


def main(args):
  train_id = args[1] if len(args) > 1 else '810'
  location = args[2] if len(args) > 2 else 'Cst'

  pager = pagerduty.PagerDuty(pagerduty_api_key)

  trains = train_info(train_id, location)

  if not trains:
    msg = 'No train information could be found!'
    ## For now assume that if no info could be found, that it's either:
    ##   (a) maintenance windowo night
    ##   (b) weekend.
    # pager.trigger(msg)
    print('\033[1;31m' + msg + '\033[0m')
    sys.exit(2)

  for train in trains:
    track           = train['TrackAtLocation']
    is_canceled     = train['Canceled']
    advertised_time = dateutil.parser.parse(train['AdvertisedTimeAtLocation'])
    estimated_time  = dateutil.parser.parse(train['EstimatedTimeAtLocation']) if 'EstimatedTimeAtLocation' in train else None
    is_late         = True if estimated_time else False

    if is_canceled:
      msg = 'Train {} is canceled!'.format(msg, train_id)
      pager.trigger(msg)
      print('\033[1;31m' + msg + '\033[0m')
      sys.exit(1)
    elif is_late:
      msg = 'Train {} is scheduled late for {} at spår {}.'.format(train_id, estimated_time.strftime('%H:%M'), track)
      pager.trigger(msg)
      print('\033[1;33m' + msg + '\033[0m')
      sys.exit(1)
    else:
      msg = 'Train {} is scheduled on time for {} at spår {}.'.format(train_id, advertised_time.strftime('%H:%M'), track)
      #pager.trigger(msg)
      print('\033[1;32m' + msg + '\033[0m')
      sys.exit(0)


if __name__ == '__main__':
  main(sys.argv)
