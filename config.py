from configparser import ConfigParser
import subprocess
import pkg_resources


def configure_packages():
    # List of required packages
    required_packages = [
        'Flask==2.3.3',
        'Flask_Navigation==0.2.0',
        'loguru==0.7.2',
        'numpy==1.25.2',
        'pandas==2.1.0',
        'psycopg2==2.9.7',
        'scikit_learn==1.3.0',
        'scipy==1.11.2',
        'Werkzeug==2.3.7'
    ]

    # Check and update packages
    for package in required_packages:
        package_name, package_version = package.split('==')

        # Check if the package is installed and get its version
        try:
            installed_version = pkg_resources.get_distribution(package_name).version
        except pkg_resources.DistributionNotFound:
            installed_version = None

        # If the package is not installed or the installed version is older, update it
        if installed_version is None or installed_version != package_version:
            print(f"Updating {package_name} to version {package_version}")
            subprocess.run(['pip', 'install', '--upgrade', package], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    print("All packages are up to date.")


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

    if parser.has_section('postgresql'):
        host_field = parser.items('postgresql')[0]
        app_configs[host_field[0]] = host_field[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    app.config['UPLOAD_FOLDER'] = app_configs["upload-folder"]
    app.config['DOWNLOAD_FOLDER'] = app_configs["download-folder"]
    app.config['DEBUG'] = app_configs["debug-mode"] == 'True'  # start debugging
    app.config['ALLOWED_EXTENSIONS'] = app_configs["allowed-extensions"].split(",")
    app.config['HOST'] = app_configs["host"]
    app.secret_key = "super secret key"
    return app, app_configs["logging-path"]

