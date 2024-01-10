import pytest
from pytestqt.qtbot import QtBot
from qgis.core import QgsProject, QgsVectorLayer
from qgis.PyQt.QtWidgets import QApplication

from drainage.Batch_Processor_dialog import BatchProcessor


@pytest.fixture
def app(qtbot: QtBot):
    """Returns BatchProcessor dialog."""
    test_app = QApplication([])
    widget = BatchProcessor()
    qtbot.addWidget(widget)
    yield test_app
    test_app.exit()


def test_path(app: QApplication):
    """Test path."""
    app.activeWindow()
    assert 1


def test_add_layer():
    layer = QgsVectorLayer("Polygon", "dummy_polygon_layer", "memory")
    QgsProject.instance().addMapLayer(layer)
    assert set(QgsProject.instance().mapLayers().values()) == {layer}
