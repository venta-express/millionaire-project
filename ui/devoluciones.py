"""
AutoParts Express - Módulo de Devoluciones a Proveedores
HU-11: Devoluciones a Proveedores (Sprint 3)

Accesible para: Gerencia e Inventario.
Permite registrar devoluciones de productos defectuosos y
cambiar su estado (Pendiente → Procesada | Rechazada).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QHeaderView,
    QAbstractItemView, QComboBox, QDialog, QDialogButtonBox,
    QLineEdit, QTextEdit, QSpinBox, QMessageBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui  import QFont, QColor

from utils.constants import FONT_FAMILY
from utils.styles        import COLORS
from models.auth         import get_usuario_activo
from models.devoluciones import (
    registrar_devolucion, listar_devoluciones, actualizar_estado_devolucion
)
from models.compras      import listar_proveedores
from models.inventario   import buscar_productos


class DevolucionesView(QWidget):
    """
    Vista del módulo de Devoluciones.
    Muestra tabla con filtro por estado y proveedor.
    Botón para registrar nueva devolución.
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        self._setup_ui()
        self._cargar()

    def _setup_ui(self):
        """Construye el layout principal."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── Encabezado ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        titulo = QLabel("↩  Devoluciones")
        titulo.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")

        subtitulo = QLabel("Registro de devoluciones a proveedores")
        subtitulo.setFont(QFont(FONT_FAMILY, 11))
        subtitulo.setStyleSheet(f"color: {COLORS['muted']};")

        title_col.addWidget(titulo)
        title_col.addWidget(subtitulo)
        header.addLayout(title_col)
        header.addStretch()

        # Botón nueva devolución
        btn_nuevo = QPushButton("＋  Nueva Devolución")
        btn_nuevo.setObjectName("btn_primary")
        btn_nuevo.setFixedHeight(40)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._abrir_dialogo)
        header.addWidget(btn_nuevo)

        layout.addLayout(header)

        # ── Filtros ───────────────────────────────────────────────────────────
        filtro_row = QHBoxLayout()
        filtro_row.setSpacing(12)

        filtro_row.addWidget(QLabel("Estado:"))
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "Pendiente", "Procesada", "Rechazada"])
        self.combo_estado.setFixedWidth(160)
        self.combo_estado.currentTextChanged.connect(self._cargar)
        filtro_row.addWidget(self.combo_estado)

        filtro_row.addWidget(QLabel("Proveedor:"))
        self.combo_prov = QComboBox()
        self.combo_prov.setFixedWidth(220)
        self.combo_prov.addItem("Todos", None)
        for p in listar_proveedores(solo_activos=False):
            self.combo_prov.addItem(p.nombre, p.id)
        self.combo_prov.currentIndexChanged.connect(self._cargar)
        filtro_row.addWidget(self.combo_prov)

        filtro_row.addStretch()
        layout.addLayout(filtro_row)

        # ── Tabla ─────────────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("QFrame#card { background: white; border-radius: 12px; }")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 16, 16, 16)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Nº Dev.", "Proveedor", "Producto",
            "Cant.", "Motivo", "Estado", "Fecha", "Acción"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)

        card_lay.addWidget(self.tabla)
        layout.addWidget(card)

    def _cargar(self):
        """Consulta la BD con los filtros activos y llena la tabla."""
        estado_sel = self.combo_estado.currentText()
        estado = None if estado_sel == "Todos" else estado_sel
        prov_id = self.combo_prov.currentData()

        devoluciones = listar_devoluciones(estado=estado, proveedor_id=prov_id)
        self.tabla.setRowCount(0)

        for dev in devoluciones:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)

            # Col 0: número de devolución (guarda ID en UserRole)
            it0 = QTableWidgetItem(dev.numero_dev)
            it0.setData(Qt.UserRole, dev.id)
            self.tabla.setItem(fila, 0, it0)

            # Col 1-4: datos de la devolución
            self.tabla.setItem(fila, 1, QTableWidgetItem(dev.proveedor_nombre))
            self.tabla.setItem(fila, 2,
                QTableWidgetItem(f"[{dev.producto_codigo}] {dev.producto_nombre}"))
            c = QTableWidgetItem(str(dev.cantidad))
            c.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(fila, 3, c)
            # Truncamos el motivo a 60 caracteres para que quepa en la celda
            motivo_corto = dev.motivo[:60] + ("…" if len(dev.motivo) > 60 else "")
            self.tabla.setItem(fila, 4, QTableWidgetItem(motivo_corto))

            # Col 5: badge de estado con color semántico
            est_lbl = QLabel(f"  {dev.estado}  ")
            est_lbl.setAlignment(Qt.AlignCenter)
            est_lbl.setFont(QFont(FONT_FAMILY, 11, QFont.DemiBold))
            colores = {
                "Pendiente": ("#FFF3CD", "#856404"),
                "Procesada": ("#D4EDDA", "#155724"),
                "Rechazada": ("#F8D7DA", "#721C24"),
            }
            bg, fg = colores.get(dev.estado, ("#EEE", "#333"))
            est_lbl.setStyleSheet(
                f"background:{bg}; color:{fg}; border-radius:6px; padding:2px 6px;"
            )
            self.tabla.setCellWidget(fila, 5, est_lbl)

            # Col 6: fecha formateada
            self.tabla.setItem(fila, 6,
                QTableWidgetItem(dev.fecha.strftime("%d/%m/%Y")))

            # Col 7: botón de cambiar estado (solo si está Pendiente)
            if dev.estado == "Pendiente":
                self.tabla.setCellWidget(fila, 7,
                    self._btn_accion(dev.id))
            else:
                self.tabla.setItem(fila, 7, QTableWidgetItem("—"))

            self.tabla.setRowHeight(fila, 44)

    def _btn_accion(self, dev_id: int) -> QWidget:
        """Crea un widget con los botones Procesar y Rechazar para una devolución."""
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(4, 4, 4, 4)
        row.setSpacing(4)

        btn_proc = QPushButton("✔ Procesar")
        btn_proc.setObjectName("btn_table_confirm")
        btn_proc.setCursor(Qt.PointingHandCursor)
        btn_proc.clicked.connect(
            lambda _, did=dev_id: self._cambiar_estado(did, "Procesada")
        )

        btn_rech = QPushButton("✕ Rechazar")
        btn_rech.setObjectName("btn_table_delete")
        btn_rech.setCursor(Qt.PointingHandCursor)
        btn_rech.clicked.connect(
            lambda _, did=dev_id: self._cambiar_estado(did, "Rechazada")
        )

        row.addWidget(btn_proc)
        row.addWidget(btn_rech)
        row.addStretch()
        return w

    def _cambiar_estado(self, dev_id: int, nuevo_estado: str):
        """Confirma y cambia el estado de la devolución."""
        msg = (
            "¿Confirmas procesar esta devolución?\n"
            "El stock del producto permanecerá reducido."
            if nuevo_estado == "Procesada"
            else "¿Rechazar esta devolución?\nSe restaurará el stock del producto."
        )
        resp = QMessageBox.question(self, f"Confirmar — {nuevo_estado}", msg,
                                    QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return

        ok, msg_r = actualizar_estado_devolucion(dev_id, nuevo_estado)
        if ok:
            QMessageBox.information(self, "Éxito", msg_r)
        else:
            QMessageBox.warning(self, "Error", msg_r)
        self._cargar()

    def _abrir_dialogo(self):
        """Abre el diálogo para registrar una nueva devolución."""
        dlg = DialogoDevolucion(self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()


class DialogoDevolucion(QDialog):
    """Diálogo modal para registrar una nueva devolución a proveedor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Devolución a Proveedor")
        self.setMinimumWidth(500)
        self._setup_ui()

    def _setup_ui(self):
        """Construye el formulario de la devolución."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        titulo = QLabel("↩  Registrar Devolución")
        titulo.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        def inp(placeholder):
            """Helper para crear campos de texto con estilo."""
            f = QLineEdit()
            f.setPlaceholderText(placeholder)
            f.setFixedHeight(36)
            f.setStyleSheet("""
                QLineEdit {
                    border: 1.5px solid #D8E0EC; border-radius: 8px;
                    padding: 0 12px; font-size: 13px; background: white;
                }
                QLineEdit:focus { border-color: #FF6B2B; }
            """)
            return f

        # Selector de proveedor
        self.combo_prov = QComboBox()
        self.combo_prov.setFixedHeight(36)
        self._proveedores = listar_proveedores(solo_activos=True)
        for p in self._proveedores:
            self.combo_prov.addItem(p.nombre, p.id)
        form.addRow("Proveedor *", self.combo_prov)

        # Campo de búsqueda de producto
        self.inp_prod = inp("Buscar producto por nombre o código...")
        form.addRow("Producto *", self.inp_prod)

        # Cantidad a devolver
        self.spin_cant = QSpinBox()
        self.spin_cant.setMinimum(1)
        self.spin_cant.setMaximum(9999)
        self.spin_cant.setValue(1)
        self.spin_cant.setFixedHeight(36)
        form.addRow("Cantidad *", self.spin_cant)

        # Motivo de la devolución
        self.txt_motivo = QTextEdit()
        self.txt_motivo.setFixedHeight(80)
        self.txt_motivo.setPlaceholderText(
            "Describa el motivo: defecto de fabricación, producto incorrecto, exceso..."
        )
        self.txt_motivo.setStyleSheet("""
            QTextEdit {
                border: 1.5px solid #D8E0EC; border-radius: 8px;
                padding: 8px; font-size: 13px; background: white;
            }
            QTextEdit:focus { border-color: #FF6B2B; }
        """)
        form.addRow("Motivo *", self.txt_motivo)

        layout.addLayout(form)

        # Botones del diálogo
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Registrar Devolución")
        botones.button(QDialogButtonBox.Ok).setObjectName("btn_primary")
        botones.accepted.connect(self._confirmar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _confirmar(self):
        """Valida y registra la devolución."""
        motivo = self.txt_motivo.toPlainText().strip()
        if not motivo:
            QMessageBox.warning(self, "Atención", "El motivo es obligatorio.")
            return

        texto_prod = self.inp_prod.text().strip()
        if not texto_prod:
            QMessageBox.warning(self, "Atención", "Ingresa el producto a devolver.")
            return

        # Buscamos el producto
        resultados = buscar_productos(texto_prod, solo_activos=True)
        if not resultados:
            QMessageBox.warning(self, "No encontrado",
                                f"No se encontró producto con '{texto_prod}'.")
            return

        prod = resultados[0]   # Primer resultado
        proveedor_id = self.combo_prov.currentData()
        usuario = get_usuario_activo()

        ok, msg, _ = registrar_devolucion(
            proveedor_id=proveedor_id,
            producto_id=prod.id,
            usuario_id=usuario.id,
            cantidad=self.spin_cant.value(),
            motivo=motivo
        )

        if ok:
            QMessageBox.information(self, "Éxito", f"Devolución {msg} registrada.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", msg)
