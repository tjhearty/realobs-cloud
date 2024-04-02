import datetime

def datetime_range(start_date,end_date,dinc=1):
    """
    Create a date time array for a range of dates.
    """

    start_year = int(start_date[0:4])
    start_month = int(start_date[5:7])
    start_day = int(start_date[8:10])
    start_dt = datetime.datetime(start_year,start_month,start_day)


    end_year = int(end_date[0:4])
    end_month = int(end_date[5:7])
    end_day = int(end_date[8:10])
    end_dt = datetime.datetime(end_year,end_month,end_day)

    dt_array = [start_dt]

    while dt_array[-1] < end_dt:
       dt_array.append(dt_array[-1]+datetime.timedelta(days=dinc))

    return dt_array
