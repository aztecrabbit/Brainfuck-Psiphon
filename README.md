# Brainfuck Tunnel Psiphon Version

Brainfuck Tunnel Psiphon Version


Requirements
------------

**CPU Architectures**

    linux-x86_64
    linux-armv7l
    linux-armv8l
    linux-aarch64


**Linux**

    Git
    Iptables
    Redsocks
    Python 3


**Android (Termux)**

    Git
    Python 3


Parameters
----------

    $ python3 app.py -h
    usage: app.py [-h] [-v] [-t] [-c CORE] [-r RESET] [-f FRONTEND_DOMAINS]
                  [-w WHITELIST_REQUESTS]

    optional arguments:
      -h, --help             show this help message and exit
      -v                     increase output verbosity
      -t                     enable multi tunnel
      -c CORE                how many core running (min 1, max 16)
      -r RESET               reset exported files (all, config, data, database)
      -f FRONTEND_DOMAINS    frontend domains, example: akamai.net,akamai.net:443
      -w WHITELIST_REQUESTS  whitelist requests, example: akamai.net,akamai.net:443
    $


Usage
-----

**Linux (debian based)**

    $ sudo apt update && sudo apt install git redsocks python3 python3-pip
    $ python3 -m pip install pysocks

    $ git clone https://github.com/AztecRabbit/Brainfuck-Psiphon brainfuck-psiphon
    $ cd brainfuck-psiphon

    $ sudo -s
    # python3 app.py


**Android (Termux)**

    $ pkg install git python
    $ python -m pip install pysocks
    
    $ git clone https://github.com/AztecRabbit/Brainfuck-Psiphon brainfuck-psiphon
    $ cd brainfuck-psiphon

    $ python app.py


Updating
--------

    $ cd brainfuck-psiphon
    $ git pull
    $ python3 app.py -r all
    $ python3 app.py


Note
----

    linux-x86_64: multi tunnel enabled by default


Contact
-------

Facebook Group : [Internet Freedom]


[Internet Freedom]: https://www.facebook.com/groups/171888786834544/
