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


module_dir = os.path.dirname(__file__)   #get current directory
file_path = os.path.join(module_dir, 'model.pkl')
model=pickle.load(open(file_path,'rb'))

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
    return render(request,'AQI.html')

def AQI_form(request):
    return render(request,'AQI_form.html')

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


        prediction = predict_custom_trained_model_sample(
                project="954920640321",
                endpoint_id="1037516764155478016",
                location="australia-southeast1",
                instance_list=[transformed_data_list]
            )

        context ={
            
            'prediction' : prediction
        }
        return render(request,'prediction.html',context)
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
