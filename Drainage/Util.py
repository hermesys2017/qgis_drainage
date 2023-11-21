# -*- coding: utf-8 -*-
import os
import os.path
import re
import subprocess
import tempfile

import win32api
from qgis.core import QgsApplication, QgsProject, QgsRasterLayer, QgsVectorLayer
from qgis.PyQt.QtCore import QFileInfo
from qgis.PyQt.QtWidgets import QComboBox, QMessageBox

from drainage.logger import get_logger


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class util(Singleton):
    def __init__(self):
        self.Input_Layer_Path = ""
        self.FillSink_Layer_Path = ""
        self.FD_Layer_Path = ""
        self.FA_Layer_Path = ""
        self.Stream_Layer_Path = ""
        self.tauDemPath = ""

        self.tauDEMCommand = self.enum(
            "SK", "FLAT", "FD", "FA", "SG", "ST", "STV", "CAT"
        )
        self.__logger = get_logger()

    def error_decorator(self, title: str):
        def inner_error_process(func: callable):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.__logger.error(e)
                    self.MessageboxShowError(title, str(e))

            return wrapper

        return inner_error_process

    def enum(*sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        reverse = dict((value, key) for key, value in enums.items())
        enums["reverse_mapping"] = reverse
        return type("Enum", (), enums)

    def is_installed_taudem(self) -> bool:
        return os.path.isdir(self.GetTaudemPath())

    def is_installed_gdal_for_taudem(self) -> bool:
        return os.path.isdir(self.get_gdal_path())

    def __get_plugin_env(self) -> dict:
        """
        cell 에디터에 맞는 PATH를 설정해주는 함수
        """
        env = os.environ.copy()
        env["PATH"] = self.get_gdal_path() + os.pathsep + env["PATH"]
        return env

    # Taudem path 받아 오기
    def GetTaudemPath(self):
        tauPath = "C:\\Program Files\\TauDEM\\TauDEM5Exe\\"
        return tauPath

    # @property
    def get_gdal_path(self):
        gdal_path = "C:\\Program Files\\GDAL"
        return gdal_path

    def Execute(self, arg):
        value = subprocess.run(
            arg,
            shell=True,
            env=self.__get_plugin_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        self.__logger.info(f"Execute: {arg}")
        if value.returncode != 0:
            self.__logger.error(
                f"Execute: {arg}\nstdout: {value.stdout}\nstderr: {value.stderr}"
            )
            raise Exception(f"Process run error: {arg}")
        return value.returncode

    # 각각의 기능별로 arg를 생성하고 반환 하는 기능
    def GetTaudemArg(
        self,
        inputfile: str,
        ouputfile: str,
        taudemcommand: str,
        facoption: bool,
        optionvalue: str,
    ):
        option = optionvalue
        tauPath = self.GetTaudemPath()
        input = inputfile.replace("\\", "\\\\")
        output = ouputfile.replace("\\", "\\\\")
        output_Temp = self.GetTempFilePath(ouputfile)

        arg = ""
        if taudemcommand == self.tauDEMCommand.SK:
            tauPath = tauPath + "PitRemove.exe"
            arg = (
                '"'
                + tauPath
                + '"'
                + " -z "
                + '"'
                + input
                + '"'
                + " -fel "
                + '"'
                + output
                + '"'
            )
        elif taudemcommand == self.tauDEMCommand.FD:
            tauPath = tauPath + "D8FlowDir.exe"
            arg = (
                '"'
                + tauPath
                + '"'
                + " -fel "
                + '"'
                + input
                + '"'
                + " -p "
                + '"'
                + output
                + '"'
                + " -sd8 "
                + '"'
                + output_Temp
                + '"'
            )
        elif taudemcommand == self.tauDEMCommand.FA:
            tauPath = tauPath + "AreaD8.exe"
            if facoption:
                arg = (
                    '"'
                    + tauPath
                    + '"'
                    + " -p "
                    + '"'
                    + input
                    + '"'
                    + " -ad8 "
                    + '"'
                    + output
                    + '"'
                )
            else:
                arg = (
                    '"'
                    + tauPath
                    + '"'
                    + " -p "
                    + '"'
                    + input
                    + '"'
                    + " -ad8 "
                    + '"'
                    + output
                    + '"'
                    + " -nc "
                )
        elif taudemcommand == self.tauDEMCommand.SG:
            tauPath = tauPath + "D8FlowDir.exe"
            arg = (
                '"'
                + tauPath
                + '"'
                + " -fel "
                + '"'
                + input
                + '"'
                + " -p "
                + '"'
                + output_Temp
                + '"'
                + " -sd8 "
                + '"'
                + output
                + '"'
            )
        elif taudemcommand == self.tauDEMCommand.ST:
            tauPath = tauPath + "Threshold.exe"
            arg = (
                '"'
                + tauPath
                + '"'
                + " -ssa "
                + '"'
                + input
                + '"'
                + " -src "
                + '"'
                + output
                + '"'
                + " -thresh "
                + option
            )
        return arg

    def GetCacthmentsArg(
        self, input_layer, fd_layer, fa_layer, stream_Layer, txtoutput
    ):
        output1 = self.GetTempFilePath(input_layer)
        output2 = output1.replace("tif", "dat")
        output3 = output1.replace("tif", "dat")
        output4 = output1.replace("tif", "shp")
        output5 = txtoutput
        input0 = input_layer
        input1 = fd_layer
        input2 = fa_layer
        input3 = stream_Layer
        tauPath = self.GetTaudemPath()
        tauPath = tauPath + "StreamNet.exe"
        arg = (
            '"'
            + tauPath
            + '"'
            + " -fel "
            + '"'
            + input0
            + '"'
            + " -p "
            + '"'
            + input1
            + '"'
            + " -ad8 "
            + '"'
            + input2
            + '"'
            + " -src "
            + '"'
            + input3
            + '"'
            + " -ord "
            + '"'
            + output1
            + '"'
            + " -tree "
            + '"'
            + output2
            + '"'
            + " -coord  "
            + '"'
            + output3
            + '"'
            + " -net "
            + '"'
            + output4
            + '"'
            + " -w "
            + '"'
            + output5
            + '"'
        )
        return arg

    def GetWatershed(self, input_layer, shape_layer, output):
        tauPath = self.GetTaudemPath() + "GageWatershed.exe"
        arg = '"{0}" -p "{1}" -o "{2}" -gw "{3}"'.format(
            tauPath, input_layer, shape_layer, output
        )
        return arg

    # Watershed 처리
    def GetWatershedArg(
        self,
        fill_layer,
        fd_layer,
        fa_layer,
        txtstream_cellvalue,
        shp_layer,
        txtoutput,
        flag,
    ):
        # shape 파일의 경로를 받아 오면 경로상에 layerid가 붙어서 넘오옴 그래서 문자열 잘라서 사용
        shpPath = shp_layer.split("|")[0]

        # 임시 파일 경로 생성 함수 tempfile.mktemp()
        # tempfile.mktemp() 파이썬 기본 모듈로 파일을 같은 경로로 옮기고 사용
        temOutput = tempfile.mktemp() + ".tif"
        temOutput2 = tempfile.mktemp() + ".tif"
        temOutput3 = tempfile.mktemp() + ".tif"
        streamOutput = tempfile.mktemp() + ".tif"

        temptif = tempfile.mktemp() + ".tif"
        tempdat = tempfile.mktemp() + ".dat"
        tempdat2 = tempfile.mktemp() + ".dat"
        tempShape = (
            os.path.dirname(shpPath)
            + "\\"
            + os.path.basename(shpPath).replace(".shp", "_net.shp")
        )

        tauPathAread8 = self.GetTaudemPath() + "Aread8.exe"
        tauPathPeukerDouglas = self.GetTaudemPath() + "PeukerDouglas.exe"
        tauPthThreshold = self.GetTaudemPath() + "Threshold.exe"
        tauPathStreamnet = self.GetTaudemPath() + "Streamnet.exe"

        returns = "1"
        arg = (
            '"'
            + tauPathAread8
            + '"'
            + " -p "
            + '"'
            + fd_layer
            + '"'
            + " -ad8 "
            + '"'
            + temOutput
            + '"'
            + " -o "
            + '"'
            + shpPath
            + '"'
        )
        re = self.Execute(arg)
        self.MessageboxShowError("re", str(re))
        if str(re) == "0":
            arg = (
                '"'
                + tauPathPeukerDouglas
                + '"'
                + " -fel "
                + '"'
                + fill_layer
                + '"'
                + " -ss "
                + '"'
                + temOutput2
                + '"'
            )
            re1 = self.Execute(arg)
            self.MessageboxShowError("re1", str(re1))
            if str(re1) == "0":
                arg = (
                    '"'
                    + tauPathAread8
                    + '"'
                    + " -p "
                    + '"'
                    + fd_layer
                    + '"'
                    + " -ad8 "
                    + '"'
                    + temOutput3
                    + '"'
                    + " -o "
                    + '"'
                    + shpPath
                    + '"'
                    + " -wg "
                    + '"'
                    + temOutput2
                    + '"'
                )
                re2 = self.Execute(arg)
                self.MessageboxShowError("re2", str(re2))
                if str(re2) == "0":
                    # stream Create
                    arg = (
                        '"'
                        + tauPthThreshold
                        + '"'
                        + " -ssa "
                        + '"'
                        + temOutput3
                        + '"'
                        + " -src "
                        + '"'
                        + streamOutput
                        + '"'
                        + " -thresh "
                        + txtstream_cellvalue
                    )
                    re3 = self.Execute(arg)
                    self.MessageboxShowError("re3", str(re3))
                    if str(re3) == "0":
                        arg = (
                            '"'
                            + tauPathStreamnet
                            + '"'
                            + " -fel "
                            + '"'
                            + fill_layer
                            + '"'
                            + " -p "
                            + '"'
                            + fd_layer
                            + '"'
                            + " -ad8 "
                            + '"'
                            + fa_layer
                            + '"'
                            + " -src "
                            + '"'
                            + streamOutput
                            + '"'
                            + " -ord "
                            + '"'
                            + temptif
                            + '"'
                            + " -tree "
                            + '"'
                            + tempdat
                            + '"'
                            + " -coord "
                            + '"'
                            + tempdat2
                            + '"'
                            + " -net "
                            + '"'
                            + tempShape
                            + '"'
                            + " -w "
                            + '"'
                            + txtoutput
                            + '"'
                            + " -o "
                            + '"'
                            + shpPath
                            + '"'
                        )
                        if str(flag) == "True":
                            arg = arg + " -sw"
                        re4 = self.Execute(arg)
                        self.MessageboxShowError("re4", str(re4))
                        if str(re4) == "0":
                            returns = "0"
        return returns

    # 윈도우 임시 폴더에 임시 파일 생성
    def GetTempFilePath(self, tempfilepath):
        output_temp = win32api.GetTempPath() + os.path.basename(tempfilepath)
        output_temp = output_temp.replace("\\", "\\\\")
        return output_temp

    # 콤보박스 리스트 셋팅 type은( tif, shp , "" 일땐 모두다)
    def SetCommbox(self, layers, commbox: QComboBox, ext: str) -> None:
        layer_list = []

        if layers is None:
            pass
        elif ext.upper() == "TIF":
            for layer in layers:
                layertype = layer.type()
                if layertype == layer.RasterLayer:
                    layer_list.append(layer.name())
        elif ext.upper() == "SHP":
            for layer in layers:
                layertype = layer.type()
                if layertype == layer.VectorLayer:
                    layer_list.append(layer.name())
        else:
            for layer in layers:
                layer_list.append(layer.name())
        commbox.clear()
        combolist = ["select layer"]
        combolist.extend(layer_list)
        commbox.addItems(combolist)

    # 메시지 박스 출력
    def MessageboxShowInfo(self, title, message):
        QMessageBox.information(None, title, message)

    def MessageboxShowError(self, title, message):
        QMessageBox.warning(None, title, message)

    # 콤보 박스에서 선택된 레이어 경로 받아 오기
    def GetcomboSelectedLayerPath(self, commbox):
        layername = commbox.currentText()
        layer = None
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == layername:
                layer = lyr
        return layer.dataProvider().dataSourceUri()

    # 파일 존재 유무 확인
    def CheckFile(self, path):
        filepath = path.replace("\\", "\\\\")
        if os.path.isfile(filepath):
            return True
        else:
            return False

    # 폴더 경로 맞는지 확인
    def CheckFolder(self, path):
        filepath = path.replace("\\", "\\\\")
        if os.path.isdir(filepath):
            return True
        else:
            return False

    def CheckTaudem(self):
        if os.path.isdir("C:\\Program Files\\TauDEM"):
            return True
        else:
            return False

    # 폴더및 파일 명칭에 한글 포함하고 있는지 체크
    def CheckKorea(self, string):
        strs = re.sub("[^가-힣]", "", string)
        if strs:
            return True
        else:
            return False

    # 파일 경로 중에 파일명만 받아 오기
    def GetFilename(self, filename):
        s = os.path.splitext(filename)
        s = os.path.split(s[0])
        return s[1]

    def Convert_TIFF_To_ASCii(self, inputfile: str):
        # nodata 설정옵션이 Gdal 에서 안먹음
        Extension = os.path.splitext(inputfile)[1]
        Output = inputfile.replace(Extension, ".asc")
        qgisPath = QgsApplication.instance().applicationDirPath()
        gdal_translate = qgisPath + r"\gdal_translate.exe"
        arg = '"{0}" -of AAIGrid -co FORCE_CELLSIZE=TRUE "{1}" "{2}"'.format(
            gdal_translate, inputfile, Output
        )
        result = self.Execute(arg)
        if result >= 0:
            self.ASC_Header_replace(Output)
            self.Addlayer_OutputFile(Output)

    def Convert_ASCii_To_TIFF(self, inputfile, OutFile):
        gdal_translate = "C:\Program Files\GDAL\gdal_translate.exe"
        arg = '"{0}" -of GTiff  "{1}" "{2}"'.format(gdal_translate, inputfile, OutFile)
        self.Execute(arg)

    def Convert_TIFF_To_ASCii_retpaht(self, inputfile):
        Extension = ""
        Extension = os.path.splitext(inputfile)[1]
        Output = inputfile.replace(Extension, "_Flat.asc")
        gdal_translate = "C:\Program Files\GDAL\gdal_translate.exe"
        # arg = '"{0}" -of AAIGrid -ot Float64 -a_nodata -9999 --config GDAL_FILENAME_IS_UTF8 NO "{1}" "{2}"'.format(gdal_translate,inputfile,Output)
        arg = '"{0}" -of AAIGrid "{1}" "{2}"'.format(gdal_translate, inputfile, Output)
        self.Execute(arg)
        return Output

    # 레스터 레이어 목록 Qgis에 올리기
    def Addlayer_OutputFile(self, outputpath):
        if os.path.isfile(outputpath):
            fileName = outputpath
            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
            layer = QgsRasterLayer(fileName, baseName, "gdal")
            QgsProject.instance().addMapLayer(layer)

    def VectorLayer_AddLayer(self, outputpath):
        fileName = outputpath
        fileInfo = QFileInfo(fileName)
        baseName = fileInfo.baseName()
        layer = QgsVectorLayer(outputpath, baseName, "ogr")
        QgsProject.instance().addMapLayer(layer)
        if not layer:
            self.MessageboxShowInfo("Vector layer add", "Layer failed to load!")

    def ASC_Header_replace(self, asc_file):
        nodata = self.ASC_Header_nodata(asc_file)
        if nodata != "" or nodata == "-9999":
            self.ASC_Replace_data(nodata, asc_file)

    def ASC_Header_nodata(self, asc_file):
        self.nodata = ""
        dataHeaderItems = open(asc_file).readlines()[:20]
        read_lower = [
            item.lower() for item in dataHeaderItems
        ]  # 리스트 의 모든 글자를 소문자화 시킴
        for row in read_lower:
            if "nodata_value" in row:
                self.nodata = row.replace("nodata_value", "").strip()
                break
        return self.nodata

    def ASC_Replace_data(self, data, file):
        # Read contents from file as a single string
        file_handle = open(file, "r")
        file_string = file_handle.read()
        file_handle.close()

        file_string = re.sub(data, "-9999", file_string)

        file_handle = open(file, "w")
        file_handle.write(file_string)
        file_handle.close()
