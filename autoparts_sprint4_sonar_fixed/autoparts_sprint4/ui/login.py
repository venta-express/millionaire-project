"""
AutoParts Express - HU-01: Pantalla de Inicio de Sesión
Diseño: Dividida en dos mitades — ilustración izquierda / formulario derecha
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient, QPixmap, QPen

from utils.styles import COLORS
from utils.constants import FONT_FAMILY, APP_NAME, LABEL_ATENCION
from models.auth import iniciar_sesion


# ── Panel izquierdo (branding) ──────────────────────────────────────────────
_BRAND_TRANSPARENT = "background: transparent; border: none;"

class BrandPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(420)
        # Necesario para que paintEvent controle el fondo
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setStyleSheet("BrandPanel { background: transparent; }")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 60, 50, 60)
        layout.setSpacing(0)

        # Logo / ícono
        icon_label = QLabel("⚙")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setStyleSheet(_BRAND_TRANSPARENT + "color: rgba(255,255,255,0.9);")
        icon_label.setAlignment(Qt.AlignCenter)

        brand = QLabel("AutoParts")
        brand.setFont(QFont("Arial", 32, QFont.Bold))
        brand.setStyleSheet(_BRAND_TRANSPARENT + "color: white;")
        brand.setAlignment(Qt.AlignCenter)

        brand2 = QLabel("Express")
        brand2.setFont(QFont("Arial", 32, QFont.Bold))
        brand2.setStyleSheet(_BRAND_TRANSPARENT + "color: #FF6B2B;")
        brand2.setAlignment(Qt.AlignCenter)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background: rgba(255,255,255,0.25); border: none; margin: 8px 60px;")

        tagline = QLabel("Sistema de Gestión\nde Repuestos y Accesorios")
        tagline.setFont(QFont("Arial", 12))
        tagline.setStyleSheet(_BRAND_TRANSPARENT + "color: rgba(255,255,255,0.75);")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setWordWrap(True)

        layout.addStretch(2)
        layout.addWidget(icon_label)
        layout.addSpacing(8)
        layout.addWidget(brand)
        layout.addWidget(brand2)
        layout.addWidget(sep)
        layout.addWidget(tagline)
        layout.addStretch(3)

        # Features
        features = [
            ("●", "Control de Inventario"),
            ("●", "Facturación Rápida"),
            ("●", "Reportes Estratégicos"),
        ]
        for icon, text in features:
            row = QWidget()
            row.setStyleSheet(_BRAND_TRANSPARENT)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(20, 6, 20, 6)
            ico = QLabel(icon)
            ico.setFont(QFont("Arial", 10))
            ico.setStyleSheet(_BRAND_TRANSPARENT + "color: #FF6B2B;")
            lbl = QLabel(text)
            lbl.setFont(QFont("Arial", 12))
            lbl.setStyleSheet(_BRAND_TRANSPARENT + "color: rgba(255,255,255,0.85);")
            row_layout.addWidget(ico)
            row_layout.addSpacing(10)
            row_layout.addWidget(lbl)
            row_layout.addStretch()
            layout.addWidget(row)

        layout.addStretch(2)

        version = QLabel("v1.0 · Sprint 1")
        version.setFont(QFont("Arial", 10))
        version.setStyleSheet(_BRAND_TRANSPARENT + "color: rgba(255,255,255,0.4);")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#1A2942"))
        grad.setColorAt(1.0, QColor("#0D1B2E"))
        painter.fillRect(self.rect(), grad)
        # Círculo decorativo
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 107, 43, 25))
        painter.drawEllipse(-80, -80, 300, 300)
        painter.setBrush(QColor(255, 107, 43, 15))
        painter.drawEllipse(self.width() - 200, self.height() - 200, 350, 350)
        # Importante: NO llamar super() para evitar que Qt redibuje fondo blanco


# ── Campo de formulario con label flotante ──────────────────────────────────
class FormField(QWidget):
    def __init__(self, label: str, placeholder: str = "", is_password: bool = False):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl = QLabel(label)
        lbl.setFont(QFont(FONT_FAMILY, 11, QFont.DemiBold))
        lbl.setStyleSheet(f"color: {COLORS['text']}; letter-spacing: 0.3px;")

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setFixedHeight(46)
        if is_password:
            self.input.setEchoMode(QLineEdit.Password)

        layout.addWidget(lbl)
        layout.addWidget(self.input)

    def value(self) -> str:
        return self.input.text()

    def set_error(self, has_error: bool):
        self.input.setProperty("error", "true" if has_error else "false")
        self.input.style().unpolish(self.input)
        self.input.style().polish(self.input)


# ── Panel derecho (formulario) ──────────────────────────────────────────────
class LoginForm(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self._on_success = on_success
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignCenter)

        # Card central
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(420)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(26, 41, 66, 35))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(42, 44, 42, 44)
        layout.setSpacing(0)

        # Título
        title = QLabel("Bienvenido")
        title.setFont(QFont(FONT_FAMILY, 26, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['primary']};")

        subtitle = QLabel("Inicia sesión para continuar")
        subtitle.setFont(QFont(FONT_FAMILY, 13))
        subtitle.setStyleSheet(f"color: {COLORS['muted']};")
        subtitle.setContentsMargins(0, 4, 0, 0)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(32)

        # Campos
        self.f_user = FormField("Usuario", "Ingresa tu usuario")
        self.f_pass = FormField("Contraseña", "••••••••", is_password=True)
        self.f_pass.input.returnPressed.connect(self._do_login)

        layout.addWidget(self.f_user)
        layout.addSpacing(16)
        layout.addWidget(self.f_pass)
        layout.addSpacing(10)

        # Mensaje de error
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("label_error")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setContentsMargins(0, 0, 0, 0)
        self.lbl_error.hide()
        layout.addWidget(self.lbl_error)

        layout.addSpacing(24)

        # Botón
        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.setObjectName("btn_primary")
        self.btn_login.setFixedHeight(48)
        self.btn_login.setFont(QFont(FONT_FAMILY, 14, QFont.DemiBold))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._do_login)
        layout.addWidget(self.btn_login)

        layout.addSpacing(20)

        # Credenciales de demo
        hint = QLabel("Demo → usuario: <b>admin</b> · contraseña: <b>admin123</b>")
        hint.setFont(QFont(FONT_FAMILY, 11))
        hint.setStyleSheet(f"color: {COLORS['muted']}; padding: 10px 14px; "
                           "background: #F4F6FA; border-radius: 8px;")
        hint.setAlignment(Qt.AlignCenter)
        hint.setTextFormat(Qt.RichText)
        layout.addWidget(hint)

        outer.addWidget(card)

    # ── Lógica de login ─────────────────────────────────────────────────────
    def _do_login(self):
        username = self.f_user.value().strip()
        password = self.f_pass.value().strip()

        # Validación básica visual
        self.f_user.set_error(not username)
        self.f_pass.set_error(not password)
        if not username or not password:
            self._show_error("Por favor completa todos los campos.")
            return

        self.btn_login.setEnabled(False)
        self.btn_login.setText("Verificando…")

        # Pequeño delay para dar feedback visual
        QTimer.singleShot(300, lambda: self._process_login(username, password))

    def _process_login(self, username: str, password: str):
        ok, msg, usuario = iniciar_sesion(username, password)

        self.btn_login.setEnabled(True)
        self.btn_login.setText("Iniciar sesión")

        if ok:
            self.lbl_error.hide()
            self._on_success(usuario)
        else:
            self._show_error(msg)
            self._shake()

    def _show_error(self, msg: str):
        self.lbl_error.setText(f"⚠  {msg}")
        self.lbl_error.show()

    def _shake(self):
        """Animación de sacudida en el card cuando hay error."""
        card = self.findChild(QFrame, "card")
        if not card:
            return
        anim = QPropertyAnimation(card, b"pos")
        anim.setDuration(300)
        orig = card.pos()
        anim.setKeyValueAt(0.0,  orig)
        anim.setKeyValueAt(0.15, orig + QPoint(-8, 0))
        anim.setKeyValueAt(0.30, orig + QPoint(8, 0))
        anim.setKeyValueAt(0.45, orig + QPoint(-6, 0))
        anim.setKeyValueAt(0.60, orig + QPoint(6, 0))
        anim.setKeyValueAt(0.75, orig + QPoint(-3, 0))
        anim.setKeyValueAt(1.0,  orig)
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()
        self._anim = anim  # mantener referencia


# ── Ventana completa de login ───────────────────────────────────────────────
class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self._on_success = on_success
        self.setWindowTitle("AutoParts Express · Iniciar sesión")
        self.setMinimumSize(880, 600)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        brand = BrandPanel()
        brand.setFixedWidth(400)

        form = LoginForm(on_success=self._handle_success)
        form.setStyleSheet(f"background-color: {COLORS['surface']};")

        layout.addWidget(brand)
        layout.addWidget(form, 1)

    def _handle_success(self, usuario):
        self._on_success(usuario)
