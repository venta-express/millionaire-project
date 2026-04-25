"""
AutoParts Express - Módulo de Compras (Pedidos a Proveedores)
HU-06: Gestión de Pedidos a Proveedores (Sprint 2)

Permite al encargado de inventario:
  - Ver la lista de proveedores activos
  - Crear pedidos seleccionando proveedor, productos y cantidades
  - Consultar el estado de todos los pedidos
  - Marcar un pedido como 'Recibido' (lo que actualiza el stock)
  - Ver alertas de pedidos vencidos (fecha estimada ya pasó)
"""

# Widgets de Qt para construir la interfaz
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QFrame,
    QHeaderView, QAbstractItemView, QComboBox, QDateEdit,
    QTextEdit, QDialog, QDialogButtonBox, QSpinBox,
    QMessageBox, QScrollArea, QSplitter, QGroupBox
)

# Clases de comportamiento y tipografía de Qt
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor

# Paleta de colores compartida
from utils.styles import COLORS
# Constante para evitar literales duplicados (SonarCloud)
MSG_ATENCION = "Atención"

from utils.constants import FONT_FAMILY, APP_NAME, LABEL_ATENCION

# Modelo de autenticación para obtener el usuario actual
from models.auth import get_usuario_activo

# Modelos de compras e inventario
from models.compras import (
    listar_proveedores, registrar_pedido, listar_pedidos,
    obtener_pedido_detalle, actualizar_estado_pedido,
    pedidos_pendientes_vencidos
)
from models.inventario import buscar_productos


class ComprasView(QWidget):
    """
    Vista principal del módulo de Compras.
    Composición:
      - Pestaña de pedidos: tabla de pedidos con filtro por estado
      - Botón para crear nuevo pedido (abre diálogo modal)
      - Panel de alerta para pedidos vencidos
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        self._setup_ui()   # Construimos la interfaz
        self._cargar_pedidos()  # Cargamos los datos iniciales

    # ── Construcción de UI ─────────────────────────────────────────────────────
    def _setup_ui(self):
        """Construye el layout principal del módulo de compras."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── Encabezado ────────────────────────────────────────────────────────
        header = QHBoxLayout()

        # Bloque de título y subtítulo
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        titulo = QLabel("🛒  Compras")
        titulo.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")

        subtitulo = QLabel("Gestión de pedidos a proveedores")
        subtitulo.setFont(QFont(FONT_FAMILY, 11))
        subtitulo.setStyleSheet(f"color: {COLORS['muted']};")

        title_col.addWidget(titulo)
        title_col.addWidget(subtitulo)
        header.addLayout(title_col)
        header.addStretch()

        # Botón para abrir el diálogo de nuevo pedido
        self.btn_nuevo = QPushButton("＋  Nuevo Pedido")
        self.btn_nuevo.setObjectName("btn_primary")
        self.btn_nuevo.setFixedHeight(40)
        self.btn_nuevo.setCursor(Qt.PointingHandCursor)
        self.btn_nuevo.clicked.connect(self._abrir_dialogo_pedido)
        header.addWidget(self.btn_nuevo)

        layout.addLayout(header)

        # ── Alerta de pedidos vencidos ────────────────────────────────────────
        self.frame_alerta = QFrame()
        self.frame_alerta.setStyleSheet("""
            QFrame {
                background: #FFF3CD;
                border: 1.5px solid #F39C12;
                border-radius: 10px;
            }
        """)
        alerta_layout = QHBoxLayout(self.frame_alerta)
        alerta_layout.setContentsMargins(16, 10, 16, 10)

        # Ícono y texto de alerta
        self.lbl_alerta = QLabel()
        self.lbl_alerta.setFont(QFont(FONT_FAMILY, 12))
        self.lbl_alerta.setStyleSheet("color: #856404;")
        alerta_layout.addWidget(self.lbl_alerta)
        alerta_layout.addStretch()

        # Ocultamos el frame hasta verificar si hay vencidos
        self.frame_alerta.hide()
        layout.addWidget(self.frame_alerta)

        # ── Filtro por estado ─────────────────────────────────────────────────
        filtro_row = QHBoxLayout()

        lbl_filtro = QLabel("Filtrar por estado:")
        lbl_filtro.setFont(QFont(FONT_FAMILY, 12))
        lbl_filtro.setStyleSheet(f"color: {COLORS['text']};")

        # ComboBox con los estados posibles + opción "Todos"
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "Pendiente", "Recibido", "Cancelado"])
        self.combo_estado.setFixedWidth(180)
        self.combo_estado.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #D1D9E6;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                background: white;
            }
        """)
        # Recargamos la tabla al cambiar el filtro
        self.combo_estado.currentTextChanged.connect(self._cargar_pedidos)

        filtro_row.addWidget(lbl_filtro)
        filtro_row.addWidget(self.combo_estado)
        filtro_row.addStretch()
        layout.addLayout(filtro_row)

        # ── Tabla de pedidos ──────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("QFrame#card { background: white; border-radius: 12px; }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)  # 6 columnas de información
        self.tabla.setHorizontalHeaderLabels([
            "Nº Pedido", "Proveedor", "Fecha Pedido",
            "Entrega Estimada", "Estado", "Acciones"
        ])

        # Hacemos que la columna de proveedor sea flexible
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setFixedHeight(400)
        self.tabla.setStyleSheet("""
            QTableWidget { border: none; font-size: 13px; }
            QHeaderView::section {
                background: #F0F4FA; font-weight: 600;
                padding: 8px; border: none;
                border-bottom: 2px solid #E0E6F0;
            }
            QTableWidget::item:selected { background: #E8F0FE; color: #1A2942; }
            QTableWidget::item:alternate { background: #F8FAFD; }
        """)

        card_layout.addWidget(self.tabla)
        layout.addWidget(card)
        layout.addStretch()

    # ── Carga de datos ─────────────────────────────────────────────────────────
    def _cargar_pedidos(self):
        """
        Consulta los pedidos en la BD según el filtro de estado activo
        y llena la tabla con los resultados.
        También actualiza la alerta de pedidos vencidos.
        """
        # Obtenemos el estado seleccionado en el ComboBox
        estado_sel = self.combo_estado.currentText()
        # Si es "Todos" pasamos None para no filtrar por estado
        estado = None if estado_sel == "Todos" else estado_sel

        # Consultamos el modelo
        pedidos = listar_pedidos(estado)

        # Limpiamos la tabla antes de rellenar
        self.tabla.setRowCount(0)

        for pedido in pedidos:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)

            # Col 0: número de pedido
            self.tabla.setItem(fila, 0, QTableWidgetItem(pedido["numero_pedido"]))

            # Col 1: nombre del proveedor
            self.tabla.setItem(fila, 1, QTableWidgetItem(pedido["proveedor_nombre"]))

            # Col 2: fecha de creación del pedido (solo fecha, sin hora)
            fecha_ped = pedido["fecha_pedido"].strftime("%d/%m/%Y")
            self.tabla.setItem(fila, 2, QTableWidgetItem(fecha_ped))

            # Col 3: fecha estimada de entrega
            from datetime import date as date_type
            fe = pedido["fecha_estimada"]
            # La fecha puede ser date o datetime según el driver
            if hasattr(fe, "strftime"):
                fecha_est = fe.strftime("%d/%m/%Y")
            else:
                fecha_est = str(fe)
            self.tabla.setItem(fila, 3, QTableWidgetItem(fecha_est))

            # Col 4: badge de estado con color semántico
            lbl_estado = QLabel(f"  {pedido['estado']}  ")
            lbl_estado.setAlignment(Qt.AlignCenter)
            lbl_estado.setFont(QFont(FONT_FAMILY, 11, QFont.DemiBold))

            # Colores según el estado del pedido
            colores = {
                "Pendiente": ("#FFF3CD", "#856404"),   # Amarillo suave
                "Recibido":  ("#D4EDDA", "#155724"),   # Verde suave
                "Cancelado": ("#F8D7DA", "#721C24"),   # Rojo suave
            }
            bg, fg = colores.get(pedido["estado"], ("#EEEEEE", "#333333"))
            lbl_estado.setStyleSheet(
                f"background: {bg}; color: {fg}; border-radius: 6px; padding: 2px 6px;"
            )
            self.tabla.setCellWidget(fila, 4, lbl_estado)

            # Col 5: botón de acción según el estado actual
            self.tabla.setCellWidget(fila, 5,
                self._crear_btn_accion(pedido["id"], pedido["estado"])
            )

            # Ajustamos la altura de la fila para que el badge quepa bien
            self.tabla.setRowHeight(fila, 42)

        # Verificamos y mostramos alerta de pedidos vencidos
        self._verificar_vencidos()

    def _crear_btn_accion(self, pedido_id: int, estado: str) -> QPushButton:
        """
        Crea el botón de acción adecuado para el estado del pedido.
        'Pendiente' → botón 'Marcar Recibido' (verde)
        Otros estados → botón 'Ver detalle' (gris)
        """
        if estado == "Pendiente":
            btn = QPushButton("✔  Recibido")
            btn.setObjectName("btn_table_confirm")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, pid=pedido_id: self._marcar_recibido(pid))
        else:
            btn = QPushButton("📄  Ver")
            btn.setObjectName("btn_table_view")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, pid=pedido_id: self._ver_detalle(pid))

        return btn

    def _verificar_vencidos(self):
        """
        Consulta pedidos pendientes cuya fecha estimada ya venció
        y muestra u oculta el banner de advertencia según corresponda.
        """
        vencidos = pedidos_pendientes_vencidos()

        if vencidos:
            # Mostramos el frame de alerta con la cantidad de pedidos atrasados
            self.lbl_alerta.setText(
                f"⚠️  {len(vencidos)} pedido(s) pendiente(s) no han llegado en la fecha estimada. "
                "Revisa el estado con tus proveedores."
            )
            self.frame_alerta.show()
        else:
            # No hay vencidos; ocultamos el frame de alerta
            self.frame_alerta.hide()

    # ── Acciones ───────────────────────────────────────────────────────────────
    def _marcar_recibido(self, pedido_id: int):
        """
        Confirma con el usuario y marca el pedido como 'Recibido'.
        Al hacerlo, el modelo suma las cantidades al stock de cada producto.
        """
        resp = QMessageBox.question(
            self,
            "Confirmar recepción",
            "¿Confirmas que este pedido fue recibido?\n"
            "Esto actualizará el stock de los productos involucrados.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return  # El usuario canceló la acción

        # Llamamos al modelo para actualizar el estado y el stock
        ok, msg = actualizar_estado_pedido(pedido_id, "Recibido")

        if ok:
            QMessageBox.information(self, "Éxito", msg)
        else:
            QMessageBox.warning(self, "Error", msg)

        # Recargamos la tabla para reflejar el cambio
        self._cargar_pedidos()

    def _ver_detalle(self, pedido_id: int):
        """
        Abre un diálogo modal con el detalle completo del pedido.
        Muestra: cabecera + lista de productos solicitados.
        """
        pedido = obtener_pedido_detalle(pedido_id)
        if not pedido:
            QMessageBox.warning(self, "Error", "No se encontró el pedido.")
            return

        # Construimos el texto del detalle
        lineas = [
            f"Pedido:     {pedido['numero_pedido']}",
            f"Proveedor:  {pedido['proveedor_nombre']}",
            f"Creado por: {pedido['usuario_nombre']}",
            f"Estado:     {pedido['estado']}",
            f"Entrega:    {pedido['fecha_estimada']}",
            "",
            "── Ítems ──────────────────────────────────────────",
        ]
        for item in pedido.get("items", []):
            lineas.append(
                f"  [{item['codigo']}] {item['producto_nombre']}  ×  {item['cantidad']} unid."
            )

        if pedido.get("notas"):
            lineas += ["", f"Notas: {pedido['notas']}"]

        # Mostramos el detalle en un QMessageBox informativo
        QMessageBox.information(self, f"Detalle — {pedido['numero_pedido']}",
                                "\n".join(lineas))

    def _abrir_dialogo_pedido(self):
        """
        Abre el diálogo modal para crear un nuevo pedido.
        Al cerrarse con Aceptar, recargamos la tabla de pedidos.
        """
        dialogo = DialogoNuevoPedido(self)
        if dialogo.exec() == QDialog.Accepted:
            self._cargar_pedidos()  # Recargamos para mostrar el nuevo pedido


class DialogoNuevoPedido(QDialog):
    """
    Diálogo modal para registrar un nuevo pedido a un proveedor.
    El usuario selecciona: proveedor, fecha estimada, productos con cantidades.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Pedido a Proveedor")
        self.setMinimumWidth(640)
        self.setMinimumHeight(560)

        # Lista interna de ítems del pedido: [{producto_id, codigo, nombre, cantidad}]
        self._items: list[dict] = []

        self._setup_ui()   # Construimos la interfaz del diálogo

    def _setup_ui(self):
        """Construye el layout del diálogo de nuevo pedido."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Título del diálogo
        titulo = QLabel("📦  Nuevo Pedido a Proveedor")
        titulo.setFont(QFont(FONT_FAMILY, 15, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")
        layout.addWidget(titulo)

        # ── Proveedor ─────────────────────────────────────────────────────────
        lbl_prov = QLabel("Proveedor *")
        lbl_prov.setFont(QFont(FONT_FAMILY, 11, QFont.DemiBold))
        layout.addWidget(lbl_prov)

        self.combo_prov = QComboBox()
        self.combo_prov.setFixedHeight(38)
        self.combo_prov.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #D1D9E6; border-radius: 8px;
                padding: 0 12px; font-size: 13px; background: white;
            }
        """)

        # Cargamos los proveedores activos desde la BD
        self._proveedores = listar_proveedores(solo_activos=True)
        for prov in self._proveedores:
            self.combo_prov.addItem(prov.nombre, prov.id)  # ID como dato oculto
        layout.addWidget(self.combo_prov)

        # ── Fecha estimada de entrega ─────────────────────────────────────────
        lbl_fecha = QLabel("Fecha estimada de entrega *")
        lbl_fecha.setFont(QFont(FONT_FAMILY, 11, QFont.DemiBold))
        layout.addWidget(lbl_fecha)

        self.date_entrega = QDateEdit()
        self.date_entrega.setCalendarPopup(True)   # Muestra un calendario emergente
        self.date_entrega.setDate(QDate.currentDate().addDays(7))  # Por defecto +7 días
        self.date_entrega.setFixedHeight(38)
        self.date_entrega.setDisplayFormat("dd/MM/yyyy")
        self.date_entrega.setStyleSheet("""
            QDateEdit {
                border: 1.5px solid #D1D9E6; border-radius: 8px;
                padding: 0 12px; font-size: 13px; background: white;
            }
        """)
        layout.addWidget(self.date_entrega)

        # ── Selector de productos ─────────────────────────────────────────────
        lbl_prod = QLabel("Agregar productos al pedido")
        lbl_prod.setFont(QFont(FONT_FAMILY, 11, QFont.DemiBold))
        layout.addWidget(lbl_prod)

        add_row = QHBoxLayout()

        # Campo de búsqueda de producto por nombre o código
        self.inp_prod = QLineEdit()
        self.inp_prod.setPlaceholderText("Buscar producto por nombre o código...")
        self.inp_prod.setFixedHeight(36)
        self.inp_prod.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #D1D9E6; border-radius: 8px;
                padding: 0 12px; font-size: 13px; background: white;
            }
        """)

        # Campo numérico para la cantidad a pedir
        self.spin_cant = QSpinBox()
        self.spin_cant.setMinimum(1)         # Mínimo 1 unidad
        self.spin_cant.setMaximum(9999)      # Máximo razonable
        self.spin_cant.setValue(1)
        self.spin_cant.setFixedWidth(80)
        self.spin_cant.setFixedHeight(36)

        # Botón para buscar el producto y agregar a la lista
        btn_agregar = QPushButton("Agregar")
        btn_agregar.setObjectName("btn_primary")
        btn_agregar.setFixedHeight(36)
        btn_agregar.clicked.connect(self._agregar_item)

        add_row.addWidget(self.inp_prod, 1)  # El campo de búsqueda ocupa el espacio disponible
        add_row.addWidget(QLabel("Cant:"))
        add_row.addWidget(self.spin_cant)
        add_row.addWidget(btn_agregar)
        layout.addLayout(add_row)

        # ── Tabla de ítems del pedido ─────────────────────────────────────────
        self.tabla_items = QTableWidget()
        self.tabla_items.setColumnCount(4)
        self.tabla_items.setHorizontalHeaderLabels(["Código", "Producto", "Cant.", ""])
        self.tabla_items.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_items.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_items.verticalHeader().setVisible(False)
        self.tabla_items.setFixedHeight(160)
        self.tabla_items.setStyleSheet("""
            QTableWidget { border: 1px solid #E0E6F0; border-radius: 8px; font-size: 12px; }
            QHeaderView::section { background: #F0F4FA; font-weight: 600; padding: 6px; border: none; }
        """)
        layout.addWidget(self.tabla_items)

        # ── Notas opcionales ──────────────────────────────────────────────────
        lbl_notas = QLabel("Notas (opcional)")
        lbl_notas.setFont(QFont(FONT_FAMILY, 11, QFont.DemiBold))
        layout.addWidget(lbl_notas)

        self.txt_notas = QTextEdit()
        self.txt_notas.setFixedHeight(64)
        self.txt_notas.setPlaceholderText("Instrucciones especiales, condiciones de entrega...")
        self.txt_notas.setStyleSheet("""
            QTextEdit {
                border: 1.5px solid #D1D9E6; border-radius: 8px;
                padding: 8px; font-size: 13px; background: white;
            }
        """)
        layout.addWidget(self.txt_notas)

        # ── Botones Aceptar / Cancelar ────────────────────────────────────────
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Generar Pedido")
        botones.button(QDialogButtonBox.Ok).setObjectName("btn_primary")
        botones.accepted.connect(self._confirmar)   # OK → validar y guardar
        botones.rejected.connect(self.reject)        # Cancel → cerrar sin guardar
        layout.addWidget(botones)

    # ── Lógica del diálogo ─────────────────────────────────────────────────────
    def _agregar_item(self):
        """
        Busca el producto ingresado y lo agrega a la lista de ítems del pedido.
        Si ya está en la lista, incrementa la cantidad en lugar de duplicar.
        """
        texto = self.inp_prod.text().strip()
        if not texto:
            QMessageBox.warning(self, MSG_ATENCION, "Ingresa el nombre o código del producto.")
            return

        # Buscamos el producto en el catálogo activo
        resultados = buscar_productos(texto, solo_activos=True)

        if not resultados:
            QMessageBox.warning(self, "No encontrado",
                                f"No se encontró ningún producto con '{texto}'.")
            return

        # Tomamos el primer resultado (el más relevante según el ORDER BY nombre)
        prod = resultados[0]
        cantidad = self.spin_cant.value()

        # Verificamos si el producto ya está en la lista de ítems
        for item in self._items:
            if item["producto_id"] == prod.id:
                # Suma la cantidad al ítem existente en lugar de duplicarlo
                item["cantidad"] += cantidad
                self._refrescar_tabla_items()
                return

        # No existe en la lista: lo agregamos como nuevo ítem
        self._items.append({
            "producto_id": prod.id,
            "codigo": prod.codigo,
            "nombre": prod.nombre,
            "cantidad": cantidad,
            "precio_ref": None   # Precio de referencia opcional, dejamos vacío
        })

        # Limpiamos el campo de búsqueda para facilitar agregar más productos
        self.inp_prod.clear()
        self._refrescar_tabla_items()

    def _refrescar_tabla_items(self):
        """Limpia y vuelve a llenar la tabla de ítems con la lista actual."""
        self.tabla_items.setRowCount(0)  # Limpiamos todas las filas

        for i, item in enumerate(self._items):
            self.tabla_items.insertRow(i)

            # Col 0: código del producto
            self.tabla_items.setItem(i, 0, QTableWidgetItem(item["codigo"]))

            # Col 1: nombre del producto
            self.tabla_items.setItem(i, 1, QTableWidgetItem(item["nombre"]))

            # Col 2: cantidad solicitada
            cant_item = QTableWidgetItem(str(item["cantidad"]))
            cant_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_items.setItem(i, 2, cant_item)

            # Col 3: botón para eliminar este ítem de la lista
            btn_del = QPushButton("✕")
            btn_del.setObjectName("btn_table_delete")
            btn_del.setCursor(Qt.PointingHandCursor)
            # Lambda con captura del índice actual
            btn_del.clicked.connect(lambda _, idx=i: self._eliminar_item(idx))
            self.tabla_items.setCellWidget(i, 3, btn_del)

    def _eliminar_item(self, idx: int):
        """Elimina un ítem de la lista interna y refresca la tabla."""
        if 0 <= idx < len(self._items):
            self._items.pop(idx)         # Removemos de la lista
            self._refrescar_tabla_items() # Actualizamos la vista

    def _confirmar(self):
        """
        Valida los datos del formulario y registra el pedido en la BD.
        Si todo es correcto, cierra el diálogo con estado Accepted.
        """
        # Validación: debe haber al menos un producto en el pedido
        if not self._items:
            QMessageBox.warning(self, MSG_ATENCION,
                                "Agrega al menos un producto al pedido.")
            return

        # Obtenemos el ID del proveedor seleccionado en el ComboBox
        proveedor_id = self.combo_prov.currentData()
        if not proveedor_id:
            QMessageBox.warning(self, MSG_ATENCION, "Selecciona un proveedor.")
            return

        # Convertimos la fecha de QDate a objeto date de Python
        qdate = self.date_entrega.date()
        from datetime import date as date_type
        fecha_estimada = date_type(qdate.year(), qdate.month(), qdate.day())

        # Obtenemos el usuario que está creando el pedido
        usuario = get_usuario_activo()

        # Llamamos al modelo para registrar el pedido
        ok, msg, _ = registrar_pedido(
            proveedor_id=proveedor_id,
            usuario_id=usuario.id,
            fecha_estimada=fecha_estimada,
            items=self._items,
            notas=self.txt_notas.toPlainText().strip()
        )

        if ok:
            QMessageBox.information(self, "Pedido generado",
                                    f"Pedido {msg} registrado correctamente.")
            self.accept()  # Cierra el diálogo con resultado Accepted
        else:
            QMessageBox.warning(self, "Error", msg)
