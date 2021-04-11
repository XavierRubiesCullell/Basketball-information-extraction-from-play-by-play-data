def FivesIntervalsMain(oncourtintervals, five):
    five = set(five)
    intervals = []
    for interval in oncourtintervals:
        if oncourtintervals[interval] == five:
            intervals.append(interval)
    return intervals