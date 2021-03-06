#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
this module provides a class CommonSettings, which is inherited by the Settings
objects of admin and client applications
'''

import os
import re

import locale
locale.setlocale(locale.LC_ALL, '')

import gettext
gettext.install("openmolar")

from lib_openmolar.common.datatypes import *

from PyQt4 import QtCore

# IMPORTANT
SCHEMA_VERSIONS = ("0.2",)
#

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

# this can't be a "singleton" because we inherit from it
# classes which inherit from it should be though!
class CommonSettings(object):

    #: where the users settings and stylesheets reside
    LOCALFOLDER = os.path.join(os.environ.get("HOME", ""), ".openmolar2")

    #: root writable settings directory.
    ROOT_FOLDER = "/etc/openmolar/"

    #: the system dictionary
    DICT_LOCATION = "/usr/share/dict/words"

    #: an array of 16 columns, and 4 rows
    #: see :doc:`../../misc/tooth_notation`
    TOOTH_GRID = (
        ( 0,  0,  0, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,  0,  0,  0),
        ( 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16),
        (32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17),
        ( 0,  0,  0, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75,  0,  0,  0,)
        )

    #: a tuple of upper back teeth ids
    upper_back  = ( 1, 2, 3, 4, 5,12,13,14,15,16,65,66,73,74)

    #: a tuple of upper lower teeth ids
    lower_back  = (17,18,19,20,21,28,29,30,31,32,84,83,76,75)

    #: a tuple of upper front teeth ids
    upper_front = ( 6, 7, 8, 9,10,11,67,68,69,70,71,72)

    #: a tuple of lower front teeth ids
    lower_front = (22,23,24,25,26,27,82,81,80,79,78,77)

    #: a tuple of deciduous teeth ids
    DECIDUOUS = TOOTH_GRID[0] + TOOTH_GRID[3]

    #: a dictionary to convert from id to shortname
    #: example TOOTHGRID_SHORTNAMES[8] returns 'ur1'
    TOOTHGRID_SHORTNAMES = {
            8:'ur1', 7:'ur2',
            6:'ur3', 5:'ur4', 4:'ur5',
            3:'ur6', 2:'ur7', 1:'ur8',
            9:'ul1', 10:'ul2', 11:'ul3',
            12:'ul4', 13:'ul5', 14:'ul6',
            15:'ul7', 16:'ul8', 24:'ll1',
            23:'ll2', 22:'ll3', 21:'ll4',
            20:'ll5', 19:'ll6', 18:'ll7',
            17:'ll8', 25:'lr1', 26:'lr2',
            27:'lr3', 28:'lr4', 29:'lr5',
            30:'lr6', 31:'lr7', 32:'lr8',
            69:'ura', 68:'urb', 67:'urc',
            66:'urd', 65:'ure', 70:'ula',
            71:'ulb', 72:'ulc', 73:'uld',
            74:'ule', 79:'lla', 78:'llb',
            77:'llc', 76:'lld', 75:'lle',
            80:'lra', 81:'lrb', 82:'lrc',
            83:'lrd', 84:'lre'
            }

    #: a dictionary to convert from id to longname
    #: example TOOTHGRID_SHORTNAMES[8] returns 'upper right 1'
    TOOTHGRID_LONGNAMES =  {
            8:'upper right 1', 7:'upper right 2',
            6:'upper right 3', 5:'upper right 4', 4:'upper right 5',
            3:'upper right 6', 2:'upper right 7', 1:'upper right 8',
            9:'upper left 1', 10:'upper left 2', 11:'upper left 3',
            12:'upper left 4', 13:'upper left 5', 14:'upper left 6',
            15:'upper left 7', 16:'upper left 8', 24:'lower left 1',
            23:'lower left 2', 22:'lower left 3', 21:'lower left 4',
            20:'lower left 5', 19:'lower left 6', 18:'lower left 7',
            17:'lower left 8', 25:'lower right 1', 26:'lower right 2',
            27:'lower right 3', 28:'lower right 4', 29:'lower right 5',
            30:'lower right 6', 31:'lower right 7', 32:'lower right 8',
            69:'upper right a', 68:'upper right b', 67:'upper right c',
            66:'upper right d', 65:'upper right e', 70:'upper left a',
            71:'upper left b', 72:'upper left c', 73:'upper left d',
            74:'upper left e', 79:'lower left a', 78:'lower left b',
            77:'lower left c', 76:'lower left d', 75:'lower left e',
            80:'lower right a', 81:'lower right b', 82:'lower right c',
            83:'lower right d', 84:'lower right e'
            }

    #: put persistant local settings in here..
    #: they are pickled and stored in QtCore.QSettings for the application
    #: meaning these survive a log out!
    PERSISTANT_SETTINGS = {}

    _PLUGIN_DIRS = None
    ALLOW_NAKED_PLUGINS = False

    def __init__(self):

        #: a pointer to the instance of :doc:`OMTypes`
        self.OM_TYPES = OMTypes()

        #initiate some placeholders
        self._proc_codes = None
        self._pydate_format = None
        self._qdate_format = None
        self._rev_toothgrid_shortnames = {}

        if not os.path.exists(self.LOCALFOLDER):
            os.makedirs(self.LOCALFOLDER)

        self.init_css()

    def init_css(self):
        '''
        create css files if they don't exist
        '''
        default_loc = os.path.join(self.LOCALFOLDER, "proxy.css")

        resource = QtCore.QResource(":css/proxy.css")
        if resource.isCompressed():
            data = QtCore.qUncompress(resource.data())
        else:
            data = resource.data()

        default_loc = os.path.join(self.LOCALFOLDER, "proxy.css")

        try:
            f = open(default_loc, "r")
            css_data = f.read()
            f.close()
            if css_data == data:
                LOGGER.debug("%s is current"% default_loc)
                return
        except IOError:
            pass

        print "initiating a new css file - %s"% default_loc
        f = open(default_loc, "w")
        f.write(data)
        f.close()

    @property
    def REV_TOOTHGRID_SHORTNAMES(self):
        if self._rev_toothgrid_shortnames != None:
            self._rev_toothgrid_shortnames = {}
            for key in self.TOOTHGRID_SHORTNAMES:
                om_code = self.TOOTHGRID_SHORTNAMES[key]
                self._rev_toothgrid_shortnames[om_code] = key

        return self._rev_toothgrid_shortnames

    def convert_tooth_shortname(self, tooth_name):
        '''
        take a shortname (like "UL8") and get the om_number
        '''
        return self.REV_TOOTHGRID_SHORTNAMES.get(tooth_name.lower())

    @property
    def PY_DATE_FORMAT(self):
        '''
        the locale string formatting to return python dates to local
        short format  eg 9/12/1969
        '''
        if not self._pydate_format:
            try:
                self._pydate_format = re.sub("y", "Y",
                    locale.nl_langinfo(locale.D_FMT))
            except AttributeError: # will happen on windows where nl_langinfo
                self._pydate_format = r"%d/%m/%Y"

        return self._pydate_format

    @property
    def QDATE_FORMAT(self):
        '''
        string to format a QDATE into local format 3/09/2010
        ie. QtCore.Qt.SystemLocaleShortDate
        '''
        return QtCore.Qt.SystemLocaleShortDate

    @property
    def QDATE_MID_FORMAT(self):
        '''
        string to format a QDATE into format 3, September, 2010
        value is "d, MMMM, yyyy"
        '''
        return "d, MMMM, yyyy"

    @property
    def QDATE_LONG_FORMAT(self):
        '''
        string to format a QDATE into format Wednesday 24, November, 2010
        ie. QtCore.Qt.SystemLocaleLongDate
        '''
        return QtCore.Qt.SystemLocaleLongDate

    @property
    def all_teeth(self):
        return self.front_teeth + self.back_teeth

    @property
    def back_teeth(self):
        return self.lower_back + self.upper_back

    @property
    def front_teeth(self):
        return self.lower_front + self.upper_front

    @property
    def PROCEDURE_CODES(self):
        '''
        the list of openmolar procedure codes
        load only when required
        '''
        if self._proc_codes == None:
            self._proc_codes = ProcedureCodesInstance()
        return self._proc_codes

    @property
    def PROCEDURE_CATEGORIES(self):
        return self.PROCEDURE_CODES.CATEGORIES

    @property
    def PROXY_CSS(self):
        css_files = ("custom_proxy.css", "proxy.css")
        for css_file in css_files:
            fp = os.path.join(self.LOCALFOLDER, css_file)
            if os.path.isfile(fp):
                LOGGER.debug("using %s for proxy_css"% fp)
                return fp

        return ""

    @property
    def schema_versions(self):
        '''
        this is where I set the range of supported schema versions.
        '''
        LOGGER.debug("Polling settings for allowed schema versions")
        return SCHEMA_VERSIONS


    @property
    def USER_CONNECTIONS_AVAILABLE_FOLDER(self):
        folder = os.path.join(self.LOCALFOLDER, "connections-available")
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return folder

    @property
    def PLUGIN_DIRS(self):
        '''
        where plugins can be stored.
        '''
        if self._PLUGIN_DIRS is None:
            folder = os.path.join(self.LOCALFOLDER, "plugins")
            if not os.path.isdir(folder):
                os.makedirs(folder)

            self._PLUGIN_DIRS = ["/usr/share/openmolar/plugins", folder]
            for folder in self._PLUGIN_DIRS:
                if not os.path.isdir(folder):
                    self._PLUGIN_DIRS.remove(folder)

        return self._PLUGIN_DIRS

if __name__ == "__main__":
    import logging
    logging.basicConfig()
    LOGGER = logging.getLogger("test")

    C_SETTINGS = CommonSettings()
    LOGGER.debug(C_SETTINGS)

    LOGGER.debug(C_SETTINGS.OM_TYPES)
    LOGGER.debug(C_SETTINGS.PY_DATE_FORMAT)
    LOGGER.debug(C_SETTINGS.QDATE_FORMAT)

    converts = []
    for tooth in ("UR8", "UL1", "urd", "LL8"):
        converts.append(C_SETTINGS.convert_tooth_shortname(tooth))
    LOGGER.debug("%s should read [1,9,66,17]"% converts)

    print C_SETTINGS.PROCEDURE_CODES
