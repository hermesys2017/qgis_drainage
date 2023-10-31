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
from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5.QtCore import QFileInfo, QObject
from qgis.core import QgsProject, QgsRasterLayer
import os
from PyQt5 import QtGui, uic
from .Util import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Batch_Processor_dialog_base.ui'))

_util = util()
class BatchProcessor(QDialog, FORM_CLASS):
    #레이어 목록 콤보 박스 셋팅
    def SetCombobox(self):
        layers = QgsProject.instance().mapLayers().values()
        _util.SetCommbox(layers, self.cmbLayer, "tif")

    #콤보 박스 선택시 이벤트 처리
    def SelectCombobox_event(self):
        index = self.cmbLayer.currentIndex()
        if index >0:
            self.LayerPath=_util.GetcomboSelectedLayerPath(self.cmbLayer)
            self.Layername=_util.GetFilename(self.LayerPath)
            self.txtFill.setText(self.Layername + "_Hydro")
            # self.txtFlat.setText(self.Layername + "_Flat")
            self.txtFD.setText(self.Layername + "_Fdr")
            self.txtFAC.setText(self.Layername + "_Fac")
            self.txtSlope.setText(self.Layername + "_Slope")
            self.txtStream.setText(self.Layername + "_Stream")
            self.txtStreamVector.setText(self.Layername + "_Stream_polyline")
            self.txtCatchment.setText(self.Layername + "_Catchment")

    def isInt(self,anyNumberOrString):
        try:
            int(anyNumberOrString)  # to check float and int use "float(anyNumberOrString)"
            return True
        except ValueError:
            return False

    def Click_Okbutton(self):
        #레이어 경로에 한글이 있으면 오류로 처리 
        if _util.CheckKorea(self.LayerPath):
            _util.MessageboxShowInfo("Batch Processor", "\n The file path contains Korean. \n")
            return

        fname, ext = os.path.splitext(self.LayerPath)
        if ext.upper() in ".ASC":
            # _util.MessageboxShowInfo("1","asc")
            inputfile=self.LayerPath
            self.LayerPath=self.LayerPath.replace(ext,".TIF")
            _util.Convert_ASCii_To_TIFF(inputfile,self.LayerPath)
            # _util.MessageboxShowInfo("Layerpath",self.LayerPath)

            # return
        elif ext.upper() in ".TIF":
            # _util.MessageboxShowInfo("1", "tif")
            pass
        else :
            _util.MessageboxShowInfo("Batch Processor","Only ASCII files and TIF file formats are supported.")
            return



        #파일 이름이 없는 텍스트 박스 확인
        if self.checkTextbox(self.txtFill):
            pass
        else:
            return

        # self.checkTextbox(self.txtFlat)


        if self.checkTextbox(self.txtFD ):
            pass
        else:
            return

        if self.checkTextbox(self.txtFAC):
            pass
        else:
            return


        if self.checkTextbox(self.txtSlope):
            pass
        else:
            return


        if self.checkTextbox(self.txtStream):
            pass
        else:
            return


        if self.txtCellValue.text() == "":
            _util.MessageboxShowError("Batch Processor", " CellValue is required. ")
            self.txtCellValue.setFocus()
            return False

        vlaue=self.txtCellValue.text()
        if not self.isInt(vlaue):
            _util.MessageboxShowError("Batch Processor", " Please enter only integers. ")
            return

        if self.chkStream.isChecked():
            self.checkTextbox(self.txtStreamVector)

        self.checkTextbox(self.txtCatchment)

        #파일 경로 변수에 셋팅
        self.SettingValue()

        #Fill sink 시작
        arg=_util.GetTaudemArg(self.LayerPath, self.Fill, _util.tauDEMCommand.SK, False,0)
        ReultFill=self.ExecuteArg(arg,self.Fill)

        # Fill sink 후에 Flat 처리를 하면 실행이 안되는거 같음 확인 해야 할 문제 
        
        # # Fill sink 가 성공적으로 처리가 되었을때 다음 루틴 처리 진행
        # if (ReultFill):
        #     # Flat 처리 부분
        #     # 1. fill sink tif 파일을 asc 로 변환
        #     RetConvert_Fill=_util.Convert_TIFF_To_ASCii_retpaht(self.Fill)
        #     # Flat 결과 파일
        #     AscFlat = self.Flat.replace(".tif",".asc")
        #
        #     # 2. Fill sink Flat 실행
        #     Flat_exe_Path = os.path.dirname(os.path.abspath(__file__)) + '\Flat\Flat.exe'
        #     arg ='"' + Flat_exe_Path + '"' +' '+  RetConvert_Fill +' '+ AscFlat
        #     # self.ExecuteArg(arg,RetConvert_Fill)
        #     _util.MessageboxShowError("arg",arg)
        #     # 3. Flat 결과를 Tiff 로 변환 처리
        #     # _util.Convert_ASCii_To_TIFF(AscFlat,self.Flat)

        if (ReultFill):
            # FD 시작
            arg = _util.GetTaudemArg(self.Fill, self.FD, _util.tauDEMCommand.FD, False,0)
            FillResult =self.ExecuteArg(arg,self.FD)
            if (FillResult):
                #FA 시작
                arg = _util.GetTaudemArg(self.FD, self.FAC, _util.tauDEMCommand.FA, False,0)
                FacResult=self.ExecuteArg(arg,self.FAC)
                if(FacResult):
                    #Slope 시작
                    arg = _util.GetTaudemArg(self.Fill,self.Slope, _util.tauDEMCommand.SG, False, 0)
                    SlopResult=self.ExecuteArg(arg,self.Slope)
                    if (SlopResult):
                        #Stream 시작
                        cellValue=self.txtCellValue.text()
                        arg = _util.GetTaudemArg(self.FAC,self.Stream, _util.tauDEMCommand.ST, False, cellValue)
                        StreamResult=self.ExecuteArg(arg,self.Stream)
                        if (StreamResult):
                            arg=self.CreateStreamVector()

                            StreamVectorResult = self.ExecuteArg(arg, self.StreamVector)
                            if (StreamVectorResult):
                                #tif 파일 asc 파일로 변환
                                self.ConvertTiff_To_Asc()
                                self.Delete_tempfile()
                                _util.MessageboxShowInfo("Batch processor","The process is complete.")
                                self.close()
    #arg 받아서 처리 완료 되면 레이어  Qgis 에서 올림
    def ExecuteArg(self,arg,outpath):
        returnValue=_util.Execute(arg)
        if returnValue==0:
            #self.Addlayer_OutputFile(outpath)
            return True
        else:
            _util.MessageboxShowError("Batch Processor", " There was an error creating the file. ")
            return False

    def Delete_tempfile(self):
        for i in range(0,3):
            os.remove(self.outFiles[i])
        if self.chkStream.isChecked():
            pass
        else:
            os.remove(self.outFiles[3])





    # 레이어 목록 Qgis에 올리기
    def Addlayer_OutputFile(self, outputpath):
        if (os.path.isfile(outputpath)):
            fileName = outputpath
            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
            layer = QgsRasterLayer(fileName, baseName, "gdal")
            QgsProject.instance().addMapLayer(layer)

    #파일 경로 변수에 셋팅
    def SettingValue(self):
        self.Fill=os.path.dirname(self.LayerPath) + "\\"+ self.txtFill.text() + ".tif"
        # self.Flat=os.path.dirname(self.LayerPath) + "\\"+ self.txtFlat.text()+ ".tif"
        self.FD=os.path.dirname(self.LayerPath) + "\\"+ self.txtFD.text()+ ".tif"
        self.FAC=os.path.dirname(self.LayerPath) + "\\"+ self.txtFAC.text()+ ".tif"
        self.Slope=os.path.dirname(self.LayerPath) + "\\"+ self.txtSlope.text()+ ".tif"
        self.Stream=os.path.dirname(self.LayerPath) + "\\"+ self.txtStream.text()+ ".tif"
        self.Catchment = os.path.dirname(self.LayerPath) +  "\\"+ self.txtCatchment.text()+ ".tif"
        self.StreamVector = os.path.dirname(self.LayerPath) + "\\" + self.txtStreamVector.text() + ".shp"
        self.CellValue= int(self.txtCellValue.text())

    def CreateStreamVector(self):
        self.outFiles =[]
        self.outFiles.append(os.path.dirname(self.Fill) + "\\temp_1.tif")
        self.outFiles.append(os.path.dirname(self.Fill) + "\\temp_1.dat")
        self.outFiles.append(os.path.dirname(self.Fill) + "\\temp_2.dat")
        # outFiles3 = "C:\GRM\Sample\Gyeongpoho_DEM_Stream.shp"
        self.outFiles.append(self.StreamVector)
        # outFiles4 = os.path.dirname(self.Fill) + "\\temp_2.tif"
        self.outFiles.append(self.Catchment)
        args =(' -fel "{0}" -p "{1}" -ad8 "{2}" -src "{3}" -ord "{4}" -tree "{5}" -coord "{6}" -net "{7}" -w "{8}" '.format(self.Fill, self.FD, self.FAC, self.Stream,self.outFiles[0], self.outFiles[1], self.outFiles[2], self.outFiles[3], self.outFiles[4]))
        streamnet = '"C:\Program Files\TauDEM\TauDEM5Exe\StreamNet.exe" '

        return streamnet+args


    #텍스트 박스에 파일 이름이 없는 경우 체크
    def checkTextbox(self,txt):
         if txt.text() == "":
            _util.MessageboxShowInfo("Batch Processor", " A filename is required. ")
            txt.setFocus()
            return False
         else:
             return True

    #기본 변수 초기화
    def Settingfile(self):
        self.LayerPath="";self.Layername=""
        self.Fill="";self.Flat="";self.FD="";self.FAC=""
        self.Slope="";self.Stream="";self.CellValue=0


    # 프로그램 종료
    def Close_Form(self):
        self.close()

    def ConvertTiff_To_Asc(self):
        _util.Convert_TIFF_To_ASCii(self.Fill)
        #_util.Convert_TIFF_To_ASCii(self.Flat)
        _util.Convert_TIFF_To_ASCii(self.FD)
        _util.Convert_TIFF_To_ASCii(self.FAC)
        _util.Convert_TIFF_To_ASCii(self.Slope)
        _util.Convert_TIFF_To_ASCii(self.Stream)
        if self.chkStream.isChecked():
            _util.VectorLayer_AddLayer(self.StreamVector)
        _util.Convert_TIFF_To_ASCii(self.Catchment)

    def checkbox_Stream(self):
        if self.chkStream.isChecked():
            self.txtStreamVector.setEnabled(True)
        else:
            self.txtStreamVector.setEnabled(False)

    def setStreamChecked(self, event):
        self.chkStream.setChecked(not self.chkStream.isChecked())


    def __init__(self, parent=None, iface=None):
        """Constructor."""
        super(BatchProcessor, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        
        Flat_Path = os.path.dirname(os.path.abspath(__file__))

        #파일 경로 변수 선언
        self.Settingfile()

        #콤보 박스 레이어 셋팅
        self.SetCombobox()

        #콤보 박스 선택 시 텍스트 창에 기본 파일 이름 적용 
        self.cmbLayer.currentIndexChanged.connect(self.SelectCombobox_event)

        # OK버튼 눌렀을때 처리 부분
        self.btnOK.clicked.connect(self.Click_Okbutton)
        # self.btnOK.clicked.connect(self.CreateStreamVector)

        # Cancle버튼 클릭 이벤트
        self.btnCancel.clicked.connect(self.Close_Form)

        # # 라디오 버튼 기본 설정
        self.chkStream.stateChanged.connect(self.checkbox_Stream)
        self.chkStream.setChecked(True)
        self.checkbox_Stream()

        # Stream chk와 label 연동
#         QObject.connect(self.lblStream, SIGNAL("clicked()"), self.setStreamChecked)
        self.lblStream.mouseReleaseEvent = self.setStreamChecked
