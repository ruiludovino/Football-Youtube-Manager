import os
import subprocess
import re
import configparser
import shutil
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QProgressBar, QPushButton, QScrollArea,
    QFrame, QSizePolicy, QHBoxLayout, QTextEdit,
    QMenu, QAction, QInputDialog, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QSize, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont



