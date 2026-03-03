from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtGui import QColor

def get_colored_icon(icon_path, color_name):
    pixmap = QPixmap(icon_path)
    if pixmap.isNull():
        return QIcon()
    
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color_name))
    painter.end()
    return QIcon(pixmap)