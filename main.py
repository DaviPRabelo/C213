"""
C213 — Identificação de Sistemas & Controle PID
Grupo 7: IMC + ITAE
Entry point da aplicação.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from app.views.main_window import MainWindow
from app.controllers.main_controller import MainController


def main():
    # Habilita DPI alto
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("C213 PID Controller")
    app.setOrganizationName("Grupo 7")

    view = MainWindow()
    controller = MainController(view)

    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
