from bs4 import BeautifulSoup
import requests
import urllib.parse
import time
import pandas as pd
import json

header = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
}

locations = json.load(open('./config/locations_carwale.json'))

data = []
for city_id,loc in locations.items():
	print(loc)
	page_num = 1
	while True:
		try:
			url = "https://www.carwale.com/webapi/classified/stockfilters/?city={}&pc=10&sc=-1&so=-1&pn={}&lcr=72&ldr=0&lir=0".format(city_id,page_num)
			print(page_num," --- ",url)
			res = requests.get(url,headers=header).json()
			for z in res['ResultData']:
				dct = {
					"car_name":z['CarName'],
					"brand":z['MakeName'],
					"brand_id":z['MakeId'],
					"model":z['RootName'],
					"model_variant":z['ModelName'],
					"model_id":z['ModelId'],
					"location":z['CityName'],
					"fuel_type":z['Fuel'],
					"registration_year":z['MakeYear'],
					"owner":z['NoOfOwners'],
					"kilometers_driven":int(z['KmNumeric']),
					"selling_price":float(z['PriceNumeric']),
					"color":z['Color'],
					"warranty":z['HasWarranty'],
					"manufacture_date":z['MfgDate'],
					"entry_date":z['EntryDate'],
					"url":"https://www.carwale.com"+z['Url']
				}
				data.append(dct)
			page_num += 1
		except Exception as e:
			print(e)
			break

df = pd.DataFrame(data)
df.to_csv('./output/carwale_v1/carwale_intermediate_v1.csv',index=False)