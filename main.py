#!/usr/bin/env python

"""
main.py

Reserves a room in a Berkeley library.
Making humans obsolete, one program at a time.

@author owenjow [at] berkeley.edu

Usage:
  main.py [-cfg CONFIG_PATH] [-c CHROMEDRIVER_PATH]
"""

import os
import re
import yaml
import time
import argparse
import calendar
from datetime import datetime
from threading import Timer

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from utils import from_military_time

P1_CONTINUE_ID = {
    'Moffitt': 'rm_tc_cont',
}
P1_SUBMIT_ID = {
    'Moffitt': 's-lc-rm-sub',
}

def reserve_room(library_info, booking_info, login_info, chromedriver):
    # Extract information
    library, url = library_info['name'], library_info['reserve_url']
    continue_id, submit_id = P1_CONTINUE_ID[library], P1_SUBMIT_ID[library]
    start_time, room = booking_info['start_time'], booking_info['room']
    green_button_pattern = r'id="([0-9]+)" onclick="return showBookingForm\(this.id,\'[a-zA-Z]+, Room %d\',\'%s ' \
                           % (room, start_time)
    calnet_id, passphrase = login_info['calnet_id'], login_info['passphrase']

    # WebDriver setup
    driver = webdriver.Chrome(chromedriver)

    def _do_calnet_login():
        """Login via the CalNet Authentication Service."""
        WebDriverWait(driver, 9).until(EC.title_contains('Central Authentication Service'))
        calnet_id_input = driver.find_element_by_id('username')
        calnet_id_input.send_keys(calnet_id)
        passphrase_input = driver.find_element_by_id('password')
        passphrase_input.send_keys(passphrase)
        sign_in_button = driver.find_element_by_name('submit')
        sign_in_button.click()

    def _finish_reserve_room():
        """Complete the room reservation.
        Wrapped in a function to facilitate midnight launch.
        """

        driver.get(url)
        actions = ActionChains(driver)

        # -----------------------------
        # First page (the provided URL)
        # -----------------------------

        WebDriverWait(driver, 9).until(EC.presence_of_element_located((By.ID, 's-lc-rm-tg-cont')))
        src = driver.page_source.encode('utf-8').strip()
        match = re.search(green_button_pattern, src)
        assert match is not None, 'source string -->\n%s\n\n---\nroom (%d) ' \
                                  'and/or time (%s) invalid' % (src, room, start_time)
        green_button_id = match.group(1)
        green_button = driver.find_element_by_id(green_button_id)
        actions.move_to_element(green_button).perform()  # make sure physical cursor is NOT inside the browser window
        WebDriverWait(driver, 9).until(EC.visibility_of_element_located((By.ID, green_button_id)))
        green_button.click()
        continue_button = WebDriverWait(driver, 9).until(EC.element_to_be_clickable((By.ID, continue_id)))
        continue_button.click()
        submit_button = WebDriverWait(driver, 9).until(EC.element_to_be_clickable((By.ID, submit_id)))
        submit_button.click()

        # --------------------------
        # Second page (CalNet login)
        # --------------------------

        if not booking_info.get('midnight_launch', False):
            _do_calnet_login()

        # ------------------------
        # Third page (Springshare)
        # ------------------------

        WebDriverWait(driver, 9).until(EC.title_is('Information Release'))
        accept_button = driver.find_element_by_name('_eventId_proceed')
        accept_button.click()

        # --------------------------
        # Fourth page (LibCal again)
        # --------------------------

        submit_button = WebDriverWait(driver, 9).until(EC.element_to_be_clickable((By.ID, submit_id)))
        submit_button.click()

        time.sleep(9)

    if booking_info.get('midnight_launch', False):
        # Log onto CalNet early
        driver.get('https://calcentral.berkeley.edu/dashboard')
        _do_calnet_login()

        # Wait until midnight to open the page (assumes that it is not YET midnight!)
        today = datetime.today()
        month_end = calendar.monthrange(today.year, today.month)[1]
        if today.day == month_end:
            tomorrow_month = today.month + 1 if today.month < 12 else 1
            tomorrow_day = 1
        else:
            tomorrow_month = today.month
            tomorrow_day = today.day + 1
        tomorrow = today.replace(month=tomorrow_month, day=tomorrow_day, hour=0, minute=0, second=0, microsecond=0)
        dt_sec = (tomorrow - today).seconds + 0.01

        print('Waiting until tomorrow to book the room (room %d at %s in %s)...' % (room, start_time, library))
        t = Timer(dt_sec, _finish_reserve_room)
        t.start()
    else:
        _finish_reserve_room()  # don't wait

def main(config, chromedriver):
    _config_path = config
    assert os.path.isfile(_config_path)
    config = yaml.load(open(_config_path, 'r'))
    library_info = config['library']
    booking_info = config['booking']
    login_info = config['credentials']
    print('[+] Loaded the config file at %s.' % _config_path)

    booking_info['start_time'] = from_military_time(booking_info['start_time'])
    reserve_room(library_info, booking_info, login_info, chromedriver=chromedriver)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-cfg', type=str, help='config path', default='config.yaml')
    parser.add_argument('--chromedriver', '-c', type=str, help='chromedriver path', default='chromedriver')
    args = parser.parse_args()

    main(args.config, args.chromedriver)
