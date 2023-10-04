import pandas as pd
import psycopg2
from config import db_config
import psycopg2.extras as extras
import numpy as np
from sklearn.manifold import TSNE
import sql_queries as sql

# get data types of our columns 
def getColumnDtypes(dataTypes):
    dataList = []
    for x in dataTypes:
        if(x == 'int64'):
            dataList.append('int')
        elif (x == 'float64'):
            dataList.append('float')
        elif (x == 'bool'):
            dataList.append('boolean')
        else:
            dataList.append('varchar')
    return dataList

# create input table in DB
def create_input_table(data):
    conn = None
    try:
        # read connection parameters
        params = db_config()  # get DB info from config.py

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()  # create a cursor

        cur.execute(sql.DROP_ALL_TABLES)

        cur.execute(sql.CREATE_DETECTORS_TABLE)
        cur.execute(sql.CREATE_PREDICTIONS_TABLE)
        cur.execute(sql.CREATE_RELIABLE_TABLE)
        cur.execute(sql.CREATE_TSNE_TABLE)


        columnName = list(data.columns.values)
        columnDataType = getColumnDtypes(data.dtypes)
        createTableStatement = sql.CREATE_INPUT_TABLE(columnName, columnDataType)
        cur.execute(createTableStatement)
        conn.commit()
        cur.close()  # close the communication with the PostgreSQL

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed, inserted successfully.')


def insert_input(table, data):  # we can use this fucntion to add to our databse. params: table name and values. THen call this functions from autood
    """ Takes df, connects to the PostgreSQL database server, uploads to postgres """
    conn = None
    try:
        # read connection parameters
        params = db_config()  # get DB info from config.py

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        cur = conn.cursor()  # create a cursor

        sql.INSERT_VALUES(table, data, cur)
        
        conn.commit()
        cur.close()  # close the communication with the PostgreSQL

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed, inserted successfully.')

def insert_tsne(table, data, label_col_name, index_col_name):
    id = data[index_col_name]
    data = data.drop(index_col_name, axis=1)
    data = data.drop(label_col_name, axis=1)
    tsne = TSNE(n_components=2, learning_rate = "auto", perplexity = 5, verbose=1, early_exaggeration = 12, random_state=123)  # perplexity for pagblocks: 30
    fit = tsne.fit_transform(data)
    fit_df = pd.DataFrame()
    fit_df["id"] = id
    fit_df["tsne1"] = fit[:,0]
    fit_df["tsne2"] = fit[:,1]
    insert_input(table, fit_df)

def truncate_all_tables():
    params = config()  # get DB info from config.py
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(sql.TRUNCATE_ALL_TABLES)  # empty tables for demo
    conn.commit()
    cur.close()
    conn.close()

def truncate_temp_tables():
    params = config()  # get DB info from config.py
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(sql.TRUNCATE_TEMP_TABLES)  # empty tables for demo
    conn.commit()
    cur.close()
    conn.close()





# if __name__ == '__main__':
#     connect()