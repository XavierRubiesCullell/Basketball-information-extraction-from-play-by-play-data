import datetime
import os

def get_team(team):
    '''
    This functions returns the codification of the team name, which is needed to access to the website
    As information is stored by using it, it also grants unicity in the database
    - team: Team name in whatever variant is desired: city, club name or both (string)
    Output: 3-letter representation of the team, which are often the first 3 letters of the city (string)
    '''
    os.chdir(os.path.dirname(__file__))
    f = open('./Teams.txt', 'r')
    while True:
        line = f.readline().strip().split(', ')
        n = len(line)
        for i in range(n-1):
            if line[i] == team:
                return line[n-1]

def other_team(team):
    '''
    Given a team, this function returns the other team
    - team: id of a team (integer)
    Output: id of the other team (integer)
    '''
    return (team*5)%3

def time_from_string(clock):
    '''
    This function returns a datetime.timedelta type value from a time represented as a string
    '''
    quarter, minutes, seconds = clock.split(":")
    Q = int(quarter[0])
    if quarter[-1] == "Q":
        minTime = datetime.timedelta(minutes = (4-Q)*12)
    else:
        minTime = datetime.timedelta(minutes = -Q*5)
    quarterTime = datetime.timedelta(minutes = int(minutes), seconds = int(seconds))
    # we need to be able to differ from 00:00 to 12:00 of the next quarter:
    if minutes == "00" and seconds == "00":
        quarterTime += datetime.timedelta(microseconds=1)
    return minTime + quarterTime

def string_from_time(clock):
    '''
    This function returns a Q:MM:SS string from a time in datetime.timedelta
    '''
    if clock >= datetime.timedelta(microseconds=1):
        seconds = clock.seconds
        minutes = seconds//60
        seconds = seconds%60
        Q = 4 - int(minutes/12)
        if minutes%12 == 0:
            if clock.microseconds == 0:
                Q += 1
                minutes = 12
            else:
                minutes = 0
        quarter = str(Q) + "Q"
    else:
        clock = -clock
        seconds = clock.seconds
        minutes = seconds//60
        seconds = seconds%60
        Q = 1 + int(minutes/5)
        if (minutes+1)%5 == 0 and seconds == 59 and clock.microseconds == 999999:
            minutes = seconds = 0
        elif minutes%5 == 0 and seconds == 0:
            minutes = 5
        quarter = str(Q) + "OT"
    return quarter + ":" + datetime.time(0, minutes, seconds).strftime("%M:%S")

def quarter_from_time(clock):
    '''
    This function returns the quarter of the introduced time
    - clock: timestamp (string)
    Ouput: quarter where clock is (string)
    '''
    quarter, _, _ = clock.split(":")
    return quarter

def quarter_index_from_time(clock):
    '''
    This function returns the quarter the introduced time belongs to
    - clock: timestamp (datetime.timedelta)
    Output: quarter where clock is (integer)
    '''
    if clock > datetime.timedelta(0,0,0):
        minutes = int(clock.seconds/60)
        return 4-int(minutes/12)
    clock = - clock
    minutes = int(clock.seconds/60)
    return 5 - int(minutes/5)

def next_quarter(Q):
    '''
    Returns the quarter that follows Q
    - Q: quarter (string)
    '''
    if Q == "4Q":
        return "1OT"
    return str(int(Q[0])+1) + Q[1:]

def quarter_from_index(Q):
    '''
    This function returns the quarter corresponding to the index introduced
    - Q: quarter (integer)
    Ouput: quarter (string)
    '''
    if Q <= 4:
        return str(Q) + "Q"
    return str(Q-4) + "OT"

def quarter_start_time(Q):
    '''
    This function returns the starting timestamp of a quarter Q
    - Q: quarter (string)
    Ouput: starting time (datetime.timedelta)
    '''
    num = int(Q[0])
    if Q[-1] == "Q":
        return datetime.timedelta(minutes = (5-num)*12)
    return datetime.timedelta(minutes = -(num-1)*5)

def quarter_end_time(Q):
    '''
    This function returns the ending timestamp of a quarter Q
    - Q: quarter (string)
    Ouput: ending time (datetime.timedelta)
    '''
    num = int(Q[0])
    if Q[-1] == "Q":
        return datetime.timedelta(minutes = (4-num)*12, microseconds=1)
    return datetime.timedelta(minutes = -num*5, microseconds=1)

def compute_interval(in_time, out_time, start=datetime.timedelta(0, 48, 0), end=datetime.timedelta(0, 0, 0)):
    '''
    This function computes the intersection of a playing interval and the desired interval
    - in_time-out_time: playing interval of a player (datetime.time)
    - start-end: interval of the match we are interested in (datetime.time)
    Output:
    - interval length
    - int_start: interval starting time (datetime.timedelta)
    - int_end: interval ending time (datetime.timedelta)
    '''    
    int_start = min(in_time, start)
    if int_start.microseconds != 0:
        int_start -= datetime.timedelta(microseconds=1)
    int_end = max(out_time, end)
    if int_end.microseconds != 0:
        int_end -= datetime.timedelta(microseconds=1)
    null = datetime.timedelta() # in case the interval is negative, we will return a null interval
    return max(int_start - int_end, null), int_start, int_end