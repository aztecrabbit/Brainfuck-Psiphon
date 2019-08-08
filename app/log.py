import sys
import datetime
from .important import *

def colors(value):
    patterns = {
        'R1' : '\033[31;1m', 'G1' : '\033[32;1m',
        'Y1' : '\033[33;1m', 'P1' : '\033[35;1m',
        'CC' : '\033[0m'
    }

    for code in patterns:
        value = value.replace('[{}]'.format(code), patterns[code])

    return value

def log(value, status='INFO', color='[G1]'):
    value = colors('{color}[{time}] [P1]:: {color}{status} [P1]:: {color}{value}[CC]'.format(
        time=datetime.datetime.now().strftime('%H:%M:%S'), value=value, status=status, color=color
    ))

    with lock: print(value)

def log_replace(value, status='INFO', color='[G1]'):
    value = colors('{}{} ({})        \r'.format(color, status, value))
    with lock:
        sys.stdout.write(value)
        sys.stdout.flush()
