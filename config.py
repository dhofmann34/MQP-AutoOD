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


def app_config(app, filename='configurations.ini'):
    # Read and store application and DB configurations
    app_configs = {}
    db_configs = {}

    parser = ConfigParser()
    parser.read(filename)
    if parser.has_section('application'):
        fields = parser.items('application')
        for field in fields:
            app_configs[field[0]] = field[1]
    else:
        raise Exception('Section application not found in the {0} file'.format(filename))

    if parser.has_section('postgresql'):
        db_params = parser.items('postgresql')
        for param in db_params:
            db_configs[param[0]] = param[1]
        app_configs['HOST'] = db_params['HOST']
    else:
        raise Exception('Section postgresql not found in the {0} file'.format(filename))

    # Set up add configs
    app.config['UPLOAD_FOLDER'] = app_configs["upload-folder"]
    app.config['DOWNLOAD_FOLDER'] = app_configs["download-folder"]
    app.config['DEBUG'] = app_configs["debug-mode"] == 'True'  # start debugging
    app.config['ALLOWED_EXTENSIONS'] = app_configs["allowed-extensions"].split(",")
    app.config['HOST'] = app_configs["host"]
    app.secret_key = "super secret key"

    return app, db_configs, app_configs["logging-path"]
