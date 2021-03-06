#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This software is licensed as described in the README.rst and LICENSE files, which you should have received as
# part of this distribution.

import datetime
import logging
import os
import sys
import subprocess
from sys import stdout
from logging import WARNING, INFO
from colorama import Fore, Back, Style


class Output():
    default_lvl = None
    logger = None
    path = None
    today = None
    cfg = None

    def __init__(self, config):
        self.cfg = config
        self.default_lvl = self.cfg.get('global', 'log_level')
        logging.basicConfig(format = '%(asctime)s :%(levelname)s: %(message)s',
                            filename = self.cfg.get('global', 'log_file'),
                            level = self.default_lvl)
        self.logger = logging.getLogger(__name__)
        # All exceptions will be logged without exit
        def log_except_hook(*exc_info):
            self.logger.critical('Unhandled exception!', exc_info=exc_info)
        sys.excepthook = log_except_hook

        self.path = self.getDir()

    def checkDate(self):
        today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        if self.today != today:
            self.path = None
            self.today = today

    def getDir(self):
        self.checkDate()
        if self.path is None:
            hddcko_path = self.cfg.get('global', 'storage_path')
            if self.cfg.getboolean('global', 'mountable_storage') and not os.path.ismount(hddcko_path):
                self.msg('%s is not mounted, try to mount' % hddcko_path, WARNING)
                subprocess.call(["mount", hddcko_path])
                if not os.path.ismount(hddcko_path):
                    self.msg('Couldnt mount %s' % hddcko_path, WARNING)
                    hddcko_path = '/tmp/lookOver'
                    if not os.path.exists(hddcko_path):
                        self.msg('Creating directory %s' % hddcko_path, INFO)
                        os.mkdir(hddcko_path)
                    hddcko_path = '/tmp'
                else:
                    self.msg('Yey %s has been mounted' % hddcko_path, INFO)

            self.path = hddcko_path + '/lookOver/' + self.today +'/'
            if not os.path.exists(self.path):
                self.msg('Creating directory %s' % self.path, INFO)
                os.mkdir(self.path)

        return self.path

    def log(self, msg, level):
        self.logger.log(level, msg)

    def prnt(self, msg, level):
        if stdout.isatty():
            # We are printing on screen with some color
            # TODO: Update this to work with written type from config
            if level == logging.CRITICAL:
                msg = Fore.RED + Style.BRIGHT + msg
            elif level == logging.ERROR:
                msg = Fore.RED + msg
            elif level == logging.WARNING:
                msg = Fore.YELLOW + msg
            elif level == logging.INFO:
                msg = Fore.GREEN + Style.BRIGHT + msg
            elif level == logging.DEBUG:
                msg = Fore.MAGENTA + msg
            print msg + Fore.RESET + Back.RESET + Style.RESET_ALL
        else:
            # Recet colors on terminal to default state
            print msg

    def msg(self, msg, level=None):
        if level is None:
            level = self.default_lvl
        if level >= self.default_lvl:
            self.prnt(msg, level)
        if self.log is not None:
            self.log(msg, level)
