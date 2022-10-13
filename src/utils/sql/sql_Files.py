from mysql.connector import OperationalError


def executeScriptsFromFile(cursor, filename):
    # Open and read the file as a single buffer
    fd = open(f"src/db/sql/{filename}", 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    try:
        cursor.execute(sqlCommands[0])
        result = cursor.fetchall()
        return result
    except OperationalError as msg:
        print("Command skipped: ", msg)