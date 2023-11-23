#
# Input processing for the received spreadsheet

import sys
import shared
import database
import ods
import convoy
import shipping
import escort
import os
import shutil
import gc
import ezodf

def unique(list1):

    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)


def Convoy( data ):
    print ( "Convoy" )
    return

#   exit if no data
    if data is None:
        return
#   Create an unique list of convoys in the sheet data
    convoy_list = [ d['convoy'] for d in data if 'convoy' in d and d['convoy'] is not None and d['convoy'] != 'None']
    #print ( convoy_list )

    for conv in convoy_list:
        #print ( conv )
        db =  ( convoy.get(conv) )
        shEntry = next(item for item in data if item['convoy'] == conv)
        if len(db) ==0:
            action, detail = convoy.validate ( {}, shEntry )
            if action == "Add":
                convoy.add ( conv,  detail )
        else:
            for dbEntry in db: 
                action, detail = convoy.validate ( dbEntry, shEntry )
                #print ( action, detail )
                if action == "Change":
                    convoy.change ( conv,  dbEntry['ID'], detail )

def Shipping( data ):
    print ( "Shipping" )
    #return

#   exit if no data
    if data is None:
        return
#   Create an unique list of the ships in each convoy in the sheet data
    convoy_list = [ { d['Convoy_number']: d['Ships_name'] } for d in data if 'Convoy_number' in d and d['Convoy_number'] is not None and d['Convoy_number'] != 'None']
    #print ( convoy_list )
#   {'HJ 001': 'FORT TOWNSHEND'}

    for conv in convoy_list:
        #print ( conv )
        db =  ( shipping.get(conv) )
        #print ( "sh: ", db, len(db) ) 
#       {'Convoy_number': 'HJF 048', 'Posn': None, 'Ships_name': 'LADY RODNEY', 'grt': 8194.0, 'year': 29.0, 'Flag': 'Br', 'Departure_Port': 'HALIFAX NS', 'Departure_date': '25/05/45', 'Arrival_Port': 'ST JOHNS NF', 'Arrival_date': '27/05/45', 'Cargo': 'GENERAL PASSENGERS', 'Notes': None}

        for key in conv:
            val = conv[key]
            shEntry = next((item for item in data if 'Convoy_number' in item and item['Convoy_number'] == key and item['Ships_name'] == val), None)
            if len(db) ==0:
                action, detail = shipping.validate ( {}, shEntry )
                if action == "Add":
                    shipping.add ( key, val,  detail )
            else:
                for dbEntry in db: 
                    action, detail = shipping.validate ( dbEntry, shEntry )
                    if action == "Change":
                        shipping.change ( conv, dbEntry['Ships_name'],  dbEntry['ID'], detail )
                #print ( action, detail )
    #print ( data[0] )

def Escort( data ):
    print ( "Escort" )
    #return

#   exit if no data
    if data is None:
        return
#   Create an unique list of the ships in each convoy in the sheet data
    convoy_list = [ { d['convoy']: d['escort'] } for d in data if 'convoy' in d and d['convoy'] != 'None' and d['convoy'] is not None]
    #print ( convoy_list )
#   {'HJ 001': 'FORT TOWNSHEND'}

    for conv in convoy_list:
        #print ( conv )
        db =  ( escort.get(conv) )
#       {'Convoy_number': 'HJF 048', 'Posn': None, 'Ships_name': 'LADY RODNEY', 'grt': 8194.0, 'year': 29.0, 'Flag': 'Br', 'Departure_Port': 'HALIFAX NS', 'Departure_date': '25/05/45', 'Arrival_Port': 'ST JOHNS NF', 'Arrival_date': '27/05/45', 'Cargo': 'GENERAL PASSENGERS', 'Notes': None}

        for key in conv:
            val = conv[key]
            shEntry = next((item for item in data if 'convoy' in item and item['convoy'] == key and item['escort'] == val), None)
            if len(db) ==0:
                action, detail = escort.validate ( {}, shEntry )
                if action == "Add":
                    escort.add ( key, val,  detail )
            else:
                for dbEntry in db: 
                    action, detail = escort.validate ( dbEntry, shEntry )
                    if action == "Change":
                        escort.change ( conv, dbEntry['Escort_detail'],  dbEntry['ID'], detail )
                #print ( action, detail )
    #print ( data[0] )

# Lets get the globals set up.

shared.conn = database.connectDB()
shared.spreadsheet = sys.argv[1]

shared.spread = ods.loadSpreadsheet(shared.spreadsheet)
shared.newspreadsheet = os.path.splitext(shared.spreadsheet)[0]+'_new.ods'
shared.dbupdate = os.path.splitext(shared.spreadsheet)[0]+'.sql'

# Let's make a copy of the incoming spreadsheet for the result
shutil.copy ( str(shared.spreadsheet), str(shared.newspreadsheet) )
shared.newss = ezodf.opendoc(shared.newspreadsheet)

# and zero the sql file
#shutil.rmtree ( shared.dbupdate, ignore_errors=True )
if os.path.exists ( shared.dbupdate ):
    os.remove ( shared.dbupdate )
#and add in some requirements to get the inserts to work using this data
#with open (shared.dbupdate, "a") as file:
#    file.write ( "ALTER TABLE `Merchant_movements` ALTER COLUMN `ARR_DATE` SET DEFAULT '0000-00-00 00:00:00';\n" )
#    file.write ( "ALTER TABLE `Merchant_movements` ALTER COLUMN `DEP_DATE` SET DEFAULT '0000-00-00 00:00:00';\n" )
#    file.write ( "UPDATE Convoy_detail SET Arrival_date = '25/08/44' where Arrival_date = '35/08/44';\n" )
#    file.write ( "ALTER TABLE `Convoy_detail` ALTER COLUMN `arr_date` SET DEFAULT '0000-00-00 00:00:00';\n" )
#    file.write ( "ALTER TABLE `Convoy_detail` ALTER COLUMN `dep_date` SET DEFAULT '0000-00-00 00:00:00';\n" )

# Process the sheets
for func in shared.spread:
    eval(func + '( shared.spread[func] )')

#and get the date fields in sync
with open (shared.dbupdate, "a") as file:
    file.write ( "UPDATE Merchant_movements SET Arrival_date = '' WHERE Arrival_date IN ( '??/10/41', '??/11/41','??/12/41' );\n" )
    file.write ( "UPDATE Convoy_detail SET arr_date = str_to_date ( Arrival_date, '%d/%m/%y' );\n" )
    file.write ( "UPDATE Convoy_detail SET dep_date = str_to_date ( Departure_date, '%d/%m/%y' );\n" )
    file.write ( "UPDATE Merchant_movements SET ARR_DATE = str_to_date ( Arrival_date, '%d/%m/%y' );\n" )
    file.write ( "UPDATE Merchant_movements SET DEP_DATE = str_to_date ( Departure_date, '%d/%m/%y' );\n" )
    file.write ( "UPDATE Merchant_movements SET ARR_DATE = date_sub(ARR_DATE, interval 100 year) WHERE year(ARR_DATE) > 2000;\n" )
    file.write ( "UPDATE Merchant_movements SET DEP_DATE = date_sub(DEP_DATE, interval 100 year) WHERE year(DEP_DATE) > 2000;\n" )
    file.write ( "UPDATE Convoy_detail SET arr_date = date_sub(arr_date, interval 100 year) WHERE year(arr_date) > 2000;\n" )
    file.write ( "UPDATE Convoy_detail SET dep_date = date_sub(dep_date, interval 100 year) WHERE year(dep_date) > 2000;\n" )

