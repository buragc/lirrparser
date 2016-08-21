from lirrparser import parse_all_stations, parse_train_schedule_response
import os
import urllib.request
import datetime
import codecs
from pytz import timezone
import pytz


class TimeTable:
    LIRR_ENDPOINT_GETALLSTATIONS = "https://traintime.lirr.org/api/StationsAll?api_key="
    LIRR_ENDPOINT_GETTIME = "https://traintime.lirr.org/api/TrainTime?api_key="
    MTA_TOKEN = ""
    ENV_VAR_MTA_TOKEN = "CONDUCTOR_MTA_KEY"
    _station_list = None

    def get_station_list(self):
        return self._station_list

    def _get_localized_time_now(self):
        eastern = timezone('US/Eastern')
        greenwich = timezone('Etc/Greenwich')
        gtime = greenwich.localize(datetime.datetime.now())
        return gtime.astimezone(eastern)

    def _get_query_params_for_now(self):
        now = self._get_localized_time_now()
        return "&year={0}&month={1}&day={2}&hour={3}&minute={4}".format(now.year,
                                                                        now.month,
                                                                        now.day,
                                                                        now.hour,
                                                                        now.minute)

    def _get_train_time_url(self, from_station, to_station, time_offset = 0):
        return self.LIRR_ENDPOINT_GETTIME + self.MTA_TOKEN + "&startsta=" + from_station + "&endsta=" + to_station + \
               self._get_query_params_for_now()

    def __get_all_stations_url(self):
        return self.LIRR_ENDPOINT_GETALLSTATIONS + self.MTA_TOKEN

    def __get_time_table(self, from_station, to_station):
        from_abr = self._get_abbreviated_station(from_station)
        to_abr = self._get_abbreviated_station(to_station)
        time_url = self._get_train_time_url(from_abr, to_abr)
        print(time_url)
        reader = codecs.getreader("utf-8")
        response = reader(urllib.request.urlopen(time_url))
        return response

    def __init__(self):
        if not os.environ[self.ENV_VAR_MTA_TOKEN]:
            raise EnvironmentError(self.ENV_VAR_MTA_TOKEN)
        else:
            self.MTA_TOKEN = os.environ[self.ENV_VAR_MTA_TOKEN]

    def load_all_stations(self):
        response = urllib.request.urlopen(self.__get_all_stations_url())
        reader = codecs.getreader("utf-8")
        all_stations = reader(response)
        self._station_list = parse_all_stations(all_stations)

    def _get_abbreviated_station(self, station_name):
        if not station_name:
            raise ValueError("station_name cannot be None")
        if not self._station_list:
            raise EnvironmentError("stations are not loaded ")
        return self._station_list[station_name]

    def get_train_time(self, from_station, to_station):
        timetable_text = self.__get_time_table(from_station, to_station)
        times = parse_train_schedule_response(timetable_text)
        print(times)
        # find the time greater than or equal to now
        now = self._get_localized_time_now()
        eastern = timezone('US/Eastern')
        for t in times:
            t_eastern = eastern.localize(datetime.datetime(now.year,now.month, now.day, int(str(t)[:2]), int(str(t)[2:]),0))
            if t_eastern > now:
                return TimeTable._convert_militarytime_to_spoken_time(t)
        return TimeTable._convert_militarytime_to_spoken_time(times[0])

    @staticmethod
    def _convert_militarytime_to_spoken_time(militarytime):
        """Takes an integer representing military time and returns a string that has the spoken time"""
        strtime = str(militarytime)
        if len(strtime) == 3:
            strtime = "0" + strtime
        t = datetime.time(hour=int(strtime[0:2]), minute=int(strtime[2:4]))
        fmt = "%I:%M %p"
        spokentime = t.strftime(fmt).replace(":", " ")
        return spokentime
