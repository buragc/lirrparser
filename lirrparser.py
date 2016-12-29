import json


def parse_all_stations(all_stations_json):
    """ Parses a JSON string containing the result of all sttations call to MTA/LIRR and returns a dictionary
    with station name and its abbreviation"""
    stations = json.loads(all_stations_json)['Stations']
    station_list = {}
    for i in stations.keys():
        station = stations["{0}".format(i)]
        nm = station['NAME'].upper()
        if 'ABBR' not in station:
            print('Could not find ABBR key for ' + station['NAME'])
        else:
            try:
                abbr = station['ABBR'].upper()
                station_list[nm] = abbr
            except:
                pass
    print len(station_list)
    return station_list


def parse_train_schedule_response(schedule_json):
    """Parses the schedule response from MTA site and returns a list of departing train times in military format as
     integers"""
    schedule = json.loads(schedule_json)
    trips = schedule["TRIPS"]
    times = []
    if len(trips) == 0:
        print ("**** NO TRIPS FOUND ****")
        return times

    for t in range(len(trips)):
        trip = trips[t]
        train_times = trip["LEGS"]
        for i in range(len(train_times)):
            train_time = train_times[i]
            times.append(int(train_time["DEPART_TIME"]))
    return times