import csv
import sqlite3

def create_table(conn,table):

    cur = conn.cursor()
    cur.execute(table)

database = "whitefield.db"

def create_tables_database():


    create_nodes_table = "CREATE TABLE nodes (id INTEGER PRIMARY KEY NOT NULL, lat REAL,lon REAL, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp TEXT);"

    create_node_tags_table = "CREATE TABLE nodes_tags (id INTEGER, key TEXT, value TEXT, type TEXT, FOREIGN KEY (id) REFERENCES nodes(id));"

    create_ways_table = "CREATE TABLE ways (id INTEGER PRIMARY KEY NOT NULL, user TEXT, uid INTEGER, version TEXT, changeset INTEGER, timestamp TEXT);"

    create_way_tags_table= "CREATE TABLE ways_tags (id INTEGER NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL,type TEXT,FOREIGN KEY (id) REFERENCES ways(id));"

    create_way_nodes_table = "CREATE TABLE ways_nodes (id INTEGER NOT NULL, node_id INTEGER NOT NULL, position INTEGER NOT NULL, FOREIGN KEY (id) REFERENCES ways(id), FOREIGN KEY (node_id) REFERENCES nodes(id));"


    conn = sqlite3.connect(database)

    if conn is not None:
        print("connection successful!")

        create_table(conn,create_nodes_table)

        create_table(conn,create_node_tags_table)

        create_table(conn,create_ways_table)

        create_table(conn, create_way_tags_table)

        create_table(conn, create_way_nodes_table)

        conn.close()
    else:
        print("Connection failed")


def populate_table_database(database,csv_filename,table,columns):

    conn = sqlite3.connect(database)
    conn.text_factory = str


    if conn is not None:

        cur = conn.cursor()
        with open(csv_filename,'rb') as file:

            reader = csv.DictReader(file)
            list_of_row_values_to_insert = [] # the values for each row of the table will be put in this list. Each row values will be separate tuple. Hence this is a list of tuples.
            for line in reader:
                row_data_tuple = ()
                for col in columns:
                    row_data_tuple = row_data_tuple+(line[col],) # append all the different column values for a row into a single tuple

                list_of_row_values_to_insert.append(row_data_tuple)


        columns_string = "("+ ", ".join(columns) + ")"
        symbol_list = []
        for i in range(0,len(columns)):
            symbol_list.append("?")
        symbol_string = "("+ ", ".join(symbol_list) + ")"

#The insert statement should look something like "INSERT INTO nodes (id,lat,lon,user,uid,version,changeset,timestamp) VALUES (?,?,?,?,?,?,?,?)".
#This will be used in the cur.executemany function, where a list will be provided with the values that should go in the place of ? in the above statement. This is created below

        insert_string = "INSERT INTO " + table + " " + columns_string + " " + "VALUES " + symbol_string + ";"
#       print(insert_string)
#        print(len(list_of_row_values_to_insert))
        cur.executemany(insert_string,list_of_row_values_to_insert)
#
        print("values inserted successfully into table")

        conn.commit()
        conn.close()




if __name__ == '__main__':
#if 1==1:
     create_tables_database()

     columns = ["id","lat","lon","user","uid","version","changeset","timestamp"]

     populate_table_database(database,"nodes.csv","nodes",columns)

     columns = ["id","key","value","type"]

     populate_table_database(database,"nodes_tags.csv","nodes_tags",columns)

     columns = ["id","user","uid","version","changeset","timestamp"]

     populate_table_database(database,"ways.csv","ways",columns)

     columns = ["id","key","value","type"]

     populate_table_database(database,"ways_tags.csv","ways_tags",columns)

     columns = ["id","node_id","position"]

     populate_table_database(database,"ways_nodes.csv","ways_nodes",columns)








