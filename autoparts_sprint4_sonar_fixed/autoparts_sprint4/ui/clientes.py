"""
AutoParts Express - Módulo de Clientes
HU-07: Historial de Compras de Clientes (Sprint 2)

Permite al vendedor buscar un cliente por nombre o cédula
y consultar el listado completo de sus facturas anteriores
con fecha, productos comprados y total de cada compra.
"""

# Widgets de layout y contenedores principales
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QFrame, QSplitter, QHeaderView, QAbstractItemView,
    QScrollArea, QGroupBox, QMessageBox
)

# Clases para tipografía, alineación y comportamientos de Qt
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

# Paleta de colores compartida de la aplicación
from utils.styles import COLORS
from utils.constants import FONT_FAMILY, APP_NAME, LABEL_ATENCION

# Funciones del modelo de ventas para buscar clientes e historial
from models.ventas import buscar_clientes_historial, historial_cliente


class ClientesView(QWidget):
    """
    Vista principal del módulo de Clientes.
    Composición:
      - Barra superior con título y campo de búsqueda
      - Panel izquierdo: tabla de clientes encontrados
      - Panel derecho: historial de facturas del cliente seleccionado
    """

    def __init__(self):
        super().__init__()
        # Color de fondo general de la vista
        self.setStyleSheet("background-color: #F4F6FA;")

        # Guardamos el ID del cliente actualmente seleccionado
        self._cliente_id_seleccionado: int | None = None

        # Timer para búsqueda diferida (evita consultas en cada tecla)
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)      # Solo dispara una vez
        self._search_timer.timeout.connect(self._ejecutar_busqueda)

        self._setup_ui()  # Construimos la interfaz

    # ── Construcción de la UI ──────────────────────────────────────────────────
    def _setup_ui(self):
        """Construye el layout principal de la vista de clientes."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── Encabezado ────────────────────────────────────────────────────────
        header = QHBoxLayout()

        # Título del módulo
        titulo = QLabel("👥  Clientes")
        titulo.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")

        # Subtítulo descriptivo
        subtitulo = QLabel("Historial de compras por cliente")
        subtitulo.setFont(QFont(FONT_FAMILY, 11))
        subtitulo.setStyleSheet(f"color: {COLORS['muted']};")

        # Columna izquierda: título + subtítulo apilados
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(titulo)
        title_col.addWidget(subtitulo)

        header.addLayout(title_col)
        header.addStretch()  # Empuja el campo de búsqueda a la derecha
        layout.addLayout(header)

        # ── Barra de búsqueda ─────────────────────────────────────────────────
        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        # Campo de texto para buscar por nombre o cédula
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("🔍  Buscar cliente por nombre o cédula...")
        self.inp_buscar.setFixedHeight(40)
        self.inp_buscar.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #D1D9E6;
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
                background: white;
            }
            QLineEdit:focus { border-color: #1A2942; }
        """)
        # Iniciamos el timer de búsqueda diferida al escribir
        self.inp_buscar.textChanged.connect(self._on_text_changed)

        search_row.addWidget(self.inp_buscar)
        layout.addLayout(search_row)

        # ── Splitter: panel clientes | panel historial ────────────────────────
        # QSplitter permite redimensionar los dos paneles arrastrando el divisor
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)
        splitter.setStyleSheet("QSplitter::handle { background: #E0E6F0; }")

        # Panel izquierdo: resultados de búsqueda de clientes
        left_panel = self._crear_panel_clientes()
        splitter.addWidget(left_panel)

        # Panel derecho: historial del cliente seleccionado
        right_panel = self._crear_panel_historial()
        splitter.addWidget(right_panel)

        # Proporción inicial: 40% clientes / 60% historial
        splitter.setSizes([400, 600])

        layout.addWidget(splitter, 1)  # El splitter ocupa el espacio restante

    def _crear_panel_clientes(self) -> QFrame:
        """Crea el panel izquierdo con la tabla de clientes."""
        frame = QFrame()
        frame.setObjectName("card")  # Estilo card del APP_STYLE
        frame.setStyleSheet("QFrame#card { background: white; border-radius: 12px; }")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Título del panel
        lbl = QLabel("Clientes encontrados")
        lbl.setFont(QFont(FONT_FAMILY, 13, QFont.DemiBold))
        lbl.setStyleSheet(f"color: {COLORS['primary']};")
        layout.addWidget(lbl)

        # Tabla de resultados de búsqueda
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(3)                       # 3 columnas
        self.tabla_clientes.setHorizontalHeaderLabels(["Cédula", "Nombre", "Facturas"])
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Nombre flexible
        self.tabla_clientes.setSelectionBehavior(QAbstractItemView.SelectRows)  # Selección por fila completa
        self.tabla_clientes.setEditTriggers(QAbstractItemView.NoEditTriggers)   # Solo lectura
        self.tabla_clientes.setAlternatingRowColors(True)           # Filas alternadas para legibilidad
        self.tabla_clientes.verticalHeader().setVisible(False)      # Ocultamos números de fila
        self.tabla_clientes.setStyleSheet("""
            QTableWidget { border: none; font-size: 13px; }
            QHeaderView::section {
                background: #1A2942; color: #FFFFFF; font-weight: 600;
                padding: 8px; border: none;
            }
            QTableWidget::item:selected { background: #E8F0FE; color: #1A2942; }
            QTableWidget::item:alternate { background: #F8FAFD; }
        """)
        # Al seleccionar un cliente, cargamos su historial
        self.tabla_clientes.itemSelectionChanged.connect(self._on_cliente_seleccionado)

        layout.addWidget(self.tabla_clientes)

        # Etiqueta de estado (muestra mensajes como "Busca un cliente arriba")
        self.lbl_estado_clientes = QLabel("Busca un cliente arriba para ver resultados.")
        self.lbl_estado_clientes.setFont(QFont(FONT_FAMILY, 11))
        self.lbl_estado_clientes.setStyleSheet(f"color: {COLORS['muted']};")
        self.lbl_estado_clientes.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_estado_clientes)

        return frame

    def _crear_panel_historial(self) -> QFrame:
        """Crea el panel derecho con el historial de facturas del cliente."""
        frame = QFrame()
        frame.setObjectName("card")
        frame.setStyleSheet("QFrame#card { background: white; border-radius: 12px; }")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Encabezado del panel con nombre del cliente y total acumulado
        header_row = QHBoxLayout()

        self.lbl_cliente_nombre = QLabel("Selecciona un cliente")
        self.lbl_cliente_nombre.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        self.lbl_cliente_nombre.setStyleSheet(f"color: {COLORS['primary']};")

        self.lbl_total_comprado = QLabel("")
        self.lbl_total_comprado.setFont(QFont(FONT_FAMILY, 12, QFont.DemiBold))
        self.lbl_total_comprado.setStyleSheet(f"color: {COLORS['accent']};")

        header_row.addWidget(self.lbl_cliente_nombre)
        header_row.addStretch()
        header_row.addWidget(self.lbl_total_comprado)
        layout.addLayout(header_row)

        # Separador visual
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #E0E6F0;")
        layout.addWidget(sep)

        # Área scrollable para mostrar las facturas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)        # El widget interno puede redimensionarse
        scroll.setFrameShape(QFrame.NoFrame)   # Sin borde exterior

        # Contenedor interno del scroll: aquí insertamos las tarjetas de facturas
        self.historial_container = QWidget()
        self.historial_layout = QVBoxLayout(self.historial_container)
        self.historial_layout.setContentsMargins(0, 0, 8, 0)
        self.historial_layout.setSpacing(12)
        self.historial_layout.addStretch()  # Empuja el contenido hacia arriba

        scroll.setWidget(self.historial_container)
        layout.addWidget(scroll, 1)

        return frame

    # ── Eventos de búsqueda ────────────────────────────────────────────────────
    def _on_text_changed(self, texto: str):
        """
        Se dispara con cada cambio en el campo de búsqueda.
        Reiniciamos el timer para esperar 300ms antes de buscar
        (evita queries en cada tecla mientras el usuario escribe).
        """
        self._search_timer.stop()    # Cancelamos el timer anterior si sigue activo

        if len(texto.strip()) < 2:
            # Con menos de 2 caracteres no buscamos para evitar resultados masivos
            self.tabla_clientes.setRowCount(0)
            self.lbl_estado_clientes.setText("Escribe al menos 2 caracteres para buscar.")
            return

        # Iniciamos el timer: buscará cuando pasen 300ms sin más cambios
        self._search_timer.start(300)

    def _ejecutar_busqueda(self):
        """
        Ejecuta la búsqueda en la BD y llena la tabla de clientes.
        Este método lo llama el timer 300ms después del último keystroke.
        """
        texto = self.inp_buscar.text().strip()
        if not texto:
            return

        # Llamamos al modelo para buscar clientes por texto
        resultados = buscar_clientes_historial(texto)

        # Limpiamos la tabla antes de llenar con nuevos resultados
        self.tabla_clientes.setRowCount(0)

        if not resultados:
            # No se encontraron clientes con ese texto
            self.lbl_estado_clientes.setText("No se encontraron clientes.")
            self.lbl_estado_clientes.show()
            return

        # Ocultamos el label de estado mientras hay resultados en la tabla
        self.lbl_estado_clientes.hide()

        # Llenamos la tabla con los resultados
        for cliente in resultados:
            fila = self.tabla_clientes.rowCount()
            self.tabla_clientes.insertRow(fila)

            # Columna 0: cédula
            item_cedula = QTableWidgetItem(cliente["cedula"])
            item_cedula.setData(Qt.UserRole, cliente["id"])  # Guardamos el ID oculto
            self.tabla_clientes.setItem(fila, 0, item_cedula)

            # Columna 1: nombre del cliente
            self.tabla_clientes.setItem(fila, 1, QTableWidgetItem(cliente["nombre"]))

            # Columna 2: número de facturas (con formato)
            facturas_str = f"{cliente['total_facturas']} factura(s)"
            item_fact = QTableWidgetItem(facturas_str)
            item_fact.setTextAlignment(Qt.AlignCenter)
            self.tabla_clientes.setItem(fila, 2, item_fact)

    # ── Selección de cliente ───────────────────────────────────────────────────
    def _on_cliente_seleccionado(self):
        """
        Se dispara cuando el usuario hace clic en una fila de la tabla de clientes.
        Carga el historial del cliente seleccionado en el panel derecho.
        """
        filas = self.tabla_clientes.selectedItems()
        if not filas:
            return  # Nada seleccionado, ignoramos

        # Obtenemos el ID del cliente desde el dato oculto en la columna 0
        fila_idx = self.tabla_clientes.currentRow()
        item_cedula = self.tabla_clientes.item(fila_idx, 0)
        cliente_id = item_cedula.data(Qt.UserRole)  # ID guardado en UserRole
        cliente_nombre = self.tabla_clientes.item(fila_idx, 1).text()

        # Guardamos el cliente seleccionado y cargamos su historial
        self._cliente_id_seleccionado = cliente_id
        self._cargar_historial(cliente_id, cliente_nombre)

    def _cargar_historial(self, cliente_id: int, cliente_nombre: str):
        """
        Consulta el historial de compras del cliente y renderiza
        una tarjeta por cada factura en el panel derecho.
        """
        # Actualizamos el encabezado del panel derecho con el nombre del cliente
        self.lbl_cliente_nombre.setText(f"📋  {cliente_nombre}")

        # Consultamos el historial en la BD
        facturas = historial_cliente(cliente_id)

        # Limpiamos el contenedor de historial (eliminamos tarjetas anteriores)
        while self.historial_layout.count() > 1:  # El último item es el stretch
            item = self.historial_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()  # Libera la memoria del widget

        if not facturas:
            # El cliente no tiene facturas registradas
            self.lbl_total_comprado.setText("Sin compras")
            lbl_vacio = QLabel("Este cliente no tiene compras registradas.")
            lbl_vacio.setFont(QFont(FONT_FAMILY, 12))
            lbl_vacio.setStyleSheet(f"color: {COLORS['muted']};")
            lbl_vacio.setAlignment(Qt.AlignCenter)
            self.historial_layout.insertWidget(0, lbl_vacio)
            return

        # Calculamos el total acumulado de todas las compras
        total_acumulado = sum(float(f["total"]) for f in facturas)
        self.lbl_total_comprado.setText(f"Total: ${total_acumulado:,.2f}")

        # Creamos una tarjeta visual por cada factura
        for i, factura in enumerate(facturas):
            tarjeta = self._crear_tarjeta_factura(factura)
            # Insertamos antes del stretch (último ítem del layout)
            self.historial_layout.insertWidget(i, tarjeta)

    def _crear_tarjeta_factura(self, factura: dict) -> QFrame:
        """
        Crea y retorna un QFrame estilizado con la información de una factura.
        Muestra: número, fecha, vendedor, productos y total.
        """
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #F8FAFD;
                border: 1px solid #E0E6F0;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # ── Fila superior: número de factura + total ───────────────────────────
        top_row = QHBoxLayout()

        # Número de factura como título de la tarjeta
        lbl_num = QLabel(f"🧾  {factura['numero_factura']}")
        lbl_num.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        lbl_num.setStyleSheet(f"color: {COLORS['primary']};")

        # Total de la factura destacado en naranja
        lbl_total = QLabel(f"${float(factura['total']):,.2f}")
        lbl_total.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))
        lbl_total.setStyleSheet(f"color: {COLORS['accent']};")

        top_row.addWidget(lbl_num)
        top_row.addStretch()
        top_row.addWidget(lbl_total)
        layout.addLayout(top_row)

        # ── Fecha, vendedor y método de pago ──────────────────────────────────
        fecha_str = factura["fecha_hora"].strftime("%d/%m/%Y %H:%M")
        meta = f"📅 {fecha_str}   |   👤 {factura['vendedor_nombre']}   |   💳 {factura['metodo_pago']}"
        lbl_meta = QLabel(meta)
        lbl_meta.setFont(QFont(FONT_FAMILY, 10))
        lbl_meta.setStyleSheet(f"color: {COLORS['muted']};")
        layout.addWidget(lbl_meta)

        # Separador ligero
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #E8ECF4;")
        layout.addWidget(sep)

        # ── Productos de esta factura ──────────────────────────────────────────
        for det in factura.get("detalles", []):
            # Línea por producto: cantidad × nombre = subtotal
            det_txt = (
                f"  {det['cantidad']}x  {det['nombre']}  "
                f"— ${float(det['subtotal']):,.2f}"
            )
            lbl_det = QLabel(det_txt)
            lbl_det.setFont(QFont(FONT_FAMILY, 11))
            lbl_det.setStyleSheet(f"color: {COLORS['text']};")
            layout.addWidget(lbl_det)

        return card
