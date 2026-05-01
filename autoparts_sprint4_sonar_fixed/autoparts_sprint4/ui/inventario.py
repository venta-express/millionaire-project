"""
AutoParts Express - HU-02: Registro de Productos + HU-03: Búsqueda y Filtrado
Pantalla completa de Inventario
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QFrame, QDialog, QSpinBox, QDoubleSpinBox,
    QHeaderView, QMessageBox, QTextEdit, QAbstractItemView,
    QScrollArea,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

from utils.styles import COLORS
from models.inventario import (
    buscar_productos, registrar_producto, actualizar_producto,
    desactivar_producto, listar_categorias, obtener_producto, Producto
)


# ── Diálogo: Nuevo / Editar Producto ────────────────────────────────────────
class DialogProducto(QDialog):
    def __init__(self, parent=None, producto: Producto = None):
        super().__init__(parent)
        self._producto = producto
        try:
            self._categorias = listar_categorias()
        except Exception:
            self._categorias = []
        titulo = "Editar Producto" if producto else "Registrar Nuevo Producto"
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setMinimumWidth(520)
        self.resize(520, 600)
        self.setStyleSheet("background-color: #F4F6FA;")
        self._setup_ui()
        if producto:
            self._fill(producto)

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: #F4F6FA; border: none; }")
        inner = QWidget()
        inner.setStyleSheet("background: #F4F6FA;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(32, 22, 32, 12)
        layout.setSpacing(7)

        title = QLabel(self.windowTitle())
        title.setFont(QFont("Arial", 17, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {COLORS['border']};")
        layout.addWidget(sep)

        def mk_label(text):
            lbl = QLabel(text)
            lbl.setFont(QFont("Arial", 10, QFont.DemiBold))
            lbl.setStyleSheet(f"color: {COLORS['text']}; background: transparent; margin-top: 3px;")
            return lbl

        layout.addWidget(mk_label("Código *"))
        self.f_codigo = QLineEdit()
        self.f_codigo.setPlaceholderText("Ej: FRE-001")
        self.f_codigo.setFixedHeight(36)
        layout.addWidget(self.f_codigo)

        layout.addWidget(mk_label("Nombre *"))
        self.f_nombre = QLineEdit()
        self.f_nombre.setPlaceholderText("Nombre del producto")
        self.f_nombre.setFixedHeight(36)
        layout.addWidget(self.f_nombre)

        layout.addWidget(mk_label("Descripción"))
        self.f_desc = QTextEdit()
        self.f_desc.setPlaceholderText("Descripción opcional...")
        self.f_desc.setFixedHeight(56)
        self.f_desc.setStyleSheet(
            f"background:white; border:1.5px solid {COLORS['border']};"
            "border-radius:8px; padding:8px; font-size:13px;"
        )
        layout.addWidget(self.f_desc)

        layout.addWidget(mk_label("Categoría *"))
        self.f_cat = QComboBox()
        self.f_cat.setFixedHeight(36)
        self.f_cat.addItem("— Selecciona categoría —", None)
        for c in self._categorias:
            self.f_cat.addItem(c["nombre"], c["id"])
        layout.addWidget(self.f_cat)

        layout.addWidget(mk_label("Precio Unitario *"))
        self.f_precio = QDoubleSpinBox()
        self.f_precio.setRange(0, 9_999_999)
        self.f_precio.setDecimals(2)
        self.f_precio.setSingleStep(1000)
        self.f_precio.setPrefix("$ ")
        self.f_precio.setFixedHeight(36)
        layout.addWidget(self.f_precio)

        layout.addWidget(mk_label("Stock Inicial"))
        self.f_stock = QSpinBox()
        self.f_stock.setRange(0, 999_999)
        self.f_stock.setFixedHeight(36)
        if self._producto:
            self.f_stock.setEnabled(False)
        layout.addWidget(self.f_stock)

        layout.addWidget(mk_label("Stock Mínimo (alerta)"))
        self.f_stock_min = QSpinBox()
        self.f_stock_min.setRange(0, 999_999)
        self.f_stock_min.setFixedHeight(36)
        layout.addWidget(self.f_stock_min)

        self.lbl_error = QLabel("")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setStyleSheet(
            "color:#E74C3C; font-size:12px; font-weight:600;"
            "background:#FDEDEC; border-radius:6px; padding:8px 12px;"
        )
        self.lbl_error.hide()
        layout.addWidget(self.lbl_error)
        layout.addStretch()

        scroll.setWidget(inner)
        outer.addWidget(scroll, 1)

        # Botones FIJOS abajo, siempre visibles
        btn_area = QWidget()
        btn_area.setStyleSheet("background: #F4F6FA; border-top: 1px solid #E0E6F0;")
        btn_row = QHBoxLayout(btn_area)
        btn_row.setContentsMargins(32, 10, 32, 14)
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setMinimumWidth(110)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Guardar Producto")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setMinimumWidth(160)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self._save)

        from PySide6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Return"), self).activated.connect(self._save)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(10)
        btn_row.addWidget(self.btn_save)
        outer.addWidget(btn_area)

    def _fill(self, p: Producto):
        self.f_codigo.setText(p.codigo)
        self.f_codigo.setEnabled(False)
        self.f_nombre.setText(p.nombre)
        self.f_desc.setPlainText(p.descripcion or "")
        for i in range(self.f_cat.count()):
            if self.f_cat.itemData(i) == p.categoria_id:
                self.f_cat.setCurrentIndex(i)
                break
        self.f_precio.setValue(float(p.precio_unitario))
        self.f_stock.setValue(p.stock_actual)
        self.f_stock_min.setValue(p.stock_minimo)

    def _save(self):
        codigo    = self.f_codigo.text().strip()
        nombre    = self.f_nombre.text().strip()
        desc      = self.f_desc.toPlainText().strip()
        cat_id    = self.f_cat.currentData()
        precio    = self.f_precio.value()
        stock     = self.f_stock.value()
        stock_min = self.f_stock_min.value()

        if not codigo:
            self._show_error("El código es obligatorio.")
            return
        if not nombre:
            self._show_error("El nombre del producto es obligatorio.")
            return
        if cat_id is None and not self._producto:
            self._show_error("Selecciona una categoría.")
            return

        try:
            if self._producto:
                ok, msg = actualizar_producto(
                    self._producto.id, nombre, desc,
                    cat_id or self._producto.categoria_id, precio, stock_min
                )
            else:
                ok, msg = registrar_producto(
                    codigo, nombre, desc, cat_id, precio, stock, stock_min
                )
            if ok:
                self.accept()
            else:
                self._show_error(msg)
        except Exception as e:
            self._show_error(f"Error de conexión: {e}")

    def _show_error(self, msg):
        self.lbl_error.setText(f"⚠  {msg}")
        self.lbl_error.show()


# ── Pantalla principal de Inventario ─────────────────────────────────────────
class InventarioView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load_table)
        try:
            self._categorias = listar_categorias()
        except Exception:
            self._categorias = []
        self._setup_ui()
        self._load_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Encabezado
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        lbl_title = QLabel("Inventario")
        lbl_title.setFont(QFont("Arial", 22, QFont.Bold))
        lbl_title.setStyleSheet(f"color:{COLORS['primary']}; background:transparent;")

        lbl_sub = QLabel("Gestión de productos y stock")
        lbl_sub.setFont(QFont("Arial", 12))
        lbl_sub.setStyleSheet(f"color:{COLORS['muted']}; background:transparent;")

        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)

        self.btn_nuevo = QPushButton("  +  Nuevo Producto")
        self.btn_nuevo.setObjectName("btn_primary")
        self.btn_nuevo.setFixedHeight(44)
        self.btn_nuevo.setMinimumWidth(170)
        self.btn_nuevo.setFont(QFont("Arial", 13, QFont.DemiBold))
        self.btn_nuevo.setCursor(Qt.PointingHandCursor)
        self.btn_nuevo.clicked.connect(self._abrir_nuevo)

        header.addLayout(title_col)
        header.addStretch()
        header.addWidget(self.btn_nuevo)
        layout.addLayout(header)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o código...")
        self.search_input.setFixedHeight(42)
        self.search_input.setMinimumWidth(280)
        self.search_input.textChanged.connect(self._on_search_change)

        self.cat_filter = QComboBox()
        self.cat_filter.setFixedHeight(42)
        self.cat_filter.setMinimumWidth(180)
        self.cat_filter.addItem("Todas las categorías", None)
        for c in self._categorias:
            self.cat_filter.addItem(c["nombre"], c["id"])
        self.cat_filter.currentIndexChanged.connect(self._load_table)

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet(
            f"color:{COLORS['muted']}; font-size:13px; background:transparent;"
        )

        filtros.addWidget(self.search_input, 3)
        filtros.addWidget(self.cat_filter, 1)
        filtros.addStretch()
        filtros.addWidget(self.lbl_count)
        layout.addLayout(filtros)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["Código", "Nombre", "Categoría", "Precio", "Stock", "Mín.", "Estado", "Acciones"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 165)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.table)

    def _on_search_change(self):
        self._search_timer.start(300)

    def _load_table(self):
        try:
            texto    = self.search_input.text()
            cat_id   = self.cat_filter.currentData()
            productos = buscar_productos(texto, cat_id)
        except Exception as e:
            self.lbl_count.setText(f"Error de conexión: {e}")
            return

        self.table.setRowCount(len(productos))
        for row, p in enumerate(productos):
            self.table.setRowHeight(row, 50)

            items = [
                (p.codigo,                     Qt.AlignLeft),
                (p.nombre,                     Qt.AlignLeft),
                (p.categoria or "—",           Qt.AlignLeft),
                (f"$ {p.precio_unitario:,.0f}", Qt.AlignRight),
                (str(p.stock_actual),          Qt.AlignCenter),
                (str(p.stock_minimo),          Qt.AlignCenter),
            ]
            for col, (val, align) in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(align | Qt.AlignVCenter)
                if col == 4 and p.stock_actual <= p.stock_minimo:
                    item.setForeground(QColor(COLORS["danger"]))
                    item.setFont(QFont("Arial", 12, QFont.Bold))
                self.table.setItem(row, col, item)

            # Badge estado
            if p.stock_actual == 0:
                badge_text  = "Sin stock"
                badge_style = "background:#FDEDEC; color:#E74C3C;"
            elif p.stock_actual <= p.stock_minimo:
                badge_text  = "Stock bajo"
                badge_style = "background:#FEF9E7; color:#F39C12;"
            else:
                badge_text  = "OK"
                badge_style = "background:#EAFAF1; color:#27AE60;"

            badge = QLabel(badge_text)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(
                badge_style +
                "border-radius:5px; padding:3px 10px; font-weight:700; font-size:12px;"
            )
            cw = QWidget()
            cw.setStyleSheet("background:transparent;")
            cl = QHBoxLayout(cw)
            cl.setContentsMargins(6, 0, 6, 0)
            cl.addStretch()
            cl.addWidget(badge)
            cl.addStretch()
            self.table.setCellWidget(row, 6, cw)

            # Botones acción
            aw = QWidget()
            aw.setStyleSheet("background:transparent;")
            al = QHBoxLayout(aw)
            al.setContentsMargins(6, 4, 6, 4)
            al.setSpacing(6)

            btn_edit = QPushButton("✏  Editar")
            btn_edit.setFixedHeight(32)
            btn_edit.setObjectName("btn_table_edit")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, pid=p.id: self._editar(pid))

            btn_del = QPushButton("🗑  Eliminar")
            btn_del.setFixedHeight(32)
            btn_del.setObjectName("btn_table_delete")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(
                lambda _, pid=p.id, pnom=p.nombre: self._eliminar(pid, pnom)
            )

            al.addWidget(btn_edit)
            al.addWidget(btn_del)
            self.table.setCellWidget(row, 7, aw)

        count = len(productos)
        self.lbl_count.setText(
            f"{count} producto{'s' if count != 1 else ''} "
            f"encontrado{'s' if count != 1 else ''}"
        )

    def _abrir_nuevo(self):
        dlg = DialogProducto(self)
        if dlg.exec() == QDialog.Accepted:
            self._load_table()
            self._show_toast("Producto registrado correctamente.")

    def _editar(self, pid: int):
        try:
            producto = obtener_producto(pid)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        if not producto:
            return
        dlg = DialogProducto(self, producto)
        if dlg.exec() == QDialog.Accepted:
            self._load_table()
            self._show_toast("Producto actualizado.")

    def _eliminar(self, pid: int, nombre: str):
        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Deseas eliminar '{nombre}' del catálogo?\n"
            "Esta acción lo marcará como inactivo.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            try:
                ok, msg = desactivar_producto(pid)
                if ok:
                    self._load_table()
                    self._show_toast("Producto eliminado del catálogo.")
                else:
                    QMessageBox.warning(self, "Error", msg)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _show_toast(self, msg: str):
        toast = QLabel(msg, self)
        toast.setStyleSheet(
            "background:#1A2942; color:white; border-radius:8px;"
            "padding:10px 20px; font-weight:600; font-size:13px;"
        )
        toast.adjustSize()
        toast.move(self.width() // 2 - toast.width() // 2, 16)
        toast.show()
        QTimer.singleShot(2500, toast.deleteLater)
