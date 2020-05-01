import urllib.request
import json
from modules.props.ConfigProps import aliceAnt
from datetime import datetime
import pysolr
from queue import Queue
from threading import Thread
# from kafka import KafkaProducer

try:
	import thread
except ImportError:
	import _thread as thread
import time

props = aliceAnt

print('Testing ...')
solr = pysolr.Solr('http://mohu.local:8983/solr/test', always_commit=True)
solr.ping()

# producer = KafkaProducer(bootstrap_servers='localhost:9092')
# producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def test1():
	interval = '5min'
	symbol = 'IBM'
	alphavantage_url = '%s/query?function=TIME_SERIES_INTRADAY&symbol=%s&interval=%s&outputsize=full&apikey=%s'%(props['ALPHAVANTAGE_URL'], symbol, interval, props['ALPHAVANTAGE_KEY'])
	print(alphavantage_url)

	req = urllib.request.urlopen(alphavantage_url)
	data = req.read()
	json_obj = json.loads(data)
	series_data = list([])
	queue = Queue()
	for key in json_obj.keys():
		print(key)
		if 'Time Series' in key:
			tick = json_obj[key]
			tick_keys = tick.keys()
			for tick_key in tick_keys:
				tick_obj = {
					"instrument_token":"ibm",
					"last_traded_price": tick[tick_key]["4. close"],
					"last_traded_time": tick_key, 
					"trade_volume": tick[tick_key]["5. volume"],
					"exchange_timestamp": tick_key, 
					"open_price": tick[tick_key]["1. open"],
					"high_price": tick[tick_key]["2. high"],
					"low_price": tick[tick_key]["3. low"],
					"close_price": tick[tick_key]["4. close"],
					"yearly_high_price": tick[tick_key]["2. high"],
					"yearly_low_price": tick[tick_key]["2. high"]
				}
				print(tick_obj)
				solr.add(tick_obj)
				# producer.send('test', tick_obj)
				# producer.flush()
			print('Completed posting data to solr server')
	queue.join()

test1()
