import datetime

def getNicePerfTime(timeDiff):
    return "%s" % str(str(datetime.timedelta(seconds=timeDiff))).split('.')[0]
