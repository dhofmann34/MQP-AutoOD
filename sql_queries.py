import psycopg2.extras as extras

def DROP_ALL_TABLES(session_id): 
    query = f"""
    DROP TABLE IF EXISTS
    "detectors_{session_id}",
    "predictions_{session_id}",
    "reliable_{session_id}",
    "tsne_{session_id}",
    "input_{session_id}"
    """
    return query

CREATE_SESSION_RUN_TABLE = """
    CREATE TABLE IF NOT EXISTS session (
        id uuid PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS run (
        id integer,
        json JSONB,
        run_configuration JSONB,
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


def get_run_configs(session_id, run_id):
    query = f"SELECT run_configuration FROM run WHERE session_id = '{session_id}' AND id = {run_id};"
    return query


def get_count(session_id):
    query = f"SELECT COUNT(*) FROM run WHERE session_id = '{session_id}';"
    return query

def create_detectors_table(session_id):
    query = f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'detectors_{session_id}') THEN
                DROP TABLE "detectors_{session_id}";
            END IF;
            CREATE TABLE "detectors_{session_id}" (
                id INTEGER,
                detector TEXT,
                k INTEGER,
                n INTEGER,
                prediction INTEGER,
                score FLOAT
            );
        END $$;
    """
    return query
    

def create_predictions_table(session_id):
    query = f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'predictions_{session_id}') THEN
                DROP TABLE "predictions_{session_id}";
            END IF;
            CREATE TABLE "predictions_{session_id}" (
                id INTEGER,
                prediction INTEGER,
                correct INTEGER
            );
        END $$;
    """
    return query

def create_reliable_table(session_id):
    query = f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reliable_{session_id}') THEN
                DROP TABLE "reliable_{session_id}";
            END IF;
            CREATE TABLE "reliable_{session_id}" (
                id INTEGER,
                iteration INTEGER,
                reliable INTEGER
            );
        END $$;
    """
    return query

def create_tsne_table(session_id):
    query = f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tsne_{session_id}') THEN
                DROP TABLE "tsne_{session_id}";
            END IF;
            CREATE TABLE "tsne_{session_id}" (
                id INTEGER,
                tsne1 FLOAT,
                tsne2 FLOAT
            );
        END $$;
    """
    return query

def CREATE_INPUT_TABLE(columnName, columnDataType, session_id):
    createTableStatement = f'CREATE TABLE IF NOT EXISTS "input_{session_id}" ('
    for i in range(len(columnDataType)):
        createTableStatement = createTableStatement + str(columnName[i]) + ' ' + columnDataType[i] + ','
    createTableStatement = createTableStatement[:-1] + ' );'
    return createTableStatement

def INSERT_VALUES(table, data, cur, id):
    cols = ','.join(list(data.columns))
    query = 'INSERT INTO "{}_{}"({}) VALUES %s'.format(table, id, cols)
    tuples = [tuple(x) for x in data.to_numpy()]
    extras.execute_values(cur, query, tuples)

def iterations_from_reliable_table(session_id):
    query = f'SELECT MAX(iteration) FROM "reliable_{session_id}"'
    return query

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

def join_all_tables(iteration, session_id):
    query = f"""
    WITH temp_mahalanobis AS (
        SELECT id, ROUND(AVG(prediction)) AS Prediction_mahalanobis, AVG(score) AS SCORE_mahalanobis
        FROM "detectors_{session_id}"
        WHERE detector = 'mahalanobis'
        GROUP BY id
    ),
    temp_if AS (
        SELECT id, ROUND(AVG(prediction)) AS Prediction_if, AVG(score) AS SCORE_if
        FROM "detectors_{session_id}"
        WHERE detector = 'IF'
        GROUP BY id
    ),
    temp_knn AS (
        SELECT id, ROUND(AVG(prediction)) AS Prediction_KNN, AVG(score) AS SCORE_KNN
        FROM "detectors_{session_id}"
        WHERE detector = 'KNN'
        GROUP BY id
    ),
    temp_lof AS (
        SELECT id, ROUND(AVG(prediction)) AS Prediction_LOF, AVG(score) AS SCORE_LOF
        FROM "detectors_{session_id}"
        WHERE detector = 'LOF'
        GROUP BY id
    )
    SELECT *
    FROM "input_{session_id}"
    LEFT JOIN "tsne_{session_id}" ON "input_{session_id}".id = "tsne_{session_id}".id
    LEFT JOIN temp_lof ON "input_{session_id}".id = temp_lof.id
    LEFT JOIN temp_knn ON "input_{session_id}".id = temp_knn.id
    LEFT JOIN temp_if ON "input_{session_id}".id = temp_if.id
    LEFT JOIN temp_mahalanobis ON "input_{session_id}".id = temp_mahalanobis.id
    LEFT JOIN "predictions_{session_id}" ON "input_{session_id}".id = "predictions_{session_id}".id
    """

    for i in range(iteration):
        query += f"""
        FULL JOIN "reliable_{session_id}_{i}" ON "input_{session_id}".id = "reliable_{session_id}_{i}".id
        """

    return query

def CREATE_REALIABLE_TABLES(iteration, session_id):
    createTableStatement = ""
    for i in range(iteration):
        createTableStatement += f"""
            CREATE TABLE "reliable_{session_id}_{i}" AS (
            SELECT id, reliable AS reliable_{i}
            FROM "reliable_{session_id}"
            WHERE iteration = {i}
            );
        """
    return createTableStatement

def JOIN_RELIABLE_TABLES(iteration, session_id):
    join_reliable = ""  # join relibale labels
    for i in range(iteration):
        join_reliable = f'{join_reliable} FULL JOIN "reliable_{session_id}_{i}" using (id)' 
    return join_reliable

def DROP_REALIABLE_TABLES(iteration, session_id):
    dropTableStatement = ""
    for i in range(iteration):
        dropTableStatement += f'DROP TABLE IF EXISTS "reliable_{session_id}_{i}";\n'
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