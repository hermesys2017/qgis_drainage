@echo off
call "C:\Program Files\QGIS 3.34.0\bin\o4w_env.bat"

@echo on
pyuic5 drainage_dialog_base.ui > drainage_dialog_base.py
pyuic5 Catchment_dialog_base.ui > Catchment_dialog_base.py
pyuic5 Drainage_dockwidget_base.ui > Drainage_dockwidget_base.py
pyuic5 FillSink_dialog_base.ui > FillSink_dialog_base.py
pyuic5 Flat_dialog_base.ui > Flat_dialog_base.py
pyuic5 Flow_Accumulation_dialog_base.ui > Flow_Accumulation_dialog_base.py
pyuic5 Flow_Direction_dialog_base.ui > Flow_Direction_dialog_base.py