import datetime

import pxsol


def debugln(*args):
    if pxsol.config.current.log:
        println(*args)


def println(*args):
    pre = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(pre, *args)
