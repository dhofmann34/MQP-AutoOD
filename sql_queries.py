import psycopg2.extras as extras

DROP_ALL_TABLES = """
    DROP TABLE IF EXISTS
    detectors,
    predictions,
    reliable,
    tsne,
    input
    """

CREATE_SESSION_RUN_TABLE = """
    CREATE TABLE IF NOT EXISTS session (
        id uuid PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS run (
        id integer,
        json JSONB,
        session_id uuid NOT NULL REFERENCES session(id) ON UPDATE CASCADE,
        PRIMARY KEY (id, session_id)
    );
"""

CREATE_SESSION_TABLE = """
    CREATE TABLE session (
        id uuid PRIMARY KEY
    );
    """

def NEW_SESSION(id):
    query = f"INSERT INTO session (id) VALUES ('{id}') ON CONFLICT (id) DO NOTHING;"
    return query

CREATE_RUN_TABLE = """
    CREATE TABLE run (
        id integer,
        json JSONB,
        run_configuration JSONB,
        session_id uuid NOT NULL REFERENCES session(id) ON UPDATE CASCADE,
        PRIMARY KEY (id, session_id)
    );
    """

NEW_RUN = """
                INSERT INTO run (id, json, run_configuration, session_id)
                VALUES (
                    (SELECT COUNT(*) FROM run WHERE session_id = %s) + 1,
                    %s,
                    %s,
                    %s
                )
            """


def get_json(session_id, run_id):
    query = f"SELECT json FROM run WHERE session_id = '{session_id}' AND id = {run_id};"
    return query

def get_count(session_id):
    query = f"SELECT COUNT(*) FROM run WHERE session_id = '{session_id}';"
    return query

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
    query = "INSERT INTO {}({}) VALUES %s".format(table, cols)
    tuples = [tuple(x) for x in data.to_numpy()]
    extras.execute_values(cur, query, tuples)

ITERATIONS_FROM_RELIABLE_TABLE = "SELECT max(iteration) FROM reliable"

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
        createTableStatement += """
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

def DROP_REALIABLE_TABLES(iteration):
    dropTableStatement = ""
    for i in range(iteration):
        dropTableStatement += f"DROP TABLE IF EXISTS reliable_{i};\n"
    return dropTableStatement

TRUNCATE_ALL_TABLES = """
                            DO $$ 
                            BEGIN
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'input') THEN
                                    EXECUTE 'TRUNCATE TABLE input';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tsne') THEN
                                    EXECUTE 'TRUNCATE TABLE tsne';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'detectors') THEN
                                    EXECUTE 'TRUNCATE TABLE detectors';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'predictions') THEN
                                    EXECUTE 'TRUNCATE TABLE predictions';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reliable') THEN
                                    EXECUTE 'TRUNCATE TABLE reliable';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'temp_if') THEN
                                    EXECUTE 'TRUNCATE TABLE temp_if';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'temp_knn') THEN
                                    EXECUTE 'TRUNCATE TABLE temp_knn';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'temp_lof') THEN
                                    EXECUTE 'TRUNCATE TABLE temp_lof';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'temp_mahalanobis') THEN
                                    EXECUTE 'TRUNCATE TABLE temp_mahalanobis';
                                END IF;
                            END $$;
                        """

TRUNCATE_TEMP_TABLES = """
                            DO $$ 
                            BEGIN
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'input') THEN
                                    EXECUTE 'TRUNCATE TABLE input';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tsne') THEN
                                    EXECUTE 'TRUNCATE TABLE tsne';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'detectors') THEN
                                    EXECUTE 'TRUNCATE TABLE detectors';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'predictions') THEN
                                    EXECUTE 'TRUNCATE TABLE predictions';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reliable') THEN
                                    EXECUTE 'TRUNCATE TABLE reliable';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'temp_if') THEN
                                    EXECUTE 'TRUNCATE TABLE temp_if';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'temp_knn') THEN
                                    EXECUTE 'TRUNCATE TABLE temp_knn';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'temp_lof') THEN
                                    EXECUTE 'TRUNCATE TABLE temp_lof';
                                END IF;
                                
                                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'temp_mahalanobis') THEN
                                    EXECUTE 'TRUNCATE TABLE temp_mahalanobis';
                                END IF;
                            END $$;
                        """