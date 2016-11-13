import json, requests
def HourlyFunction():
	url = 'http://apidev.accuweather.com/locations/v1/search'

	params = dict(
		q='state college',
		apikey='PSUHackathon112016'
	)

	response = requests.get(url=url, params=params)
	data = json.loads(response.text)

	locationKey = (data[0]['Key'])

	params = dict(
		metric='false',
		details='false',
		apikey='PSUHackathon112016'
	)

	url = 'http://apidev.accuweather.com/forecasts/v1/hourly/72hour/'+locationKey

	response = requests.get(url=url,params=params)
	hourlyData = json.loads(response.text)

	#print(hourlyData[0])

	currentUrl = url = 'http://apidev.accuweather.com/currentconditions/v1/'+locationKey+'.json'

	response = requests.get(url=url,params=params)
	currentData = json.loads(response.text)

	current = {
		'EpochDateTime': currentData[0]['EpochTime'],
		'Temperature': {
			'Value': currentData[0]['Temperature']['Imperial']['Value']
		},
		'PrecipitationProbability':0
	}

	if((currentData[0]['WeatherIcon'] >= 12 and currentData[0]['WeatherIcon'] <= 18) or (currentData[0]['WeatherIcon'] >= 25 and currentData[0]['WeatherIcon'] <= 29) or (currentData[0]['WeatherIcon'] >= 39 and currentData[0]['WeatherIcon'] <= 42)):
		current['PrecipitationProbability'] = 100

	hourlyData.append(current)

	#print(hourlyData)

	return hourlyData




