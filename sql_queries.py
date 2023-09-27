import psycopg2.extras as extras

DROP_ALL_TABLES = """
    DROP TABLE IF EXISTS
    detectors,
    predictions,
    reliable,
    tsne,
    input
    """

CREATE_DETECTORS_TABLE = """
    CREATE TABLE detectors (id integer, detector text, k integer, n integer, prediction integer, score float);
    """

CREATE_PREDICTIONS_TABLE = """
    CREATE TABLE predictions (id integer, prediction integer, correct integer);
    """

CREATE_RELIABLE_TABLE = """
    CREATE TABLE reliable (id integer, iteration integer, reliable integer);
    """

CREATE_TSNE_TABLE = """
    CREATE TABLE tsne (id integer, tsne1 float, tsne2 float);
    """

def CREATE_INPUT_TABLE(columnName, columnDataType):
    createTableStatement = 'CREATE TABLE IF NOT EXISTS input ('
    for i in range(len(columnDataType)):
        createTableStatement = createTableStatement + str(columnName[i]) + ' ' + columnDataType[i] + ','
    createTableStatement = createTableStatement[:-1] + ' );'
    return createTableStatement

def INSERT_VALUES(table, data, cur):
    cols = ','.join(list(data.columns))
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    tuples = [tuple(x) for x in data.to_numpy()]
    extras.execute_values(cur, query, tuples)

DROP_ALL_TEMP_TABLES = """
    DROP TABLE IF EXISTS
    temp_lof,
    temp_knn,
    temp_if,
    temp_mahalanobis;
    """
CREATE_TEMP_LOF_TABLE = """
    CREATE TABLE temp_lof AS (
    SELECT id, ROUND(AVG(prediction)) AS Prediction_LOF, AVG(score) AS SCORE_LOF 
    FROM detectors 
    WHERE detector = 'LOF' 
    GROUP BY id
    )
    """

CREATE_TEMP_KNN_TABLE = """
    CREATE TABLE temp_knn AS (
    SELECT id, ROUND(AVG(prediction)) AS Prediction_KNN, AVG(score) AS SCORE_KNN 
    FROM detectors 
    WHERE detector = 'KNN' 
    GROUP BY id
    )
    """

CREATE_TEMP_IF_TABLE = """
    CREATE TABLE temp_if AS (
    SELECT id, ROUND(AVG(prediction)) AS Prediction_if, AVG(score) AS SCORE_if
    FROM detectors 
    WHERE detector = 'IF' 
    GROUP BY id
    )
    """

CREATE_TEMP_MAHALANOBIS_TABLE = """
    CREATE TABLE temp_mahalanobis AS (
    SELECT id, ROUND(AVG(prediction)) AS Prediction_mahalanobis, AVG(score) AS SCORE_mahalanobis
    FROM detectors 
    WHERE detector = 'mahalanobis' 
    GROUP BY id
    )
    """

JOIN_ALL_TABLES = """  
        SELECT *
        FROM input 
        FULL JOIN tsne using (id)
        FULL JOIN temp_lof using (id)
        FULL JOIN temp_knn using (id)
        FULL JOIN temp_if using (id)
        FULL JOIN temp_mahalanobis using (id)
        FULL JOIN predictions using (id)
        """

def CREATE_REALIABLE_TABLES(iteration):
    createTableStatement = ""
    for i in range(iteration):
        sql_statements += """
            CREATE TABLE reliable_{} AS (
            SELECT id, reliable as reliable_{}
            FROM reliable 
            WHERE iteration = {}
            );
        """.format(i, i, i)
    return createTableStatement

def JOIN_RELIABLE_TABLES(iteration):
    join_reliable = ""  # join relibale labels
    for i in range(iteration):
        join_reliable = f"{join_reliable} FULL JOIN reliable_{i} using (id)" 
    return join_reliable