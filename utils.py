from datetime import datetime
import re

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def fixDate ( input ):
    if input is None:
        return ""
    elif input.strip() == "0000-00-00":
        return ""
    elif input.find ( "-" ) > -1:
        data = [int(re.sub("[^0-9]", "", s)) for s in input.split ( "-" )]
    elif input.find ( "/" ) > -1:
        data = [int(re.sub("[^0-9]", "", s)) for s in input.split ( "/" )]
    else: 
        return ""
    if data[0] > 1900:
        base = str(data[0])+"-"+str(data[1])+"-"+str(data[2])
    elif data[2] > 1900:
        base = str(data[2])+"-"+str(data[1])+"-"+str(data[0])
    else:
        base = str((1900+data[2]))+"-"+str(data[1])+"-"+str(data[0])
    stamp = datetime.strptime ( base, "%Y-%m-%d" )
    return ( stamp.strftime ( "%d/%m/%y" ) )

# Darn. Some convoys are numeric
def isint ( field, value ):
    if field == "Convoy_number" and isFloat(value):
        return str(int(float(value)))
    return str(int(float(value))) if field in [ 'USN', 'Other', 'grt', 'Posn', 'year', 'survivor', 'TDS', 'CCB', 'ROP', 'CBD-Hist' ] else value
