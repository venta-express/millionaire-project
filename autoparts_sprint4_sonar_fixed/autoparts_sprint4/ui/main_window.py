"""
AutoParts Express - Ventana Principal con Sidebar
Sprint 4: Agrega modulos Auditoria y Configuracion.

Indices del QStackedWidget:
  0  -> HomeView
  1  -> InventarioView
  2  -> VentasView
  3  -> ClientesView
  4  -> ComprasView
  5  -> UsuariosView
  6  -> ReportesView
  7  -> DevolucionesView
  8  -> PromocionesView
  9  -> AuditoriaWidget    NUEVO Sprint 4
  10 -> ConfiguracionWidget NUEVO Sprint 4
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui  import QFont, QColor, QPainter, QLinearGradient

from utils.styles import COLORS
from utils.constants import FONT_FAMILY, APP_NAME
from models.auth  import get_usuario_activo, cerrar_sesion

from ui.inventario   import InventarioView
from ui.ventas       import VentasView
from ui.clientes     import ClientesView
from ui.compras      import ComprasView
from ui.usuarios     import UsuariosView
from ui.reportes     import ReportesView
from ui.devoluciones import DevolucionesView
from ui.promociones  import PromocionesView
from ui.auditoria    import AuditoriaWidget
from ui.configuracion import ConfiguracionWidget


class NavItem(QPushButton):
    def __init__(self, icon: str, label: str):
        super().__init__()
        self.setObjectName("btn_nav")
        self.setText(f"  {icon}  {label}")
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont(FONT_FAMILY, 13))
        self.setCheckable(True)


class Sidebar(QWidget):
    def __init__(self, on_navigate, on_logout, usuario_actual):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(230)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setStyleSheet("Sidebar { background: transparent; }")
        self._nav_items: list = []
        self._on_navigate = on_navigate
        self.usuario_actual = usuario_actual
        self._setup_ui(on_logout)

    def _setup_ui(self, on_logout):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 24, 14, 20)
        layout.setSpacing(0)

        logo = QLabel("  AutoParts")
        logo.setFont(QFont(FONT_FAMILY, 15, QFont.Bold))
        logo.setStyleSheet("color: white; letter-spacing: 1px;")
        layout.addWidget(logo)

        express = QLabel("    Express")
        express.setFont(QFont(FONT_FAMILY, 15, QFont.Bold))
        express.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 1px;")
        layout.addWidget(express)

        layout.addSpacing(8)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.12);")
        layout.addWidget(sep)
        layout.addSpacing(16)

        usuario = get_usuario_activo()
        if usuario:
            uname = QLabel(usuario.nombre)
            uname.setFont(QFont(FONT_FAMILY, 12, QFont.DemiBold))
            uname.setStyleSheet("color: white;")
            uname.setContentsMargins(10, 0, 0, 0)
            uname.setWordWrap(True)
            rol_badge = QLabel(usuario.rol)
            rol_badge.setFont(QFont(FONT_FAMILY, 10))
            rol_badge.setStyleSheet(
                f"color: {COLORS['accent']}; background: rgba(255,107,43,0.15);"
                "border-radius: 4px; padding: 2px 10px; margin-left: 10px;"
            )
            layout.addWidget(uname)
            layout.addWidget(rol_badge)
            layout.addSpacing(16)

        nav_label = QLabel("MODULOS")
        nav_label.setFont(QFont(FONT_FAMILY, 9, QFont.Bold))
        nav_label.setStyleSheet("color: rgba(255,255,255,0.35); letter-spacing: 1.5px;")
        nav_label.setContentsMargins(12, 0, 0, 0)
        layout.addWidget(nav_label)
        layout.addSpacing(6)

        MODULOS = [
            ("", "Inicio",         0,  ["Gerencia", "Vendedor", "Inventario"]),
            ("", "Inventario",     1,  ["Gerencia", "Inventario"]),
            ("", "Ventas",         2,  ["Gerencia", "Vendedor"]),
            ("", "Clientes",       3,  ["Gerencia", "Vendedor"]),
            ("", "Compras",        4,  ["Gerencia", "Inventario"]),
            ("", "Usuarios",       5,  ["Gerencia"]),
            ("", "Reportes",       6,  ["Gerencia"]),
            ("", "Devoluciones",   7,  ["Gerencia", "Inventario"]),
            ("", "Promociones",    8,  ["Gerencia", "Vendedor"]),
            ("", "Auditoria",      9,  ["Gerencia"]),
            ("", "Configuracion",  10, ["Gerencia"]),
        ]

        rol_actual = usuario.rol if usuario else ""
        for icon, label, idx, roles in MODULOS:
            if rol_actual not in roles:
                continue
            item = NavItem(icon, label)
            item.clicked.connect(lambda _, i=idx, btn=item: self._select(i, btn))
            self._nav_items.append(item)
            layout.addWidget(item)

        layout.addStretch()

        sep3 = QFrame()
        sep3.setFixedHeight(1)
        sep3.setStyleSheet("background: rgba(255,255,255,0.1);")
        layout.addWidget(sep3)
        layout.addSpacing(10)

        btn_logout = QPushButton("  Cerrar sesion")
        btn_logout.setObjectName("btn_nav")
        btn_logout.setFixedHeight(44)
        btn_logout.setFont(QFont(FONT_FAMILY, 12))
        btn_logout.setStyleSheet(
            "QPushButton { color: rgba(255,107,43,0.8); background: transparent;"
            "border: none; text-align: left; padding: 0 8px; border-radius: 8px; }"
            "QPushButton:hover { background: rgba(231,76,60,0.15); color: #FF6B2B; }"
        )
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.clicked.connect(on_logout)
        layout.addWidget(btn_logout)

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


class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        usuario = get_usuario_activo()
        nombre  = usuario.nombre if usuario else "Usuario"

        greeting = QLabel(f"Hola, {nombre}!")
        greeting.setFont(QFont(FONT_FAMILY, 26, QFont.Bold))
        greeting.setStyleSheet(f"color: {COLORS['primary']};")

        sub = QLabel("Sistema de Gestion AutoParts Express - Sprint 4")
        sub.setFont(QFont(FONT_FAMILY, 13))
        sub.setStyleSheet(f"color: {COLORS['muted']};")

        layout.addWidget(greeting)
        layout.addWidget(sub)
        layout.addSpacing(10)

        def stat_card(icon, title, subtitle, color):
            card = QFrame()
            card.setObjectName("card")
            card.setFixedHeight(110)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(18, 16, 18, 16)
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont(FONT_FAMILY, 26))
            icon_lbl.setStyleSheet(
                f"background: {color}22; border-radius: 10px;"
                f"padding: 6px; color: {color};"
            )
            icon_lbl.setFixedSize(54, 54)
            icon_lbl.setAlignment(Qt.AlignCenter)
            text_col = QVBoxLayout()
            text_col.setSpacing(2)
            t = QLabel(title)
            t.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
            t.setStyleSheet(f"color: {COLORS['primary']};")
            s = QLabel(subtitle)
            s.setFont(QFont(FONT_FAMILY, 10))
            s.setStyleSheet(f"color: {COLORS['muted']};")
            text_col.addWidget(t)
            text_col.addWidget(s)
            cl.addWidget(icon_lbl)
            cl.addSpacing(12)
            cl.addLayout(text_col)
            cl.addStretch()
            return card

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        for icon, title, sub_t, color in [
            ("INV", "Inventario",  "Productos y stock",   COLORS["primary"]),
            ("VTA", "Ventas",      "Facturacion",         COLORS["accent"]),
            ("CLI", "Clientes",    "Historial",           COLORS["success"]),
            ("COM", "Compras",     "Pedidos",             "#8E44AD"),
        ]:
            cards_row.addWidget(stat_card(icon, title, sub_t, color))
        layout.addLayout(cards_row)

        cards_row2 = QHBoxLayout()
        cards_row2.setSpacing(12)
        for icon, title, sub_t, color in [
            ("RPT", "Reportes",     "Analisis y exportacion", "#2980B9"),
            ("DEV", "Devoluciones", "A proveedores",           COLORS["warning"]),
            ("AUD", "Auditoria",    "Log del sistema",         "#E74C3C"),
            ("CFG", "Configuracion","Parametros globales",     "#7F8C8D"),
        ]:
            cards_row2.addWidget(stat_card(icon, title, sub_t, color))
        layout.addLayout(cards_row2)

        sprint_lbl = QLabel("Sprint 4 - Historias completadas:")
        sprint_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.DemiBold))
        sprint_lbl.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(sprint_lbl)

        hus = [
            ("OK", "Sprint 4", "Integracion completa con base de datos PostgreSQL"),
            ("OK", "Sprint 4", "Panel de auditoria de acciones del sistema"),
            ("OK", "Sprint 4", "Configuracion global de la empresa y prefijos"),
            ("OK", "Sprint 4", "Backup de base de datos desde la interfaz"),
            ("OK", "Sprint 4", "Schema acumulativo Sprint 1+2+3+4 sin errores de encoding"),
        ]
        for check, code, desc in hus:
            row = QLabel(f"{check}  {code} - {desc}")
            row.setFont(QFont(FONT_FAMILY, 12))
            row.setStyleSheet(f"color: {COLORS['text']}; margin-left: 8px;")
            layout.addWidget(row)


class MainWindow(QMainWindow):
    def __init__(self, on_logout):
        super().__init__()
        self._on_logout_cb = on_logout
        self.setWindowTitle("AutoParts Express - Sprint 4")
        self.setMinimumSize(1280, 720)
        self._usuario_actual = get_usuario_activo()
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.addWidget(HomeView())                                              # 0
        self.stack.addWidget(InventarioView())                                        # 1
        self.stack.addWidget(VentasView())                                            # 2
        self.stack.addWidget(ClientesView())                                          # 3
        self.stack.addWidget(ComprasView())                                           # 4
        self.stack.addWidget(UsuariosView())                                          # 5
        self.stack.addWidget(ReportesView())                                          # 6
        self.stack.addWidget(DevolucionesView())                                      # 7
        self.stack.addWidget(PromocionesView())                                       # 8
        self.stack.addWidget(AuditoriaWidget(self._usuario_actual))                   # 9  NUEVO
        self.stack.addWidget(ConfiguracionWidget(self._usuario_actual))               # 10 NUEVO

        sidebar = Sidebar(
            on_navigate=self.stack.setCurrentIndex,
            on_logout=self._handle_logout,
            usuario_actual=self._usuario_actual
        )

        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)

    def _handle_logout(self):
        cerrar_sesion()
        self._on_logout_cb()
