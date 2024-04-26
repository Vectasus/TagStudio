import math
from PySide6.QtWidgets import QVBoxLayout, QWidget, QDialog, QHBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import Qt, pyqtSignal, pyqtSlot
from PySide6.QtGui import QLinearGradient, QColor, QPainter, QConicalGradient, QPainterPath, QPalette

def calculateBrightness(h, s, l):
        color = QColor.fromHsl(h, s, l);
        r, g, b = color.toTuple()
        return 0.299 * r + 0.587 * g + 0.114 * b

class SelectSL(QWidget):
    valueChanged = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hue = 0
        self.sat = 0
        self.lum = 0
        self.dragging = False

    def setHue(self, hue):
        self.hue = hue
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        solidColor = QColor.fromHsl(self.hue, 100, 50)
        painter.fillRect(self.rect(), solidColor)

        satGradient = QLinearGradient(0, 0, self.width(), 0)
        satGradient.setColorAt(0, QColor(128, 128, 128))
        satGradient.setColorAt(1, QColor(128, 128, 128, 0))
        painter.fillRect(self.rect(), satGradient)
        
        lumGradient = QLinearGradient(0, 0, 0, self.height())
        lumGradient.setColorAt(0, QColor(0, 0, 0, 0))
        lumGradient.setColorAt(1, QColor(0, 0, 0))
        painter.fillRect(self.rect(), lumGradient)

    def setValue(self, pos):
        self.sat = pos.x()
        self.lum = pos.y()
        self.update()
        self.valueChanged.emit(self.sat, self.lum)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragging = True
            self.setValue(event.pos())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.setValue(event.pos())

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.setValue(event.pos())

class SelectH(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        outerRadius = min(self.width(), self.height()) // 3
        innerRadius = outerRadius / 2

        centerX = self.width() / 2
        centerY = self.height() / 2

        gradient = QConicalGradient(centerX, centerY, 0)
        gradient.setColorAt(0,   QColor(255,   0,   0))
        gradient.setColorAt(1/6, QColor(255, 255,   0))
        gradient.setColorAt(2/6, QColor(  0, 255,   0))
        gradient.setColorAt(3/6, QColor(  0, 255, 255))
        gradient.setColorAt(4/6, QColor(  0,   0, 255))
        gradient.setColorAt(5/6, QColor(255,   0, 255))
        gradient.setColorAt(1,   QColor(255,   0,   0))

        path = QPainterPath()
        path.addEllipse(centerX - outerRadius, centerY - outerRadius, outerRadius * 2, outerRadius * 2)
        path.addEllipse(centerX - innerRadius, centerY - innerRadius, innerRadius * 2, innerRadius * 2)
        painter.setClipPath(path)

        painter.fillRect(event.rect(), gradient)

    def setValue(self, pos):
        relX = pos.x() - self.width() / 2
        relY = pos.y() - self.height() / 2
        self.value = math.atan2(relY, relX) / math.pi * 360
        self.update()
        self.valueChanged.emit(self.value)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragging = True
            self.setValue(event.pos())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.setValue(event.pos())

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.setValue(event.pos())

class ColorPicker(QDialog):
    def __init__(self):
        super().__init__()

        self.h = 0
        self.s = 0
        self.l = 0

        self.setWindowTitle("Color Picker")

        layout = QVBoxLayout()

        self.selectH = SelectH()
        self.selectSL = SelectSL()
        self.hexInput = QLineEdit()
        self.colorRect = QWidget()
        self.colorRect.setFixedSize(50, 50)
        self.submitButton = QPushButton("Submit")

        selectors = QHBoxLayout()
        selectors.addWidget(self.selectH)
        selectors.addWidget(self.selectSL)

        showColor = QHBoxLayout()
        showColor.addWidget(self.hexInput)
        showColor.addWidget(self.colorRect)

        layout.addLayout(selectors)
        layout.addLayout(showColor)
        layout.addWidget(self.submitButton)
        self.setLayout(layout)

        self.selectH.valueChanged.connect(self.onHueChange)
        self.selectSL.valueChanged.connect(self.onSatLumChange)
        self.hexInput.textChanged.connect(self.onHexInputChange)

    def updateHexInput(self):
        hex_value = "#{:02x}{:02x}{:02x}".format(self.h, self.s, self.l)
        self.hexInput.setText(hex_value)

    def updateColorDisplay(self):
        palette = self.colorRect.palette()
        palette.setColor(QPalette.Background, QColor(self.h, self.s, self.l))
        self.colorRect.setAutoFillBackground(True)
        self.colorRect.setPalette(palette)

    @pyqtSlot(int)
    def onHueChange(self, hue):
        self.h = hue
        self.updateHexInput()
        self.updateColorDisplay()

    @pyqtSlot(int, int)
    def onSatLumChange(self, sat, lum):
        self.s = sat
        self.l = lum
        self.updateHexInput()
        self.updateColorDisplay()

    @pyqtSlot(str)
    def onHexInputChange(self, hex_value):
        hex_value = hex_value.strip('#')
        if len(hex_value) < 6:
            hex_value = hex_value.zfill(6)
        
        r, g, b = hex_value[:2], hex_value[2:4], hex_value[4:6]
        
        try:
            color = QColor(int(r, 16), int(g, 16), int(b, 16))
            hsl_color = color.toHsl()
            
            self.h = hsl_color.hue()
            self.s = hsl_color.saturation()
            self.l = hsl_color.lightness()
            
            self.updateColorDisplay()
        except ValueError:
            pass
