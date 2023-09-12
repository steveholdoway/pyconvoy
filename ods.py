#
# The spreadsheed processing stuff
import os.path
import shared
import ezodf
import utils

def updateNewSpreadsheet ( sheet, name, data, highlight, cola=0, colb=2 ):
    #print ( data )
    #newss = ezodf.opendoc(shared.newspreadsheet)
    newsheet = shared.newss.sheets[sheet]
#   Find the row to change
#   Simple col 0 for convoy. col0 and 2 for shipping
    rownum = 0
    if isinstance ( name, str ):
        for cell in newsheet.column(cola):
            #print ( cell.value )
            if name == cell.value:
                break
            rownum = rownum + 1
    else:
        for col0 in name:
            col2 = name[col0]
            for row in newsheet.rows():
                #print ( row[0].value, row[2].value )
                if row[cola].value == col0 and row[colb].value == col2:
                    #print ( row[0].value, row[2].value )
                    break
                rownum = rownum + 1
    #print (rownum )

    for entry in data:
        colnum = 0
        for cell in newsheet.row(0):
            #print ( cell.value, entry )
            found = False
            if str(entry) == str(cell.value).strip():
                found = True
                break
            colnum = colnum+1
#       Change colour of the cell if it's been changed.
        if found:
            #print ( newsheet[rownum,colnum].style_name )
            #print ( newsheet.nrows(), rownum, colnum )
            nrows = newsheet.nrows()
            if rownum < nrows:
                newsheet[rownum,colnum].style_name = highlight
            #newsheet[rownum,colnum].set_value ( "CHANGED: "+str(data[entry]))
            #print ( entry, data[entry], rownum, colnum )
            
    shared.newss.save()

def findSpreadsheet ( ods ):
    if os.path.exists( ods ):
        retval =  ods
    elif os.path.exists( 'data/'+ods ):
        retval =  'data/'+ods
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

    return retval

def loadSheet ( sheet ):
    #print("-"*40)
    #print("   Sheet name : '%s'" % sheet.name)
    #print("Size of Sheet : (rows=%d, cols=%d)" % (sheet.nrows(), sheet.ncols()) )

#   Empty sheet?
    if sheet.nrows() <= 1:
        return None

#   Column names in the first row
    names = []
    for row in sheet.row(0):
        if row.value is not None:
            names.append ( str(row.value).strip() ) 

#   Remove the top line, and save the info
    sheet.delete_rows( index=0, count=1 )
    data = []
    for row in sheet.rows():
        saved={}
        if row[0].value is not None:
            #print ( row[0].value )
            for index, cell in zip ( names, row ):
                if index.lower().find ( "date" ) > -1 or index.lower() == "from_" or index.lower() == "to":
                    saved[index] = utils.fixDate (cell.value)
                else:
                    saved[index] = str(cell.value).strip()
        data.append ( saved )
    #print ( data )
    return data

def loadSpreadsheet ( ods ):
    retval = {}
#   Grab the data
    doc = ezodf.opendoc(findSpreadsheet(ods))
    print("Spreadsheet contains %d sheet(s)." % len(doc.sheets))
    for sheet in doc.sheets:
        retval[sheet.name] = loadSheet ( sheet )

    #for set in retval:
        #print ( set )
        #for newdata in retval[set][0]:
               #print( newdata )
    return retval
