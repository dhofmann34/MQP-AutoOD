"""'Run this code to start the server. Imports necessary packages if not using venv.'"""
from application import create_app, config

config.configure_packages()
app = create_app("application/configurations.ini")

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=8081)  # 5000 for VM, 8080 for local machine
