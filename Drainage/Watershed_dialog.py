# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WatershedDialog
                                 A QGIS plugin
 Watershed
                             -------------------
        begin                : 2017-04-04
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Hermesys
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

from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtCore import QFileInfo
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QGroupBox, QMessageBox, QTextEdit

from drainage.ui.Watershed_dialog_base import Ui_WatershedDialogBase
from drainage.Util import util

_Prj_Back_Path = ""
_util = util()


class WatershedDialog(QDialog, Ui_WatershedDialogBase):
    def __init__(self, parent=None):
        super(WatershedDialog, self).__init__(parent)
        self.setupUi(self)
        self.__init_attr()
        self.__init_qt()

    def __init_attr(self):
        self.TifPath = ""
        self.Shape = ""

    def __init_qt(self):
        # LineEdit 컨트롤러 초기화
        self.txtOutput.clear()

        # 레이어목록 콤보 박스 리스트 넣기 이벤트
        layers = QgsProject.instance().mapLayers().values()

        # 전달인자 layer 목록, 콤보박스,layertype("tif" or "shp" or ""-->전체 목록)
        _util.SetCommbox(layers, self.cmbLayers, "tif")
        _util.SetCommbox(layers, self.cmbShape, "shp")

        # Event
        self.btnOpenDialog.clicked.connect(self.__select_output_file)
        self.btnOK.clicked.connect(self.__click_ok_button)
        self.btnCancel.clicked.connect(self.close)
        self.cmbLayers.currentIndexChanged.connect(self.__set_tif_path)
        self.cmbShape.currentIndexChanged.connect(self.__set_shape)

    # 저장 위치 출력 다이얼 로그
    def __select_output_file(self):
        self.txtOutput.clear()
        dir = os.path.dirname(self.TifPath)
        if self.TifPath != "" and os.path.isdir(dir):
            filename = QFileDialog.getSaveFileName(
                self, "select output file ", dir, "*.tif"
            )[0]
        else:
            filename = QFileDialog.getSaveFileName(
                self, "select output file ", os.getcwd(), "*.tif"
            )[0]
        self.txtOutput.setText(filename)

    def __set_tif_path(self, index: int) -> None:
        if index == 0:
            self.TifPath = ""
        else:
            self.TifPath = self.__get_path_by_layer(self.cmbLayers.currentText())

    def __set_shape(self, index: int) -> None:
        if index == 0:
            self.Shape = ""
        else:
            self.Shape = self.__get_path_by_layer(self.cmbShape.currentText())

    def __get_path_by_layer(self, layername: str) -> str:
        layer = QgsProject.instance().mapLayersByName(layername)[0]
        layer_path = layer.dataProvider().dataSourceUri()
        return layer_path.split("|")[0]

    # 레이어 목록 Qgis에 올리기
    def Addlayer_OutputFile(self, outputpath):
        if os.path.isfile(outputpath):
            fileName = outputpath
            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
            layer = QgsRasterLayer(fileName, baseName, "gdal")
            QgsProject.instance().addMapLayer(layer)

    @_util.error_decorator("Watershed")
    def __click_ok_button(self, is_checked: bool):
        # 콤보박스 레이어 선택 하지 않았을때
        raster_layer_index = self.cmbLayers.currentIndex()
        shape_layer_index = self.cmbShape.currentIndex()

        if raster_layer_index == 0:
            raise Exception("No raster layer selected.")
        if shape_layer_index == 0:
            raise Exception("No shape layer selected.")

        # 텍스트 박스에 결과 파일 경로가 없을때 오류 메시지 출력
        if self.txtOutput.text() == "":
            raise Exception("No output file path selected.")

        # True 면 한글 포함 하고 있음, False 면 한글 없음
        if _util.CheckKorea(self.txtOutput.text()):
            _util.MessageboxShowInfo(
                "Watershed", "\n The file path contains Korean. \n"
            )
            return

        # 선택된 레이어 경로 한글 체크
        if _util.CheckKorea(self.TifPath):
            _util.MessageboxShowInfo(
                "Watershed", "\n selected raster layer path contains Korean. \n"
            )
            return

        # 선택된 레이어 경로 한글 체크
        if _util.CheckKorea(self.Shape):
            _util.MessageboxShowInfo(
                "Watershed", "\n selected shape layer path contains Korean. \n"
            )
            return

        # True 이면 기존 파일 존재함
        if _util.CheckFile(self.txtOutput.text()):
            _util.MessageboxShowInfo(
                "Watershed", "\n A file with the same name already exists. \n"
            )
            return

        """
        Watershed   진행 하기 전에 raster 파일과 shape 파일의 좌표계 정보가 다르면 
        파일이 잘 생성 되지 않을수 있다는 메시지 출력     
        """

        # 레스터 레이어
        baseName = _util.GetFilename(self.TifPath)
        rlayer = QgsRasterLayer(self.TifPath, baseName)
        if rlayer.isValid():
            self.rcsr = self.layerCRS(rlayer)
        else:
            self.rcsr = ""
        # 벡터 레이어
        name = _util.GetFilename(self.Shape)
        vlayer = QgsVectorLayer(self.Shape, name, "ogr")
        if vlayer.isValid():
            self.scsr = self.layerCRS(vlayer)
        if self.rcsr != self.scsr:
            self.aboutApp()
            # _util.MessageboxShowInfo(" Caution!!", "If the coordinate system of the two layers are different, there may be a problem in the watershed processing. ")
        self.checkPrjFile(self.Shape)

        # 타우프로그램 실행 시킬 arg 문자열 받아 오기
        arg = _util.GetWatershed(self.TifPath, self.Shape, self.txtOutput.text())
        _util.Execute(arg)
        self.checkPrjFile_back()
        _util.Convert_TIFF_To_ASCii(self.txtOutput.text())
        _util.MessageboxShowInfo("Watershed", "processor complete")
        self.close()

    def layerCRS(self, layer):
        lyrCRS = layer.crs()
        if lyrCRS.isValid():
            return lyrCRS.toProj4()
        else:
            return ""

    def checkPrjFile(self, shapefile: str):
        global _Prj_Back_Path
        file_ex = os.path.splitext(shapefile)
        ext = file_ex[1]
        ext2 = _util.GetFilename(shapefile)
        ReplaceFile = shapefile.replace(ext, ".prj")

        backfile = ReplaceFile.replace(ext2, ext2 + "_back")
        _Prj_Back_Path = backfile
        if _util.CheckFile(ReplaceFile):
            os.rename(ReplaceFile, backfile)

    def checkPrjFile_back(self):
        if _util.CheckFile(_Prj_Back_Path):
            Reback_name_file = _Prj_Back_Path.replace("_back", "")
            os.rename(_Prj_Back_Path, Reback_name_file)

    # 정보창 띄움
    def aboutApp(self):
        website = "http://code.google.com/p/comictagger"
        email = "comictagger@gmail.com"
        Project = "test"
        msgBox = QMessageBox()
        msgBox.addButton("Continue", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        msgBox.setWindowTitle(self.tr("Caution!!"))
        msgBox.setTextFormat(QtCore.Qt.RichText)
        msgBox.setIconPixmap(QtGui.QPixmap(Project))
        msgBox.setText(
            "If the coordinate system of the two layers are different, there may be a problem in the watershed processing.<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><font color=white>"
            + "{0},{1}</font><br><br>".format(website, email + "comictagger@gma")
        )

        self.addGroupWidget(msgBox)
        ret = msgBox.exec_()
        if ret == QMessageBox.AcceptRole:
            pass
        else:
            #             self.post_grid_remove()
            self.rdo_selection()
            self.mapcanvas.refresh()
            self.scale_changed_mapcanvas()
            self.tool.scale_changed_disconnect()

    # 메시지 창에 그룹 박스와 그룹 박스안 텍스트 창넣기
    def addGroupWidget(self, parentItem):
        self.groupWidget = QGroupBox(parentItem)
        self.groupWidget.setTitle("FD CRS")
        self.groupWidget.setGeometry(QtCore.QRect(10, 50, 480, 130))  # 사이즈
        self.groupWidget.setObjectName("groupWidget")

        self.groupWidget1 = QGroupBox(parentItem)
        self.groupWidget1.setTitle("Point CRS")
        self.groupWidget1.setGeometry(QtCore.QRect(10, 190, 480, 130))  # 사이즈
        self.groupWidget1.setObjectName("groupWidget1")

        self.txtCSR_FD = QTextEdit(self.groupWidget)
        self.txtCSR_FD.setGeometry(10, 15, 460, 105)
        self.txtCSR_FD.setText(self.rcsr)

        self.txtCSR_Point = QTextEdit(self.groupWidget1)
        self.txtCSR_Point.setGeometry(10, 15, 460, 105)
        self.txtCSR_Point.setText(self.scsr)
