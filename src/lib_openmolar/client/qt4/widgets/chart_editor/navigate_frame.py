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

from PyQt4 import QtCore, QtGui

class NavigateFrame(QtGui.QWidget):
    '''
    provides buttons for common static chart editing by mouse
    '''

    nav_signal = QtCore.pyqtSignal(object)
    '''
    this is a signal emitted when user clicks on of the buttons
    argument will be ("next", "prev" or "stay")
    '''

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        back_icon = QtGui.QIcon(':icons/agt_back.png')
        next_icon = QtGui.QIcon(':icons/agt_forward.png')

        self.prev_button = QtGui.QPushButton(back_icon, "")
        self.prev_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.prev_button.setToolTip(_(u"previous tooth"))

        self.add_button = QtGui.QPushButton("&&")
        self.add_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.add_button.setToolTip(_(u"commit & stay on this tooth"))

        self.next_button = QtGui.QPushButton(next_icon, "")
        self.next_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.next_button.setToolTip(_(u"next tooth"))

        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.setSpacing(2)
        layout.addWidget(self.prev_button,0,0)
        layout.addWidget(self.add_button,0,1)
        layout.addWidget(self.next_button,0,2)

        self.prev_button.clicked.connect(self.emit_prev)
        self.add_button.clicked.connect(self.emit_add)
        self.next_button.clicked.connect(self.emit_next)

    def sizeHint(self):
        return QtCore.QSize(200,30)

    def emit_next(self):
        self.nav_signal.emit("next")

    def emit_add(self):
        self.nav_signal.emit("stay")

    def emit_prev(self):
        self.nav_signal.emit("prev")

if __name__ == "__main__":

    from lib_openmolar import client

    def sig_catcher(*args):
        print args

    app = QtGui.QApplication([])
    obj = NavigateFrame()

    obj.nav_signal.connect(sig_catcher)

    obj.show()
    app.exec_()
