"""
AutoParts Express - Ventana Principal con Sidebar
Contiene navegación y carga los módulos del Sprint 1
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QSizePolicy,
    QSpacerItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient, QIcon

from utils.styles import COLORS
from models.auth import get_usuario_activo, cerrar_sesion
from ui.inventario import InventarioView
from ui.ventas import VentasView


# ── Ítem de navegación en sidebar ───────────────────────────────────────────
class NavItem(QPushButton):
    def __init__(self, icon: str, label: str):
        super().__init__()
        self.setObjectName("btn_nav")
        self.setText(f"  {icon}  {label}")
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 13))
        self.setCheckable(True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    def __init__(self, on_navigate, on_logout):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(230)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setStyleSheet("Sidebar { background: transparent; }")
        self._nav_items: list[NavItem] = []
        self._on_navigate = on_navigate
        self._setup_ui(on_logout)

    def _setup_ui(self, on_logout):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 24, 14, 20)
        layout.setSpacing(0)

        # Logo
        logo = QLabel("⚙  AutoParts")
        logo.setFont(QFont("Segoe UI", 15, QFont.Bold))
        logo.setStyleSheet("color: white; letter-spacing: 1px;")
        logo.setContentsMargins(10, 0, 0, 0)
        layout.addWidget(logo)

        express = QLabel("    Express")
        express.setFont(QFont("Segoe UI", 15, QFont.Bold))
        express.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 1px;")
        layout.addWidget(express)

        layout.addSpacing(8)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.12);")
        layout.addWidget(sep)
        layout.addSpacing(16)

        # Info del usuario
        usuario = get_usuario_activo()
        if usuario:
            uname = QLabel(usuario.nombre)
            uname.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
            uname.setStyleSheet("color: white;")
            uname.setContentsMargins(10, 0, 0, 0)
            uname.setWordWrap(True)

            rol_badge = QLabel(usuario.rol)
            rol_badge.setFont(QFont("Segoe UI", 10))
            rol_badge.setStyleSheet(
                f"color: {COLORS['accent']}; background: rgba(255,107,43,0.15);"
                "border-radius: 4px; padding: 2px 10px; margin-left: 10px;"
            )
            layout.addWidget(uname)
            layout.addWidget(rol_badge)
            layout.addSpacing(16)

        # Sección nav label
        nav_label = QLabel("MÓDULOS")
        nav_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        nav_label.setStyleSheet("color: rgba(255,255,255,0.35); letter-spacing: 1.5px;")
        nav_label.setContentsMargins(12, 0, 0, 0)
        layout.addWidget(nav_label)
        layout.addSpacing(6)

        # Items de navegación
        menus = [
            ("🏠", "Inicio",       0),
            ("📦", "Inventario",   1),
            ("🧾", "Ventas",       2),
        ]
        # Sprint 2+ (deshabilitados visualmente)
        next_sprint = [
            ("👥", "Clientes"),
            ("🛒", "Compras"),
            ("📊", "Reportes"),
        ]

        for icon, label, idx in menus:
            item = NavItem(icon, label)
            item.clicked.connect(lambda _, i=idx, btn=item: self._select(i, btn))
            self._nav_items.append(item)
            layout.addWidget(item)

        layout.addSpacing(10)
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background: rgba(255,255,255,0.08);")
        layout.addWidget(sep2)
        layout.addSpacing(6)

        coming = QLabel("PRÓXIMOS SPRINTS")
        coming.setFont(QFont("Segoe UI", 9, QFont.Bold))
        coming.setStyleSheet("color: rgba(255,255,255,0.25); letter-spacing: 1.5px;")
        coming.setContentsMargins(12, 0, 0, 0)
        layout.addWidget(coming)
        layout.addSpacing(6)

        for icon, label in next_sprint:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("btn_nav")
            btn.setFixedHeight(44)
            btn.setEnabled(False)
            btn.setFont(QFont("Segoe UI", 13))
            btn.setStyleSheet(
                "QPushButton { color: rgba(255,255,255,0.2); background: transparent;"
                "border: none; text-align: left; padding: 0 8px; border-radius: 8px; }"
            )
            layout.addWidget(btn)

        layout.addStretch()

        # Cerrar sesión
        sep3 = QFrame()
        sep3.setFixedHeight(1)
        sep3.setStyleSheet("background: rgba(255,255,255,0.1);")
        layout.addWidget(sep3)
        layout.addSpacing(10)

        btn_logout = QPushButton("  ⎋  Cerrar sesión")
        btn_logout.setObjectName("btn_nav")
        btn_logout.setFixedHeight(44)
        btn_logout.setFont(QFont("Segoe UI", 12))
        btn_logout.setStyleSheet(
            "QPushButton { color: rgba(255,107,43,0.8); background: transparent;"
            "border: none; text-align: left; padding: 0 8px; border-radius: 8px; }"
            "QPushButton:hover { background: rgba(231,76,60,0.15); color: #FF6B2B; }"
        )
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.clicked.connect(on_logout)
        layout.addWidget(btn_logout)

        # Seleccionar Inicio por defecto
        if self._nav_items:
            self._select(0, self._nav_items[0])

    def _select(self, idx: int, btn: NavItem):
        for item in self._nav_items:
            item.setChecked(False)
            item.setProperty("active", "false")
            item.style().unpolish(item)
            item.style().polish(item)
        btn.setChecked(True)
        btn.setProperty("active", "true")
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        self._on_navigate(idx)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#1A2942"))
        grad.setColorAt(1.0, QColor("#0D1B2E"))
        painter.fillRect(self.rect(), grad)
        # NO llamar super() para evitar repintado blanco por stylesheet global


# ── Vista de Inicio (Dashboard simple) ──────────────────────────────────────
class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        usuario = get_usuario_activo()
        nombre = usuario.nombre if usuario else "Usuario"

        greeting = QLabel(f"¡Hola, {nombre}! 👋")
        greeting.setFont(QFont("Segoe UI", 26, QFont.Bold))
        greeting.setStyleSheet(f"color: {COLORS['primary']};")

        sub = QLabel("Sistema de Gestión AutoParts Express · Sprint 1")
        sub.setFont(QFont("Segoe UI", 13))
        sub.setStyleSheet(f"color: {COLORS['muted']};")

        layout.addWidget(greeting)
        layout.addWidget(sub)
        layout.addSpacing(10)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        def stat_card(icon, title, subtitle, color):
            card = QFrame()
            card.setObjectName("card")
            card.setFixedHeight(120)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(20, 20, 20, 20)
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI", 28))
            icon_lbl.setStyleSheet(
                f"background: {color}22; border-radius: 12px;"
                f"padding: 8px; color: {color};"
            )
            icon_lbl.setFixedSize(60, 60)
            icon_lbl.setAlignment(Qt.AlignCenter)
            text_col = QVBoxLayout()
            text_col.setSpacing(3)
            t = QLabel(title)
            t.setFont(QFont("Segoe UI", 16, QFont.Bold))
            t.setStyleSheet(f"color: {COLORS['primary']};")
            s = QLabel(subtitle)
            s.setFont(QFont("Segoe UI", 11))
            s.setStyleSheet(f"color: {COLORS['muted']};")
            text_col.addWidget(t)
            text_col.addWidget(s)
            cl.addWidget(icon_lbl)
            cl.addSpacing(14)
            cl.addLayout(text_col)
            cl.addStretch()
            return card

        cards_row.addWidget(stat_card("📦", "Inventario", "Gestión de productos", COLORS["primary"]))
        cards_row.addWidget(stat_card("🧾", "Ventas", "Registro y facturación", COLORS["accent"]))
        cards_row.addWidget(stat_card("🔒", "Seguridad", "Control de acceso activo", COLORS["success"]))
        layout.addLayout(cards_row)

        sprint_lbl = QLabel("Sprint 1 — Módulos disponibles:")
        sprint_lbl.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        sprint_lbl.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(sprint_lbl)

        hus = [
            ("✅", "HU-01", "Inicio de Sesión seguro con roles"),
            ("✅", "HU-02", "Registro y gestión de productos en inventario"),
            ("✅", "HU-03", "Búsqueda y filtrado en tiempo real"),
            ("✅", "HU-04", "Registro de ventas y emisión de facturas"),
        ]
        for check, code, desc in hus:
            row = QLabel(f"{check}  <b>{code}</b> — {desc}")
            row.setFont(QFont("Segoe UI", 12))
            row.setStyleSheet(f"color: {COLORS['text']}; margin-left: 8px;")
            row.setTextFormat(Qt.RichText)
            layout.addWidget(row)


# ── Ventana principal ────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self, on_logout):
        super().__init__()
        self._on_logout_cb = on_logout
        self.setWindowTitle("AutoParts Express · Sistema de Gestión")
        self.setMinimumSize(1200, 720)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Stack de páginas
        self.stack = QStackedWidget()
        self.stack.addWidget(HomeView())       # 0
        self.stack.addWidget(InventarioView()) # 1
        self.stack.addWidget(VentasView())     # 2

        sidebar = Sidebar(
            on_navigate=self.stack.setCurrentIndex,
            on_logout=self._handle_logout
        )

        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)

    def _handle_logout(self):
        cerrar_sesion()
        self._on_logout_cb()
