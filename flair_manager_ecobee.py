#from pyowm import OWM
import time
import requests
import json
import datetime 
import os.path
import os 
import collections
#import scipy 

class AveragingBuffer(object):
    def __init__(self, maxlen):
        assert( maxlen>1)
        self.q=collections.deque(maxlen=maxlen)
        self.xbar=0.0
    def append(self, x):
        if len(self.q)==self.q.maxlen:
            # remove first item, update running average
            d=self.q.popleft()
            self.xbar=self.xbar+(self.xbar-d)/float(len(self.q))
        # append new item, update running average
        self.q.append(x)
        self.xbar=self.xbar+(x-self.xbar)/float(len(self.q))

def ecobee_get_credentials():
	if os.path.isfile('./credentials_ecobee.txt'):
		credentials = open("credentials_ecobee.txt","r")
		data = json.loads(credentials.read())
		credentials.close()
		access_token_key_id = data['access_token']
		refresh_token_key_id = data['refresh_token']
#		print("Current Refresh Token is:",refresh_token_key_id)
	return data

def ecobee_refresh_credentials(apikey_id,refresh_token):
	url = "https://api.ecobee.com/token?grant_type=refresh_token&refresh_token=" + refresh_token + "&client_id=" + apikey_id + "&ecobee_type=jwt"
	payload = {}
	headers = {}
	response = requests.request("POST", url, headers=headers, data = payload)
	text_response=response.text
	os.system('cp credentials_ecobee.txt credentials_ecobee.txt.prev')  
	credentials = open("credentials_ecobee.txt","w+")
	credentials.write(text_response)
	credentials.close()
	data = response.json()
#	print(data)
	return data

def ecobee_switch_hothours(access_token):
	url = "https://api.ecobee.com/1/thermostat?format=json"
	hothours = open("thermostat_hothours.json","r")
	hothours_text = hothours.read()
	hothours.close()
	headers = {'Content-Type': 'application/json;charset=UTF-8','Authorization': 'Bearer ' + access_token}
	response = requests.request("POST", url, headers=headers, data=hothours_text.encode('utf8'))
	text_response=response.text
#	print(text_response)
	return text_response

def ecobee_switch_coldhours(access_token):
	url = "https://api.ecobee.com/1/thermostat?format=json"
	coldhours = open("thermostat_coldhours.json","r")
	coldhours_text = coldhours.read()
	coldhours.close()
	headers = {'Content-Type': 'application/json;charset=UTF-8','Authorization': 'Bearer ' + access_token}
	response = requests.request("POST", url, headers=headers, data=coldhours_text.encode('utf8'))
	text_response=response.text
#	print(text_response)
	return text_response

def ecobee_get_empty_thermostat():
	thermostat = open("thermostat_empty.json","r")
	data = json.loads(thermostat.read())
	thermostat.close()
#	access_token_key_id = data['access_token']
#	refresh_token_key_id = data['refresh_token']
#	print("Current Refresh Token is:",refresh_token_key_id)
	return data
	
def ecobee_new_thermostat_cold(temp_f,access_token):
	url = "https://api.ecobee.com/1/thermostat"
	payload = {'json': ('{"selection":{"selectionType":"registered","includeSensors":true}}')}
	headers = {'Content-Type': 'application/json;charset=UTF-8','cache-control': 'no-cache','Authorization': 'Bearer ' + access_token}
	
	response = requests.request("GET", url, headers=headers, params=payload)
	data = response.json()
	remote_sensors = data["thermostatList"][0]["remoteSensors"]
	new_thermostat = ecobee_get_empty_thermostat()
	new_remote_sensors = [ ]
#	mini_sensors = { "id": "ei:0:1", "name": "Home" }
	mini_sensors =  [ { "id": "ei:0:1","name": "Home" },{ "id": "rs2:101:1","name": "Anges bedroom"},{ "id": "rs2:100:1","name": "Embrosias Bedroom" },{ "id": "rs2:102:1","name": "Masters Bedroom" },{ "id": "rs2:103:1","name": "Moving Sensor" } ]
#	coldest_sensor_temp = 950
	for sensor in remote_sensors:
#		if int(sensor["capability"][0]["value"]) < coldest_sensor_temp:
#			coldest_sensor_temp = int(sensor["capability"][0]["value"])
#			mini_sensors = { "id" : sensor["id"]+":1" , "name" : sensor["name"] }
		# print(sensor["id"],":",sensor["name"],":",sensor["capability"][0]["value"])
		if int(sensor["capability"][0]["value"]) < (temp_f*10):
			new_sensor = { "id" : sensor["id"]+":1" , "name" : sensor["name"] }
			#new_remote_sensors.append('{"id":"'+sensor["id"]+'","name": "'+sensor["name"]+'"}')
			new_remote_sensors.append(new_sensor)

	if len(new_remote_sensors) == 0:
		new_remote_sensors = mini_sensors
#		new_remote_sensors.append(mini_sensors)
	new_thermostat["thermostat"]["program"]["climates"][0]["sensors"]=new_remote_sensors
	
	return new_thermostat

def ecobee_get_average_temp(access_token):
	url = "https://api.ecobee.com/1/thermostat"
	payload = {'json': ('{"selection":{"selectionType":"registered","includeSensors":true}}')}
	headers = {'Content-Type': 'application/json;charset=UTF-8','cache-control': 'no-cache','Authorization': 'Bearer ' + access_token}
	response = requests.request("GET", url, headers=headers, params=payload)
	data = response.json()
	remote_sensors = data["thermostatList"][0]["remoteSensors"]
	average_temp = 0.0
	for sensor in remote_sensors:
		# print(sensor["id"],":",sensor["name"],":",sensor["capability"][0]["value"])
		average_temp = average_temp + (int(sensor["capability"][0]["value"]) / 10)
	average_temp = average_temp / len(remote_sensors)
	return average_temp


def ecobee_new_thermostat_hot(temp_f,access_token):
	url = "https://api.ecobee.com/1/thermostat"
	payload = {'json': ('{"selection":{"selectionType":"registered","includeSensors":true}}')}
	headers = {'Content-Type': 'application/json;charset=UTF-8','cache-control': 'no-cache','Authorization': 'Bearer ' + access_token}
	
	response = requests.request("GET", url, headers=headers, params=payload)
	data = response.json()
	remote_sensors = data["thermostatList"][0]["remoteSensors"]
	new_thermostat = ecobee_get_empty_thermostat()
	new_remote_sensors = [ ]
#	mini_sensors = { "id": "ei:0:1", "name": "Home" }
	mini_sensors =  [ { "id": "ei:0:1","name": "Home" },{ "id": "rs2:101:1","name": "Anges bedroom"},{ "id": "rs2:100:1","name": "Embrosias Bedroom" },{ "id": "rs2:102:1","name": "Masters Bedroom" },{ "id": "rs2:103:1","name": "Moving Sensor" } ]
#	warmest_sensor_temp = 0
	for sensor in remote_sensors:
#		if int(sensor["capability"][0]["value"]) > warmest_sensor_temp:
#			warmest_sensor_temp = int(sensor["capability"][0]["value"])
#			mini_sensors = { "id" : sensor["id"]+":1" , "name" : sensor["name"] }
		# print(sensor["id"],":",sensor["name"],":",sensor["capability"][0]["value"])
		if int(sensor["capability"][0]["value"]) > (temp_f*10):
			new_sensor = { "id" : sensor["id"]+":1" , "name" : sensor["name"] }
			#new_remote_sensors.append('{"id":"'+sensor["id"]+'","name": "'+sensor["name"]+'"}')
			new_remote_sensors.append(new_sensor)

	if len(new_remote_sensors) == 0:
		new_remote_sensors = mini_sensors
#		new_remote_sensors.append(mini_sensors)
	new_thermostat["thermostat"]["program"]["climates"][0]["sensors"]=new_remote_sensors
	
	return new_thermostat
	
def ecobee_check_cold_thermostat(temp_f,access_token):
	url = "https://api.ecobee.com/1/thermostat"
	payload = {'json': ('{"selection":{"selectionType":"registered","includeProgram":true,"includeSensors":true}}')}
	headers = {'Content-Type': 'application/json;charset=UTF-8','cache-control': 'no-cache','Authorization': 'Bearer ' + access_token}
	
	response = requests.request("GET", url, headers=headers, params=payload)
	data = response.json()
	remote_sensors = data["thermostatList"][0]["remoteSensors"]
#	mini_sensors = { "id": "ei:0:1", "name": "Home" }
	mini_sensors =  [ { "id": "ei:0:1","name": "Home" },{ "id": "rs2:101:1","name": "Anges bedroom"},{ "id": "rs2:100:1","name": "Embrosias Bedroom" },{ "id": "rs2:102:1","name": "Masters Bedroom" },{ "id": "rs2:103:1","name": "Moving Sensor" } ]
	existing_sensors = data["thermostatList"][0]["program"]["climates"][0]["sensors"]
	new_thermostat = ecobee_get_empty_thermostat()
	new_remote_sensors = [ ]
#	coldest_sensor_temp = 950
	for sensor in remote_sensors:
#		if int(sensor["capability"][0]["value"]) < coldest_sensor_temp:
#			coldest_sensor_temp = int(sensor["capability"][0]["value"])
#			mini_sensors = { "id" : sensor["id"]+":1" , "name" : sensor["name"] }
		if int(sensor["capability"][0]["value"]) < (temp_f*10):
			new_sensor = { "id" : sensor["id"]+":1" , "name" : sensor["name"] }
			new_remote_sensors.append(new_sensor)
	
	if len(new_remote_sensors) == 0:
		new_remote_sensors = mini_sensors
#		new_remote_sensors.append(mini_sensors)
		
#	print(new_remote_sensors)		
	
	if (existing_sensors == new_remote_sensors):
		return True
	else:
		return False

def ecobee_check_hot_thermostat(temp_f,access_token):
	url = "https://api.ecobee.com/1/thermostat"
	payload = {'json': ('{"selection":{"selectionType":"registered","includeProgram":true,"includeSensors":true}}')}
	headers = {'Content-Type': 'application/json;charset=UTF-8','cache-control': 'no-cache','Authorization': 'Bearer ' + access_token}
	
	response = requests.request("GET", url, headers=headers, params=payload)
	data = response.json()
	remote_sensors = data["thermostatList"][0]["remoteSensors"]
	mini_sensors =  [ { "id": "ei:0:1","name": "Home" },{ "id": "rs2:101:1","name": "Anges bedroom"},{ "id": "rs2:100:1","name": "Embrosias Bedroom" },{ "id": "rs2:102:1","name": "Masters Bedroom" },{ "id": "rs2:103:1","name": "Moving Sensor" } ]
	existing_sensors = data["thermostatList"][0]["program"]["climates"][0]["sensors"]
	new_thermostat = ecobee_get_empty_thermostat()
	new_remote_sensors = [ ]
#	warmest_sensor_temp = 0
	for sensor in remote_sensors:
#		if int(sensor["capability"][0]["value"]) > warmest_sensor_temp:
#			warmest_sensor_temp = int(sensor["capability"][0]["value"])
#			mini_sensors = { "id" : sensor["id"]+":1" , "name" : sensor["name"] }
		if int(sensor["capability"][0]["value"]) > (temp_f*10):
			new_sensor = { "id" : sensor["id"]+":1" , "name" : sensor["name"] }
			new_remote_sensors.append(new_sensor)
	
	if len(new_remote_sensors) == 0:
		new_remote_sensors = mini_sensors
#		new_remote_sensors.append(mini_sensors)
		
#	print(new_remote_sensors)		
	
	if (existing_sensors == new_remote_sensors):
		return True
	else:
		return False
		
def ecobee_switch_thermostat(access_token,thermostat):
	url = "https://api.ecobee.com/1/thermostat?format=json"
	headers = {'Content-Type': 'application/json;charset=UTF-8','Authorization': 'Bearer ' + access_token}
	response = requests.request("POST", url, headers=headers, data=json.dumps(thermostat).encode('utf8'))
#	print(json.dumps(thermostat).encode('utf8'))
	text_response=response.text
#	print(text_response)
	return text_response

def ecobee_get_mode(access_token):
	url = "https://api.ecobee.com/1/thermostat"
	payload = {'json': ('{"selection":{"selectionType":"registered","includeSettings":true}}')}
	headers = {'Content-Type': 'application/json;charset=UTF-8','cache-control': 'no-cache','Authorization': 'Bearer ' + access_token}
	response = requests.request("GET", url, headers=headers, params=payload)
	data = response.json()
	ecobee_mode = data["thermostatList"][0]["settings"]["hvacMode"].strip()
	return ecobee_mode

def ecobee_set_mode(access_token,mode):
	url = "https://api.ecobee.com/1/thermostat?format=json"
	headers = {'Content-Type': 'application/json;charset=UTF-8','cache-control': 'no-cache','Authorization': 'Bearer ' + access_token}
	payload = '{"selection":{"selectionType":"registered","selectionMatch":""},"thermostat": {"settings":{"hvacMode":"'+mode+'"}}}' 
	response = requests.request("POST", url, headers=headers, data=payload)
#	text_response=response.text
#	print(text_response)
	return response	

def flair_authenticate(client_id,client_secret):
	url = "https://api.flair.co/oauth/token?client_id=" + client_id + "&client_secret=" + client_secret + "&scope=vents.view+vents.edit+thermostats.view+structures.view+structures.edit&grant_type=client_credentials"

	payload = {}
	headers = {
	'Content-Type': 'application/x-www-form-urlencoded'
	}
	
	response = requests.request("POST", url, headers=headers, data = payload)

	#print(response.text.encode('utf8'))
	data = response.json()
	#print(data)
	access_token = data['access_token'] 
	return access_token

def flair_get_structid(oauth_token):
	url = "https://api.flair.co/api/structures"
	payload = {}
	headers = { 'Content-Type': 'application/x-www-form-urlencoded','Accept': 'application/json','Authorization': 'Bearer ' + oauth_token }
	response = requests.request("GET", url, headers=headers, data = payload)
#	print(response.text.encode('utf8'))
	data = response.json()
	id = data['data'][0]['id']
	return id
	
def flair_get_current_setpoint(oauth_token):
	url = "https://api.flair.co/api/structures"
	payload = {}
	headers = { 'Content-Type': 'application/x-www-form-urlencoded','Accept': 'application/json','Authorization': 'Bearer ' + oauth_token }
	response = requests.request("GET", url, headers=headers, data = payload)
	
	data = response.json()
	attributes = data['data'][0]['attributes']
	current_setpoint = attributes['set-point-temperature-c']
	return current_setpoint

def flair_get_current_mode(oauth_token):
	url = "https://api.flair.co/api/structures"
	payload = {}
	headers = { 'Content-Type': 'application/x-www-form-urlencoded','Accept': 'application/json','Authorization': 'Bearer ' + oauth_token }
	response = requests.request("GET", url, headers=headers, data = payload)
	
	data = response.json()
	attributes = data['data'][0]['attributes']
	mode = attributes['structure-heat-cool-mode']
	return mode

def flair_update_current_setpoint(oauth_token,struct_id,new_temp_f):
	url = "https://api.flair.co/api/structures/" + struct_id
	temp_c = (new_temp_f - 32) * 5 / 9
	payload = "{\"data\":{\"type\":\"structures\",\"attributes\":{\"set-point-temperature-c\":" + str(round(temp_c,2)) + "}}}"
	headers = { 'Authorization': 'Bearer ' + oauth_token }
	response = requests.request("PATCH",url,headers=headers,data=payload)
	print("New Temp In Celsius : ", round(temp_c,2))
	return response

def flair_update_current_mode(oauth_token,struct_id,new_mode):
	url = "https://api.flair.co/api/structures/" + struct_id
	payload = "{\"data\":{\"type\":\"structures\",\"attributes\":{\"structure-heat-cool-mode\": \"" + new_mode + "\"}}}"
	headers = { 'Authorization': 'Bearer ' + oauth_token }
	response = requests.request("PATCH",url,headers=headers,data=payload)
	print("New mode is : ", new_mode)
	return response

def flair_update_current_setpoint_and_mode(oauth_token,struct_id,new_temp_f,new_mode):
	url = "https://api.flair.co/api/structures/" + struct_id
	temp_c = (new_temp_f - 32) * 5 / 9
	payload = "{\"data\":{\"type\":\"structures\",\"attributes\":{\"structure-heat-cool-mode\": \"" + new_mode + "\",\"set-point-temperature-c\":" + str(round(temp_c,2)) + "}}}"
	headers = { 'Authorization': 'Bearer ' + oauth_token }
	response = requests.request("PATCH",url,headers=headers,data=payload)
	print("New Temp In Celsius : ", round(temp_c,2))
	return response

def flair_update_current_structure_mode(oauth_token,struct_id,new_mode):
	url = "https://api.flair.co/api/structures/" + struct_id
	payload = "{\"data\":{\"type\":\"structures\",\"attributes\":{\"mode\": \"" + new_mode + "\"}}}"
	headers = { 'Authorization': 'Bearer ' + oauth_token }
	response = requests.request("PATCH",url,headers=headers,data=payload)
	return response		

def flair_update_current_hysteresis(oauth_token,struct_id,new_hysteresis_F):
	url = "https://api.flair.co/api/structures/" + struct_id
	real_new_hysteresis = int((5 * new_hysteresis_F / 9) * 100)
	payload = "{\"data\":{\"type\":\"structures\",\"attributes\":{\"hysteresis-heat-cool-mode\": " + str(real_new_hysteresis) + "}}}"
	headers = { 'Authorization': 'Bearer ' + oauth_token }
	response = requests.request("PATCH",url,headers=headers,data=payload)
	print("New hysteresis is : ", real_new_hysteresis)
	return response

def flair_get_current_temperature(oauth_token,struct_id):
	url = "https://api.flair.co/api/structures/" + str(struct_id) + "/current-weather"
	payload = {}
	headers = { 'Content-Type': 'application/x-www-form-urlencoded','Accept': 'application/json','Authorization': 'Bearer ' + oauth_token }
	response = requests.request("GET", url, headers=headers, data = payload)
	data = response.json()
	current_temp_c = data['data']['attributes']['outside-temperature-c']
	return current_temp_c

def flair_vent_halfopen(oauth_token,vent_id):
	url = "https://api.flair.co/api/vents/"+vent_id
	payload = "{\n    \"data\": {\n        \"type\": \"vents\",\n        \"attributes\": {\n            \"percent-open\": 50\n        },\n        \"relationships\": {}\n    }\n}"
	headers = {'Authorization': 'Bearer '+ oauth_token }
	response = requests.request("PATCH", url, headers=headers, data = payload)
	return response

def flair_vent_fullopen(oauth_token,vent_id):
	url = "https://api.flair.co/api/vents/"+vent_id
	payload = "{\n    \"data\": {\n        \"type\": \"vents\",\n        \"attributes\": {\n            \"percent-open\": 100\n        },\n        \"relationships\": {}\n    }\n}"
	headers = {'Authorization': 'Bearer '+ oauth_token }
	response = requests.request("PATCH", url, headers=headers, data = payload)
	return response

def flair_vent_closed(oauth_token,vent_id):
	url = "https://api.flair.co/api/vents/"+vent_id
	payload = "{\n    \"data\": {\n        \"type\": \"vents\",\n        \"attributes\": {\n            \"percent-open\": 0\n        },\n        \"relationships\": {}\n    }\n}"
	headers = {'Authorization': 'Bearer '+ oauth_token }
	response = requests.request("PATCH", url, headers=headers, data = payload)
	return response

def flair_get_vents(oauth_token):
	url = "https://api.flair.co/api/vents"
	payload = {}
	headers = { 'Content-Type': 'application/x-www-form-urlencoded','Accept': 'application/json','Authorization': 'Bearer ' + oauth_token }
	response = requests.request("GET", url, headers=headers, data = payload)
	data = response.json()
#	print(data)
	vents = data['data']
	return vents
	
def f_to_c(temp_f):
	temp_c = (temp_f - 32) * 5 / 9
	return temp_c

def c_to_f(temp_c):
	temp_f = (temp_c * 9 / 5) + 32
	return temp_f

def get_current_temp_weatherapi():
	url = "https://weatherapi-com.p.rapidapi.com/current.json"
	querystring = {"q":"39.576362,-104.995439"}
	headers = {'x-rapidapi-host': "weatherapi-com.p.rapidapi.com", 'x-rapidapi-key': "YOUR_FLAIR_WEATHERAPIKEY"}
	response = requests.request("GET", url, headers=headers, params=querystring)
	data = response.json()
	return data["current"]["temp_f"]
	


op_count = 45
api_key_id = "YOUR_API_KEY"

credentials = ecobee_get_credentials()
ecobee_access_token = credentials['access_token']
ecobee_refresh_token = credentials['refresh_token']
rolling_outdoor_temp = AveragingBuffer(10)
rolling_avg_temp = AveragingBuffer(5)
current_ecobee_mode = "initial"

last_switch_mode_time = datetime.datetime.now() - datetime.timedelta(minutes=30)
last_switch_setpoint_time = last_switch_mode_time
last_get_token = datetime.datetime.now() - datetime.timedelta(hours=3)

while 1 == 1:
# if op_count > 44:
 if (datetime.datetime.now()-last_get_token).total_seconds() > 2700: 
  print("Getting a new Flair token & Ecobee Token")
  access_token = flair_authenticate("YOUR_FLAIR_APIKEY","YOUR_FLAIR_SECRET")
  id = flair_get_structid(access_token)
  credentials =  ecobee_refresh_credentials(api_key_id,ecobee_refresh_token)
  ecobee_access_token = credentials['access_token']
  ecobee_refresh_token = credentials['refresh_token']
  last_get_token = datetime.datetime.now()
  op_count = 0
  
 current_temp = c_to_f(flair_get_current_temperature(access_token,id))
 #current_temp = get_current_temp_weatherapi()
 print("Current Temp: ",current_temp,"F")
 
 rolling_outdoor_temp.append(current_temp)
 print("Current Average Outdoor Temp:",rolling_outdoor_temp.xbar,"F")
 
 dt = datetime.datetime.today()
 month = dt.month
 hour = dt.hour
# Jun-Jul-Aug : Cool enabled 
 avg_tmp = ecobee_get_average_temp(ecobee_access_token)
 rolling_avg_temp.append(avg_tmp)
 print("Current Average Indoor Temp:",rolling_avg_temp.xbar,"F")
 
# if avg_tmp > 72.5 and current_temp > 75:
 if rolling_avg_temp.xbar > 72.5 and rolling_outdoor_temp.xbar > 75.0:
     print("Cool mode enabled")
     mode = "cool"
     set_point = 75.0
 # elif current_temp < 55 and month < 6:
     # mode = "heat"
     # set_point = 69
 # elif current_temp < 55 and month > 8:
     # mode = "heat"
     # set_point = 69
 # elif current_temp > 65	and current_temp < 75:
     # mode = "float"
     # set_point = 76
 elif rolling_avg_temp.xbar > 76.0 or rolling_outdoor_temp.xbar > 85:
     print("Cool mode enabled")
     mode = "cool"
     set_point = 75.0 
 elif rolling_avg_temp.xbar < 71.0 or rolling_outdoor_temp.xbar < 55:
#     set_point = 72.5
#     mode = "auto"
     print("Heat mode enabled")
     if hour > 22 or hour < 6:
      set_point = 67.0
     else:
      set_point = 70.0
     mode = "heat"
 else:
     mode = "float"
     set_point = 80.0

 real_setpoint = flair_get_current_setpoint(access_token)
 real_mode = flair_get_current_mode(access_token)
 setpoint_c = round((set_point - 32) * 5 / 9,2)
  
 if real_mode != mode and real_setpoint != setpoint_c and (datetime.datetime.now()-last_switch_mode_time).total_seconds()> 1800 and (datetime.datetime.now()-last_get_token).total_seconds() < 2700:
  response = flair_update_current_setpoint_and_mode(access_token,id,set_point,mode)
  time.sleep(60)
  response = flair_update_current_structure_mode(access_token,id,"manual")
  vents = flair_get_vents(access_token)
  for vent in vents:
   if mode == "float":
    flair_vent_fullopen(access_token,vent['id'])
#	ecobee_set_mode(ecobee_access_token,"auto")
   else:
    flair_vent_halfopen(access_token,vent['id'])
#   print("Vent id:",vent['id'],"Percent Open:",vent['attributes']['percent-open'],"%") 
  time.sleep(60)
  vents = flair_get_vents(access_token)
  for vent in vents:
#   flair_vent_halfopen(access_token,vent['id'])
   print("Vent id:",vent['id'],"Percent Open:",vent['attributes']['percent-open'],"%") 
  response = flair_update_current_structure_mode(access_token,id,"auto")
  last_switch_mode_time = datetime.datetime.now()
  last_switch_setpoint_time = last_switch_mode_time
  real_mode = flair_get_current_mode(access_token)
  real_setpoint = flair_get_current_setpoint(access_token)  
 
 if real_mode != mode and (datetime.datetime.now()-last_switch_mode_time).total_seconds()> 1800 and (datetime.datetime.now()-last_get_token).total_seconds() < 2700:
  response = flair_update_current_mode(access_token,id,mode)
  time.sleep(60)
  response = flair_update_current_structure_mode(access_token,id,"manual")
  vents = flair_get_vents(access_token)
  for vent in vents:
   if mode == "float":
    flair_vent_fullopen(access_token,vent['id'])
#	ecobee_set_mode(ecobee_access_token,"auto")
   else:
    flair_vent_halfopen(access_token,vent['id'])
#   print("Vent id:",vent['id'],"Percent Open:",vent['attributes']['percent-open'],"%")
  time.sleep(60)
  vents = flair_get_vents(access_token)
  for vent in vents:
#   flair_vent_halfopen(access_token,vent['id'])
   print("Vent id:",vent['id'],"Percent Open:",vent['attributes']['percent-open'],"%") 
  response = flair_update_current_structure_mode(access_token,id,"auto")
  last_switch_mode_time = datetime.datetime.now()
  real_mode = flair_get_current_mode(access_token)
  
 if real_setpoint != setpoint_c and (datetime.datetime.now()-last_switch_setpoint_time).total_seconds()> 1800 and (datetime.datetime.now()-last_get_token).total_seconds() < 2700: 
  response = flair_update_current_setpoint(access_token,id,set_point)
  last_switch_setpoint_time = datetime.datetime.now()
  real_setpoint = flair_get_current_setpoint(access_token)
 
# print("Mode is: ",real_mode," and set point is: ",c_to_f(real_setpoint),"F")
 print("Last changes for the mode were made at :", last_switch_mode_time, "and the set point at ", last_switch_setpoint_time)
# print("Real Mode is: ",mode," and Real set point is: ",real_setpoint,"C")

 current_ecobee_mode = ecobee_get_mode(ecobee_access_token)
 
 if (datetime.datetime.now()-last_get_token).total_seconds() < 2700 and current_ecobee_mode == "heat" and not ecobee_check_cold_thermostat(set_point,ecobee_access_token) and (hour > 22 or hour < 6):
  new_thermo = ecobee_new_thermostat_cold(set_point,ecobee_access_token)
  ecobee_switch_thermostat(ecobee_access_token,new_thermo)
  print("New sensors for heat mode")
 elif (datetime.datetime.now()-last_get_token).total_seconds() < 2700 and current_ecobee_mode == "heat" and not ecobee_check_cold_thermostat(set_point,ecobee_access_token) and not (hour > 22 or hour < 6): 
  new_thermo = ecobee_new_thermostat_cold(set_point,ecobee_access_token)
  ecobee_switch_thermostat(ecobee_access_token,new_thermo)
  print("New sensors for heat mode")
  ecobee_switch_thermostat(ecobee_access_token,new_thermo)
 elif  (datetime.datetime.now()-last_get_token).total_seconds() < 2700 and current_ecobee_mode == "cool" and not ecobee_check_hot_thermostat(set_point,ecobee_access_token):
  new_thermo = ecobee_new_thermostat_hot(set_point,ecobee_access_token)
  print("Changing Sensors in cool mode")
  ecobee_switch_thermostat(ecobee_access_token,new_thermo)
 
 if mode == "float" and not current_ecobee_mode == "auto":
  ecobee_set_mode(ecobee_access_token,"auto")
  current_ecobee_mode = "auto"
 if mode == "heat" and not current_ecobee_mode == "heat":  
  ecobee_set_mode(ecobee_access_token,"heat")
  current_ecobee_mode = "heat"
 if mode == "cool" and not current_ecobee_mode == "cool":  
  ecobee_set_mode(ecobee_access_token,"cool")
  current_ecobee_mode = "cool"
  
 print("Current Ecobee Mode is ",current_ecobee_mode)
 print("Current Average Temp is ",avg_tmp)
 print("Last token renewal was ", (datetime.datetime.now()-last_get_token).total_seconds(),"seconds ago")

 op_count += 1
 print("Entering end of loop - safe to break")
 time.sleep(180)
 print("Don't break now....")
 
