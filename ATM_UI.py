"""
ATM_UI.py  –  PySide6 front-end for the ATM simulator.
All business / auth logic lives in ATM_auth.py.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ATM_auth as auth

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame, QGraphicsDropShadowEffect, QTextEdit, QDialog,
    QDialogButtonBox, QSizePolicy, QSpacerItem, QScrollArea,
)
from PySide6.QtCore  import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QSize
from PySide6.QtGui   import (
    QColor, QFont, QFontDatabase, QPalette, QPixmap,
    QLinearGradient, QPainter, QBrush, QPen, QIcon,
)

# ─────────────────────────────────────────────────────────────
#  Palette / design tokens
# ─────────────────────────────────────────────────────────────
BG          = "#0a0f1e"          # deep navy
PANEL       = "#111827"          # card background
BORDER      = "#1e293b"          # subtle border
ACCENT      = "#38bdf8"          # sky-blue accent
ACCENT2     = "#818cf8"          # indigo soft
TEXT        = "#f1f5f9"          # primary text
MUTED       = "#64748b"          # muted label
SUCCESS     = "#34d399"          # emerald
ERROR       = "#f87171"          # rose
WARN        = "#fbbf24"          # amber

SERVICE_FEE = 18.0


def shadow(radius=24, color="#000000", opacity=160):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(radius)
    fx.setOffset(0, 6)
    fx.setColor(QColor(color))
    fx.color().setAlpha(opacity)
    return fx


def card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setStyleSheet(f"""
        QFrame {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 16px;
        }}
    """)
    f.setGraphicsEffect(shadow())
    return f


def styled_btn(text, color=ACCENT, text_color="#0a0f1e", small=False) -> QPushButton:
    h = 40 if small else 52
    btn = QPushButton(text)
    btn.setFixedHeight(h)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {color};
            color: {text_color};
            border: none;
            border-radius: {h//2}px;
            font-size: {'13px' if small else '15px'};
            font-weight: 700;
            letter-spacing: 0.5px;
            padding: 0 24px;
        }}
        QPushButton:hover  {{ background: {color}cc; }}
        QPushButton:pressed{{ background: {color}88; }}
    """)
    return btn


def ghost_btn(text, color=ACCENT) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(44)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            color: {color};
            border: 1.5px solid {color};
            border-radius: 22px;
            font-size: 14px;
            font-weight: 600;
            padding: 0 20px;
        }}
        QPushButton:hover  {{ background: {color}22; }}
        QPushButton:pressed{{ background: {color}44; }}
    """)
    return btn


def field(placeholder="", echo_password=False) -> QLineEdit:
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setFixedHeight(50)
    if echo_password:
        e.setEchoMode(QLineEdit.Password)
    e.setStyleSheet(f"""
        QLineEdit {{
            background: #1e293b;
            border: 1.5px solid {BORDER};
            border-radius: 10px;
            padding: 0 14px;
            font-size: 15px;
            color: {TEXT};
        }}
        QLineEdit:focus {{
            border: 1.5px solid {ACCENT};
            background: #172033;
        }}
        QLineEdit::placeholder {{ color: {MUTED}; }}
    """)
    return e


def lbl(text, size=14, color=TEXT, bold=False, align=Qt.AlignLeft) -> QLabel:
    l = QLabel(text)
    l.setAlignment(align)
    weight = "700" if bold else "400"
    l.setStyleSheet(f"color:{color}; font-size:{size}px; font-weight:{weight}; background:transparent;")
    return l


# ─────────────────────────────────────────────────────────────
#  Toast notification
# ─────────────────────────────────────────────────────────────
class Toast(QLabel):
    def __init__(self, parent, message, kind="info"):
        super().__init__(message, parent)
        colors = {"info": ACCENT, "success": SUCCESS, "error": ERROR, "warn": WARN}
        c = colors.get(kind, ACCENT)
        self.setStyleSheet(f"""
            QLabel {{
                background: {c}22;
                color: {c};
                border: 1px solid {c}66;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.adjustSize()
        pw = parent.width()
        self.setFixedWidth(min(pw - 60, 480))
        self.move((pw - self.width()) // 2, parent.height() - 80)
        self.raise_()
        self.show()
        QTimer.singleShot(3200, self.deleteLater)


# ─────────────────────────────────────────────────────────────
#  Login screen
# ─────────────────────────────────────────────────────────────
class LoginScreen(QWidget):
    def __init__(self, on_login):
        super().__init__()
        self.on_login = on_login
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        # outer card
        c = card()
        c.setFixedSize(420, 560)
        cl = QVBoxLayout(c)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(0)

        # logo / icon area
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignCenter)
        icon_frame = QFrame()
        icon_frame.setFixedSize(64, 64)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {ACCENT}, stop:1 {ACCENT2});
                border-radius: 18px;
            }}
        """)
        icon_lbl = QLabel("₱", icon_frame)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"color:#0a0f1e; font-size:32px; font-weight:900; background:transparent;")
        icon_lbl.setGeometry(0, 0, 64, 64)
        logo_row.addWidget(icon_frame)
        cl.addLayout(logo_row)
        cl.addSpacing(24)

        cl.addWidget(lbl("Welcome back", 22, TEXT, bold=True, align=Qt.AlignCenter))
        cl.addSpacing(6)
        cl.addWidget(lbl("Sign in to your account", 13, MUTED, align=Qt.AlignCenter))
        cl.addSpacing(28)

        # account number
        cl.addWidget(lbl("Account Number", 13, MUTED))
        cl.addSpacing(6)
        self.acc_field = field("Enter your account number")
        cl.addWidget(self.acc_field)
        cl.addSpacing(16)

        # PIN
        cl.addWidget(lbl("PIN", 13, MUTED))
        cl.addSpacing(6)
        self.pin_field = field("Enter your PIN", echo_password=True)
        self.pin_field.returnPressed.connect(self._attempt_login)
        cl.addWidget(self.pin_field)
        cl.addSpacing(28)

        # login button
        self.login_btn = styled_btn("Sign In")
        self.login_btn.clicked.connect(self._attempt_login)
        cl.addWidget(self.login_btn)

        cl.addStretch()

        # error label
        self.err_lbl = lbl("", 12, ERROR, align=Qt.AlignCenter)
        self.err_lbl.setWordWrap(True)
        self.err_lbl.hide()
        cl.addWidget(self.err_lbl)

        root.addWidget(c, alignment=Qt.AlignCenter)

    def _attempt_login(self):
        acc_text = self.acc_field.text().strip()
        pin_text = self.pin_field.text().strip()

        if not acc_text or not pin_text:
            self._show_err("Please fill in both fields.")
            return

        if not acc_text.isdigit():
            self._show_err("Account number must be numeric.")
            return

        try:
            account = auth.verify_pin(int(acc_text), pin_text)
        except FileNotFoundError as e:
            self._show_err(str(e))
            return

        if account:
            self.err_lbl.hide()
            self.on_login(account)
        else:
            self._show_err("Invalid account number or PIN.")
            self.pin_field.clear()

    def _show_err(self, msg):
        self.err_lbl.setText(msg)
        self.err_lbl.show()


# ─────────────────────────────────────────────────────────────
#  Dashboard screen
# ─────────────────────────────────────────────────────────────
class DashboardScreen(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout
        self.account   = None
        self._build()

    # ── public API ──────────────────────────────
    def load_account(self, account: dict):
        self.account = account
        self._refresh()

    # ── builder ─────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(20)

        # ── top bar ──
        bar = QHBoxLayout()
        self.greeting = lbl("", 18, TEXT, bold=True)
        bar.addWidget(self.greeting)
        bar.addStretch()
        logout_btn = ghost_btn("Log out", ERROR)
        logout_btn.clicked.connect(self.on_logout)
        bar.addWidget(logout_btn)
        root.addLayout(bar)

        # ── balance card ──
        bal_card = QFrame()
        bal_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0369a1, stop:1 #4f46e5);
                border-radius: 20px;
            }}
        """)
        bal_card.setFixedHeight(150)
        bal_layout = QVBoxLayout(bal_card)
        bal_layout.setContentsMargins(32, 24, 32, 24)
        bal_lbl = lbl("Available Balance", 13, "#bae6fd")
        bal_layout.addWidget(bal_lbl)
        self.balance_lbl = lbl("", 36, "#ffffff", bold=True)
        bal_layout.addWidget(self.balance_lbl)
        self.acc_lbl = lbl("", 12, "#bae6fd")
        bal_layout.addWidget(self.acc_lbl)
        root.addWidget(bal_card)

        # ── action grid ──
        grid = QHBoxLayout()
        grid.setSpacing(14)

        self.deposit_btn  = self._action_tile("Deposit",  "↑", ACCENT)
        self.withdraw_btn = self._action_tile("Withdraw", "↓", ACCENT2)
        self.history_btn  = self._action_tile("History",  "≡", WARN)

        for btn in [self.deposit_btn, self.withdraw_btn, self.history_btn]:
            grid.addWidget(btn)

        self.deposit_btn.clicked.connect(self._do_deposit)
        self.withdraw_btn.clicked.connect(self._do_withdraw)
        self.history_btn.clicked.connect(self._do_history)

        root.addLayout(grid)

        # ── inline amount panel (hidden by default) ──
        self.amt_panel = card()
        self.amt_panel.hide()
        ap = QVBoxLayout(self.amt_panel)
        ap.setContentsMargins(28, 24, 28, 24)
        ap.setSpacing(12)

        self.amt_title = lbl("", 16, TEXT, bold=True)
        ap.addWidget(self.amt_title)

        self.amt_note = lbl("", 12, MUTED)
        self.amt_note.setWordWrap(True)
        ap.addWidget(self.amt_note)

        self.amt_field = field("Enter amount (Php)")
        ap.addWidget(self.amt_field)

        btn_row = QHBoxLayout()
        self.confirm_btn = styled_btn("Confirm")
        self.cancel_btn  = ghost_btn("Cancel")
        self.cancel_btn.clicked.connect(self._hide_amt_panel)
        btn_row.addWidget(self.confirm_btn)
        btn_row.addWidget(self.cancel_btn)
        ap.addLayout(btn_row)

        root.addWidget(self.amt_panel)

        # ── history panel (hidden by default) ──
        self.hist_panel = card()
        self.hist_panel.hide()
        hp = QVBoxLayout(self.hist_panel)
        hp.setContentsMargins(24, 20, 24, 20)
        hp.setSpacing(10)

        hist_top = QHBoxLayout()
        hist_top.addWidget(lbl("Transaction History", 15, TEXT, bold=True))
        hist_top.addStretch()
        close_hist = ghost_btn("Close", MUTED)
        close_hist.clicked.connect(self.hist_panel.hide)
        hist_top.addWidget(close_hist)
        hp.addLayout(hist_top)

        self.hist_text = QTextEdit()
        self.hist_text.setReadOnly(True)
        self.hist_text.setStyleSheet(f"""
            QTextEdit {{
                background: #0a0f1e;
                color: {TEXT};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 12px;
            }}
        """)
        self.hist_text.setFixedHeight(200)
        hp.addWidget(self.hist_text)
        root.addWidget(self.hist_panel)

        # ── receipt panel (hidden by default) ──
        self.rcpt_panel = card()
        self.rcpt_panel.hide()
        rp = QVBoxLayout(self.rcpt_panel)
        rp.setContentsMargins(24, 20, 24, 20)
        rp.setSpacing(10)

        rcpt_top = QHBoxLayout()
        rcpt_top.addWidget(lbl("Receipt", 15, TEXT, bold=True))
        rcpt_top.addStretch()
        close_rcpt = ghost_btn("Close", MUTED)
        close_rcpt.clicked.connect(self.rcpt_panel.hide)
        rcpt_top.addWidget(close_rcpt)
        rp.addLayout(rcpt_top)

        self.rcpt_text = QTextEdit()
        self.rcpt_text.setReadOnly(True)
        self.rcpt_text.setStyleSheet(f"""
            QTextEdit {{
                background: #0a0f1e;
                color: {SUCCESS};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 12px;
            }}
        """)
        self.rcpt_text.setFixedHeight(200)
        rp.addWidget(self.rcpt_text)
        root.addWidget(self.rcpt_panel)

        root.addStretch()

    def _action_tile(self, label, icon, color) -> QPushButton:
        btn = QPushButton(f"{icon}\n{label}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(90)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color}18;
                color: {color};
                border: 1.5px solid {color}55;
                border-radius: 16px;
                font-size: 22px;
                font-weight: 700;
            }}
            QPushButton:hover  {{ background: {color}30; border-color: {color}aa; }}
            QPushButton:pressed{{ background: {color}50; }}
        """)
        return btn

    # ── helpers ─────────────────────────────────
    def _refresh(self):
        self.greeting.setText(f"Account  #{self.account['accountNumber']}")
        self.balance_lbl.setText(f"Php {self.account['balance']:,.2f}")
        self.acc_lbl.setText(f"Account No. {self.account['accountNumber']}")

    def _hide_amt_panel(self):
        self.amt_panel.hide()
        self.rcpt_panel.hide()

    def _show_amt_panel(self, title, note, on_confirm):
        self.amt_title.setText(title)
        self.amt_note.setText(note)
        self.amt_field.clear()
        self.hist_panel.hide()
        self.rcpt_panel.hide()
        self.amt_panel.show()

        # reconnect confirm button
        try:
            self.confirm_btn.clicked.disconnect()
        except RuntimeError:
            pass
        self.confirm_btn.clicked.connect(on_confirm)

    # ── actions ─────────────────────────────────
    def _do_deposit(self):
        self._show_amt_panel(
            "Deposit Funds",
            "Enter the amount you wish to deposit into your account.",
            self._confirm_deposit,
        )

    def _confirm_deposit(self):
        txt = self.amt_field.text().strip()
        if not txt.replace(".", "", 1).isdigit():
            Toast(self, "Please enter a valid amount.", "error")
            return
        amount = float(txt)
        try:
            new_bal = auth.deposit(self.account["accountNumber"], amount, self.account["balance"])
            self.account["balance"] = new_bal
            self._refresh()
            self._hide_amt_panel()
            receipt = auth.build_receipt(self.account["accountNumber"], "Deposit", amount, new_bal)
            self.rcpt_text.setText(receipt)
            self.rcpt_panel.show()
            Toast(self, f"Deposited Php {amount:,.2f} successfully!", "success")
        except Exception as e:
            Toast(self, str(e), "error")

    def _do_withdraw(self):
        self._show_amt_panel(
            "Withdraw Funds",
            f"A service fee of Php {SERVICE_FEE:.2f} will be deducted in addition to your withdrawal amount.",
            self._confirm_withdraw,
        )

    def _confirm_withdraw(self):
        txt = self.amt_field.text().strip()
        if not txt.replace(".", "", 1).isdigit():
            Toast(self, "Please enter a valid amount.", "error")
            return
        amount = float(txt)
        try:
            new_bal = auth.withdraw(
                self.account["accountNumber"], amount,
                self.account["balance"], SERVICE_FEE
            )
            self.account["balance"] = new_bal
            self._refresh()
            self._hide_amt_panel()
            receipt = auth.build_receipt(self.account["accountNumber"], "Withdraw", amount, new_bal)
            self.rcpt_text.setText(receipt)
            self.rcpt_panel.show()
            Toast(self, f"Withdrew Php {amount:,.2f} successfully!", "success")
        except Exception as e:
            Toast(self, str(e), "error")

    def _do_history(self):
        self._hide_amt_panel()
        history = auth.get_transaction_history(self.account["accountNumber"])
        self.hist_text.setText(history if history else "No transactions found.")
        self.hist_panel.show()


# ─────────────────────────────────────────────────────────────
#  Main window  (holds both screens in a QStackedWidget)
# ─────────────────────────────────────────────────────────────
class ATMWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATM Simulator")
        self.setMinimumSize(880, 680)
        self._apply_global_style()

        central = QWidget()
        self.setCentralWidget(central)

        # gradient background
        central.setStyleSheet(f"background: {BG};")

        self.stack = QStackedWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.stack)

        self.login_screen    = LoginScreen(self._on_login)
        self.dashboard_screen = DashboardScreen(self._on_logout)

        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.dashboard_screen)
        self.stack.setCurrentWidget(self.login_screen)

    def _apply_global_style(self):
        self.setStyleSheet(f"""
            * {{ font-family: 'Segoe UI', 'SF Pro Display', sans-serif; }}
            QMainWindow {{ background: {BG}; }}
            QScrollBar:vertical {{
                background: {PANEL};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {MUTED};
                border-radius: 3px;
            }}
        """)

    def _on_login(self, account: dict):
        self.dashboard_screen.load_account(account)
        self.stack.setCurrentWidget(self.dashboard_screen)

    def _on_logout(self):
        self.stack.setCurrentWidget(self.login_screen)
        self.login_screen.acc_field.clear()
        self.login_screen.pin_field.clear()
        self.login_screen.err_lbl.hide()


# ─────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # dark palette so native widgets blend in
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
