from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import time
from HourlyFunction import HourlyFunction

breakPeriod = 60*30
percentRain = 30
coatNone = 65
coatJacket = 50
coatHeavy = -9001

NO_COAT = 0
JACKET = 1
HEAVY_COAT = 2

customCal = '9ko3hclinda581cam69hjetrg0@group.calendar.google.com'
primaryCal = 'primary' #'44ob66bdnohqkj7a8mbbnd5a8c@group.calendar.google.com'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials



def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    page_token = None
    while True:
        events = service.events().list(calendarId=customCal, pageToken=page_token).execute()
        for event in events['items']:#clear calendar
            service.events().delete(calendarId=customCal, eventId=event['id']).execute()
        events = service.events().list(calendarId=primaryCal, pageToken=page_token).execute()#get primary
        eventList = events['items']
        for event in eventList:
            startTime = event['start']['dateTime'][0:-3] + event['start']['dateTime'][-2:]
            event['startTime'] = int(time.mktime(time.strptime(startTime, '%Y-%m-%dT%H:%M:%S%z')))
            endTime = event['end']['dateTime'][0:-3] + event['end']['dateTime'][-2:]
            event['endTime'] = int(time.mktime(time.strptime(endTime, '%Y-%m-%dT%H:%M:%S%z')))
        eventList = sorted(eventList, key=lambda x: x['startTime'])
        for event in eventList:
            i = 0
            while i < len(eventList):
                if((eventList[i]['startTime'] >= event['endTime']) and (eventList[i]['startTime'] <= event['endTime'] + breakPeriod)):
                    event['endTime'] = eventList[i]['endTime']
                    eventList.pop(i)
                else:
                    i = i + 1
        #checkweather
        hourlyWeather = HourlyFunction()
        for event in eventList:
            print(event['summary'] + " :")
            umbrella = False
            startCoat = NO_COAT
            endCoat = NO_COAT
            notifyText = ""
            descriptionText = ""
            for hour in hourlyWeather:
                if ((hour['EpochDateTime'] <= event['startTime']) and (hour['EpochDateTime'] > (event['startTime']-3600))):
                    if(hour['PrecipitationProbability'] >= percentRain):
                        umbrella = True
                        print("rain")
                    if(hour['Temperature']['Value'] > coatNone):
                        startCoat = NO_COAT
                        print("No coat needed")
                    elif(hour['Temperature']['Value'] > coatJacket):
                        startCoat = JACKET
                        print("Jacket needed")
                    elif(hour['Temperature']['Value'] > coatHeavy):
                        startCoat = HEAVY_COAT
                        print("ITS TOO FRIGGIN COLD MAN!")
                    else:
                        print("Something broke")
                if ((hour['EpochDateTime'] >= event['endTime']) and (hour['EpochDateTime'] < (event['endTime']+3600))):
                    if(hour['PrecipitationProbability'] >= percentRain):
                        umbrella = True
                        print("rain")
                    if(hour['Temperature']['Value'] > coatNone):
                        endCoat = NO_COAT
                        print("No coat needed")
                    elif(hour['Temperature']['Value'] > coatJacket):
                        endCoat = JACKET
                        print("Jacket needed")
                    elif(hour['Temperature']['Value'] > coatHeavy):
                        endCoat = HEAVY_COAT
                        print("ITS TOO FRIGGIN COLD MAN!")
                    else:
                        print("Something broke")
                if(startCoat > NO_COAT or endCoat > NO_COAT or umbrella):
                    if(startCoat == endCoat):
                        if(startCoat == JACKET):
                            notifyText = "JACKET "
                            descriptionText = "Today you will need a: "
                        if(startCoat == HEAVY_COAT):
                            notifyText = "HEAVY COAT "
                            descriptionText = "Today you will need a: "
                        if((umbrella) and (startCoat != NO_COAT)):
                            notifyText = notifyText + " and an UMBRELLA"
                            descriptionText = "Today you will need a: "
                        elif(umbrella):
                            notifyText = notifyText + "UMBRELLA"
                            descriptionText = "Today you will need an: "
                    else:
                        if(startCoat > endCoat):
                            if(startCoat == JACKET):
                                notifyText = "JACKET "
                                descriptionText = "Today you will need a: "
                            if(startCoat == HEAVY_COAT):
                                notifyText = "HEAVY COAT "
                                descriptionText = "Today you will need a: "
                        else:
                            if(endCoat == JACKET):
                                notifyText = "JACKET 4L8R "
                                descriptionText = "Today you will need a: "
                            if(endCoat == HEAVY_COAT):
                                notifyText = "HEAVY COAT 4L8R "
                                descriptionText = "Today you will need a: "
                        if(umbrella):
                            notifyText = notifyText + "and an UMBRELLA"
                            descriptionText = "Today you will need a: "
            if(notifyText != ""):
                startDateTime = time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(event['startTime']))
                startDateTime = startDateTime[0:-2]+":"+startDateTime[-2:]
                print(startDateTime)
                endDateTime = time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(event['endTime']))
                endDateTime = endDateTime[0:-2]+":"+endDateTime[-2:]
                newEvent = {
                    'summary': notifyText,
                    'description': descriptionText,
                    'start': {
                        'dateTime': startDateTime
                    },
                    'end': {
                        'dateTime': endDateTime
                    }
                }
                addedEvent = service.events().insert(calendarId=customCal, body=newEvent).execute()
                print ('Event created: ' + event.get('htmlLink'))
        page_token = events.get('nextPageToken')
        if not page_token:
            break

if __name__ == '__main__':
    main()
