"""
AutoParts Express - Ventana Principal con Sidebar
Sprint 3: Agrega módulos Reportes, Devoluciones y Promociones.
          Acceso por módulo controlado por rol.

Índices del QStackedWidget (deben coincidir con Sidebar):
  0 → HomeView
  1 → InventarioView
  2 → VentasView
  3 → ClientesView
  4 → ComprasView
  5 → UsuariosView
  6 → ReportesView      ← NUEVO Sprint 3
  7 → DevolucionesView  ← NUEVO Sprint 3
  8 → PromocionesView   ← NUEVO Sprint 3
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui  import QFont, QColor, QPainter, QLinearGradient

from utils.styles import COLORS
from utils.constants import FONT_FAMILY, APP_NAME, LABEL_ATENCION
from models.auth  import get_usuario_activo, cerrar_sesion

# ── Módulos Sprint 1 ──────────────────────────────────────────────────────────
from ui.inventario  import InventarioView
from ui.ventas      import VentasView

# ── Módulos Sprint 2 ──────────────────────────────────────────────────────────
from ui.clientes    import ClientesView
from ui.compras     import ComprasView
from ui.usuarios    import UsuariosView

# ── Módulos Sprint 3 ──────────────────────────────────────────────────────────
from ui.reportes    import ReportesView
from ui.devoluciones import DevolucionesView
from ui.promociones import PromocionesView


# ── Ítem de navegación ────────────────────────────────────────────────────────
class NavItem(QPushButton):
    """
    Botón de navegación del sidebar.
    Checkable para marcar el módulo activo visualmente.
    """
    def __init__(self, icon: str, label: str):
        super().__init__()
        self.setObjectName("btn_nav")
        self.setText(f"  {icon}  {label}")
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont(FONT_FAMILY, 13))
        self.setCheckable(True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    """
    Barra lateral de navegación con ítems filtrados por rol.

    Módulos visibles por rol:
      Gerencia:   todos (Inicio, Inventario, Ventas, Clientes, Compras,
                         Usuarios, Reportes, Devoluciones, Promociones)
      Vendedor:   Inicio, Ventas, Clientes, Promociones (solo ver)
      Inventario: Inicio, Inventario, Compras, Devoluciones
    """

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
        """Construye la barra lateral con ítems según el rol activo."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 24, 14, 20)
        layout.setSpacing(0)

        # ── Logo ──────────────────────────────────────────────────────────────
        logo = QLabel("⚙  AutoParts")
        logo.setFont(QFont(FONT_FAMILY, 15, QFont.Bold))
        logo.setStyleSheet("color: white; letter-spacing: 1px;")
        logo.setContentsMargins(10, 0, 0, 0)
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

        # ── Info del usuario ──────────────────────────────────────────────────
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

        # ── Etiqueta de sección ───────────────────────────────────────────────
        nav_label = QLabel("MÓDULOS")
        nav_label.setFont(QFont(FONT_FAMILY, 9, QFont.Bold))
        nav_label.setStyleSheet(
            "color: rgba(255,255,255,0.35); letter-spacing: 1.5px;"
        )
        nav_label.setContentsMargins(12, 0, 0, 0)
        layout.addWidget(nav_label)
        layout.addSpacing(6)

        # ── Definición de módulos con permisos por rol ────────────────────────
        # Formato: (icono, label, stack_index, roles_permitidos)
        MODULOS = [
            ("🏠", "Inicio",       0, ["Gerencia", "Vendedor", "Inventario"]),
            ("📦", "Inventario",   1, ["Gerencia", "Inventario"]),
            ("🧾", "Ventas",       2, ["Gerencia", "Vendedor"]),
            ("👥", "Clientes",     3, ["Gerencia", "Vendedor"]),
            ("🛒", "Compras",      4, ["Gerencia", "Inventario"]),
            ("🔐", "Usuarios",     5, ["Gerencia"]),
            ("📊", "Reportes",     6, ["Gerencia"]),
            ("↩", "Devoluciones", 7, ["Gerencia", "Inventario"]),
            ("🏷️", "Promociones",  8, ["Gerencia", "Vendedor"]),
        ]

        rol_actual = usuario.rol if usuario else ""

        for icon, label, idx, roles in MODULOS:
            if rol_actual not in roles:
                continue  # El usuario no tiene acceso a este módulo
            item = NavItem(icon, label)
            item.clicked.connect(lambda _, i=idx, btn=item: self._select(i, btn))
            self._nav_items.append(item)
            layout.addWidget(item)

        layout.addStretch()

        # ── Cerrar sesión ─────────────────────────────────────────────────────
        sep3 = QFrame()
        sep3.setFixedHeight(1)
        sep3.setStyleSheet("background: rgba(255,255,255,0.1);")
        layout.addWidget(sep3)
        layout.addSpacing(10)

        btn_logout = QPushButton("  ⎋  Cerrar sesión")
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

        # Seleccionamos Inicio por defecto
        if self._nav_items:
            self._select(0, self._nav_items[0])

    def _select(self, idx: int, btn: NavItem):
        """Actualiza el estado visual y navega al módulo."""
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
        """Fondo degradado del sidebar pintado con QPainter."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#1A2942"))
        grad.setColorAt(1.0, QColor("#0D1B2E"))
        painter.fillRect(self.rect(), grad)


# ── Dashboard de bienvenida ────────────────────────────────────────────────────
class HomeView(QWidget):
    """Vista de inicio con tarjetas de módulos y resumen de HU completadas."""

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        usuario = get_usuario_activo()
        nombre  = usuario.nombre if usuario else "Usuario"

        greeting = QLabel(f"¡Hola, {nombre}! 👋")
        greeting.setFont(QFont(FONT_FAMILY, 26, QFont.Bold))
        greeting.setStyleSheet(f"color: {COLORS['primary']};")

        sub = QLabel("Sistema de Gestión AutoParts Express · Sprint 3")
        sub.setFont(QFont(FONT_FAMILY, 13))
        sub.setStyleSheet(f"color: {COLORS['muted']};")

        layout.addWidget(greeting)
        layout.addWidget(sub)
        layout.addSpacing(10)

        # ── Tarjetas de módulos ───────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

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

        # Fila 1 de tarjetas
        for icon, title, sub_t, color in [
            ("📦", "Inventario",  "Productos y stock",   COLORS["primary"]),
            ("🧾", "Ventas",      "Facturación",         COLORS["accent"]),
            ("👥", "Clientes",    "Historial",           COLORS["success"]),
            ("🛒", "Compras",     "Pedidos",             "#8E44AD"),
        ]:
            cards_row.addWidget(stat_card(icon, title, sub_t, color))
        layout.addLayout(cards_row)

        cards_row2 = QHBoxLayout()
        cards_row2.setSpacing(12)
        for icon, title, sub_t, color in [
            ("📊", "Reportes",     "Análisis y exportación", "#2980B9"),
            ("↩", "Devoluciones", "A proveedores",           COLORS["warning"]),
            ("🏷️", "Promociones",  "Descuentos activos",      "#16A085"),
            ("🔐", "Usuarios",    "Control de acceso",       COLORS["danger"]),
        ]:
            cards_row2.addWidget(stat_card(icon, title, sub_t, color))
        layout.addLayout(cards_row2)

        # ── HU completadas ────────────────────────────────────────────────────
        sprint_lbl = QLabel("Sprint 3 — Historias completadas:")
        sprint_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.DemiBold))
        sprint_lbl.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(sprint_lbl)

        hus = [
            ("✅", "HU-09", "Reportes de ventas e inventario exportables a PDF/Excel"),
            ("✅", "HU-10", "Reporte de ventas por vendedor con filtro de período"),
            ("✅", "HU-11", "Devoluciones a proveedores con actualización de stock"),
            ("✅", "HU-12", "Configuración de promociones y descuentos automáticos"),
        ]
        for check, code, desc in hus:
            row = QLabel(f"{check}  <b>{code}</b> — {desc}")
            row.setFont(QFont(FONT_FAMILY, 12))
            row.setStyleSheet(f"color: {COLORS['text']}; margin-left: 8px;")
            row.setTextFormat(Qt.RichText)
            layout.addWidget(row)


# ── Ventana Principal ──────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    """
    Ventana principal: sidebar + QStackedWidget con todos los módulos.
    Los índices del stack son fijos y deben coincidir con MODULOS en Sidebar.
    """

    def __init__(self, on_logout):
        super().__init__()
        self._on_logout_cb = on_logout
        self.setWindowTitle("AutoParts Express · Sprint 3")
        self.setMinimumSize(1280, 720)
        self._setup_ui()

    def _setup_ui(self):
        """Construye sidebar + stack con todos los módulos."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── QStackedWidget (índices fijos, ver docstring de clase) ────────────
        self.stack = QStackedWidget()

        self.stack.addWidget(HomeView())          # 0
        self.stack.addWidget(InventarioView())    # 1
        self.stack.addWidget(VentasView())        # 2
        self.stack.addWidget(ClientesView())      # 3
        self.stack.addWidget(ComprasView())       # 4
        self.stack.addWidget(UsuariosView())      # 5
        self.stack.addWidget(ReportesView())      # 6 ← NUEVO
        self.stack.addWidget(DevolucionesView())  # 7 ← NUEVO
        self.stack.addWidget(PromocionesView())   # 8 ← NUEVO

        # ── Sidebar ────────────────────────────────────────────────────────
        sidebar = Sidebar(
            on_navigate=self.stack.setCurrentIndex,
            on_logout=self._handle_logout
        )

        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)

    def _handle_logout(self):
        """Limpia sesión y regresa al login."""
        cerrar_sesion()
        self._on_logout_cb()
