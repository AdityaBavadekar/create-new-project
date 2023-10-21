import os
from datetime import datetime
from selenium import webdriver
import time
import requests
import tkinter as tk
from tkinter import simpledialog
import art
import ctypes
import win32gui
import win32con
import win32console
import json

# USER CONSTANTS
try:
    USER_NAME = str(os.environ['GH_NAME'])
    USER_DISPLAY_NAME = str(os.environ['GH_DISPLAY_NAME'])
    USER_PASS = str(os.environ['GH_PASS'])[5:-5]
except KeyError as e:
    print('Error :', str(e))
    print("Cause : Required Envirnment Variables are not set. Please see README.md")
    exit(-1)

GITHUB = 'https://github.com/login'

# XPATHS
LOG_USERNAME = '/html/body/div[1]/div[3]/main/div/div[4]/form/input[2]'
LOG_PASSWORD = '/html/body/div[1]/div[3]/main/div/div[4]/form/div/input[1]'
LOG_SIGNIN = '/html/body/div[1]/div[3]/main/div/div[4]/form/div/input[13]'
TFA_SEND = '/html/body/div[1]/div[4]/main/div/div[2]/div[2]/form/button'
TFA_CODE_INPUT = '/html/body/div[1]/div[3]/main/div/div[5]/div[2]/form/input[2]'
TFA_VERIFY_BUTTON = '/html/body/div[1]/div[3]/main/div/div[5]/div[2]/form/button'
CREATE_NEW_REPO_BUTTON = '/html/body/div[1]/div[6]/div/div/aside/div/div/loading-context/div/div[1]/div/h2/a/span'
REPO_NAME_INPUT = '/html/body/div[1]/div[6]/main/react-app/div/form/div[4]/div[1]/div[1]/div[1]/fieldset/div/div[2]/span/input'
DESCRIPTION_INPUT = '/html/body/div[1]/div[6]/main/react-app/div/form/div[4]/div[1]/div[1]/div[3]/span/input'
CREATE_REPO_BUTTON = '/html/body/div[1]/div[6]/main/react-app/div/form/div[6]/button'
PUBLIC_REPO_RADIO = '/html/body/div[1]/div[6]/main/react-app/div/form/div[4]/div[1]/div[2]/div/div/div/fieldset/div/div[1]/div[1]'
PRIVATE_REPO_RADIO = '/html/body/div[1]/div[6]/main/react-app/div/form/div[4]/div[1]/div[2]/div/div/div/fieldset/div/div[2]/div[1]'

# Get the current directory of the script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_files():
    files = []

    json_file_path = os.path.join(CURRENT_DIR, 'files_data.json')
    with open(CURRENT_DIR+'/files_data.json', 'r') as f:
        files_data = json.load(f)
        files = files_data['FILES_DATA']

    # From files_data.json VARS_USED
    var_values = dict(
        timestamp=timestamp,
        year=year,
        user_name=USER_NAME,
        user_display_name=USER_DISPLAY_NAME,
        project_name=REPO_NAME,
        art_text=art.text2art(display_name, 'collosal'))

    for src_file in files:
        file_name = os.path.join(PATH, src_file['file'])
        with open(file_name, 'w') as f:
            values = dict()
            f.write(src_file['contents'].format(**var_values))


def log(msg: str, start='[*]'):
    if start != '':
        msg = f'{start} {msg}'
    print(msg)


def get_window_handle_for_title(title: str):
    window_matchs = []

    def enum_windows_proc(hwnd, lparam):
        window_title = win32gui.GetWindowText(hwnd)
        if window_title and window_title == title:
            window_matchs.append((hwnd, window_title))

    win32gui.EnumWindows(enum_windows_proc, 0)
    if len(window_matchs) != 0:
        return window_matchs[0][0]
    return None


def change_window_state(window_handle, state):
    state_mapping = {
        1: win32con.SW_HIDE,
        2: win32con.SW_SHOW,
        3: win32con.SW_MINIMIZE,
        4: win32con.SW_MAXIMIZE,
        5: win32con.SW_RESTORE
    }
    if window_handle and win32gui.IsWindow(window_handle):
        win32gui.ShowWindow(window_handle, state_mapping[state])
        try:
            if foreground:
                win32gui.SetForegroundWindow(window_handle)
        except:
            pass
        return True
    else:
        print("System does not recongnise this as a valid window.")
        return False


def hasNetwork():
    try:
        requests.get('https://google.com')
        return True
    except:
        return False


def create_github_repo():
    browser = webdriver.Chrome()
    try:
        browser.get(GITHUB)
        log('Browser Launched')
    except Exception as e:
        log('Errror occurred while Launching Browser:', str(e))
        exit(-1)

    current_browser_title = browser.title + ' - Google Chrome'
    log(f"Window has title '{current_browser_title}'")
    window = get_window_handle_for_title(current_browser_title)

    def find_elements_by_xpath(path):
        return browser.find_element("xpath", path)

    def hide_browser():
        return change_window_state(window, 1)

    def show_browser():
        return change_window_state(window, 2)

    def show_int_input_box(title: str, message: str):
        root = tk.Tk()
        root.withdraw()
        user_input = simpledialog.askinteger(title, message, parent=root)
        return user_input

    def enter_text(sxpath: str, text: str):
        find_elements_by_xpath(sxpath).send_keys(text)

    def click(sxpath: str):
        find_elements_by_xpath(sxpath).click()

    time.sleep(4)

    # Login Screen
    log('SCREEN : Login')
    enter_text(LOG_USERNAME, USER_NAME)
    enter_text(LOG_PASSWORD, USER_PASS)
    click(LOG_SIGNIN)

    time.sleep(1.8)

    # TFA Screen
    log('SCREEN : Confirm to Send Passcode')
    click(TFA_SEND)

    time.sleep(3.5)

    # TFA Enter OTP Screen
    def get_otp():
        log('', '+'*40)
        log('', '')
        log('Your GitHub account Two Factor Authentication enabled.')
        log('', '')
        log('-'*15 + ' [INPUT REQUIRED] ' + '-'*15, '')
        sms_code = str(
            input('>>>'*3 + ' Enter GitHub TFA OTP Sent on your mobile address :'))
        while not sms_code and len(sms_code) != 6:
            log("Invalid OTP. Please recheck and enter again.", '[!]')
            sms_code = str(
                input('>>>'*3 + ' Enter GitHub TFA OTP Sent on your mobile address :'))
        log('', '')
        return str(sms_code)

    log('SCREEN : Enter Passcode')
    if hide_browser():
        log("Enter the OTP Sent to your device. The Browser window will be shown back again.")
    sms_code = get_otp()

    log("Switching back to Browser window")
    show_browser()
    enter_text(TFA_CODE_INPUT, sms_code)

    time.sleep(7)

    # Home Screen
    log('SCREEN : Home')
    click(CREATE_NEW_REPO_BUTTON)

    time.sleep(4)

    # Create New Repo Screen
    log('SCREEN : Create New Repository GitHub')
    enter_text(REPO_NAME_INPUT, REPO_NAME)

    description_text = display_name
    enter_text(DESCRIPTION_INPUT, description_text)

    click(PRIVATE_REPO_RADIO)

    log('All Details are filled. Waiting for conformation...')

    option = ctypes.windll.user32.MessageBoxW(
        0, "All details are filled. Continue to create the Repository ?", "New Project Creation", 4)
    if option != 6:
        exit(0)

    log('Creating...')
    click(CREATE_REPO_BUTTON)

    time.sleep(4)
    return f"https://github.com/{USER_NAME}/{REPO_NAME}"


print(art.text2art('New Project Creation', 'small'))
log('*'*35+'\nNew Project Creation\n'+'*'*35, '')

# Take Project Name
display_name = str(input('Enter project dsiplay name : ')).strip()
assert (display_name != '')
REPO_NAME = str(input('Enter project name : ')).strip()
assert (REPO_NAME != '')

timestamp = datetime.now().strftime('%d-%m-%Y-%H-%M')
year = datetime.now().strftime('%Y')
REPO_NAME = REPO_NAME.replace(' ', '-')

if not hasNetwork():
    log('Not Connected! Connect to a network.')
    exit(-1)

REPO_URL = create_github_repo()
log(f"Repository successfully created at {REPO_URL}")

commands = [c.format(repo_url=REPO_URL, repo_name=REPO_NAME) for c in """
git init
git add .
git commit -m "Initial commit"
git branch -M master
git remote add origin {repo_url}
git push -u origin master
git status
code .
""".split('\n') if c.strip() != '']
default_dirs = []

PATH = os.path.join(os.getcwd(), REPO_NAME)
if os.path.exists(PATH):
    log('WARN : Directory with same name already exists! Will Overwrite.')
else:
    os.mkdir(PATH)

os.chdir(PATH)
PATH = os.getcwd()
if not PATH.endswith('/'):
    PATH += '/'

default_dirs = [os.path.join(PATH, dir_name) for dir_name in default_dirs]

log('Creating files...')
for dirname in default_dirs:
    os.mkdir(dirname)

create_files()
log('Created required files')
log("Creating an 'Initial Commit' :\n")
for c in commands:
    os.system(c)

log('\nDone.','')
