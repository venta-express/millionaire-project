"""
AutoParts Express - Módulo de Promociones y Descuentos
HU-12: Configuración de Promociones (Sprint 3)

Accesible para: Gerencia solamente.
Permite crear, activar/desactivar y eliminar promociones
con vigencia por fechas para productos o categorías.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QHeaderView,
    QAbstractItemView, QComboBox, QDialog, QDialogButtonBox,
    QLineEdit, QDateEdit, QDoubleSpinBox, QButtonGroup,
    QRadioButton, QMessageBox, QFormLayout, QGroupBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui  import QFont, QColor

from utils.constants import FONT_FAMILY, LABEL_ATENCION
from utils.styles     import COLORS
from models.auth      import get_usuario_activo
from models.promociones import (
    listar_promociones, crear_promocion,
    activar_desactivar_promocion, eliminar_promocion
)
from models.inventario import listar_categorias, buscar_productos
from datetime import date as date_type



# ── Helpers de módulo ──────────────────────────────────────────────────────────
def _fmt_fecha(f) -> str:
    """Formatea un objeto date o str a dd/MM/yy."""
    return f.strftime("%d/%m/%y") if hasattr(f, "strftime") else str(f)


def _estado_promo(activa: bool, fecha_ini, fecha_fin, hoy) -> tuple[str, str, str]:
    """Calcula el texto, color de fondo y color de texto del estado de una promoción."""
    fi_d = fecha_ini if isinstance(fecha_ini, date_type) else date_type.fromisoformat(str(fecha_ini))
    ff_d = fecha_fin if isinstance(fecha_fin, date_type) else date_type.fromisoformat(str(fecha_fin))
    if activa and fi_d <= hoy <= ff_d:
        return "✅ Vigente",  "#D4EDDA", "#155724"
    if activa and hoy > ff_d:
        return "⌛ Vencida",  "#FFF3CD", "#856404"
    return "⏸ Inactiva", "#F8D7DA", "#721C24"


class PromocionesView(QWidget):
    """
    Vista del módulo de Promociones.
    Muestra tabla con todas las promociones y permite crear nuevas.
    Botones de acción: activar/desactivar y eliminar.
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        self._setup_ui()
        self._cargar()

    def _setup_ui(self):
        """Construye el layout principal del módulo."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── Encabezado ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        titulo = QLabel("🏷️  Promociones")
        titulo.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")

        subtitulo = QLabel("Descuentos automáticos por producto o categoría")
        subtitulo.setFont(QFont(FONT_FAMILY, 11))
        subtitulo.setStyleSheet(f"color: {COLORS['muted']};")

        title_col.addWidget(titulo)
        title_col.addWidget(subtitulo)
        header.addLayout(title_col)
        header.addStretch()

        btn_nuevo = QPushButton("＋  Nueva Promoción")
        btn_nuevo.setObjectName("btn_primary")
        btn_nuevo.setFixedHeight(40)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._abrir_dialogo)
        header.addWidget(btn_nuevo)

        layout.addLayout(header)

        # ── Filtro solo activas ───────────────────────────────────────────────
        filtro_row = QHBoxLayout()
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todas las promociones", "Solo activas y vigentes"])
        self.combo_filtro.setFixedWidth(240)
        self.combo_filtro.currentIndexChanged.connect(self._cargar)
        filtro_row.addWidget(QLabel("Mostrar:"))
        filtro_row.addWidget(self.combo_filtro)
        filtro_row.addStretch()
        layout.addLayout(filtro_row)

        # ── Tabla de promociones ──────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("QFrame#card { background: white; border-radius: 12px; }")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 16, 16, 16)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels([
            "Nombre", "Tipo", "Valor",
            "Aplica a", "Vigencia", "Estado",
            "Act.", "🗑", "▶"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)

        card_lay.addWidget(self.tabla)
        layout.addWidget(card)

    def _cargar(self):
        """Consulta la BD y llena la tabla con las promociones."""
        solo_activas = self.combo_filtro.currentIndex() == 1
        promociones = listar_promociones(solo_activas=solo_activas)

        self.tabla.setRowCount(0)
        hoy = date_type.today()

        for promo in promociones:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)

            # Guardamos el ID de la promoción en UserRole de la primera celda
            it0 = QTableWidgetItem(promo["nombre"])
            it0.setData(Qt.UserRole, promo["id"])
            self.tabla.setItem(fila, 0, it0)

            # Tipo de descuento en texto legible
            tipo_txt = "Porcentaje" if promo["tipo_descuento"] == "porcentaje" else "Valor Fijo"
            self.tabla.setItem(fila, 1, QTableWidgetItem(tipo_txt))

            # Valor con formato según el tipo
            if promo["tipo_descuento"] == "porcentaje":
                val_txt = f"{float(promo['valor']):.1f}%"
            else:
                val_txt = f"${float(promo['valor']):,.2f}"
            it_val = QTableWidgetItem(val_txt)
            it_val.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(fila, 2, it_val)

            # Columna "Aplica a": nombre del producto o de la categoría
            aplica = promo.get("producto_nombre") or promo.get("categoria_nombre") or "—"
            prefijo = "Prod:" if promo["producto_id"] else "Cat:"
            self.tabla.setItem(fila, 3, QTableWidgetItem(f"{prefijo} {aplica}"))

            # Vigencia: rango de fechas
            fi = promo["fecha_inicio"]
            ff = promo["fecha_fin"]
            vigencia = f"{_fmt_fecha(fi)} → {_fmt_fecha(ff)}"
            it_vig = QTableWidgetItem(vigencia)
            it_vig.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(fila, 4, it_vig)

            # Estado: activa+vigente / activa+vencida / inactiva
            estado_txt, est_bg, est_fg = _estado_promo(
                promo["activa"], promo["fecha_inicio"], promo["fecha_fin"], hoy
            )

            est_lbl = QLabel(f"  {estado_txt}  ")
            est_lbl.setAlignment(Qt.AlignCenter)
            est_lbl.setFont(QFont(FONT_FAMILY, 11))
            est_lbl.setStyleSheet(
                f"background:{est_bg}; color:{est_fg}; border-radius:6px; padding:2px 4px;"
            )
            self.tabla.setCellWidget(fila, 5, est_lbl)

            # Col 6: toggle activa/inactiva
            pid = promo["id"]
            if promo["activa"]:
                btn_tog = QPushButton("⏸ Pausar")
                btn_tog.setObjectName("btn_table_cancel")
            else:
                btn_tog = QPushButton("▶ Activar")
                btn_tog.setObjectName("btn_table_confirm")
            btn_tog.setCursor(Qt.PointingHandCursor)
            btn_tog.clicked.connect(
                lambda _, i=pid, a=promo["activa"]: self._toggle(i, not a)
            )
            self.tabla.setCellWidget(fila, 6, btn_tog)

            # Col 7: eliminar
            btn_del = QPushButton("🗑")
            btn_del.setObjectName("btn_table_delete")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, i=pid: self._eliminar(i))
            self.tabla.setCellWidget(fila, 7, btn_del)

            # Col 8: ver/editar (placeholder — Sprint 4)
            btn_ver = QPushButton("👁")
            btn_ver.setObjectName("btn_table_view")
            btn_ver.setCursor(Qt.PointingHandCursor)
            btn_ver.setToolTip(f"ID: {pid}")
            self.tabla.setCellWidget(fila, 8, btn_ver)

            self.tabla.setRowHeight(fila, 44)

    # ── Acciones ───────────────────────────────────────────────────────────────
    def _toggle(self, promo_id: int, nuevo_estado: bool):
        """Activa o desactiva una promoción."""
        ok, msg = activar_desactivar_promocion(promo_id, nuevo_estado)
        if ok:
            self._cargar()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _eliminar(self, promo_id: int):
        """Pide confirmación y elimina la promoción."""
        resp = QMessageBox.question(
            self, "Eliminar promoción",
            "¿Eliminar esta promoción definitivamente?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            ok, msg = eliminar_promocion(promo_id)
            if ok:
                self._cargar()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _abrir_dialogo(self):
        """Abre el diálogo para crear una nueva promoción."""
        dlg = DialogoPromocion(self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()


class DialogoPromocion(QDialog):
    """Diálogo para crear una nueva promoción."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Promoción")
        self.setMinimumWidth(520)
        self._setup_ui()

    def _setup_ui(self):
        """Construye el formulario de creación de promoción."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        titulo = QLabel("🏷️  Nueva Promoción")
        titulo.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        def inp(placeholder):
            """Helper que crea un QLineEdit estilizado."""
            f = QLineEdit()
            f.setPlaceholderText(placeholder)
            f.setFixedHeight(36)
            f.setStyleSheet("""
                QLineEdit { border: 1.5px solid #D8E0EC; border-radius: 8px;
                            padding: 0 12px; font-size: 13px; background: white; }
                QLineEdit:focus { border-color: #FF6B2B; }
            """)
            return f

        # Nombre de la promoción
        self.inp_nombre = inp("Ej: Descuento Frenos Semana Santa")
        form.addRow("Nombre *", self.inp_nombre)

        # Tipo de descuento con radio buttons
        tipo_grp = QGroupBox()
        tipo_grp.setFlat(True)
        tipo_lay = QHBoxLayout(tipo_grp)
        tipo_lay.setContentsMargins(0, 0, 0, 0)
        self.radio_pct = QRadioButton("Porcentaje (%)")
        self.radio_fijo = QRadioButton("Valor Fijo ($)")
        self.radio_pct.setChecked(True)       # Porcentaje seleccionado por defecto
        tipo_lay.addWidget(self.radio_pct)
        tipo_lay.addWidget(self.radio_fijo)
        tipo_lay.addStretch()
        form.addRow("Tipo *", tipo_grp)

        # Valor del descuento
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setMinimum(0.01)
        self.spin_valor.setMaximum(100.0)     # Máximo 100% o valor libre
        self.spin_valor.setValue(10.0)
        self.spin_valor.setFixedHeight(36)
        self.spin_valor.setSuffix(" %")       # Sufijo actualizable al cambiar tipo
        # Actualizar el máximo y sufijo al cambiar el tipo
        self.radio_pct.toggled.connect(self._actualizar_spin)
        form.addRow("Valor *", self.spin_valor)

        # Target: producto o categoría
        target_grp = QGroupBox()
        target_grp.setFlat(True)
        target_lay = QHBoxLayout(target_grp)
        target_lay.setContentsMargins(0, 0, 0, 0)
        self.radio_producto  = QRadioButton("Producto específico")
        self.radio_categoria = QRadioButton("Categoría completa")
        self.radio_producto.setChecked(True)
        self.radio_producto.toggled.connect(self._actualizar_target)
        target_lay.addWidget(self.radio_producto)
        target_lay.addWidget(self.radio_categoria)
        target_lay.addStretch()
        form.addRow("Aplica a *", target_grp)

        # Campo para buscar producto
        self.inp_prod = inp("Nombre o código del producto...")
        form.addRow("Producto", self.inp_prod)

        # ComboBox de categorías (oculto inicialmente)
        self.combo_cat = QComboBox()
        self.combo_cat.setFixedHeight(36)
        for cat in listar_categorias():
            self.combo_cat.addItem(cat["nombre"], cat["id"])
        self.combo_cat.hide()           # Mostrar solo si se elige "Categoría"
        form.addRow("Categoría", self.combo_cat)

        # Fechas de vigencia
        hoy = QDate.currentDate()
        self.date_ini = QDateEdit()
        self.date_ini.setCalendarPopup(True)
        self.date_ini.setDate(hoy)
        self.date_ini.setDisplayFormat("dd/MM/yyyy")
        self.date_ini.setFixedHeight(36)
        form.addRow("Fecha inicio *", self.date_ini)

        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(hoy.addDays(30))  # Por defecto 30 días
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.setFixedHeight(36)
        form.addRow("Fecha fin *", self.date_fin)

        layout.addLayout(form)

        # Botones
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Crear Promoción")
        botones.button(QDialogButtonBox.Ok).setObjectName("btn_primary")
        botones.accepted.connect(self._confirmar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _actualizar_spin(self, pct_checked: bool):
        """Actualiza el SpinBox al cambiar de tipo de descuento."""
        if pct_checked:
            self.spin_valor.setMaximum(100.0)
            self.spin_valor.setSuffix(" %")
            self.spin_valor.setValue(min(self.spin_valor.value(), 100.0))
        else:
            self.spin_valor.setMaximum(9_999_999.0)
            self.spin_valor.setSuffix("")

    def _actualizar_target(self, prod_checked: bool):
        """Muestra el campo de producto u oculta el combo de categoría."""
        self.inp_prod.setVisible(prod_checked)
        self.combo_cat.setVisible(not prod_checked)

    def _confirmar(self):
        """Valida y registra la nueva promoción."""
        nombre = self.inp_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, LABEL_ATENCION, "El nombre es obligatorio.")
            return

        tipo = "porcentaje" if self.radio_pct.isChecked() else "valor_fijo"
        valor = self.spin_valor.value()

        # Determinamos el target (producto o categoría)
        producto_id  = None
        categoria_id = None

        if self.radio_producto.isChecked():
            texto = self.inp_prod.text().strip()
            if not texto:
                QMessageBox.warning(self, LABEL_ATENCION, "Ingresa el producto.")
                return
            resultados = buscar_productos(texto, solo_activos=True)
            if not resultados:
                QMessageBox.warning(self, "No encontrado",
                                    f"No se encontró '{texto}'.")
                return
            producto_id = resultados[0].id
        else:
            categoria_id = self.combo_cat.currentData()
            if not categoria_id:
                QMessageBox.warning(self, LABEL_ATENCION, "Selecciona una categoría.")
                return

        # Convertimos fechas de QDate a date de Python
        def qdate_to_date(qd):
            return date_type(qd.year(), qd.month(), qd.day())

        fi = qdate_to_date(self.date_ini.date())
        ff = qdate_to_date(self.date_fin.date())

        usuario = get_usuario_activo()

        ok, msg = crear_promocion(
            nombre=nombre,
            tipo_descuento=tipo,
            valor=valor,
            producto_id=producto_id,
            categoria_id=categoria_id,
            fecha_inicio=fi,
            fecha_fin=ff,
            creado_por=usuario.id
        )

        if ok:
            QMessageBox.information(self, "Éxito", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", msg)
