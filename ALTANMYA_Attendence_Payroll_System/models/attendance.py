# -*- coding: utf-8 -*-
import datetime
class Attendance(object):
    def __init__(self, user_id, timestamp, status, punch=0, uid=0):
        self.uid = uid # not really used any more
        self.user_id = user_id
       # d = timestamp - datetime.timedelta(hours=2)  # to be modified
        if timestamp.month >3 and timestamp.month<10:
            d = timestamp - datetime.timedelta(hours=3)
        elif timestamp.month ==3 and timestamp.day>=29:
            d = timestamp - datetime.timedelta(hours=3)
        elif timestamp.month == 10 and timestamp.day <= 28:
            d = timestamp - datetime.timedelta(hours=3)
        else:
            d = timestamp - datetime.timedelta(hours=2)

        self.timestamp = d
        self.status = status
        self.punch = punch

    def __str__(self):
        return '<Attendance>: {} : {} ({}, {})'.format(self.user_id, self.timestamp, self.status, self.punch)

    def __repr__(self):
        return '<Attendance>: {} : {} ({}, {})'.format(self.user_id, self.timestamp,self.status, self.punch)
