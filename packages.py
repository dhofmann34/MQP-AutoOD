import subprocess
import pkg_resources

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
        subprocess.run(['pip', 'install', '--upgrade', package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("All packages are up to date.")