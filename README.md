# webdriver_auto_update
A program to check existing local chromedriver version and automatically downloads the latest available version online.

一個檢查本地端chromedriver是否符合Chrome 版本的程式，如不符合目前運行Chrome 版本，將會自動更新chromedriver

# Program Functionality
- Checks local chromedriver driver version on your computer and compares it with the latest version available online.
- The latest online version/release will be downloaded if it does not match your local version.
- If no local chromedriver executable file is found in the specified folder path, it will be downloaded automatically to that particular folder.

## Pre-requisites:
1. Download Google Chrome
2. pip install selenium
3. pip install pypiwin32

## Installation
- Make sure you have Python installed in your system.
- Download webdriver_auto_update.py from Github.
- Move webdriver_auto_update.py to Project Directory.
```
https://github.com/husan42/webdriver_auto_update/blob/main/webdriver_auto_update.py
```

## Import check_driver from webdriver_auto_update.py.
Example
```
from webdriver_auto_update import check_driver
```

## check_driver
- Use check_driver fuction to check Chrome Version.
- If local chromedriver version is not support Chrome Version,will auto download chromedriver.
## Example
```
## Make sure to pass in the folder used for storing and downloading chromedriver executable
check_driver('chromedriver/directory')
check_driver("./Model")
```


Incompatible Version
- Auto download Compatible version chromedriver.
```
>>> check_driver('./Model')
Chrome Version : 111.0.5563.111
Local chromedriver version: 108.0.5359.71
Latest online chromedriver version: 111.0.5563.64
Attempting to download latest available driver ......
https://chromedriver.storage.googleapis.com/111.0.5563.64/chromedriver_win32.zip
100% [..........................................................................] 7117143 / 7117143
Successfully downloaded chromedriver version 111.0.5563.64 to:Model
>>>
```

Compatible Version
- Pass and return True.
```
>>> check_driver('./Model')
Chrome Version : 111.0.5563.111
Local chromedriver version: 111.0.5563.64
Latest online chromedriver version: 111.0.5563.64
True
>>>
```

if error
```
ModuleNotFoundError: No module named 'win32com'
```

pip install pypiwin32
```
PS Microsoft.PowerShell.Core\FileSystem::\> pip install pypiwin32
Defaulting to user installation because normal site-packages is not writeable
Collecting pypiwin32
  Downloading pypiwin32-223-py3-none-any.whl (1.7 kB)
Collecting pywin32>=223
  Downloading pywin32-306-cp310-cp310-win_amd64.whl (9.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 9.2/9.2 MB 13.7 MB/s eta 0:00:00
Installing collected packages: pywin32, pypiwin32
Successfully installed pypiwin32-223 pywin32-306

[notice] A new release of pip is available: 23.0 -> 23.0.1
[notice] To update, run: python.exe -m pip install --upgrade pip
PS Microsoft.PowerShell.Core\FileSystem::\>
```


## Note
- The objective of this program is to reduce redundancy of searching and downloading the updated version of chrome driver to the OpenSource community.
- Intended to be used in Selenium projects, browser testing or web automation.
