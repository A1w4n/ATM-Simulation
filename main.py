import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print(
            "[ERROR] PySide6 is not installed.\n"
            "Install it with:  pip install PySide6"
        )
        sys.exit(1)

    try:
        import openpyxl  # noqa: F401
    except ImportError:
        print(
            "[ERROR] openpyxl is not installed.\n"
            "Install it with:  pip install openpyxl"
        )
        sys.exit(1)

    from ATM_UI import ATMWindow
    from PySide6.QtGui import QPalette, QColor
    from PySide6.QtWidgets import QApplication

    BG    = "#0a0f1e"
    TEXT  = "#f1f5f9"
    PANEL = "#111827"
    BORDER= "#1e293b"
    ACCENT= "#38bdf8"

    app = QApplication(sys.argv)
    app.setApplicationName("ATM Simulator")
    app.setApplicationDisplayName("ATM Simulator")
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(BG))
    palette.setColor(QPalette.WindowText,      QColor(TEXT))
    palette.setColor(QPalette.Base,            QColor(PANEL))
    palette.setColor(QPalette.AlternateBase,   QColor(BORDER))
    palette.setColor(QPalette.Text,            QColor(TEXT))
    palette.setColor(QPalette.Button,          QColor(PANEL))
    palette.setColor(QPalette.ButtonText,      QColor(TEXT))
    palette.setColor(QPalette.Highlight,       QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor(BG))
    app.setPalette(palette)

    window = ATMWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
