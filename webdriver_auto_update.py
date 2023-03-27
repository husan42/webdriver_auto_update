import os,re
import requests
import subprocess
import wget
import zipfile
import sys
from win32com.client import Dispatch


def download_latest_version(version_number, driver_directory):
    """Download latest version of chromedriver to a specified directory.
    :param driver_directory: Directory to save and download chromedriver files into.
    :type driver_directory: str
    :param version_number: Latest online chromedriver release from chromedriver.storage.googleapis.com.
    :type version_number: str
    :return: None
    """ 
    print("Attempting to download latest available driver ......")
    download_url = "https://chromedriver.storage.googleapis.com/" + version_number + "/chromedriver_" + obtain_os() + ".zip"
    print(download_url)
    download_tmp="chromedriver_tmp"
    # Download driver as a zip file to specified folder
    latest_driver_zip = wget.download(download_url, out=download_tmp)
    # Read zip file
    with zipfile.ZipFile(latest_driver_zip, 'r') as downloaded_zip:
        # Extract contents from downloaded zip file to specified folder path
        downloaded_zip.extractall(path=".")
        print(f"\nSuccessfully downloaded chromedriver version {version_number} to:{driver_directory}")
    # Delete the zip file downloaded
    os.remove(latest_driver_zip)
    return


def check_driver(driver_directory):
    """Check local chromedriver version and compare it with latest available version online.
    :param driver_directory: Directory to store chromedriver executable. Required to add driver_directory to path before using.
    :type driver_directory: str
    :return: True if chromedriver executable is already in driver_directory, else it is automatically downloaded.
    """
    running_chrome_version = get_running_chrome_version()
    online_driver_version = get_specify_release(running_chrome_version)
    #online_driver_version = get_latest_chromedriver_release()
    try:
        # Executes cmd line entry to check for existing web-driver version locally
        old_dir=os.getcwd()
        os.chdir(driver_directory)
        cmd_run = subprocess.run("chromedriver --version",
                                 capture_output=True,
                                 text=True)     
    except FileNotFoundError:
        os.chdir("..")
        # Handling case if chromedriver not found in path
        print("No chromedriver executable found in specified path\n")
        download_latest_version(online_driver_version, driver_directory)
    else:
        # Extract local driver version number as string from terminal output
        local_driver_version = cmd_run.stdout.split()[1]
        print(f"Local chromedriver version: {local_driver_version}")
        print(f"Latest online chromedriver version: {online_driver_version}")
        if local_driver_version == online_driver_version:
            os.chdir(old_dir)
            return True
        else:
            download_latest_version(online_driver_version, driver_directory)
            os.chdir(old_dir)


def get_latest_chromedriver_release():
    """ Check for latest chromedriver release version online"""
    latest_release_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
    response = requests.get(latest_release_url)
    online_driver_version = response.text
    return online_driver_version

def get_version_via_com(filename):
    parser = Dispatch("Scripting.FileSystemObject")
    try:
        version = parser.GetFileVersion(filename)
    except Exception:
        return None
    return version
    
def get_specify_release(version):
    specify_release_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version}"
    response = requests.get(specify_release_url)
    specify_driver_version = response.text
    return specify_driver_version

def get_running_chrome_version():
    paths = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
    version = list(filter(None, [get_version_via_com(p) for p in paths]))[0]
    print(f"Chrome Version : {version}")
    version = re.findall(r"\d+.\d+.\d+",version)[0]
    return version

            
def obtain_os():
    """Obtains operating system based on chromedriver supported by from https://chromedriver.chromium.org/
    :return: str"""
    if sys.platform.startswith('win32'):
        os_name='win32'
    elif sys.platform.startswith('linux'):
        os_name='linux64'
    elif sys.platform.startswith('darwin'):
        os_name='mac64'
    return os_name
