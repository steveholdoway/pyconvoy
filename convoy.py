import shared
import mysql.connector
from mysql.connector import Error
import ods
import utils

Lookup = {
	'Convoy_number': 'convoy',
	'Departure_Port': 'dep_port',
	'Departure_date': 'dep_date',
	'Arrival_Port': 'arr_port',
	'Arrival_date': 'arr_date',
	'Commodore': 'Commodore',
	'CommName': 'CommName',
	'Vice_Commodore': 'ViceCommodore',
	'ViceCommName': 'ViceCommName',
	'Rear_Commodore': 'RearCommodore',
	'Rear_Commodore 2': 'RearCommodore2',
	'TDS': 'TDS',
	'CCB': 'CCB',
	'ROP': 'ROP',
	'CBD-Hist': 'CBD_Hist',
	'USN': 'USN',
	'Other': 'Other',
}

Lookup1 = {
    'source': 'source',
	'Convoy_number': 'Convoy_number',
	'Departure_Port': 'Departure_Port',
	'Departure_date': 'Departure_date',
	'Arrival_Port': 'Arrival_Port',
	'Arrival_date': 'Arrival_date',
	'Commodore': 'Commodore',
	'Link1': 'Link1',
	'CommName': 'CommName',
	'Vice_Commodore': 'Vice_Commodore',
	'Link2': 'Link2',
	'ViceCommName': 'ViceCommName',
	'Rear_Commodore': 'Rear_Commodore',
	'TDS': 'TDS',
	'CCB': 'CCB',
	'ROP': 'ROP',
	'Rear_Commodore': 'Rear_Commodore',
	'CBD-Hist': 'CBD-Hist',
	'USN': 'USN',
	'Other': 'Other',
	'Rear_Commodore': 'Rear_Commodore',
	'MV_sunk': 'MV_sunk',
	'MV_damaged': 'MV_damaged',
	'Warships': 'MV_damaged',
}

def check (entry):
    #print ( "check" )
    cursor = shared.conn.cursor()
    query = ("select distinct * from Convoy_detail"
            " where convoy_number = %s")
    cursor.execute ( query, ( entry ) )
    ret = []
    for row in cursor:
        ret.append ( row )
        #print  ( row )
    cursor.close()
    #print ( ret )
    return ( ret )

def get (entry):
    #print ("getConvoy ", entry )
    cursor = shared.conn.cursor(dictionary=True)
    query = ("select distinct * from Convoy_detail where convoy_number = %s")
    cursor.execute ( query, [ entry ] )
    data = []
    for row in cursor:
        data.append ( row )
        #print ( row )
    cursor.close()
    return ( data )

def change ( name, id, data ):
    #print ( "Change", name, id, data )
    set = ""
    for datum in data:
        if data[datum] != 'None' and str(data[datum]) != "" and data[datum] is not None:
            set = set+',`'+str(datum)+'`="'+utils.isint(datum, str(data[datum]))+'"'
#   Strip off the extra "," at the start
    if set != "":
        set = set[1:]
#       Append to an sql script
        sql = "UPDATE Convoy_detail SET "+set+' WHERE `ID`='+str(id)+';\n'
        with open (shared.dbupdate, "a") as file:
            file.write ( sql )
#       Update the spreadsheet.
        ssdata = { Lookup[k]: data[k] for k in data }
        ods.updateNewSpreadsheet ( "Convoy", name, ssdata, "Good" )
        #print ( sql )

def add ( name, data ):
    #print ( "Add", name, data )
    fields = ""
    values = ""
    for datum in data:
        if data[datum] != 'None' and str(data[datum]) != "" and data[datum] is not None:
            fields = fields+',`'+str(datum)+'`'
            values = values+',"'+utils.isint(datum, str(data[datum]))+'"'
#   Strip off the extra "," at the start
    if fields != "":
        fields = fields[1:]
        values = values[1:]
#       Append to an sql script
        sql = "INSERT INTO Convoy_detail ( "+fields+" ) VALUES ( "+values+" );\n"
        with open (shared.dbupdate, "a") as file:
            file.write ( sql )
#       Update the spreadsheet.
        ssdata = { Lookup[k]: data[k] for k in data }
        ods.updateNewSpreadsheet ( "Convoy", name, ssdata, "Accent 1" )
    #print ( sql )

def validate ( db, ss ):
    if len(db) == 0:
        diff = {k: ss[Lookup[k]] for k in Lookup if ss[Lookup[k]] is not None}
        return "Add", diff
    #print ( "db", db )
    #print ( "ss", ss )
    diff = {k: ss[Lookup[k]] for k in db if k in Lookup and Lookup[k] in ss and db[k] != ss[Lookup[k]] and ss[Lookup[k]] is not None}
    if diff is None:
        return "None", ""
    else:
        return "Change", diff
    #print ( "diff", diff )

