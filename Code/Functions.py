import datetime
import os

def get_team(team, date):
    '''
    This functions returns the codification of the team name, which is needed to access to the website
    As information is stored by using it, it also grants unicity in the database
    - team: name of the team (string)
        - Location
        - Club name
        - The combination of the previous options 
    - date: date of the match/season (string)
    Output: 3-letter representation of the team, which are often the first 3 letters of the city (string)
    '''
    if "/" in date: # match
        year, month, _ = date.split("/")
        year, month = int(year), int(month)
        if month < 9:
            season1, season2 = year-1, year
        else:
            season1, season2 = year, year+1
    else: # season
        season1, season2 = date.split("-")
        season1, season2 = int(season1), int(season2)
    
    os.chdir(os.path.dirname(__file__))
    f = open('./Teams.txt', 'r')
    lines = f.readlines()
    for line in lines:
        names, interval = line.strip("\n").split("; ")
        names, interval = names.split(", "), interval.split(" - ")
        for name in names:
            if name == team and int(interval[0]) <= season1 and (interval[1] == "" or season2 <= int(interval[1])):
                return names[0]
    return None

def other_team(team):
    '''
    Given a team, this function returns the other team
    - team: team id (either 1 or 2, integer)
    Output: id of the other team (integer)
    '''
    return (team*5)%3

def time_from_string(clock):
    '''
    This function returns a datetime.timedelta type value from a time represented as a string
    - clock: It must have the structure quarter:MM:SS where quarter can be xQ (with x={1,2,3,4} or xOT).
            MM:SS should be maximum 12:00 if the quarter is a Q and 5:00 if it is an OT
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
        Q = 4 - int(minutes/12)
        minutes %= 12
        seconds %= 60
        if minutes%12 == 0 and seconds == 0:
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
        Q = 1 + int(minutes/5)
        minutes %= 5
        seconds %= 60
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

def compute_interval(start, end, restrStart=None, restrEnd=None):
    '''
    This function computes the intersection of a playing interval and the desired interval
    - start-end: playing interval of a player (datetime.time)
    - restrStart-restrEnd: interval of the match we are interested in (datetime.time)
    Output:
    - interval length
    - start: intersection interval starting time (datetime.timedelta)
    - end: intersection interval ending time (datetime.timedelta)
    '''
    if restrStart is not None:
        start = min(start, restrStart)
    if start.microseconds != 0:
        start -= datetime.timedelta(microseconds=1)
    if restrEnd is not None:
        end = max(end, restrEnd)
    if end.microseconds != 0:
        end -= datetime.timedelta(microseconds=1)
    null = datetime.timedelta() # in case the interval is negative, we will return a null interval
    return max(start - end, null), start, end