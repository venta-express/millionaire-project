"""
AutoParts Express - HU-04: Registro de Venta y Emisión de Factura
Panel de ventas: búsqueda de productos, carrito, cliente y confirmación
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QFrame, QDialog, QHeaderView, QAbstractItemView,
    QScrollArea, QMessageBox, QTextEdit, QSizePolicy, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

from utils.styles import COLORS
from models.ventas import (
    ItemVenta, buscar_clientes, obtener_o_crear_cliente,
    buscar_cliente_por_cedula, registrar_venta, obtener_venta
)
from models.inventario import buscar_productos
from models.auth import get_usuario_activo


# ── Factura imprimible / vista previa ────────────────────────────────────────
class DialogFactura(QDialog):
    def __init__(self, venta: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Factura {venta['numero_factura']}")
        self.setModal(True)
        self.setMinimumSize(520, 600)
        self._venta = venta
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        content = QWidget()
        content.setStyleSheet("background: white;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(0)

        v = self._venta

        # Encabezado
        brand = QLabel("AutoParts Express")
        brand.setFont(QFont("Segoe UI", 20, QFont.Bold))
        brand.setStyleSheet(f"color: {COLORS['primary']};")
        brand.setAlignment(Qt.AlignCenter)

        sub = QLabel("Tienda de Repuestos y Accesorios de Motos")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color: {COLORS['muted']};")
        sub.setAlignment(Qt.AlignCenter)

        sep1 = QFrame()
        sep1.setFixedHeight(2)
        sep1.setStyleSheet(f"background: {COLORS['primary']}; margin: 16px 0;")

        num = QLabel(f"FACTURA N.° {v['numero_factura']}")
        num.setFont(QFont("Segoe UI", 13, QFont.Bold))
        num.setStyleSheet(f"color: {COLORS['accent']};")
        num.setAlignment(Qt.AlignCenter)

        cl.addWidget(brand)
        cl.addWidget(sub)
        cl.addWidget(sep1)
        cl.addWidget(num)
        cl.addSpacing(20)

        # Datos
        fecha = v['fecha_hora'].strftime("%d/%m/%Y %H:%M") if hasattr(v['fecha_hora'], 'strftime') else str(v['fecha_hora'])

        info_grid = QWidget()
        info_layout = QHBoxLayout(info_grid)
        info_layout.setContentsMargins(0, 0, 0, 0)

        def info_col(pairs):
            w = QWidget()
            vl = QVBoxLayout(w)
            vl.setContentsMargins(0, 0, 0, 0)
            vl.setSpacing(6)
            for key, val in pairs:
                row = QHBoxLayout()
                lk = QLabel(f"{key}:")
                lk.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
                lk.setStyleSheet(f"color: {COLORS['muted']};")
                lk.setFixedWidth(90)
                lv = QLabel(str(val))
                lv.setFont(QFont("Segoe UI", 11))
                lv.setStyleSheet(f"color: {COLORS['text']};")
                row.addWidget(lk)
                row.addWidget(lv)
                row.addStretch()
                vl.addLayout(row)
            return w

        col_left = info_col([
            ("Fecha", fecha),
            ("Vendedor", v["vendedor_nombre"]),
        ])
        col_right = info_col([
            ("Cliente", v["cliente_nombre"]),
            ("Cédula", v["cliente_cedula"]),
            ("Pago", v["metodo_pago"]),
        ])
        info_layout.addWidget(col_left)
        info_layout.addStretch()
        info_layout.addWidget(col_right)
        cl.addWidget(info_grid)
        cl.addSpacing(20)

        # Tabla de ítems
        table = QTableWidget(len(v["detalles"]), 4)
        table.setHorizontalHeaderLabels(["Código", "Producto", "Cant.", "Subtotal"])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setShowGrid(False)
        table.setStyleSheet(
            "QTableWidget { border: 1px solid #E8ECF4; border-radius: 8px; }"
            "QHeaderView::section { background: #1A2942; color: white; padding: 8px; font-size: 12px; }"
            "QTableWidget::item { padding: 8px; border-bottom: 1px solid #F0F4FA; }"
        )
        for row, d in enumerate(v["detalles"]):
            table.setRowHeight(row, 40)
            table.setItem(row, 0, QTableWidgetItem(d["codigo"]))
            table.setItem(row, 1, QTableWidgetItem(d["nombre"]))
            item_cant = QTableWidgetItem(str(d["cantidad"]))
            item_cant.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            table.setItem(row, 2, item_cant)
            item_sub = QTableWidgetItem(f"$ {d['subtotal']:,.0f}")
            item_sub.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 3, item_sub)

        table.setFixedHeight(min(len(v["detalles"]) * 42 + 40, 300))
        cl.addWidget(table)
        cl.addSpacing(16)

        # Totales
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {COLORS['border']};")
        cl.addWidget(sep2)
        cl.addSpacing(12)

        totals_row = QHBoxLayout()
        totals_row.addStretch()
        totals_col = QVBoxLayout()
        totals_col.setSpacing(6)

        def total_row(label, valor, bold=False):
            r = QHBoxLayout()
            lk = QLabel(label)
            lk.setFont(QFont("Segoe UI", 12, QFont.Bold if bold else QFont.Normal))
            lk.setStyleSheet(f"color: {COLORS['muted'] if not bold else COLORS['primary']};")
            lk.setFixedWidth(100)
            lv = QLabel(f"$ {valor:,.0f}")
            lv.setFont(QFont("Segoe UI", 12, QFont.Bold if bold else QFont.Normal))
            lv.setStyleSheet(f"color: {COLORS['accent'] if bold else COLORS['text']};")
            lv.setAlignment(Qt.AlignRight)
            r.addWidget(lk)
            r.addWidget(lv)
            return r

        totals_col.addLayout(total_row("Subtotal:", v["subtotal"]))
        totals_col.addLayout(total_row("Descuento:", v["descuento"]))
        totals_col.addLayout(total_row("TOTAL:", v["total"], bold=True))
        totals_row.addLayout(totals_col)
        cl.addLayout(totals_row)
        cl.addSpacing(24)

        gracias = QLabel("¡Gracias por su compra!")
        gracias.setFont(QFont("Segoe UI", 11))
        gracias.setStyleSheet(f"color: {COLORS['muted']};")
        gracias.setAlignment(Qt.AlignCenter)
        cl.addWidget(gracias)
        cl.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(16, 8, 16, 16)
        btn_row.addStretch()
        btn_close = QPushButton("Cerrar")
        btn_close.setObjectName("btn_secondary")
        btn_close.setFixedHeight(40)
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)


# ── Pantalla principal de Ventas ─────────────────────────────────────────────
class VentasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        self._carrito: list[ItemVenta] = []
        self._cliente_id: int = None
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._buscar_productos)
        self._setup_ui()

    def _setup_ui(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(20)

        # ── Columna izquierda: buscador + lista de productos ─────────────────
        left = QVBoxLayout()
        left.setSpacing(14)

        lbl = QLabel("Catálogo de Productos")
        lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl.setStyleSheet(f"color: {COLORS['primary']};")

        self.prod_search = QLineEdit()
        self.prod_search.setPlaceholderText("🔍  Buscar producto…")
        self.prod_search.setFixedHeight(42)
        self.prod_search.textChanged.connect(lambda: self._search_timer.start(250))

        self.prod_table = QTableWidget()
        self.prod_table.setColumnCount(4)
        self.prod_table.setHorizontalHeaderLabels(["Código", "Nombre", "Precio", "Stock"])
        self.prod_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.prod_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.prod_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.prod_table.verticalHeader().setVisible(False)
        self.prod_table.setShowGrid(False)
        self.prod_table.setFocusPolicy(Qt.NoFocus)
        self.prod_table.doubleClicked.connect(self._agregar_al_carrito)

        hint = QLabel("Doble clic o ↓ para agregar al carrito")
        hint.setStyleSheet(f"color: {COLORS['muted']}; font-size: 11px;")

        btn_add = QPushButton("Agregar al carrito ➜")
        btn_add.setObjectName("btn_secondary")
        btn_add.setFixedHeight(40)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._agregar_al_carrito)

        left.addWidget(lbl)
        left.addWidget(self.prod_search)
        left.addWidget(self.prod_table, 1)
        left.addWidget(hint)
        left.addWidget(btn_add)

        # ── Columna derecha: carrito + cliente ────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(14)

        lbl2 = QLabel("Carrito de Venta")
        lbl2.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl2.setStyleSheet(f"color: {COLORS['primary']};")

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Producto", "Precio", "Cant.", "Subtotal", ""])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setShowGrid(False)
        self.cart_table.setFocusPolicy(Qt.NoFocus)

        # Total
        total_frame = QFrame()
        total_frame.setObjectName("card")
        total_frame.setStyleSheet(
            f"background: {COLORS['primary']}; border-radius: 10px; padding: 14px;"
        )
        total_layout = QHBoxLayout(total_frame)
        self.lbl_total = QLabel("Total: $ 0")
        self.lbl_total.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.lbl_total.setStyleSheet("color: white;")
        total_layout.addStretch()
        total_layout.addWidget(self.lbl_total)

        # Cliente
        cliente_frame = QFrame()
        cliente_frame.setObjectName("card")
        cliente_fl = QVBoxLayout(cliente_frame)
        cliente_fl.setContentsMargins(16, 14, 16, 14)
        cliente_fl.setSpacing(10)

        lbl_cli = QLabel("Datos del Cliente")
        lbl_cli.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_cli.setStyleSheet(f"color: {COLORS['primary']};")

        cedula_row = QHBoxLayout()
        self.f_cedula = QLineEdit()
        self.f_cedula.setPlaceholderText("Cédula del cliente")
        self.f_cedula.setFixedHeight(38)
        btn_buscar_cli = QPushButton("Buscar")
        btn_buscar_cli.setObjectName("btn_secondary")
        btn_buscar_cli.setFixedHeight(38)
        btn_buscar_cli.setCursor(Qt.PointingHandCursor)
        btn_buscar_cli.clicked.connect(self._buscar_cliente)
        cedula_row.addWidget(self.f_cedula, 3)
        cedula_row.addWidget(btn_buscar_cli, 1)

        self.f_nombre_cli = QLineEdit()
        self.f_nombre_cli.setPlaceholderText("Nombre del cliente")
        self.f_nombre_cli.setFixedHeight(38)

        # Método de pago
        pago_row = QHBoxLayout()
        lbl_pago = QLabel("Método:")
        lbl_pago.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        lbl_pago.setStyleSheet(f"color: {COLORS['text']};")
        self.combo_pago = QComboBox()
        self.combo_pago.addItems(["Efectivo", "Transferencia"])
        self.combo_pago.setFixedHeight(38)
        self.combo_pago.currentTextChanged.connect(self._toggle_referencia)
        pago_row.addWidget(lbl_pago)
        pago_row.addWidget(self.combo_pago, 1)

        self.f_referencia = QLineEdit()
        self.f_referencia.setPlaceholderText("Referencia de transferencia")
        self.f_referencia.setFixedHeight(38)
        self.f_referencia.hide()

        cliente_fl.addWidget(lbl_cli)
        cliente_fl.addLayout(cedula_row)
        cliente_fl.addWidget(self.f_nombre_cli)
        cliente_fl.addLayout(pago_row)
        cliente_fl.addWidget(self.f_referencia)

        btn_confirmar = QPushButton("✓  Confirmar Venta y Generar Factura")
        btn_confirmar.setObjectName("btn_primary")
        btn_confirmar.setFixedHeight(50)
        btn_confirmar.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        btn_confirmar.setCursor(Qt.PointingHandCursor)
        btn_confirmar.clicked.connect(self._confirmar_venta)

        btn_limpiar = QPushButton("Limpiar carrito")
        btn_limpiar.setObjectName("btn_secondary")
        btn_limpiar.setFixedHeight(38)
        btn_limpiar.setCursor(Qt.PointingHandCursor)
        btn_limpiar.clicked.connect(self._limpiar_carrito)

        right.addWidget(lbl2)
        right.addWidget(self.cart_table, 1)
        right.addWidget(total_frame)
        right.addWidget(cliente_frame)
        right.addWidget(btn_confirmar)
        right.addWidget(btn_limpiar)

        main.addLayout(left, 5)
        main.addLayout(right, 4)

        self._buscar_productos()

    # ── Lógica ───────────────────────────────────────────────────────────────
    def _toggle_referencia(self, text):
        self.f_referencia.setVisible(text == "Transferencia")

    def _buscar_productos(self):
        texto = self.prod_search.text()
        prods = buscar_productos(texto)
        self.prod_table.setRowCount(len(prods))
        self._prods_cache = prods
        for row, p in enumerate(prods):
            self.prod_table.setRowHeight(row, 44)
            self.prod_table.setItem(row, 0, QTableWidgetItem(p.codigo))
            self.prod_table.setItem(row, 1, QTableWidgetItem(p.nombre))
            precio_item = QTableWidgetItem(f"$ {p.precio_unitario:,.0f}")
            precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.prod_table.setItem(row, 2, precio_item)
            stock_item = QTableWidgetItem(str(p.stock_actual))
            stock_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            if p.stock_actual == 0:
                stock_item.setForeground(QColor(COLORS["danger"]))
            self.prod_table.setItem(row, 3, stock_item)

    def _agregar_al_carrito(self):
        row = self.prod_table.currentRow()
        if row < 0 or row >= len(self._prods_cache):
            return
        p = self._prods_cache[row]
        if p.stock_actual == 0:
            QMessageBox.warning(self, "Sin stock", f"'{p.nombre}' no tiene stock disponible.")
            return

        # Si ya está en el carrito, incrementar
        for item in self._carrito:
            if item.producto_id == p.id:
                if item.cantidad < p.stock_actual:
                    item.cantidad += 1
                    item.subtotal = round(item.precio_unitario * item.cantidad, 2)
                else:
                    QMessageBox.warning(self, "Stock máximo",
                                        f"Solo hay {p.stock_actual} unidades disponibles.")
                self._refresh_cart()
                return

        self._carrito.append(ItemVenta(
            producto_id=p.id,
            codigo=p.codigo,
            nombre=p.nombre,
            precio_unitario=p.precio_unitario,
            cantidad=1,
        ))
        self._refresh_cart()

    def _refresh_cart(self):
        self.cart_table.setRowCount(len(self._carrito))
        total = 0
        for row, item in enumerate(self._carrito):
            self.cart_table.setRowHeight(row, 48)
            self.cart_table.setItem(row, 0, QTableWidgetItem(item.nombre))
            pr = QTableWidgetItem(f"$ {item.precio_unitario:,.0f}")
            pr.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.cart_table.setItem(row, 1, pr)

            # Spinner de cantidad
            spin = QSpinBox()
            spin.setRange(1, 999)
            spin.setValue(item.cantidad)
            spin.setFixedHeight(36)
            spin.setStyleSheet(
                "QSpinBox { border: 1px solid #D8E0EC; border-radius:6px; "
                "padding:4px; background:white; }"
            )
            idx = row
            spin.valueChanged.connect(lambda val, i=idx: self._cambiar_cantidad(i, val))
            self.cart_table.setCellWidget(row, 2, spin)

            sub = QTableWidgetItem(f"$ {item.subtotal:,.0f}")
            sub.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.cart_table.setItem(row, 3, sub)

            # Botón eliminar
            btn_rem = QPushButton("✕")
            btn_rem.setFixedHeight(32)
            btn_rem.setStyleSheet(
                "QPushButton { background: #FDEDEC; color: #E74C3C; border:none;"
                "border-radius:6px; font-weight:700; font-size:14px;}"
                "QPushButton:hover { background: #E74C3C; color: white; }"
            )
            btn_rem.setCursor(Qt.PointingHandCursor)
            btn_rem.clicked.connect(lambda _, i=idx: self._quitar_item(i))
            cell_w = QWidget()
            cell_l = QHBoxLayout(cell_w)
            cell_l.setContentsMargins(4, 4, 4, 4)
            cell_l.addWidget(btn_rem)
            self.cart_table.setCellWidget(row, 4, cell_w)

            total += item.subtotal

        self.lbl_total.setText(f"Total: $ {total:,.0f}")

    def _cambiar_cantidad(self, idx: int, val: int):
        if idx < len(self._carrito):
            self._carrito[idx].cantidad = val
            self._carrito[idx].subtotal = round(
                self._carrito[idx].precio_unitario * val, 2
            )
            self._refresh_cart()

    def _quitar_item(self, idx: int):
        if idx < len(self._carrito):
            self._carrito.pop(idx)
            self._refresh_cart()

    def _limpiar_carrito(self):
        self._carrito.clear()
        self._cliente_id = None
        self.f_cedula.clear()
        self.f_nombre_cli.clear()
        self._refresh_cart()

    def _buscar_cliente(self):
        cedula = self.f_cedula.text().strip()
        if not cedula:
            return
        cliente = buscar_cliente_por_cedula(cedula)
        if cliente:
            self.f_nombre_cli.setText(cliente.nombre)
            self._cliente_id = cliente.id

    def _confirmar_venta(self):
        if not self._carrito:
            QMessageBox.warning(self, "Carrito vacío", "Agrega productos al carrito antes de confirmar.")
            return

        cedula = self.f_cedula.text().strip()
        nombre = self.f_nombre_cli.text().strip()
        if not cedula or not nombre:
            QMessageBox.warning(self, "Datos del cliente",
                                "Ingresa la cédula y el nombre del cliente.")
            return

        ok_cli, msg_cli, cli_id = obtener_o_crear_cliente(cedula, nombre)
        if not ok_cli:
            QMessageBox.warning(self, "Cliente", msg_cli)
            return

        metodo = self.combo_pago.currentText()
        referencia = self.f_referencia.text().strip() if metodo == "Transferencia" else ""

        vendedor = get_usuario_activo()
        if not vendedor:
            QMessageBox.critical(self, "Sesión", "No hay sesión activa.")
            return

        ok, result, venta_id = registrar_venta(
            cli_id, vendedor.id, self._carrito, metodo, referencia
        )

        if not ok:
            QMessageBox.warning(self, "Error en la venta", result)
            return

        # Mostrar factura
        venta_data = obtener_venta(venta_id)
        dlg = DialogFactura(venta_data, self)
        dlg.exec()

        # Limpiar para nueva venta
        self._limpiar_carrito()
        self._buscar_productos()
