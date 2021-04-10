from Functions import *


def check_fives(intervals, clock):
    for interval, five in intervals.items():
        if time_from_string(interval[0]) >= clock and clock >= time_from_string(interval[1]):
            if clock == time_from_string(interval[1]):
                fives = [five]
            elif clock == time_from_string(interval[0]):
                if string_from_time(clock) == "48:00":
                    return five
                else:
                    fives.append(five)
                    return fives
            else:
                return five


def FiveOnCourtMain(oncourtintervals, clock):
    fives = [None, None]
    clock = time_from_string(clock)
    for team in range(1,3):
        fives[team-1] = check_fives(oncourtintervals[team-1], clock)
    return fives