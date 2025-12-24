# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FillSinkDialog
                                 A QGIS plugin
 FillSink plug-in
                             -------------------
        begin                : 2017-03-13
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

from qgis.core import QgsMapLayer, QgsProject
from qgis.PyQt.QtGui import QIntValidator
from qgis.PyQt.QtWidgets import QDialog, QLineEdit

from drainage.ui.Batch_Processor_dialog_base import Ui_WatershedDialogBase
from drainage.Util import util

_util = util()


class BatchProcessor(QDialog, Ui_WatershedDialogBase):
    def __init__(self, iface=None, parent=None):
        """Constructor."""
        super().__init__(parent=parent)
        self.setupUi(self)
        self.iface = iface

        self.__init_var_setting()
        self.__init_event_setting()
        self.__init_validator_setting()

    def __init_var_setting(self):
        """
        초기 세팅 구성
        """
        self.__setting_file()
        self.__set_combobox()

    def __setting_file(self):
        """
        파일 경로 변수 선언
        """
        self.LayerPath = ""
        self.Layername = ""
        self.fpnFilledDEM = ""
        self.fpnFlatArea = ""
        self.fpnFD = ""
        self.fpnFAC = ""
        self.fpnSlope = ""
        self.fpnStream = ""
        self.thresholdValueForStream = 0
        self.fpnCatchment = ""
        self.fpnStreamVector = ""

    def __set_combobox(self):
        """
        Setting combobox items
        """

        # Add only raster layers to the combo box
        # layer.type() => 0: Vector, 1: Raster
        layers: list[QgsMapLayer] = QgsProject.instance().mapLayers().values()
        _util.SetCommbox(layers, self.cmbLayer, "tif")

    def __init_event_setting(self):
        """
        이벤트 세팅 구성
        """
        # 콤보 박스 선택 시 텍스트 창에 기본 파일 이름 적용
        self.cmbLayer.currentIndexChanged.connect(self.__select_combobox_event)

        # OK버튼 눌렀을때 처리 부분
        self.btnOK.clicked.connect(self.__click_ok_button)

        # Cancle버튼 클릭 이벤트
        self.btnCancel.clicked.connect(self.close)

        # # 라디오 버튼 기본 설정
        self.chkStream.stateChanged.connect(self.checkbox_Stream)
        self.chkStream.setChecked(True)
        self.checkbox_Stream()

        # Stream chk와 label 연동
        self.lblStream.mouseReleaseEvent = self.setStreamChecked

    def __init_validator_setting(self):
        """
        Configure the validator for the text box.
        """
        only_int = QIntValidator()
        self.txtThresholdValueForStream.setValidator(only_int)

    def __select_combobox_event(self):
        index = self.cmbLayer.currentIndex()
        if index != 0:
            self.LayerPath = _util.GetcomboSelectedLayerPath(self.cmbLayer)
            self.Layername = _util.GetFilename(self.LayerPath)
            self.txtFilledDEM.setText(self.Layername + "_Filled")
            self.txtFD.setText(self.Layername + "_Fdr")
            self.txtFAC.setText(self.Layername + "_Fac")
            self.txtSlope.setText(self.Layername + "_Slope")
            self.txtStream.setText(self.Layername + "_Stream")
            self.txtStreamVector.setText(self.Layername + "_Stream_polyline")
            self.txtCatchment.setText(self.Layername + "_Catchment")

    def __asc_to_tiff(self, asc_path: str) -> str:
        """
        asc 파일을 tiff 파일로 변환
        """
        tiff_path = asc_path.replace(".asc", ".tif")
        _util.Convert_ASCii_To_TIFF(asc_path, tiff_path)
        return tiff_path

    def __get_extension(self, path: str) -> str:
        """
        파일 확장자 가져오기
        """
        return os.path.splitext(path)[1]

    @_util.error_decorator("Batch Processor")
    def __click_ok_button(self, is_checked: bool):
        # 레이어 경로에 한글이 있으면 오류로 처리
        if _util.CheckKorea(self.LayerPath):
            raise Exception("The file path contains Korean.")

        # only ASCII files and TIF file formats are supported.
        ext = self.__get_extension(self.LayerPath)
        if ext.lower() == ".asc":
            self.LayerPath = self.__asc_to_tiff(self.LayerPath)
        elif ext.lower() == ".tif":
            pass
        else:
            raise Exception("Only ASCII files and TIF file formats are supported.")

        # 비어있는 텍스트 박스 체크
        self.__error_empty_textbox(self.txtFilledDEM, "Sink filled DEM file name is required.")
        self.__error_empty_textbox(self.txtFD, "Flow direction file name is required.")
        self.__error_empty_textbox(self.txtFAC, "Flow accumulation file name is required.")
        self.__error_empty_textbox(self.txtSlope, "Slope file name is required.")
        self.__error_empty_textbox(self.txtStream, "Stream raster file name is required.")
        self.__error_empty_textbox(self.txtThresholdValueForStream, "Threshold value is required.")
        self.__error_empty_textbox(self.txtCatchment, "Catchment is required.")
        if self.chkStream.isChecked():
            self.__error_empty_textbox(
                self.txtStreamVector, "Stream polyline layer name is required."
            )

        # 파일 경로 변수에 셋팅
        self.__setting_value()

        # Fill sink 시작
        arg = _util.GetTaudemArg(
            self.LayerPath, self.fpnFilledDEM, _util.tauDEMCommand.SK, False, 0
        )
        _util.Execute(arg)

        # FD 시작
        arg = _util.GetTaudemArg(self.fpnFilledDEM, self.fpnFD, _util.tauDEMCommand.FD, False, 0)
        _util.Execute(arg)
        # FA 시작
        arg = _util.GetTaudemArg(self.fpnFD, self.fpnFAC, _util.tauDEMCommand.FA, False, 0)
        _util.Execute(arg)
        # Slope 시작
        arg = _util.GetTaudemArg(
            self.fpnFilledDEM, self.fpnSlope, _util.tauDEMCommand.SG, False, 0
        )
        _util.Execute(arg)
        # Stream 시작
        cell_value = self.txtThresholdValueForStream.text()
        arg = _util.GetTaudemArg(
            self.fpnFAC,
            self.fpnStream,
            _util.tauDEMCommand.ST,
            False,
            cell_value,
        )
        _util.Execute(arg)
        arg = self.__create_stream_vector()

        _util.Execute(arg)

        # tif 파일 asc 파일로 변환
        self.__convert_tiff_to_asc()

        # 임시 파일 삭제
        self.__delete_tempfile()

        # 메시지 박스 출력
        _util.MessageboxShowInfo("Batch processor", "The process is complete.")
        self.close()

    def __delete_tempfile(self):
        for i in range(0, 3):
            os.remove(self.outFiles[i])
        if self.chkStream.isChecked():
            pass
        else:
            os.remove(self.outFiles[3])

    # 파일 경로 변수에 셋팅
    def __setting_value(self):
        pathString =os.path.dirname(self.LayerPath) + "\\"
        self.fpnFilledDEM = pathString + self.txtFilledDEM.text()  + ".tif"
        self.fpnFD = pathString + self.txtFD.text() + ".tif"
        self.fpnFAC = pathString + self.txtFAC.text() + ".tif"
        self.fpnSlope = pathString + self.txtSlope.text() + ".tif"
        self.fpnStream = pathString + self.txtStream.text() + ".tif"
        self.fpnCatchment = pathString + self.txtCatchment.text() + ".tif"
        self.fpnStreamVector = pathString + self.txtStreamVector.text() + ".shp"
        self.thresholdValueForStream = pathString + self.txtThresholdValueForStream.text()

    def __create_stream_vector(self):
        self.outFiles = []
        self.outFiles.append(os.path.dirname(self.fpnFilledDEM) + "\\temp_1.tif")
        self.outFiles.append(os.path.dirname(self.fpnFilledDEM) + "\\temp_1.dat")
        self.outFiles.append(os.path.dirname(self.fpnFilledDEM) + "\\temp_2.dat")
        # outFiles3 = "C:\GRM\Sample\Gyeongpoho_DEM_Stream.shp"
        self.outFiles.append(self.fpnStreamVector)
        # outFiles4 = os.path.dirname(self.Fill) + "\\temp_2.tif"
        self.outFiles.append(self.fpnCatchment)
        args = ' -fel "{0}" -p "{1}" -ad8 "{2}" -src "{3}" -ord "{4}" -tree "{5}" -coord "{6}" -net "{7}" -w "{8}" '.format(
            self.fpnFilledDEM,
            self.fpnFD,
            self.fpnFAC,
            self.fpnStream,
            self.outFiles[0],
            self.outFiles[1],
            self.outFiles[2],
            self.outFiles[3],
            self.outFiles[4],
        )
        streamnet = '"C:\Program Files\TauDEM\TauDEM5Exe\StreamNet.exe" '

        return streamnet + args

    # 텍스트 박스에 파일 이름이 없는 경우 체크
    def __error_empty_textbox(
        self, txt: QLineEdit, err_msg: str = "A filename is required."
    ):
        if txt.text() == "":
            txt.setFocus()
            raise Exception(err_msg)

    def __convert_tiff_to_asc(self):
        _util.Convert_TIFF_To_ASCii(self.fpnFilledDEM)
        # _util.Convert_TIFF_To_ASCii(self.Flat)
        _util.Convert_TIFF_To_ASCii(self.fpnFD)
        _util.Convert_TIFF_To_ASCii(self.fpnFAC)
        _util.Convert_TIFF_To_ASCii(self.fpnSlope)
        _util.Convert_TIFF_To_ASCii(self.fpnStream)
        if self.chkStream.isChecked():
            _util.VectorLayer_AddLayer(self.fpnStreamVector)
        _util.Convert_TIFF_To_ASCii(self.fpnCatchment)

    def checkbox_Stream(self):
        if self.chkStream.isChecked():
            self.txtStreamVector.setEnabled(True)
        else:
            self.txtStreamVector.setEnabled(False)

    def setStreamChecked(self, event):
        self.chkStream.setChecked(not self.chkStream.isChecked())
