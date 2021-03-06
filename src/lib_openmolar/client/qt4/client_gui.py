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

import logging
import os
import pickle
import sys
from PyQt4 import QtGui, QtCore

from lib_openmolar.client.connect import ClientConnection

from lib_openmolar.common.qt4.widgets import (
    SignallingApplication,
    Preference)

from lib_openmolar.common.qt4.dialogs import PreferencesDialog

from lib_openmolar.common.qt4.postgres.postgres_mainwindow import \
    PostgresMainWindow

from lib_openmolar.client.qt4.widgets import StatusBarWidget

from lib_openmolar.client.qt4.client_session_widget import ClientSessionWidget
from lib_openmolar.client.qt4.patient_records import PatientInterface
from lib_openmolar.client.qt4.diary import DiaryInterface

##TODO for windows version... this will need to be tweaked.
settings_dir = os.path.join(
    os.getenv("HOME"), ".openmolar2", "client", "connections")
if not os.path.isdir(settings_dir):
    os.makedirs(settings_dir)

CONNECTION_CONFDIRS = [settings_dir, "/etc/openmolar/client/connections"]

class ClientMainWindow(PostgresMainWindow):

    _stacked_widget = None

    #:customise the base class
    CONN_CLASS = ClientConnection

    ALLOW_MULTIPLE_SESSIONS = False

    def __init__(self, parent=None):
        PostgresMainWindow.__init__(self, parent)

        self.setWindowIcon(QtGui.QIcon(":icons/openmolar.png"))
        self.setWindowTitle("OpenMolar Client (%s)"% _("OFFLINE"))
        self.setMinimumSize(700,400)

        self.system_font = self.font()
        self.loadSettings()

        icon = QtGui.QIcon(':icons/database.png')
        self.action_patient = QtGui.QAction(icon, _("Patient Database"), self)

        icon = QtGui.QIcon.fromTheme("x-office-calendar",
            QtGui.QIcon(':icons/vcalendar.png'))
        self.action_diary = QtGui.QAction(icon, _("Diary"), self)

        insertpoint = self.action_help
        self.main_toolbar.insertAction(insertpoint, self.action_patient)
        self.main_toolbar.insertAction(insertpoint, self.action_diary)

        #: the :doc:`PatientInterface`
        self.patient_interface = PatientInterface(self)
        #: the :doc:`DiaryInterface`
        self.diary_interface = DiaryInterface(self)

        self.central_widget.add(self.patient_interface, "")
        self.central_widget.add(self.diary_interface, "")

        #:
        self.status_widget = StatusBarWidget()
        self.statusbar.addPermanentWidget(self.status_widget)

        self.connect_signals()

        QtCore.QTimer.singleShot(100, self.new_pg_session)

        SETTINGS.main_ui = self
        SETTINGS.load_plugins("client")

    @property
    def central_widget(self):
        if self._central_widget is None:
            self._central_widget = ClientSessionWidget()
        return self._central_widget

    def add_session(self, session):
        '''
        Overwrite the method of PostgresMainWindow
        Client is a single session widget.
        '''
        self.session_widgets = [self.central_widget]
        self.central_widget.set_session(session)
        self.diary_interface.refresh()

    @property
    def is_dirty(self):
        return self.patient_interface.is_dirty

    def set_users(self):
        self.status_widget.set_users()

    def user1_changed(self, user):
        SETTINGS.set_user1(user)

    def user2_changed(self, user):
        SETTINGS.set_user2(user)

    def end_pg_sessions(self, shutting_down=False):
        '''
        overwrite baseclass function
        '''
        PostgresMainWindow.end_pg_sessions(self)
        SETTINGS.psql_conn = None

    def connect_signals(self):
        self.action_patient.triggered.connect(self.page_changer)
        self.action_diary.triggered.connect(self.page_changer)

        self.connect(self.patient_interface, QtCore.SIGNAL("Advise"),
            self.advise)

        self.connect(self.patient_interface, QtCore.SIGNAL("Patient Loaded"),
            self._patient_loaded)

        self.connect(self.patient_interface, QtCore.SIGNAL("Show Fee Widget"),
            self.add_dock_widget)

        self.connect(self.diary_interface, QtCore.SIGNAL("Advise"),
            self.advise)

        self.connect(self.status_widget, QtCore.SIGNAL("mode changed"),
            self.patient_interface.apply_mode)

        self.connect(self.status_widget, QtCore.SIGNAL("user1 changed"),
            self.user1_changed)

        self.connect(self.status_widget, QtCore.SIGNAL("user2 changed"),
            self.user2_changed)

    def closeEvent(self, event=None):
        '''
        re-implement the close event of QtGui.QMainWindow, and check the user
        really meant to do this.
        '''
        ##TODO fix this.
        if self.is_dirty:
            self.advise("you have unsaved changes")

        if (QtGui.QMessageBox.question(self, _("Confirm"),
        _("Quit Application?"),
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No):
            event.ignore()
        else:
            self.saveSettings()
            self.end_pg_sessions(shutting_down=True)

    def page_changer(self):
        sender = self.sender()
        if sender == self.action_patient:
            i = 0
        elif sender == self.action_diary:
            i = 1
        self.central_widget.setCurrentIndex(i)

    def _patient_loaded(self, patient):
        '''
        updates the taskbar
        '''
        if patient:
            message = u"%s <b>%s</b>"% (_("editing"), patient.full_name)
        else:
            message = _("No Patient Loaded")
        self.status_label.setText(message)

    def preferences_dialog(self):
        if self._preferences_dialog is None:
            dl = self._preferences_dialog = \
                PostgresMainWindow.preferences_dialog(self)

        return self._preferences_dialog

    def show_about(self):
        '''
        raise a dialog showing version info etc.
        '''
        ABOUT_TEXT = "<pre>%s\n%s</pre><p>%s<br />%s</p>"% (
            _("Version"), SETTINGS.VERSION,
            "<a href='http://www.openmolar.com'>www.openmolar.com</a>",
            'Neil Wallace - rowinggolfer@googlemail.com')
        self.advise(ABOUT_TEXT, 1)

    def show_help(self):
        '''
        todo - this is the same as show_about
        '''
        self.show_about()

    def add_dock_widget(self, dw):
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dw)

def main():
    '''
    main entry point for lib_openmolar.client
    '''
    if "-v" in sys.argv:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)

    app = SignallingApplication("openmolar-client")
    ui = ClientMainWindow()
    ui.show()
    app.exec_()
    app = None

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    sys.exit(main())
