import datetime

def other_team(team):
    '''
    Given a team, this function returns the other team
    '''
    return (team*5)%3

def time_from_string(clock):
    '''
    This function returns a datetime.time type value from a time represented as a string
    '''
    clock = clock.split(":")
    return datetime.time(0, int(clock[0]), int(clock[1]))

def string_from_time(clock):
    '''
    This function returns a MM:SS string from a time in datetime.time
    '''
    return clock.strftime("%M:%S")

def get_quarter(clock):
    '''
    This function returns the quarter the introduced time belongs to
    '''
    return 4-int(clock.minute/12)

def compute_interval(in_time, out_time, start=datetime.time(0, 48, 0), end=datetime.time(0, 0, 0)):
    '''
    This function computes the interval in common between a playing interval and the desired interval
    - in_time-out_time: playing interval of a player (datetime.time)
    - start-end: interval of the match we are interested in (datetime.time)
    '''
    my_date = datetime.date(1, 1, 1)
    
    int_start = min(in_time, start)
    int_end = max(out_time, end)
    date_int_start = datetime.datetime.combine(my_date, int_start)
    date_int_end = datetime.datetime.combine(my_date, int_end)
    null = datetime.timedelta() # in case the interval is negative, we will return a null interval
    return max(date_int_start - date_int_end, null), int_start, int_end