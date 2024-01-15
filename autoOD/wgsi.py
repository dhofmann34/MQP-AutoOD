"""'Run this code to start the server. Imports necessary packages if not using venv.'"""
from autoOD import create_app
import config

app = create_app("configuration.ini")

if __name__ == '__main__':
    config.configure_packages()
    app.run(host=app.config['HOST'], port=8080)  # 5000 for VM, 8080 for local machine
