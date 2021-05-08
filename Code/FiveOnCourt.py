from Functions import *

def check_fives(intervals, clock):
    '''
    This function returns the fives on court at timestamp clock
    - intervals: fives during the match (dictionary of {string: list of tuples})
    - clock: match timestamp (datetime.timedelta)
    Output: either one five or two fives (set or list of sets)
    '''
    for interval, five in intervals.items():
        if time_from_string(interval[0]) >= clock and clock >= time_from_string(interval[1]):
            if clock == time_from_string(interval[1]):
                if clock == quarter_end_time(quarter_from_time(string_from_time(clock))):
                    return five
                fives = [five]
            elif clock == time_from_string(interval[0]):
                if clock == quarter_start_time(quarter_from_time(string_from_time(clock))):
                    return five
                else:
                    fives.append(five)
                    return fives
            else:
                return five

def main(oncourtintervals, clock):
    '''
    This function returns the fives of each team on court at timestamp clock
    - oncourtintervals: fives during the match, obtained with game.playing_intervals[0] (dictionary of {string: list of tuples})
    - clock: match timestamp (string)
    Output: either one five or two fives (list: [set or list of sets])
    '''
    fives = [None, None]
    clock = time_from_string(clock)
    for team in range(1,3):
        fives[team-1] = check_fives(oncourtintervals[team-1], clock)
    return fives