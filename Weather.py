#!/usr/bin/env python
from collections import ChainMap, namedtuple
from datetime import datetime, timedelta
from config import api_key, url, history_file_name
from uuid import uuid4
from save_weather_history import save_history
import requests
import pandas as pd
from geopy.geocoders import Nominatim

class Weather:

    units="metric"
    geolocator = Nominatim(user_agent="WeatherApp")
    list_of_attr = ["id","city_name","temperature","wind_speed",
                    "pressure","condition","datetime"]
    instance_hist_template = namedtuple("instance_hist", list_of_attr)

    def __init__(self,city_name):
        self.id = uuid4().hex
        self.city_name = city_name
        self.location = self.get_location(self.city_name)
        self._response = self.get_response(self.location)
        if self._response is not None:
            self.temperature = self._response["main"]["temp"]
            self.wind_speed = self._response["wind"]["speed"]
            self.pressure = self._response["main"]["pressure"]
            self.condition = self._response["weather"][0]["main"]
            self.datetime = (datetime.utcnow()  + timedelta(seconds = self._response["timezone"])).isoformat(timespec='minutes')
            self.is_fahrenheit = False
            self.create_instance_hist()
            save_history(self._instance_hist,history_file_name)

    def get_location(self,*args):
        try:
            Loc_tup = namedtuple("Location", "lat lon")
            location = Weather.geolocator.geocode(args, language='en')
            return Loc_tup(location.raw["lat"],location.raw["lon"])
        except AttributeError:
            return None
    
    def get_response(self,loc):
        if loc:
            full_url = f"{url}lat={loc.lat}&lon={loc.lon}&appid={api_key}&units={Weather.units}"
            response = requests.get(full_url, headers = {"Accept":"application/json"}).json()
            return response    
        else:
            return None
       
    def create_instance_hist(self):
        self._instance_hist = pd.DataFrame(data=[Weather.instance_hist_template(self.id,
            self.city_name,
            self.temperature,
            self.wind_speed,
            self.pressure,
            self.condition,
            self.datetime)])
        
    def show_info(self):
        """repr func"""
        return self._instance_hist

    def to_fahrenheitdegree(self):
        """From Celsius to Fahrenheit"""
        self.is_fahrenheit = True
        self.temperature = (self.temperature * 9/5) + 32
    
    def to_celsius(self):
        """From Fahrenheit to Celsius"""
        self.is_fahrenheit = False
        self.temperature = (self.temperature - 32) * 5/9

    def give_advise(self):
        """get recommendations"""
        switcher = {
            "Rain": "Не забудь взять с собой зонтик!",
            "Clouds": "Так пасмурно, что даже солнца не видно!",
            "Clear": "Наслаждайся хорошей погодой!"
        }
        return switcher.get(self.condition, "I can not recommend you anything :( ")

    @property
    def sunrise(self):
        return datetime.fromtimestamp(self._response["sys"]["sunrise"]).strftime("%I:%M:%S") + " AM"

    @property
    def sunset(self):
        return datetime.fromtimestamp(self._response["sys"]["sunset"]).strftime("%I:%M:%S") + " PM"

    @property
    def correct_response(self):
        return True if self._response is not None else False