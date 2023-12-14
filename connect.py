import pandas as pd
import psycopg2
from psycopg2.extras import Json
from loguru import logger
from config import get_db_config
from sklearn.manifold import TSNE
import sql_queries as sql
import json


from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

# get data types of our columns
def get_column_dtypes(dataTypes):
    dataList = []
    for x in dataTypes:
        if x == 'int64':
            dataList.append('int')
        elif x == 'float64':
            dataList.append('float')
        elif x == 'bool':
            dataList.append('boolean')
        else:
            dataList.append('varchar')
    return dataList


# create input table in DB
def create_input_table(data):
    conn = None
    try:
        logger.info('Connecting to the PostgresSQL database...')
        conn = psycopg2.connect(**get_db_config())
        cur = conn.cursor()  # create a cursor

        cur.execute(sql.DROP_ALL_TABLES)

        cur.execute(sql.CREATE_DETECTORS_TABLE)
        cur.execute(sql.CREATE_PREDICTIONS_TABLE)
        cur.execute(sql.CREATE_RELIABLE_TABLE)
        cur.execute(sql.CREATE_TSNE_TABLE)

        columnName = list(data.columns.values)
        columnDataType = get_column_dtypes(data.dtypes)
        createTableStatement = sql.CREATE_INPUT_TABLE(columnName, columnDataType)
        cur.execute(createTableStatement)
        conn.commit()
        cur.close()  # close the communication with the PostgreSQL

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Error connecting to the database or executing query.")
        print(error)

    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed, inserted successfully.')


def insert_input(table, data):  # we can use this fucntion to add to our databse. params: table name and values. THen call this functions from autood
    """ Takes df, connects to the PostgreSQL database server, uploads to postgres """
    conn = None
    try:
        # connect to the PostgreSQL server
        logger.info('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**get_db_config())
        cur = conn.cursor()  # create a cursor

        sql.INSERT_VALUES(table, data, cur)

        conn.commit()
        cur.close()  # close the communication with the PostgreSQL

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Error connecting to the database or executing query.")
        print(error)

    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed, inserted successfully.')


def insert_tsne(table, data, label_col_name, index_col_name):
    id = data[index_col_name]
    data = data.drop(index_col_name, axis=1)
    data = data.drop(label_col_name, axis=1)
    tsne = TSNE(n_components=2, learning_rate="auto", perplexity=5, verbose=1, early_exaggeration=12,
                random_state=123)  # perplexity for pagblocks: 30
    fit = tsne.fit_transform(data)
    fit_df = pd.DataFrame()
    fit_df["id"] = id
    fit_df["tsne1"] = fit[:, 0]
    fit_df["tsne2"] = fit[:, 1]
    insert_input(table, fit_df)


def truncate_all_tables():
    conn = None
    try:
        conn = psycopg2.connect(**get_db_config())
        cur = conn.cursor()
        # cur.execute(sql.TRUNCATE_ALL_TABLES)
        conn.commit()
        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Error connecting to the database or executing query.")
        print(error)

    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed, inserted successfully.')


def truncate_temp_tables():
    conn = None
    try:
        conn = psycopg2.connect(**get_db_config())
        cur = conn.cursor()
        cur.execute(sql.TRUNCATE_TEMP_TABLES)
        conn.commit()
        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Error connecting to the database or executing query.")
        print(error)

    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed, inserted successfully.')

def new_session(id):
    conn = None
    try:
        conn = psycopg2.connect(**get_db_config())
        cur = conn.cursor()
        cur.execute(sql.NEW_SESSION(id))
        conn.commit()
        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Error connecting to the database or executing query.")
        print(error)

    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed, inserted successfully.')

def new_run(id):
    conn = None
    try:
        conn = psycopg2.connect(**get_db_config())
        cur = conn.cursor()

        cur.execute(sql.ITERATIONS_FROM_RELIABLE_TABLE)  # number of iterations for reliable labels
        iteration = cur.fetchall()[0][0] + 1

        # drop all tables on each run
        cur.execute(sql.DROP_ALL_TEMP_TABLES)

        # create temp tables so that we can pass the data in a way that JS/D3 needs it
        cur.execute(sql.CREATE_TEMP_LOF_TABLE)

        cur.execute(sql.CREATE_TEMP_KNN_TABLE)

        cur.execute(sql.CREATE_TEMP_IF_TABLE)

        cur.execute(sql.CREATE_TEMP_MAHALANOBIS_TABLE)

        cur.execute(sql.CREATE_REALIABLE_TABLES(iteration))

        # Join all tables together
        SQL_statement = sql.JOIN_ALL_TABLES
        join_reliable = sql.JOIN_RELIABLE_TABLES(iteration)
        drop_reliable = sql.DROP_REALIABLE_TABLES(iteration)

        cur.execute(f"{SQL_statement}{join_reliable}")

        # data = [col for col in cur]
        field_names = [i[0] for i in cur.description]
        result = [dict(zip(field_names, row)) for row in cur.fetchall()]
        cur.execute(f"{drop_reliable}")
        #print(json.dumps(result, cls=DecimalEncoder, indent=None))
        sql_query= sql.NEW_RUN
        json_data_float = json.loads(json.dumps(result, cls=DecimalEncoder))
        cur.execute(sql_query, (id, Json(json_data_float), id))
        conn.commit()
        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Error connecting to the database or executing query.")
        print(error)

    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed, inserted successfully.')

def create_session_run_tables():
    conn = None
    try:
        logger.info('Connecting to the PostgresSQL database...')
        conn = psycopg2.connect(**get_db_config())
        cur = conn.cursor()  # create a cursor
        cur.execute(sql.CREATE_SESSION_RUN_TABLE)
        conn.commit()
        cur.close()  # close the communication with the PostgreSQL

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Error connecting to the database or executing query.")
        print(error)

    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed, inserted successfully.')