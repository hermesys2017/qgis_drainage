@echo off
call "C:\Program Files\QGIS 3.28.9\bin\o4w_env.bat"

@echo on
pyuic5 GRM_dialog_base.ui > GRM_dialog_base.py