import time
import os
import json
from datetime import date
import glob

import imageio

FREQUENCY = 25
IMAGES_DIR = 'timelapse/'


def copy_photo(i):
    today_date = date.today().strftime('%Y_%m_%d')
    dir = os.path.join(IMAGES_DIR, today_date)
    try:
        os.stat(dir)
    except:
        os.mkdir(dir)
    os.system('cp /var/lib/motion/lastsnap.jpg %s' %
              os.path.join(dir, '%i.jpg' % i))


def save_photo():
    os.system('curl http://localhost:8080/0/action/snapshot')
    time.sleep(5)

def rename_files(dir):
    filepath_list = glob.glob(os.path.join(dir, '*.jpg'))
    filepath_list.sort(key=os.path.getmtime)
    pad = len(str(len(filepath_list)))
    for n, filepath in enumerate(filepath_list, 1):
        os.rename(
            filepath,
            os.path.join(dir, 'pic_{:>0{}}.jpg'.format(n, pad))
        )    

def make_timelapse(today_date):
    images = []
    dir = os.path.join(IMAGES_DIR, today_date)
    rename_files(dir)
    cmd = 'avconv -y -i ' + dir + '/pic_%4d.jpg -r 25 -vcodec libx264 -q:v 3 ' + '%s.mp4;' % today_date
    print(cmd)
    os.system(cmd)

def snap(i):
    save_photo()
    copy_photo(i)


if __name__ == '__main__':
    today_date = date.today().strftime('%Y_%m_%d')
    i = 0
    while True:
        if not date.today().strftime('%Y_%m_%d') == today_date:
            make_timelapse(today_date)
            today_date = date.today().strftime('%Y_%m_%d')
            i = 0
        else:
            snap(i)
        i += 1
        time.sleep(FREQUENCY)