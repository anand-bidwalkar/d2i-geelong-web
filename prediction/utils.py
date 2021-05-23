import googlemaps
import requests
import json
from typing import Dict

'''
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
'''

API_key = 'AIzaSyCLYt6uWqP3gI8ubO8BkcfmmBdi8by1bFQ' #Insert your API
gmaps = googlemaps.Client(key=API_key)
radius = 1000

sub_list = ['Armstrong Creek', 'Bell Park', 'Bell Post Hill', 'Belmont', 'BreakWater', 'Corio', 'Drumcondra',
             'East Geelong', 'Freshwater Creek', 'Geelong', 'Geelong West', 'Grovedale', 'Hamlyn Heights', 'Herne Hill', 
              'Highton', 'Lara', 'Manifold Heights', 'Marshall', 'Mount Duneed', 'Newcomb', 'Newtown', 'Norlane', 
              'North Geelong', 'North Shore', 'RippleSide', 'South Geelong', 'St Albans Park', 'Thomson',
               'Wandana Heights', 'Waurn Ponds', 'Whittington']

def get_suburb_encoder(sub_selection):
    sub_length = len(sub_list)
    sub_encoder = [0 for x in range(0, sub_length)]
    sub_encoder[int(sub_selection)] = 1
    return sub_encoder

def find_number_obj(address, suburb_name, keyword, radius):
  
  #Find the Lat and Long of the Address
  geocode_result = gmaps.geocode(f"{address + ' ' +  suburb_name}, Victoria, Australia")[0]['geometry']['location']
  lat_value = geocode_result['lat']
  long_value = geocode_result['lng']

  #Find number of obj around the specific address
  url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat_value}, {long_value}&radius={radius}&keyword={keyword}&key={API_key}"
  respon = requests.get(url)
  jj = json.loads(respon.text)
  results = jj['results']
  output = len(results)
  return output

def get_suburb_info(address_name, sub_selection):
    suburb_name = sub_list[int(sub_selection)]
    no_school = find_number_obj(address_name, suburb_name, "school", radius)
    no_shop = find_number_obj(address_name, suburb_name, "shop", radius)
    no_station = find_number_obj(address_name, suburb_name, "station", radius)
    no_park = find_number_obj(address_name, suburb_name, "park", radius)
    no_hospital = find_number_obj(address_name, suburb_name, "hospital", radius)
    return [no_school, no_shop, no_station, no_park, no_hospital]


def predict_custom_trained_model_sample(
    project: str,
    endpoint_id: str,
    instance_list: list,
    location: str = "australia-southeast1",
    api_endpoint: str = "australia-southeast1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )   

    response = client.predict(
        endpoint=endpoint, instances=instance_list
    )
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    predictions = response.predictions
    print(predictions)
    return predictions[0][0]
