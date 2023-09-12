import shared
import mysql.connector
from mysql.connector import Error
import ods
import utils

Lookup = {
    #'source': 'source',
	'Convoy_number': 'Convoy_number',
	'Posn': 'Posn',
	'Ships_name': 'Ships_name',
	'grt': 'grt',
	'year': 'year',
	'Flag': 'Flag',
	'Departure_Port': 'Departure_Port',
	'Departure_date': 'Dep_date',
	'Arrival_Port': 'Arrival_Port',
	'Arrival_date': 'Arr_date',
	'Cargo': 'Cargo',
	'Notes': 'Notes',
    #'survivor': 'survivor',
}

def get (entry ):
    #print ("getShipping ", entry )
    cursor = shared.conn.cursor(dictionary=True)
    data = []
    for key, value in entry.items():
        query = ("select distinct * from Merchant_movements where Convoy_number = %s and Ships_name = %s")
        cursor.execute ( query, [ key, value ] )
        for row in cursor:
            data.append ( row )
            #print ( row )
        cursor.close()
    #print ("getShipping ", data )
    return ( data )

def change ( name, ship, id, data ):
    #print ( "Change", name, id, data )
    set = ""
    for datum in data:
        if data[datum] != 'None' and str(data[datum]) != "" and data[datum] is not None:
            set = set+',`'+str(datum)+'`="'+utils.isint(datum, str(data[datum]))+'"'
    if set != "":
#   Strip off the extra "," at the start
        set = set[1:]
#   Append to an sql script
        sql = 'UPDATE Merchant_movements SET '+set+' WHERE `ID`='+str(id)+';\n'
        with open (shared.dbupdate, "a") as file:
            file.write ( sql )
#      Update the spreadsheet.
        ssdata = { Lookup[k]: data[k] for k in data }
        ods.updateNewSpreadsheet ( "Shipping", name, ssdata, "Good" )
#      print ( sql )

def add ( name, ship, data ):
    #print ( "Add", name, data )
    fields = ""
    values = ""
    for datum in data:
        if data[datum] != 'None' and str(data[datum]) != "" and data[datum] is not None:
            fields = fields+',`'+str(datum)+'`'
            values = values+',"'+utils.isint(datum, str(data[datum]))+'"'
#   Add the source field if missing
    if fields != "":
        if fields.find("`source`") == -1:
            fields = "`source`"+fields
            values = '"T"'+values
        else:
            fields = fields[1:]
            values = values[1:]

#       Append to an sql script
        sql = "INSERT INTO Merchant_movements ( "+fields+" ) VALUES ( "+values+" );\n"
        with open (shared.dbupdate, "a") as file:
            file.write ( sql )
#       Update the spreadsheet.
        ssdata = { Lookup[k]: data[k] for k in data }
        ods.updateNewSpreadsheet ( "Shipping", { name: ship }, ssdata, "Accent 1" )
        #print ( sql )

def validate ( db, ss ):
    if len(db) == 0:
        diff = {k: ss[Lookup[k]] for k in Lookup if ss[Lookup[k]] is not None}
        return "Add", diff
    diff = {k: ss[Lookup[k]] for k in db if k in Lookup and Lookup[k] in ss and db[k] != ss[Lookup[k]] and ss[Lookup[k]] is not None and ss[Lookup[k]] != "None" }
    if diff is None:
        return "None", ""
    else:
        return "Change", diff

