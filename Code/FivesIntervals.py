def main(oncourtintervals, five):
    '''
    This function returns the intervals an introduced five played
    Input:
    - oncourtintervals: fives intervals of a team (list)
    - five: list of players we are interested in (list)
    '''
    five = set(five)
    intervals = []
    for interval in oncourtintervals:
        if oncourtintervals[interval] == five:
            intervals.append(interval)
    return intervals