from bs4 import BeautifulSoup
import requests
import urllib.parse
import time

"""
    This method is used to fetch all the links and patrial data of the used cars available for the given location.
    Arguments:
        location: str
    Returns:
        A dictionary.
"""
def get_used_car_intermediate_data(location):    
    data = {}
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    }
    url_lat_long = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(location+", India") +'?format=json'
    response = requests.get(url_lat_long).json()
    lat = response[0]["lat"]
    lng = response[0]["lon"]
    pagefrom = 0
    count = 1
    try:
        while pagefrom < count:
            print(pagefrom)
            url = f"https://listing.cardekho.com/v1/srp/cardekho?=&cityId=312&connectoid=ad074861-d927-8467-1941-f3bf9f3ae1f3&sessionid=1650fb5567199a7885c2c4fb3f8d815d&lang_code=en&regionId=0&searchstring=used-cars+in+{location}&pagefrom={pagefrom}&sortby=&sortorder=&mink=0&maxk=200000&dealer_id=&regCityNames=&regStateNames=&cellValue=0&lat={lat}&lng={lng}&address={location.capitalize()}, India&Pincode=&pincodeCity={location.capitalize()}"
            req = requests.get(url,headers=header).json()
            count = int(req['data']['count'])
            # print(req)
            for cars in req['data']['cars']:
                # print(json.dumps(cars,indent=4))
                # print("*"*50)
                if "bookNow" in cars:
                    data.setdefault("main_page_link",list()).append(cars['bookNow']['bookingVdpLink'])
                else:
                    data.setdefault("main_page_link",list()).append("https://www.cardekho.com"+cars['vlink'])
                data.setdefault("isAssured",list()).append(cars['isAssured'])
                data.setdefault("car_name",list()).append(cars['dvn'])    
                data.setdefault("model",list()).append(cars['model'].strip(cars['oem']).strip())    
                data.setdefault("brand",list()).append(cars['oem'])
                data.setdefault("location",list()).append(cars['city'])
                data.setdefault("seller_type",list()).append(cars['utype'])
                data.setdefault("selling_location",list()).append(cars['seller_location']['address'])
                data.setdefault("transmission_type",list()).append(cars['transmissionType'])
                data.setdefault("km_driven",list()).append(cars['km'])
                data.setdefault("car_variant",list()).append(cars['carVariant'])
                data.setdefault("fuel_type",list()).append(cars['ft'])
                data.setdefault("selling_price",list()).append(float(cars['p_numeric']))
            pagefrom += 20
            # print(json.dumps(data,indent=4))
            time.sleep(3)
    except Exception as e:
        print("Exception: ",e)
    return data


"""
    Scrape all the data for a given used car.
    Args:
        - url: str
        - required_keys: dict ... to initialize the empty_data_dict
        - isAssured: boolean .... cardekho assured cars have slight different DOM structure
"""
def extract_data_from_used_car_url(url,required_keys,isAssured):
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    }
    req = requests.get(url,headers=header)
    soup = BeautifulSoup(req.content, 'html.parser')
    
    extra_data = {}
    for key in required_keys:
        extra_data[key] = ''
    try:   
        if isAssured:
            on_road_div = soup.find('div',{'class':'priceGraph'}).findAll('div',{'class':'rangetext'})[-1]
            if "On Road Price" in on_road_div.text:
                on_road_price = soup.find('div',{'class':'priceGraph'}).findAll('div',{'class':'rangePrice'})[-1].text
            else:
                on_road_price = ""
            extra_data['On_road_price'] = on_road_price

            overview = [x.find('div',{'class':'value'}).text for x in soup.find('div',{'class':'overviewCArd'}).findAll('div',{'class':'listIcons'})]        
            extra_data['registration_year'] = overview[1]
            extra_data['owner'] = overview[5]
            extra_data['insurance'] = overview[-1] 
            extra_data['make_year'] = int(overview[0])

            max_power_count = 0
            for li in soup.find('div',{'id':'specification-wdght'}).findAll('div',{'class':'listIcons'}):
                # print(li.find('div',{'class':'head'}).text)
                if max_power_count < 1 or li.find('div',{'class':'head'}).text != "Max Power":
                    extra_data[li.find('div',{'class':'head'}).text] = li.find('div',{'class':'value'}).text
                if li.find('div',{'class':'head'}).text == "Max Power":
                    max_power_count += 1
                # print(li.find('div',{'class':'value'}).text)

            for sec in soup.find('div',{'class':'featuresCard'}).findAll('div',{'class':'borderBottom'}):
                # print(sec.find('h3').text)
                # print([x.text.strip() for x in sec.findAll('li',{'class':'fchild'})])
                extra_data[sec.find('h3').text.strip()] = [x.text.strip() for x in sec.findAll('li',{'class':'fchild'})]
        else:
            try:
                on_road_price = soup.find('div',{'class':'EmiSecUC'}).text.replace(u'\xa0', u' ')
            except:
                print("no on road price mentioned")
                on_road_price = ''
            extra_data['On_road_price'] = on_road_price
            overview = [x.text for x in soup.find('ul',{'class':'gsc_row clearfix'}).findAll('div',{'class':'iconDetail'})]

            extra_data['registration_year'] = overview[0]
            extra_data['owner'] = overview[3]
            extra_data['insurance'] = overview[-2]

            max_power_count = 0
            for li in soup.find('div',{'class':'SpecsFeatureList'}).findAll('li'):
                # print(li.find('div',{'class':'smallSpec'}).text)
                if max_power_count < 1 or li.find('div',{'class':'smallSpec'}).text != "Max Power":
                    extra_data[li.find('div',{'class':'smallSpec'}).text] = li.find('div',{'class':'largeSpec'}).text
                if li.find('div',{'class':'smallSpec'}).text == "Max Power":
                    max_power_count += 1
                # print(li.find('div',{'class':'largeSpec'}).text)

            for sec in soup.find('div',{'data-track-section':'Features'}).findAll('div',{'class':'borderBottom'}):
                # print(title)
                # print([x.text.replace("•","").strip() for x in sec.findAll('li',{'class':'fchild'})])
                extra_data[sec.find('h3').text.replace("Features","").strip()] = [x.text.replace("•","").strip() for x in sec.findAll('li',{'class':'fchild'})]
    except Exception as e:
        print(e)
    return extra_data

