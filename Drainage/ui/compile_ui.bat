@echo off
call "C:\Program Files\QGIS 3.34.0\bin\o4w_env.bat"

@echo on
pyuic5 Slope_dialog_base.ui > Slope_dialog_base.py
pyuic5 Stream_Definition_dialog_base.ui > Stream_Definition_dialog_base.py
pyuic5 Watershed_dialog_base.ui > Watershed_dialog_base.py