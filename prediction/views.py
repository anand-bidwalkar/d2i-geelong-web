from django.shortcuts import render
from .forms import SuburbForm
from django.contrib.auth.decorators import login_required
import pickle
import os
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import HttpResponse, render, redirect
from . forms import WeatherForm, RegionForm
from pandas import DataFrame
import numpy as np
import pandas as pd
import sklearn
from sklearn import preprocessing
import csv
import io
import joblib
import os

from django.conf import settings
from django.contrib import messages

from prediction.encoder import OneHotEncoder

import plotly.express as px
from . utils import *

import requests
import json

# Additional imports for AQI forecast predictions
import pytz
from datetime import datetime
import math
from scipy.special import inv_boxcox
import plotly.graph_objects as go

module_dir = os.path.dirname(__file__)   #get current directory
scaler_file_path = os.path.join(module_dir, 'scaler.pkl')
transformer=pickle.load(open(scaler_file_path,'rb'))

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/login.html', {'form': form})

def home(request):
    return render(request,'index.html')

def population(request):
    return render(request,'Population_prediction.html')

def wifi(request):
    return render(request,'wifi_analysis.html')

def crash(request):
    return render(request,'crash.html')

def health(request):
    return render(request,'health.html')

def urban(request):
    return render(request,'urbanplanning.html')

def parking(request):
    return render(request,'parking.html')

def parkingdashboard(request):
    return render(request,'parkingdashboard.html')

def parkinganalysis(request):
    return render(request,'parkinganalysis.html')

def AQI(request):

    #First we are grabbing the current weather forecast for Geelong - you can modify lat, lon to grab forecasts for other areas

    lat = '-38.150002'
    lon = '144.350006'
    exclude = 'minutely,hourly,alerts'
    units = 'metric'
    api_key = '5605e86f9bd5db980b3c2dfbd330811e'

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat=-38.150002&lon=144.350006&exclude=minutely,hourly,alerts&units=metric&appid=5605e86f9bd5db980b3c2dfbd330811e'


    response = requests.get(url)
    weather_data = json.loads(response.text)

    # we will pass the plotly graphs and other data through to the page with a dictionary
    page_data = {}

    # next we are extracting the daily weather forecasting data for the next 7 days
    
    daily = weather_data['daily']

    # we will pass through the weekly forecast to the page - not sure if we are going to use it yet....
    weekly_forecast = []

    for entry in daily:
        dt = datetime.fromtimestamp(entry['dt'], pytz.timezone('Australia/Victoria'))
        temp = entry['temp']
        wind_gust = entry['wind_gust']
        wind_dir = entry['wind_deg']
        try:
            rain = entry['rain']
        except:
            rain = 0
        
        forecast = {'day' : dt,
                    'maxtemp' : temp['max'],
                    'rainfall' : rain,
                    'spd_maxgust' : wind_gust,
                    'month' : dt.month}
        
        weekly_forecast.append(forecast)

    # add the forecast to the page data   
    page_data['forecast'] = weekly_forecast

    # Creating a dataframe to work with the feature transformations
    dfForecast = pd.DataFrame(weekly_forecast)
    dfForecast['mnth_sin'] = np.sin((dfForecast.month-1)*(2.*np.pi/12))
    dfForecast['month_cos'] = np.cos((dfForecast.month-1)*(2.*np.pi/12))
    dfForecast.rainfall = dfForecast.rainfall.transform(lambda x: math.log(x + 1))
    dfForecast = dfForecast.drop(['day', 'month'], axis = 1)

    # manually scaling the data according to the parameters of the models training data
    temp_mean = 20.295245
    temp_sd = 5.323982

    rf_mean = 0.154721
    rf_sd = 0.296177

    ws_mean = 36.223193
    ws_sd = 11.415994

    dfForecast['maxtemp'] = dfForecast['maxtemp'].apply(lambda x: (x - temp_mean) / temp_sd)
    dfForecast['rainfall'] = dfForecast['rainfall'].apply(lambda x: (x - rf_mean) / rf_sd)
    dfForecast['spd_maxgust'] = dfForecast['spd_maxgust'].apply(lambda x: (x - ws_mean) / ws_sd)

    #debug print to console
    #print(dfForecast)

    # from here, we run the transformed weather data against the model through API endpoint
    endpoint_url = 'http://d2i-model-api.herokuapp.com/bulk_aqi_prediction/'
    forecast_data = dfForecast.values
    forecast_data = forecast_data.tolist()

    aqi_forecast = []
    
    j_bulk = json.dumps(forecast_data)
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(endpoint_url, data=j_bulk, headers=headers)
    result = json.loads(r.text)

    aqi_forecast = [float(i) for i in result['Results']]
    
    #this line can be uncommented to use the model locally
    #aqi_forecast = aqi_model.predict(dfForecast)

    # the model is predicitng a box cox transformation of the target variable, inverse that transformation to get the index value
    fitted_lambda = 0.16332629036390786
    aqi_forecast = inv_boxcox(aqi_forecast, fitted_lambda)
    #debug print to console
    #print(aqi_forecast)

    

    # This next part will plot the gauge plots from plotly and render html strings
    days = []
    for entry in daily:
        dt = datetime.fromtimestamp(entry['dt'], pytz.timezone('Australia/Victoria'))
        friendly_date = dt.strftime('%d %B %Y')
        days.append(friendly_date)

    i = 0
    while i < len(days):
        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = aqi_forecast[i],
            mode = "gauge+number",
            title = {'text': f"pm10 index forecast: {days[i]}"},
            gauge = {'axis': {'range': [None, 150]},
                    'bar': {'color': "green"},
                    'steps' : [
                        {'range': [0, 51], 'color': "lightgreen"},
                        {'range': [51, 101], 'color': "yellow"},
                        {'range': [101, 150], 'color': "orange"}],
                    #'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': aq_forecast[i]}
                    }))
        
        graph = fig.to_html(full_html=False, default_height=300, default_width=400)
        page_data[f'plot_{i}'] = graph
        i += 1  
    
    #debug to console
    print(page_data.keys())

    # debug to console
    # print(plots)

    # this section will 
    if request.method == 'POST':
        data = []
        for key in request.POST:
            print(key)
            if key != 'csrfmiddlewaretoken':
                value = request.POST[key]
                data.append(value)
        
        data = [float(i) for i in data]
        #print(data)

        feats = ['maxtemp', 'rainfall', 'spd_maxgust', 'month']

        onthefly = dict(zip(feats, data))
        #print(onthefly)

        # performing the same data transformation on the submitted data
        dfOnTheFly = pd.DataFrame(onthefly, index = [0])
        dfOnTheFly['mnth_sin'] = np.sin((dfOnTheFly.month-1)*(2.*np.pi/12))
        dfOnTheFly['month_cos'] = np.cos((dfOnTheFly.month-1)*(2.*np.pi/12))
        dfOnTheFly.rainfall = dfOnTheFly.rainfall.transform(lambda x: math.log(x + 1))
        dfOnTheFly = dfOnTheFly.drop(['month'], axis = 1)

        dfOnTheFly['maxtemp'] = dfOnTheFly['maxtemp'].apply(lambda x: (x - temp_mean) / temp_sd)
        dfOnTheFly['rainfall'] = dfOnTheFly['rainfall'].apply(lambda x: (x - rf_mean) / rf_sd)
        dfOnTheFly['spd_maxgust'] = dfOnTheFly['spd_maxgust'].apply(lambda x: (x - ws_mean) / ws_sd)

        # run the transformed data through the model

        endpoint = 'http://d2i-model-api.herokuapp.com/bulk_aqi_prediction/'

        otf_data = dfOnTheFly.values
        otf_data = otf_data.tolist()
        j_data = json.dumps(otf_data)
        print(f'j_data: {j_data}')
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        r = requests.post(endpoint, data=j_data, headers=headers)
        print(f'on the fly: {r}')
        result = json.loads(r.text)

        '''aqi_predict = aqi_model.predict(dfOnTheFly)
        print(aqi_predict)'''

        aqi_predict = inv_boxcox(float(result['Results'][0]), fitted_lambda)
        #print(f'Result from box cox inversion: {aqi_predict}')

        #generate an on the fly plot for the submitted data
        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = aqi_predict,
            mode = "gauge+number",
            title = {'text': f"pm10 index prediction"},
            gauge = {'axis': {'range': [None, 150]},
                    'bar': {'color': "green"},
                    'steps' : [
                        {'range': [0, 51], 'color': "lightgreen"},
                        {'range': [51, 101], 'color': "yellow"},
                        {'range': [101, 150], 'color': "orange"}],
                    }))
        
        graph = fig.to_html(full_html=False, default_height=300, default_width=400)

        #add the plot and the submitted data to the page data
        page_data['plot_onthefly'] = graph
        page_data['submitted_data'] = onthefly


        #prediction=model.predict([data])
        #form = SuburbForm(request.POST)
        

    
    return render(request,'AQI.html', page_data)

def aboutus(request):
    return render(request,'aboutus.html')

def predict(request):
    
    if request.method == 'POST':
        data = []
        suburb_selection = request.POST['suburb']
        house_address = request.POST['haddress']
        suburb_encoder = get_suburb_encoder(suburb_selection)
        data.extend(suburb_encoder)
        last_sell_price = request.POST['fname']
        data.extend([last_sell_price])
 
        bedrooms = request.POST['bedrooms']
        data.extend([bedrooms])

        bathrooms = request.POST['bathrooms']
        data.extend([bathrooms])

        cars = request.POST['cars']
        data.extend([cars])

        sub_info = get_suburb_info(house_address, suburb_selection)
        data.extend(sub_info)

        rent = request.POST['rent']
        data.extend([rent])
        
        auction = request.POST['auction']
        data.extend([auction])

        lname = request.POST['lname']
        data.extend([lname])
        
        input_data = [float(x) for x in data]
        data_df = DataFrame(input_data)

        transformed_data = transformer.fit_transform(data_df)
        transformed_data_list = [x[0] for x in transformed_data]

        
        # Production
        url = 'https://d2i-model-api.herokuapp.com/api/'
        '''

        url = 'http://127.0.0.1:5000/api/'
        '''

        j_data = json.dumps([transformed_data_list])
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        r = requests.post(url, data=j_data, headers=headers)
        s = json.loads(r.text)
        pred_result = s['Result'] if 'Result' in s.keys() else None

               
        #prediction = model.predict([transformed_data_list])
        
        '''
        # Use this when project gets dedicated GCP account
        prediction = predict_custom_trained_model_sample(
                project="xxxxx",
                endpoint_id="xxxx",
                location="australia-southeast1",
                instance_list=[transformed_data_list]
            )
        '''
        context ={
            'prediction' : pred_result
        }
        return render(request,'property_prediction.html',context)
    else:
        form = SuburbForm()
        context ={
            'form':form
        }
        
    return render(request,'property.html',context)



def contactus(request):
    return render(request, 'contactus.html')

def wifi(request):
    return render(request, 'wifi.html')

def weather_form(request):
    '''
    This function is called by urls.py when /wifi/weather_form is requested.

    if the action calling the form is a POST, then the function collects the submitted details and
    calls the survival_check function

    The results of the survival_check function are parsed and passed to the django messages framework
    to post the results below the form
    '''
    if request.method=='POST':
        form = WeatherForm(request.POST)
        if form.is_valid():
            prcp = form.cleaned_data['prcp']
            tavg = form.cleaned_data['tavg']
            cbdreg = form.cleaned_data['cbdreg']
            
            query_dict = (request.POST).dict()
            df_weather = pd.DataFrame(query_dict, index=[0])
            print(df_weather)
            #print(survival_check(df_passenger))
            city_pop = weather_check(df_weather)
            
            messages.success(request, "The median population in the city for this weather is predicted to be {}".format(city_pop))
    form = WeatherForm()

    return render(request, 'weather_form.html', {'form': form})


def weather_check(weather_data):
    '''
    This function runs the model on a single set of weather data
    form
    '''
    weather_data.drop(['csrfmiddlewaretoken'], inplace = True, axis = 1)
    print(weather_data)
    lr_model = joblib.load(os.path.join(settings.MODELS, 'regmodel.dump'))
    #data_array = weatherdata.iloc[0].as_matrix()
    #rf_scaler = joblib.load(os.path.join(settings.MODELS, 'rf_scaler.dump'))
    #rf_model = joblib.load('/titanic/models/rf_model.dump')
    #rf_scaler = joblib.load('titanic/models/rf_scaler.dump')
    #test_X = rf_scaler.transform(passenger_data)
    #print(test_X)
    print('weather data:')
    print(weather_data)
    y_pred = lr_model.predict(weather_data)
    df_results = pd.DataFrame(y_pred, columns=['med_pop'])
    print(df_results)
    print('The median population in the city for this weather is predicted to be {}'.format(df_results['med_pop'][0]))

    return (df_results)

def weather_prediction(request):
    print(request.POST)

    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months = ['January', 'February','March','April','May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    rainstatus = ['No', 'Yes']

    month = int(request.POST.get('month'))
    weekday = int(request.POST.get('weekday'))
    mintemp = int(request.POST.get('mintemp'))
    maxtemp = int(request.POST.get('maxtemp'))
    rain = int(request.POST.get('rainfall'))

    
    devices = ['hawk-013a4f', 'hawk-013a23', 'hawk-013a51', 'hawk-013a33',
       'hawk-013a21', 'hawk-013a1e', 'hawk-013a2e', 'hawk-013a31',
       'hawk-013a2c', 'hawk-013a22', 'hawk-013a20', 'hawk-013a1f',
       '014d9e', '014d9a', '014daa', '014d98', '014de9', '014dc6',
       '014db4', '014ddb', '014dbe']
    
    col_names = ['device_id', 'month', 'dayofweek', 'mintemp', 'maxtemp', 'rainfall']
    

    row_list = []
    for device in devices:
        for n in range(0, 7):

            row = {"device_id": device, 
                    "month": month, 
                    "dayofweek": n, 
                    "mintemp": mintemp, 
                    "maxtemp": maxtemp, 
                    "rainfall": rain}
            row_list.append(row)

    dfdata = pd.DataFrame(row_list)

    encoder = OneHotEncoder()
    encoded = pd.DataFrame(encoder.fit_transform(dfdata[['dayofweek', 'device_id']]))
    dfencoded = dfdata.join(encoded)

    dfmodel = dfencoded.drop(['device_id', 'dayofweek', ], axis = 1)


    rf_model = joblib.load(os.path.join(settings.MODELS, 'rf_model_1.dump'))
    y_pred = rf_model.predict(dfmodel)
    dfresults = pd.DataFrame(y_pred, columns=['dev_count'])
    dfdata = dfdata.join(dfresults)

    dfrequested = dfdata[(dfdata['dayofweek'] == weekday)][['device_id', 'dev_count']]
    dfrequested.sort_values(['dev_count'], inplace = True, ascending = False)
    
    dfdevices = pd.read_csv('wifi/models/devices.csv')
    dfdevices.columns = ['device_id', 'location', 'lat', 'long']
    #dfrequested.join(dfdevices, on = 'device_id', how = 'inner')
    dfrequested = dfrequested.merge(dfdevices, how = 'inner', on = 'device_id')
    dfrequested['dev_count'] = dfrequested['dev_count'].astype(int)
    result_table = dfrequested.to_html(classes=['w3-table-all'])

    px.set_mapbox_access_token(open("wifi/models/.mapbox_token").read())
    fig = px.scatter_mapbox(dfrequested, lat="lat", lon="long",     color="location", size="dev_count",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=30, zoom=11)
    
    map_graph = fig.to_html(full_html=False, default_height=700, default_width=1000)

    form_data = {
        "mintemp": request.POST.get('mintemp'),
        "maxtemp": request.POST.get('maxtemp'),
        "month": months[int(request.POST.get('month'))],
        "weekday": weekdays[int(request.POST.get('weekday'))], 
        "rainfall": rainstatus[int(request.POST.get('rainfall'))], 
        "result_table": result_table,
        "map_graph": map_graph
    }

    


    print(dfrequested.info())
    print(dfrequested)

    return render(request, "wifi_device_count_prediction.html", form_data)


def region_form(request):
    '''
    This function is called by urls.py when /wifi/weather_form is requested.

    if the action calling the form is a POST, then the function collects the submitted details and
    calls the survival_check function

    The results of the survival_check function are parsed and passed to the django messages framework
    to post the results below the form
    '''
    if request.method=='POST':
        form = RegionForm(request.POST)
        if form.is_valid():
            prcp = form.cleaned_data['prcp']
            tavg = form.cleaned_data['tavg']
            cbdreg = 0
            
            query_dict = (request.POST).dict()
            print(query_dict)
            df_weather = pd.DataFrame(query_dict, index=[0])
            df_weather = df_weather.append({'prcp': form.cleaned_data['prcp'], 
                                            'tavg': form.cleaned_data['tavg'],
                                            'cbdreg': 0}, ignore_index=True)
            
            df_weather = df_weather.append({'prcp': form.cleaned_data['prcp'], 
                                            'tavg': form.cleaned_data['tavg'],
                                            'cbdreg': 1}, ignore_index=True)
            df_weather = df_weather.iloc[1:]
            print(df_weather)
            #print(survival_check(df_passenger))
            city_pop = weather_check(df_weather)
            print(city_pop)
            messages.success(request, "The median population in the CBD for this weather is predicted to be {:02.3f}".format(city_pop['med_pop'][0]))
            messages.success(request, "The median population in the Regional areas for this weather is predicted to be {:02.3f}".format(city_pop['med_pop'][1]))
    form = RegionForm()

    return render(request, 'region_form.html', {'form': form})
