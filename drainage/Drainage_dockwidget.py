# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DrainageDockWidget
                                 A QGIS plugin
 Drainage
                             -------------------
        begin                : 2017-04-14
        git sha              : $Format:%H$
        copyright            : (C) 2017 by HermeSys
        email                : shpark@hermesys.co.kr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.gui import QgisInterface
from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtCore import pyqtSignal

from drainage.Batch_Processor_dialog import BatchProcessor
from drainage.ui.Drainage_dockwidget_base import Ui_DrainageDockWidgetBase

# import Qtree
from drainage.Util import util
from drainage.Watershed_dialog import WatershedDialog

# 아이콘 경로들 임 추후에 변경 할것임
path = os.path.dirname(os.path.realpath(__file__))
Drainage_icon = path + "\image\internet.png"
Cube = path + "\image\cube.png"
_util = util()


class DrainageDockWidget(QtWidgets.QDockWidget, Ui_DrainageDockWidgetBase):
    closingPlugin = pyqtSignal()

    def __init__(self, iface: QgisInterface, parent: QtWidgets.QWidget = None) -> None:
        """Constructor."""
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        # 트리 위젯에 메뉴 항목을 넣는 부분임
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Drainage")
        # 배경 색상 회색
        self.treeWidget.setItemsExpandable(True)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setItemsExpandable(True)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderLabels([""])

        # Qtree 박스에 헤더 부분 제거
        self.treeWidget.setHeaderHidden(True)
        item10 = QtWidgets.QTreeWidgetItem(self.treeWidget, ["Drainage"])

        item16 = QtWidgets.QTreeWidgetItem(item10, ["Batch Processor"])
        icon = QtGui.QIcon(Cube)
        item16.setIcon(0, icon)
        item17 = QtWidgets.QTreeWidgetItem(
            item10, ["Create OutletPoint Layer and Draw OutletPoint"]
        )
        icon = QtGui.QIcon(Cube)
        item17.setIcon(0, icon)
        item18 = QtWidgets.QTreeWidgetItem(item10, ["Watershed"])
        icon = QtGui.QIcon(Cube)
        item18.setIcon(0, icon)
        self.treeWidget.expandAll()

        self.mainLayout = QtWidgets.QGridLayout(self)
        self.mainLayout.addWidget(self.treeWidget)
        # 더블 클릭 했을대 메뉴 명칭 확인
        self.treeWidget.itemDoubleClicked.connect(self.onDoubleClick)

    def onDoubleClick(self, item: QtWidgets.QTreeWidgetItem):
        SelectItme = item.text(0)
        if SelectItme == "Batch Processor":
            results_dialog = BatchProcessor(iface=self.iface, parent=self)
            results_dialog.exec_()
        elif SelectItme == "Create OutletPoint Layer and Draw OutletPoint":
            _util.MessageboxShowInfo(
                "info",
                "The base layer and coordinate information must be created identically.",
            )
            self.iface.actionNewVectorLayer().trigger()
            # ADD 상태
            self.iface.actionAddFeature().trigger()
        elif SelectItme == "Watershed":
            results_dialog = WatershedDialog()
            results_dialog.exec_()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
