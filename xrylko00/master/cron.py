import timer
import sys
import os

crontab='crontab'

def log(msg):
    sys.stderr.write(str(msg) + "\n")

def cron():
    """
    Open `crontab` and run line per line 
        (ignore empty lines and lines with leading #).
    """
    while True:
        file = open(crontab, 'r')
        scripts = [x.strip() for x in file]
        file.close()
        for x in scripts:
            x = x.strip()
            if not x.startswith('#') and x:
                #log('running {%s}' % x)
                #retval = subprocess.call(shlex.split(x), shell=True)
                retval = os.system(x)
                if retval:
                    log('return value = {%s} for line {%s}' % (retval, x))
                    log('*'*80)
        print 'going to sleep to tomorrow'
        timer.sleep_to_tomorrow()

if __name__ == '__main__':
    sys.exit(cron())
