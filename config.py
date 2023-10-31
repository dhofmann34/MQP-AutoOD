from configparser import ConfigParser

def db_config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def app_config(app, filename='configurations.ini', section='application'):
    parser = ConfigParser()
    parser.read(filename)
    app_configs = {}
    if parser.has_section(section):
        fields = parser.items(section)
        for field in fields:
            app_configs[field[0]] = field[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    app.config['UPLOAD_FOLDER'] = app_configs["upload-folder"]
    app.config['DOWNLOAD_FOLDER'] = app_configs["download-folder"]
    app.config['DEBUG'] = app_configs["debug-mode"] == 'True'  # start debugging
    app.config['ALLOWED_EXTENSIONS'] = app_configs["allowed-extensions"].split(",")
    app.secret_key = "super secret key"
    return app, app_configs["logging-path"]

