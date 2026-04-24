"""
AutoParts Express - Ventana Principal con Sidebar
Sprint 2: Se agregan módulos Clientes, Compras y Usuarios al sidebar.
          Los módulos visibles cambian según el rol del usuario autenticado.

Estructura:
  - Sidebar: navegación lateral con ítems según rol
  - QStackedWidget: área de contenido que muestra un módulo a la vez
  - HomeView: dashboard de bienvenida con resumen de sprint
"""

# Widgets de layout y contenedores
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QSizePolicy,
    QSpacerItem
)

# Clases de comportamiento, tipografía y gráficos
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient, QIcon

# Paleta de colores de la aplicación
from utils.styles import COLORS

# Modelo de autenticación para obtener el usuario activo y cerrar sesión
from models.auth import get_usuario_activo, cerrar_sesion

# Módulos de UI del Sprint 1 (sin cambios)
from ui.inventario import InventarioView
from ui.ventas import VentasView

# Módulos de UI nuevos del Sprint 2
from ui.clientes import ClientesView
from ui.compras import ComprasView
from ui.usuarios import UsuariosView


# ── Ítem de navegación en sidebar ─────────────────────────────────────────────
class NavItem(QPushButton):
    """
    Botón de navegación del sidebar.
    Es checkable (puede estar activo/inactivo) y muestra ícono + etiqueta.
    """

    def __init__(self, icon: str, label: str):
        super().__init__()
        self.setObjectName("btn_nav")   # ID para los estilos del APP_STYLE
        self.setText(f"  {icon}  {label}")
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)  # Cursor de mano al pasar el mouse
        self.setFont(QFont("Segoe UI", 13))
        self.setCheckable(True)  # Permite marcar el ítem activo visualmente


# ── Sidebar ────────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    """
    Barra lateral de navegación.
    Muestra solo los módulos a los que el usuario tiene acceso según su rol:
      - Gerencia:   Inicio, Inventario, Ventas, Clientes, Compras, Usuarios
      - Vendedor:   Inicio, Ventas, Clientes
      - Inventario: Inicio, Inventario, Compras
    """

    def __init__(self, on_navigate, on_logout):
        """
        Parámetros:
            on_navigate: callback(index: int) que cambia el módulo visible
            on_logout:   callback() que cierra sesión y vuelve al login
        """
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(230)                              # Ancho fijo del sidebar
        self.setAttribute(Qt.WA_StyledBackground, False)    # Fondo manejado en paintEvent
        self.setStyleSheet("Sidebar { background: transparent; }")

        self._nav_items: list[NavItem] = []   # Lista de ítems de navegación activos
        self._on_navigate = on_navigate        # Callback de navegación

        self._setup_ui(on_logout)  # Construimos la interfaz

    def _setup_ui(self, on_logout):
        """Construye el contenido del sidebar según el rol del usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 24, 14, 20)
        layout.setSpacing(0)

        # ── Logo ────────────────────────────────────────────────────────────
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

        # Separador decorativo después del logo
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.12);")
        layout.addWidget(sep)
        layout.addSpacing(16)

        # ── Info del usuario logueado ────────────────────────────────────────
        usuario = get_usuario_activo()
        if usuario:
            # Nombre del usuario en blanco
            uname = QLabel(usuario.nombre)
            uname.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
            uname.setStyleSheet("color: white;")
            uname.setContentsMargins(10, 0, 0, 0)
            uname.setWordWrap(True)

            # Badge con el nombre del rol en color acento
            rol_badge = QLabel(usuario.rol)
            rol_badge.setFont(QFont("Segoe UI", 10))
            rol_badge.setStyleSheet(
                f"color: {COLORS['accent']}; background: rgba(255,107,43,0.15);"
                "border-radius: 4px; padding: 2px 10px; margin-left: 10px;"
            )
            layout.addWidget(uname)
            layout.addWidget(rol_badge)
            layout.addSpacing(16)

        # ── Etiqueta de sección ───────────────────────────────────────────────
        nav_label = QLabel("MÓDULOS")
        nav_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        nav_label.setStyleSheet("color: rgba(255,255,255,0.35); letter-spacing: 1.5px;")
        nav_label.setContentsMargins(12, 0, 0, 0)
        layout.addWidget(nav_label)
        layout.addSpacing(6)

        # ── Definición de módulos según rol ──────────────────────────────────
        # Formato: (icono, etiqueta, índice en el QStackedWidget)
        # El índice coincide con el orden en que se agregan los widgets al stack
        # en MainWindow._setup_ui()
        todos_los_menus = [
            ("🏠", "Inicio",       0, ["Gerencia", "Vendedor", "Inventario"]),
            ("📦", "Inventario",   1, ["Gerencia", "Inventario"]),
            ("🧾", "Ventas",       2, ["Gerencia", "Vendedor"]),
            ("👥", "Clientes",     3, ["Gerencia", "Vendedor"]),
            ("🛒", "Compras",      4, ["Gerencia", "Inventario"]),
            ("🔐", "Usuarios",     5, ["Gerencia"]),               # Solo Gerencia
        ]

        # Filtramos los módulos según el rol del usuario activo
        rol_actual = usuario.rol if usuario else ""
        menus_visibles = [
            (icon, label, idx)
            for icon, label, idx, roles in todos_los_menus
            if rol_actual in roles
        ]

        # Creamos un NavItem por cada módulo visible
        for icon, label, idx in menus_visibles:
            item = NavItem(icon, label)
            # Usamos valores por defecto en el lambda para evitar el closure problem
            item.clicked.connect(lambda _, i=idx, btn=item: self._select(i, btn))
            self._nav_items.append(item)
            layout.addWidget(item)

        layout.addSpacing(10)

        # Separador antes de "Próximos Sprints"
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background: rgba(255,255,255,0.08);")
        layout.addWidget(sep2)
        layout.addSpacing(6)

        # Etiqueta para módulos futuros
        coming = QLabel("PRÓXIMOS SPRINTS")
        coming.setFont(QFont("Segoe UI", 9, QFont.Bold))
        coming.setStyleSheet("color: rgba(255,255,255,0.25); letter-spacing: 1.5px;")
        coming.setContentsMargins(12, 0, 0, 0)
        layout.addWidget(coming)
        layout.addSpacing(6)

        # Módulos del Sprint 3 (deshabilitados visualmente)
        sprint3 = [
            ("📊", "Reportes"),
        ]
        for icon, label in sprint3:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("btn_nav")
            btn.setFixedHeight(44)
            btn.setEnabled(False)  # No clickeable
            btn.setFont(QFont("Segoe UI", 13))
            btn.setStyleSheet(
                "QPushButton { color: rgba(255,255,255,0.2); background: transparent;"
                "border: none; text-align: left; padding: 0 8px; border-radius: 8px; }"
            )
            layout.addWidget(btn)

        layout.addStretch()  # Empuja el botón de logout hacia abajo

        # ── Botón de cerrar sesión ────────────────────────────────────────────
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

        # Seleccionamos "Inicio" como módulo activo por defecto al iniciar
        if self._nav_items:
            self._select(0, self._nav_items[0])

    def _select(self, idx: int, btn: NavItem):
        """
        Actualiza el estado visual de los ítems de navegación y
        llama al callback para cambiar el módulo visible en el stack.
        """
        # Desactivamos todos los ítems
        for item in self._nav_items:
            item.setChecked(False)
            item.setProperty("active", "false")
            item.style().unpolish(item)  # Forzamos re-aplicación de estilos
            item.style().polish(item)

        # Activamos el ítem seleccionado
        btn.setChecked(True)
        btn.setProperty("active", "true")
        btn.style().unpolish(btn)
        btn.style().polish(btn)

        # Notificamos al MainWindow para cambiar el widget visible
        self._on_navigate(idx)

    def paintEvent(self, event):
        """
        Renderizamos el fondo degradado del sidebar manualmente.
        Usamos QPainter en lugar de stylesheets para el degradado
        ya que QSS no soporta gradientes en paintEvent implícito.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Degradado vertical de azul oscuro a casi negro
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#1A2942"))  # Azul marino arriba
        grad.setColorAt(1.0, QColor("#0D1B2E"))  # Casi negro abajo

        painter.fillRect(self.rect(), grad)
        # No llamamos a super() para evitar que el fondo blanco del stylesheet pise el degradado


# ── Vista de Inicio (Dashboard) ────────────────────────────────────────────────
class HomeView(QWidget):
    """
    Vista de bienvenida que muestra tarjetas de los módulos disponibles
    y el listado de historias de usuario completadas en cada sprint.
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        # Obtenemos el nombre del usuario para el saludo personalizado
        usuario = get_usuario_activo()
        nombre = usuario.nombre if usuario else "Usuario"

        # Saludo principal
        greeting = QLabel(f"¡Hola, {nombre}! 👋")
        greeting.setFont(QFont("Segoe UI", 26, QFont.Bold))
        greeting.setStyleSheet(f"color: {COLORS['primary']};")

        # Subtítulo con versión del sprint
        sub = QLabel("Sistema de Gestión AutoParts Express · Sprint 2")
        sub.setFont(QFont("Segoe UI", 13))
        sub.setStyleSheet(f"color: {COLORS['muted']};")

        layout.addWidget(greeting)
        layout.addWidget(sub)
        layout.addSpacing(10)

        # ── Tarjetas de módulos ───────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        def stat_card(icon, title, subtitle, color):
            """Helper que crea una tarjeta de módulo con ícono y texto."""
            card = QFrame()
            card.setObjectName("card")
            card.setFixedHeight(120)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(20, 20, 20, 20)

            # Ícono con fondo semitransparente del color del módulo
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI", 28))
            icon_lbl.setStyleSheet(
                f"background: {color}22; border-radius: 12px;"
                f"padding: 8px; color: {color};"
            )
            icon_lbl.setFixedSize(60, 60)
            icon_lbl.setAlignment(Qt.AlignCenter)

            # Texto: título grande + subtítulo
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

        # Tarjetas de los 5 módulos activos en Sprint 2
        cards_row.addWidget(stat_card("📦", "Inventario", "Gestión de productos",      COLORS["primary"]))
        cards_row.addWidget(stat_card("🧾", "Ventas",     "Registro y facturación",    COLORS["accent"]))
        cards_row.addWidget(stat_card("👥", "Clientes",   "Historial de compras",      COLORS["success"]))
        cards_row.addWidget(stat_card("🛒", "Compras",    "Pedidos a proveedores",     "#8E44AD"))
        cards_row.addWidget(stat_card("🔐", "Usuarios",   "Gestión de accesos",        "#E74C3C"))
        layout.addLayout(cards_row)

        # ── Historias de usuario completadas ──────────────────────────────────
        sprint_lbl = QLabel("Sprint 2 — Historias de usuario completadas:")
        sprint_lbl.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        sprint_lbl.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(sprint_lbl)

        # Lista de HU del Sprint 2 con sus descripciones
        hus = [
            ("✅", "HU-05", "Alertas automáticas de stock mínimo"),
            ("✅", "HU-06", "Gestión de pedidos a proveedores"),
            ("✅", "HU-07", "Historial de compras de clientes"),
            ("✅", "HU-08", "Gestión de usuarios y roles (solo Gerencia)"),
            # HU del Sprint 1 (mantenidas)
            ("✅", "HU-01", "Inicio de sesión seguro con roles"),
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


# ── Ventana Principal ──────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.
    Combina el Sidebar de navegación con el QStackedWidget de módulos.
    El índice del stack debe coincidir con los índices definidos en Sidebar.
    """

    def __init__(self, on_logout):
        """
        Parámetros:
            on_logout: callback() llamado al cerrar sesión; regresa al login
        """
        super().__init__()
        self._on_logout_cb = on_logout  # Guardamos el callback de logout
        self.setWindowTitle("AutoParts Express · Sistema de Gestión · Sprint 2")
        self.setMinimumSize(1200, 720)
        self._setup_ui()

    def _setup_ui(self):
        """
        Construye el layout principal: sidebar a la izquierda,
        QStackedWidget con todos los módulos a la derecha.
        El orden de addWidget al stack define los índices de navegación.
        """
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── QStackedWidget: un widget por módulo ─────────────────────────────
        self.stack = QStackedWidget()

        # Índice 0: Dashboard de bienvenida
        self.stack.addWidget(HomeView())

        # Índice 1: Módulo de Inventario (Sprint 1)
        self.stack.addWidget(InventarioView())

        # Índice 2: Módulo de Ventas (Sprint 1)
        self.stack.addWidget(VentasView())

        # Índice 3: Módulo de Clientes (Sprint 2 - nuevo)
        self.stack.addWidget(ClientesView())

        # Índice 4: Módulo de Compras (Sprint 2 - nuevo)
        self.stack.addWidget(ComprasView())

        # Índice 5: Módulo de Usuarios (Sprint 2 - nuevo, solo Gerencia)
        self.stack.addWidget(UsuariosView())

        # ── Sidebar ────────────────────────────────────────────────────────
        sidebar = Sidebar(
            on_navigate=self.stack.setCurrentIndex,  # Cambia el módulo visible
            on_logout=self._handle_logout
        )

        # Sidebar fijo a la izquierda, stack ocupa el resto (factor 1)
        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)

    def _handle_logout(self):
        """
        Limpia la sesión activa y llama al callback de logout.
        El callback (definido en main.py) cierra esta ventana y muestra el login.
        """
        cerrar_sesion()          # Limpiamos _sesion_activa en el modelo
        self._on_logout_cb()     # Notificamos a App para redirigir al login
