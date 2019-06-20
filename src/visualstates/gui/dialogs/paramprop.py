'''
   Copyright (C) 1997-2019 JDERobot Developers Team

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Library General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, see <http://www.gnu.org/licenses/>.

   Authors : Baidyanath Kundu (kundubaidya99@gmail.com)

  '''
import sys
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, \
    QPushButton, QApplication, QHBoxLayout, QVBoxLayout, \
    QScrollArea, QComboBox, QGridLayout, QPlainTextEdit, \
    QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import *
from visualstates.core.parameter import Parameter, isParamName, isTypeEqualValue

class ParamPropDialog(QDialog):

    paramAdded = pyqtSignal(list)
    paramUpdated = pyqtSignal(list, int)

    def __init__(self, params=None, id=-1):
        super(QDialog, self).__init__()
        self.params = params
        self.id = id
        self.param = Parameter()
        if self.id != -1:
            self.param = self.params[self.id]
        self.setFixedSize(400, 360)
        if id == -1:
            self.setWindowTitle('Add Parameter')
        else:
            self.setWindowTitle('Edit Parameter')

        Layout = QVBoxLayout()
        self.setLayout(Layout)
        rowLayout = QHBoxLayout()
        nameLbl = QLabel('Name :')
        nameLbl.setFixedWidth(100)
        rowLayout.addWidget(nameLbl)
        self.nameEdit = QLineEdit(self.param.name)
        rowLayout.addWidget(self.nameEdit)
        Layout.addLayout(rowLayout)

        rowLayout = QHBoxLayout()
        typeLbl = QLabel('Type :')
        typeLbl.setFixedWidth(100)
        rowLayout.addWidget(typeLbl)
        self.typeCb = QComboBox()
        self.typeCb.addItems(['String', 'Character', 'Integer', 'Float', 'Boolean'])
        self.typeCb.setCurrentText(self.param.type)
        rowLayout.addWidget(self.typeCb)
        Layout.addLayout(rowLayout)

        rowLayout = QHBoxLayout()
        valueLbl = QLabel('Value :')
        valueLbl.setFixedWidth(100)
        rowLayout.addWidget(valueLbl)
        self.valueEdit = QLineEdit(self.param.value)
        rowLayout.addWidget(self.valueEdit)
        Layout.addLayout(rowLayout)

        rowLayout = QHBoxLayout()
        descLbl = QLabel('Description :')
        descLbl.setFixedWidth(100)
        descLbl.setAlignment(Qt.AlignTop)
        rowLayout.addWidget(descLbl)
        self.descEdit = QPlainTextEdit(self.param.desc)
        self.descEdit.setFixedHeight(200)
        rowLayout.addWidget(self.descEdit)
        Layout.addLayout(rowLayout)

        btnLayout = QHBoxLayout()
        btnLayout.setAlignment(Qt.AlignRight)
        saveBtn = QPushButton("Save")
        saveBtn.setFixedWidth(80)
        saveBtn.clicked.connect(self.saveClicked)
        btnLayout.addWidget(saveBtn)
        closeBtn = QPushButton("Close")
        closeBtn.setFixedWidth(80)
        closeBtn.clicked.connect(self.closeClicked)
        btnLayout.addWidget(closeBtn)
        Layout.addLayout(btnLayout)
        self.setLayout(Layout)

    def saveClicked(self):
        if not isTypeEqualValue(self.typeCb.currentText(), self.valueEdit.text().strip()):
            QMessageBox.warning(self, 'Error', 'Value is not same as type')
        elif not isParamName(self.nameEdit.text().strip()):
            QMessageBox.warning(self, 'Error', 'Name does not meet requirements of a parameter')
        else:
            for param in self.params:
                if self.id != -1 and param == self.params[self.id]:
                    continue
                if param.name == self.nameEdit.text():
                    QMessageBox.warning(self, 'Error', 'Name already in use')
                    return
            newParam = False
            if self.id == -1:
                newParam = True
            self.param.setName(self.nameEdit.text().strip())
            self.param.setType(self.typeCb.currentText())
            self.param.setValue(self.valueEdit.text().strip())
            self.param.setDesc(self.descEdit.toPlainText())
            if newParam:
                self.params.append(self.param)
                self.paramAdded.emit(self.params)
            else:
                self.paramUpdated.emit(self.params, self.id)
            self.close()

    def closeClicked(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = ParamPropDialog(params=[])
    dialog.exec_()