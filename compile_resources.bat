@echo off
call "C:\Program Files\QGIS 3.28.9\bin\o4w_env.bat"

@echo on
pyrcc5 -o resources.py resources.qrc