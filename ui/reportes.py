"""
AutoParts Express - Módulo de Reportes
HU-09: Reportes de Ventas e Inventario (Sprint 3)
HU-10: Reporte de Ventas por Vendedor   (Sprint 3)

Tres pestañas: Ventas por período | Inventario | Por Vendedor.
Cada pestaña tiene selector de fechas, tabla de resultados
y botones de exportar a Excel / PDF.
"""

import os                        # Para construir rutas de archivos
import tempfile                  # Para guardar archivos temporalmente

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QTabWidget,
    QHeaderView, QAbstractItemView, QDateEdit, QComboBox,
    QMessageBox, QFileDialog, QSizePolicy, QGroupBox
)
from PySide6.QtCore  import Qt, QDate
from PySide6.QtGui   import QFont, QColor

from utils.constants import FONT_FAMILY
from utils.styles    import COLORS
from models.reportes import (
    reporte_ventas, reporte_inventario, reporte_por_vendedor,
    exportar_excel, exportar_pdf
)
from models.auth     import listar_usuarios       # Para el combo de vendedores
from datetime        import date as date_type


class ReportesView(QWidget):
    """
    Vista principal del módulo de Reportes.
    Usa QTabWidget con tres pestañas independientes.
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        self._setup_ui()

    # ── Construcción de UI ─────────────────────────────────────────────────────
    def _setup_ui(self):
        """Construye el layout con encabezado + QTabWidget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── Encabezado ────────────────────────────────────────────────────────
        titulo = QLabel("📊  Reportes")
        titulo.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")

        subtitulo = QLabel("Análisis de ventas, inventario y rendimiento del equipo")
        subtitulo.setFont(QFont(FONT_FAMILY, 11))
        subtitulo.setStyleSheet(f"color: {COLORS['muted']};")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        # ── QTabWidget: una pestaña por tipo de reporte ───────────────────────
        self.tabs = QTabWidget()
        self.tabs.addTab(self._tab_ventas(),    "🧾  Ventas por Período")
        self.tabs.addTab(self._tab_inventario(),"📦  Inventario Actual")
        self.tabs.addTab(self._tab_vendedor(),  "👤  Por Vendedor")

        layout.addWidget(self.tabs, 1)  # El tabs ocupa el espacio restante

    # ═══════════════════════════════════════════════════════════════════════════
    # PESTAÑA 1 — Ventas por Período
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab_ventas(self) -> QWidget:
        """Construye la pestaña de ventas por período."""
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # ── Selector de fechas + botón generar ────────────────────────────────
        control_row = QHBoxLayout()
        control_row.setSpacing(12)

        control_row.addWidget(QLabel("Desde:"))
        self.date_v_ini = QDateEdit()
        self.date_v_ini.setCalendarPopup(True)
        # Por defecto: primer día del mes actual
        hoy = QDate.currentDate()
        self.date_v_ini.setDate(QDate(hoy.year(), hoy.month(), 1))
        self.date_v_ini.setDisplayFormat("dd/MM/yyyy")
        self.date_v_ini.setFixedWidth(130)
        control_row.addWidget(self.date_v_ini)

        control_row.addWidget(QLabel("Hasta:"))
        self.date_v_fin = QDateEdit()
        self.date_v_fin.setCalendarPopup(True)
        self.date_v_fin.setDate(hoy)         # Por defecto: hoy
        self.date_v_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_v_fin.setFixedWidth(130)
        control_row.addWidget(self.date_v_fin)

        btn_gen = QPushButton("▶  Generar Reporte")
        btn_gen.setObjectName("btn_primary")
        btn_gen.setFixedHeight(38)
        btn_gen.clicked.connect(self._generar_ventas)
        control_row.addWidget(btn_gen)

        control_row.addStretch()

        # Botones de exportar (inicialmente desactivados)
        self.btn_excel_v = QPushButton("📥  Excel")
        self.btn_excel_v.setObjectName("btn_success")
        self.btn_excel_v.setFixedHeight(38)
        self.btn_excel_v.setEnabled(False)
        self.btn_excel_v.clicked.connect(lambda: self._exportar("ventas", "excel"))
        control_row.addWidget(self.btn_excel_v)

        self.btn_pdf_v = QPushButton("📄  PDF")
        self.btn_pdf_v.setObjectName("btn_danger")
        self.btn_pdf_v.setFixedHeight(38)
        self.btn_pdf_v.setEnabled(False)
        self.btn_pdf_v.clicked.connect(lambda: self._exportar("ventas", "pdf"))
        control_row.addWidget(self.btn_pdf_v)

        lay.addLayout(control_row)

        # ── Tarjetas de resumen ───────────────────────────────────────────────
        self.cards_ventas = QHBoxLayout()
        self.cards_ventas.setSpacing(12)
        self._v_cards = {}   # Guardamos referencias para actualizarlas

        for key, titulo_c, icono in [
            ("total_ventas",     "Total Ventas",     "🧾"),
            ("ingresos_totales", "Ingresos",          "💰"),
            ("descuentos",       "Descuentos",        "🏷️"),
            ("ticket_promedio",  "Ticket Promedio",   "📈"),
        ]:
            card, lbl_val = self._crear_stat_card(icono, titulo_c, "—")
            self._v_cards[key] = lbl_val
            self.cards_ventas.addWidget(card)

        lay.addLayout(self.cards_ventas)

        # ── Tabla de top productos ────────────────────────────────────────────
        lbl_top = QLabel("Top 10 productos más vendidos")
        lbl_top.setFont(QFont(FONT_FAMILY, 13, QFont.DemiBold))
        lbl_top.setStyleSheet(f"color: {COLORS['primary']};")
        lay.addWidget(lbl_top)

        self.tabla_v = self._crear_tabla(
            ["Código", "Producto", "Categoría", "Unidades", "Ingresos"]
        )
        lay.addWidget(self.tabla_v, 1)

        # Guardamos referencia a los datos para exportar
        self._datos_ventas = None

        return tab

    # ═══════════════════════════════════════════════════════════════════════════
    # PESTAÑA 2 — Inventario Actual
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab_inventario(self) -> QWidget:
        """Construye la pestaña de inventario actual."""
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # ── Botón generar + exportar ──────────────────────────────────────────
        ctrl = QHBoxLayout()

        btn_gen = QPushButton("▶  Generar Reporte de Inventario")
        btn_gen.setObjectName("btn_primary")
        btn_gen.setFixedHeight(38)
        btn_gen.clicked.connect(self._generar_inventario)
        ctrl.addWidget(btn_gen)

        ctrl.addStretch()

        self.btn_excel_i = QPushButton("📥  Excel")
        self.btn_excel_i.setObjectName("btn_success")
        self.btn_excel_i.setFixedHeight(38)
        self.btn_excel_i.setEnabled(False)
        self.btn_excel_i.clicked.connect(lambda: self._exportar("inventario", "excel"))
        ctrl.addWidget(self.btn_excel_i)

        self.btn_pdf_i = QPushButton("📄  PDF")
        self.btn_pdf_i.setObjectName("btn_danger")
        self.btn_pdf_i.setFixedHeight(38)
        self.btn_pdf_i.setEnabled(False)
        self.btn_pdf_i.clicked.connect(lambda: self._exportar("inventario", "pdf"))
        ctrl.addWidget(self.btn_pdf_i)

        lay.addLayout(ctrl)

        # Tarjetas de resumen
        self.cards_inv = QHBoxLayout()
        self._i_cards = {}
        for key, titulo_c, icono in [
            ("total_productos",  "Productos Activos", "📦"),
            ("total_unidades",   "Unidades en Stock", "🔢"),
            ("valor_inventario", "Valor Total",        "💵"),
            ("productos_criticos","Stock Crítico",     "⚠️"),
        ]:
            card, lbl_val = self._crear_stat_card(icono, titulo_c, "—")
            self._i_cards[key] = lbl_val
            self.cards_inv.addWidget(card)
        lay.addLayout(self.cards_inv)

        lbl = QLabel("Detalle de inventario")
        lbl.setFont(QFont(FONT_FAMILY, 13, QFont.DemiBold))
        lbl.setStyleSheet(f"color: {COLORS['primary']};")
        lay.addWidget(lbl)

        self.tabla_i = self._crear_tabla(
            ["Código", "Producto", "Categoría", "Precio", "Stock", "Mínimo", "Estado"]
        )
        lay.addWidget(self.tabla_i, 1)

        self._datos_inventario = None
        return tab

    # ═══════════════════════════════════════════════════════════════════════════
    # PESTAÑA 3 — Por Vendedor
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab_vendedor(self) -> QWidget:
        """Construye la pestaña de reportes por vendedor."""
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(12)

        ctrl.addWidget(QLabel("Desde:"))
        self.date_vend_ini = QDateEdit()
        self.date_vend_ini.setCalendarPopup(True)
        hoy = QDate.currentDate()
        self.date_vend_ini.setDate(QDate(hoy.year(), hoy.month(), 1))
        self.date_vend_ini.setDisplayFormat("dd/MM/yyyy")
        self.date_vend_ini.setFixedWidth(130)
        ctrl.addWidget(self.date_vend_ini)

        ctrl.addWidget(QLabel("Hasta:"))
        self.date_vend_fin = QDateEdit()
        self.date_vend_fin.setCalendarPopup(True)
        self.date_vend_fin.setDate(hoy)
        self.date_vend_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_vend_fin.setFixedWidth(130)
        ctrl.addWidget(self.date_vend_fin)

        ctrl.addWidget(QLabel("Vendedor:"))
        self.combo_vendedor = QComboBox()
        self.combo_vendedor.setFixedWidth(200)
        self.combo_vendedor.addItem("Todos", None)
        # Cargamos los usuarios con rol Vendedor o Gerencia
        for u in listar_usuarios():
            if u["rol"] in ("Vendedor", "Gerencia"):
                self.combo_vendedor.addItem(u["nombre"], u["id"])
        ctrl.addWidget(self.combo_vendedor)

        btn_gen = QPushButton("▶  Generar")
        btn_gen.setObjectName("btn_primary")
        btn_gen.setFixedHeight(38)
        btn_gen.clicked.connect(self._generar_vendedor)
        ctrl.addWidget(btn_gen)

        ctrl.addStretch()

        self.btn_excel_vend = QPushButton("📥  Excel")
        self.btn_excel_vend.setObjectName("btn_success")
        self.btn_excel_vend.setFixedHeight(38)
        self.btn_excel_vend.setEnabled(False)
        self.btn_excel_vend.clicked.connect(lambda: self._exportar("vendedor", "excel"))
        ctrl.addWidget(self.btn_excel_vend)

        self.btn_pdf_vend = QPushButton("📄  PDF")
        self.btn_pdf_vend.setObjectName("btn_danger")
        self.btn_pdf_vend.setFixedHeight(38)
        self.btn_pdf_vend.setEnabled(False)
        self.btn_pdf_vend.clicked.connect(lambda: self._exportar("vendedor", "pdf"))
        ctrl.addWidget(self.btn_pdf_vend)

        lay.addLayout(ctrl)

        lbl = QLabel("Rendimiento por vendedor")
        lbl.setFont(QFont(FONT_FAMILY, 13, QFont.DemiBold))
        lbl.setStyleSheet(f"color: {COLORS['primary']};")
        lay.addWidget(lbl)

        self.tabla_vend = self._crear_tabla(
            ["Vendedor", "Total Ventas", "Ingresos", "Ticket Promedio", "Venta Máxima"]
        )
        lay.addWidget(self.tabla_vend, 1)

        self._datos_vendedor = None
        return tab

    # ── Helpers de UI ─────────────────────────────────────────────────────────
    def _crear_stat_card(self, icono: str, titulo: str, valor: str):
        """
        Crea una tarjeta de estadística con ícono, título y valor numérico.
        Retorna (card_widget, lbl_valor) para poder actualizar el valor dinámicamente.
        """
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(100)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 12, 16, 12)
        card_lay.setSpacing(4)

        # Fila superior: ícono + título
        top = QHBoxLayout()
        lbl_icon = QLabel(icono)
        lbl_icon.setFont(QFont(FONT_FAMILY, 18))
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(QFont(FONT_FAMILY, 11))
        lbl_titulo.setStyleSheet(f"color: {COLORS['muted']};")
        top.addWidget(lbl_icon)
        top.addWidget(lbl_titulo)
        top.addStretch()
        card_lay.addLayout(top)

        # Valor grande
        lbl_val = QLabel(valor)
        lbl_val.setFont(QFont(FONT_FAMILY, 16, QFont.Bold))
        lbl_val.setStyleSheet(f"color: {COLORS['primary']};")
        card_lay.addWidget(lbl_val)

        return card, lbl_val

    def _crear_tabla(self, columnas: list) -> QTableWidget:
        """Crea una QTableWidget de solo lectura con las columnas dadas."""
        t = QTableWidget()
        t.setColumnCount(len(columnas))
        t.setHorizontalHeaderLabels(columnas)
        t.horizontalHeader().setSectionResizeMode(
            1 if len(columnas) > 1 else 0, QHeaderView.Stretch
        )
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectRows)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        return t

    def _qdate_to_date(self, qdate: QDate) -> date_type:
        """Convierte un QDate de Qt a un objeto date de Python."""
        return date_type(qdate.year(), qdate.month(), qdate.day())

    # ── Generación de reportes ─────────────────────────────────────────────────
    def _generar_ventas(self):
        """Consulta el modelo y rellena la pestaña de ventas."""
        ini = self._qdate_to_date(self.date_v_ini.date())
        fin = self._qdate_to_date(self.date_v_fin.date())

        if fin < ini:
            QMessageBox.warning(self, "Fechas inválidas",
                                "La fecha de fin debe ser posterior a la de inicio.")
            return

        datos = reporte_ventas(ini, fin)  # Consultamos el modelo
        self._datos_ventas = datos         # Guardamos para exportar

        # Actualizar tarjetas de resumen
        r = datos["resumen"]
        self._v_cards["total_ventas"].setText(str(int(r["total_ventas"])))
        self._v_cards["ingresos_totales"].setText(f"${float(r['ingresos_totales']):,.2f}")
        self._v_cards["descuentos"].setText(f"${float(r['descuentos_totales']):,.2f}")
        self._v_cards["ticket_promedio"].setText(f"${float(r['ticket_promedio']):,.2f}")

        # Llenar tabla de top productos
        self.tabla_v.setRowCount(0)
        for p in datos["productos_top"]:
            fila = self.tabla_v.rowCount()
            self.tabla_v.insertRow(fila)
            self.tabla_v.setItem(fila, 0, QTableWidgetItem(p["codigo"]))
            self.tabla_v.setItem(fila, 1, QTableWidgetItem(p["producto_nombre"]))
            self.tabla_v.setItem(fila, 2, QTableWidgetItem(p["categoria"] or "—"))
            unid = QTableWidgetItem(str(int(p["unidades_vendidas"])))
            unid.setTextAlignment(Qt.AlignCenter)
            self.tabla_v.setItem(fila, 3, unid)
            ing = QTableWidgetItem(f"${float(p['ingresos']):,.2f}")
            ing.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla_v.setItem(fila, 4, ing)

        # Activamos los botones de exportar
        self.btn_excel_v.setEnabled(True)
        self.btn_pdf_v.setEnabled(True)

    def _generar_inventario(self):
        """Consulta el modelo y rellena la pestaña de inventario."""
        datos = reporte_inventario()
        self._datos_inventario = datos

        r = datos["resumen"]
        self._i_cards["total_productos"].setText(str(int(r["total_productos"])))
        self._i_cards["total_unidades"].setText(str(int(r["total_unidades"])))
        self._i_cards["valor_inventario"].setText(f"${float(r['valor_inventario']):,.2f}")
        self._i_cards["productos_criticos"].setText(str(int(r["productos_criticos"])))

        self.tabla_i.setRowCount(0)
        for p in datos["detalle"]:
            fila = self.tabla_i.rowCount()
            self.tabla_i.insertRow(fila)
            self.tabla_i.setItem(fila, 0, QTableWidgetItem(p["codigo"]))
            self.tabla_i.setItem(fila, 1, QTableWidgetItem(p["nombre"]))
            self.tabla_i.setItem(fila, 2, QTableWidgetItem(p["categoria"] or "—"))
            self.tabla_i.setItem(fila, 3,
                QTableWidgetItem(f"${float(p['precio_unitario']):,.2f}"))
            for col_idx, val in [(4, p["stock_actual"]), (5, p["stock_minimo"])]:
                it = QTableWidgetItem(str(val))
                it.setTextAlignment(Qt.AlignCenter)
                self.tabla_i.setItem(fila, col_idx, it)
            # Badge de estado con color
            lbl_estado = QTableWidgetItem(p["estado_stock"])
            lbl_estado.setTextAlignment(Qt.AlignCenter)
            color_estado = {
                "Sin stock": QColor("#E74C3C"),
                "Crítico":   QColor("#E67E22"),
                "Bajo":      QColor("#F39C12"),
                "Normal":    QColor("#27AE60"),
            }
            fg = color_estado.get(p["estado_stock"], QColor("#1A2942"))
            lbl_estado.setForeground(fg)
            if p["estado_stock"] in ("Sin stock", "Crítico"):
                lbl_estado.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
            self.tabla_i.setItem(fila, 6, lbl_estado)

        self.btn_excel_i.setEnabled(True)
        self.btn_pdf_i.setEnabled(True)

    def _generar_vendedor(self):
        """Consulta el modelo y rellena la pestaña de vendedor."""
        ini = self._qdate_to_date(self.date_vend_ini.date())
        fin = self._qdate_to_date(self.date_vend_fin.date())
        if fin < ini:
            QMessageBox.warning(self, "Fechas inválidas",
                                "La fecha de fin debe ser posterior a la de inicio.")
            return

        vid = self.combo_vendedor.currentData()  # None = todos
        datos = reporte_por_vendedor(ini, fin, vid)
        self._datos_vendedor = datos

        self.tabla_vend.setRowCount(0)
        for v in datos["por_vendedor"]:
            fila = self.tabla_vend.rowCount()
            self.tabla_vend.insertRow(fila)
            self.tabla_vend.setItem(fila, 0, QTableWidgetItem(v["vendedor_nombre"]))
            n_it = QTableWidgetItem(str(int(v["total_ventas"])))
            n_it.setTextAlignment(Qt.AlignCenter)
            self.tabla_vend.setItem(fila, 1, n_it)
            for col_idx, val in [
                (2, f"${float(v['ingresos_totales']):,.2f}"),
                (3, f"${float(v['ticket_promedio']):,.2f}"),
                (4, f"${float(v['venta_maxima']):,.2f}"),
            ]:
                it = QTableWidgetItem(val)
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla_vend.setItem(fila, col_idx, it)

        self.btn_excel_vend.setEnabled(True)
        self.btn_pdf_vend.setEnabled(True)

    # ── Exportación ────────────────────────────────────────────────────────────
    def _exportar(self, tipo: str, formato: str):
        """
        Abre un diálogo de guardar y exporta el reporte al formato indicado.
        tipo:    'ventas' | 'inventario' | 'vendedor'
        formato: 'excel' | 'pdf'
        """
        # Obtenemos los datos según la pestaña
        datos_map = {
            "ventas":     self._datos_ventas,
            "inventario": self._datos_inventario,
            "vendedor":   self._datos_vendedor,
        }
        datos = datos_map[tipo]
        if not datos:
            QMessageBox.warning(self, "Sin datos",
                                "Genera el reporte primero antes de exportar.")
            return

        # Definimos extensión y filtro según el formato
        if formato == "excel":
            ext, filtro = ".xlsx", "Excel (*.xlsx)"
        else:
            ext, filtro = ".pdf", "PDF (*.pdf)"

        # Diálogo para elegir dónde guardar el archivo
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte", f"reporte_{tipo}{ext}", filtro
        )
        if not ruta:
            return  # El usuario canceló el diálogo

        # Llamamos a la función de exportación del modelo
        if formato == "excel":
            ok, msg = exportar_excel(tipo, datos, ruta)
        else:
            ok, msg = exportar_pdf(tipo, datos, ruta)

        if ok:
            QMessageBox.information(self, "Exportación exitosa",
                                    f"Reporte guardado correctamente.\n{ruta}")
        else:
            QMessageBox.warning(self, "Error de exportación", msg)
