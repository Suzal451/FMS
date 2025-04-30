import datetime
from home.models import Bookings


def check_availibility(bookingtime_start,bookingtime_finish):
    avail_list = []
    if bookingtime_start > bookingtime_finish or bookingtime_finish < bookingtime_start:
        avail_list.append(True)
    else:
        avail_list.append(False)

    return all(avail_list)