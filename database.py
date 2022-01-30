from wsgiref.util import request_uri
import pandas as pd
import requests
import sqlite3
import os.path
from config import Config
from alertus_api import alertus_api_func

class process():
    def __init__(self, latitude = 39.7456, longitude = -97.0892,
        threshold_value= 80, check_in_frequency = 30 ,database_name="sample123"):

        self.latitude = latitude
        self.longitude = longitude
        self.threshold_value = int(threshold_value)
        self.check_in_frequency = check_in_frequency
        self.database_name = database_name
    
    def convert_to_date(self, date_time_str, event = "undefined"):
        date_dict = {}
        date_dict[f"{event}_date"] = date_time_str.split("T")[0]
        date_time_str = date_time_str.split("T")[1]
        date_dict[f"{event}_hour"] = date_time_str.split("-")[0]
        return date_dict
    
    def create_database_table(self, df : pd.DataFrame) -> dict[str, list]:
        timestamp = []
        ls_longitude = []
        ls_latitude = []
        first_forecast = [] 
        second_forecast = []
        third_forecast  = []
        ls_alert_generated = []
        ls_alert_id = []

        for i in range(len(df.index) - 3):
            timestamp.append(df["startTime"][i])
            ls_longitude.append(self.longitude)
            ls_latitude.append(self.latitude)
            first_forecast.append(df["temperature"][i])
            second_forecast.append(df["temperature"][i+1])
            third_forecast.append(df["temperature"][i+2])
        
        for i in range(len(first_forecast)):
            alert_generated = False
            alert_id = "no_problem"
            large_range   = int(third_forecast[i] - first_forecast[i])
            small_range_1 = int(second_forecast[i] - first_forecast[i])
            small_range_2 = int(third_forecast[i] - second_forecast[i])
            
            if( abs(large_range) >= int(self.threshold_value) or
            abs(small_range_1) >= int(self.threshold_value) or
            abs(small_range_2) >= int(self.threshold_value)):
            
                alert_generated = True
                if(large_range < 0 ): alert_id= "low-temp"
                else : alert_id= "high-temp"
        
            
            ls_alert_generated.append(alert_generated)
            ls_alert_id.append(alert_id)


            temp_data = {
                'timestamp': timestamp, 
                'longitude': ls_longitude,
                'latitude':ls_latitude,
                'first_forecast':first_forecast,
                'second_forecast':second_forecast,
                'third_forecast':third_forecast,
                'alert_generated':ls_alert_generated,
                'alert_id':ls_alert_id
                }
        
        return temp_data
    
    def weather_api_integration(self):
        response = requests.get(f'https://api.weather.gov/points/{float(self.latitude)},{float(self.longitude)}',headers={"Content-Type":"application/cap+xml"})
        data = response.json()
        response = requests.get(data["properties"]["forecastHourly"])
        data1 = response.json()
        df = pd.DataFrame(data1["properties"]["periods"])
        list_of_time_start = [self.convert_to_date(temp_text, "startTime") for temp_text in df["startTime"]]
        list_of_time_end   = [self.convert_to_date(temp_text ,"endTime") for temp_text in df["endTime"]]
        df2 = pd.DataFrame(list_of_time_start)
        df3 = pd.DataFrame(list_of_time_end)
        frames = [df, df2, df3]
        result = pd.concat(frames,axis=1)
        del result["number"]
        del result["endTime"]

        result = result[['name','startTime','startTime_date', 'startTime_hour',
            'endTime_date', 'endTime_hour','isDaytime', 'temperature', 'temperatureUnit',
            'temperatureTrend', 'windSpeed', 'windDirection', 'icon',
            'shortForecast', 'detailedForecast']]
        return result
    
    def create_database(self):
        con = sqlite3.connect(f'{self.database_name}.db')

        con.execute("""CREATE TABLE samples2
                (Id integer, timestamp text,longitude integer,latitude integer,
                first_forecast integer, second_forecast integer, third_forecast integer,
                alert_generated text, alert_id text)""")
        con.commit()
        con.close()

    def insert_element_to_database(self,database_data):
        con = sqlite3.connect(f'{self.database_name}.db')
        cur = con.cursor()
        for i in range(len(database_data["timestamp"])):
            con.execute(f"""INSERT INTO samples2 VALUES ({i}, '{database_data["timestamp"][i]}',
            {database_data["longitude"][i]},{database_data["latitude"][i]},
            {database_data["first_forecast"][i]},{database_data["second_forecast"][i]},
            {database_data["third_forecast"][i]},'{database_data["alert_generated"][i]}',
            '{database_data["alert_id"][i]}')""")

        con.commit()
        con.close()

    def sql_data_to_list_of_dicts(self,path_to_db, select_query="SELECT * from samples2  LIMIT 10"):
        try:
            con = sqlite3.connect(f'{path_to_db}.db')
            con.row_factory = sqlite3.Row
            things = con.execute(select_query).fetchall()
            unpacked = [{k: item[k] for k in item.keys()} for item in things]
            return unpacked
        except Exception as e:
            print(f"Failed to execute. Query: {select_query}\n with error:\n{e}")
            return []
        finally:
            con.close()

    def clean_sql_database(self, query="DELETE FROM samples2;" ):
        try:
            con = sqlite3.connect(f'{self.database_name}.db')
            con.execute(f"{query}")
            con.commit()
        except Exception as e:
            print(f"Failed to execute. Query: {query}\n with error:\n{e}")
            return []
        finally:
            con.close()

    def main_process(self, clean_database=True):
        request_text = "Empty"
        temp_variable = self.weather_api_integration()
        database_data = self.create_database_table(temp_variable)
        
        if not os.path.exists(f'{self.database_name}.db'):
            self.create_database()
        
        if(clean_database):
            self.clean_sql_database()

        number_of_alert = database_data["alert_generated"].count(True)

        if(number_of_alert):
            alert = alertus_api_func(numberAlert = number_of_alert)
            request_text = alert.post_request()

        self.insert_element_to_database(database_data)
        
        return self.sql_data_to_list_of_dicts(self.database_name), request_text
        