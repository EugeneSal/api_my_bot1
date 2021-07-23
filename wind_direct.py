d1 = {
    'north': '⬆',
    'northeast': '↗',
    'northwest': '↖',
    'west': '⬅',
    'east': '➡',
    'south': '⬇',
    'southeast': '↘',
    'southwest': '↙',
}


def wind(wind_direction):
    wd_favour = ''
    if 20 > wind_direction >= 0 or 360 >= wind_direction >= 340:
        wd_favour = d1['north']
    elif 67 > wind_direction >= 20:
        wd_favour = d1['northeast']
    elif 112 > wind_direction >= 67:
        wd_favour = d1['east']
    elif 157 > wind_direction >= 112:
        wd_favour = d1['southeast']
    elif 202 > wind_direction >= 157:
        wd_favour = d1['south']
    elif 247 > wind_direction >= 202:
        wd_favour = d1['southwest']
    elif 292 > wind_direction >= 247:
        wd_favour = d1['west']
    elif 340 > wind_direction >= 292:
        wd_favour = d1['northwest']
    return wd_favour
