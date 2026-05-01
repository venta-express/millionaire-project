"""
AutoParts Express - Módulo de Gestión de Usuarios
HU-08: Gestión de Usuarios y Roles (Sprint 2)

Solo accesible para usuarios con rol 'Gerencia'.
Permite: listar, crear, editar y desbloquear usuarios del sistema.
"""

# Widgets principales de la interfaz
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QHeaderView,
    QAbstractItemView, QDialog, QDialogButtonBox,
    QLineEdit, QComboBox, QCheckBox, QMessageBox, QFormLayout
)

# Clases de comportamiento y tipografía
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

# Paleta de colores compartida
from utils.styles import COLORS
from utils.constants import FONT_FAMILY, APP_NAME, LABEL_ATENCION

# Funciones del modelo de autenticación para CRUD de usuarios
from models.auth import (
    listar_usuarios, crear_usuario, editar_usuario,
    desbloquear_usuario, listar_roles, get_usuario_activo
)



# ── Helpers de módulo ──────────────────────────────────────────────────────────
_COLORES_ROL = {
    "Gerencia":   ("#D4EDDA", "#155724"),
    "Inventario": ("#CCE5FF", "#004085"),
    "Vendedor":   ("#FFF3CD", "#856404"),
}

def _color_rol(rol: str) -> tuple[str, str]:
    """Devuelve (bg, fg) según el rol del usuario."""
    return _COLORES_ROL.get(rol, ("#EEEEEE", "#333333"))


class UsuariosView(QWidget):
    """
    Vista del módulo de gestión de usuarios.
    Solo se carga en el sidebar si el usuario tiene rol 'Gerencia'.
    Muestra la tabla de usuarios con botones de acción por fila.
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F4F6FA;")
        self._setup_ui()      # Construimos la interfaz
        self._cargar_datos()  # Cargamos la lista de usuarios

    # ── Construcción de UI ─────────────────────────────────────────────────────
    def _setup_ui(self):
        """Construye el layout completo de la vista de usuarios."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── Encabezado ────────────────────────────────────────────────────────
        header = QHBoxLayout()

        # Bloque título + subtítulo
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        titulo = QLabel("🔐  Usuarios")
        titulo.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")

        subtitulo = QLabel("Gestión de usuarios y roles del sistema")
        subtitulo.setFont(QFont(FONT_FAMILY, 11))
        subtitulo.setStyleSheet(f"color: {COLORS['muted']};")

        title_col.addWidget(titulo)
        title_col.addWidget(subtitulo)
        header.addLayout(title_col)
        header.addStretch()

        # Botón para crear un nuevo usuario
        self.btn_nuevo = QPushButton("＋  Nuevo Usuario")
        self.btn_nuevo.setObjectName("btn_primary")
        self.btn_nuevo.setFixedHeight(40)
        self.btn_nuevo.setCursor(Qt.PointingHandCursor)
        self.btn_nuevo.clicked.connect(self._abrir_dialogo_crear)
        header.addWidget(self.btn_nuevo)

        layout.addLayout(header)

        # ── Tabla de usuarios ─────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("QFrame#card { background: white; border-radius: 12px; }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)  # 7 columnas de información
        self.tabla.setHorizontalHeaderLabels([
            "Cédula", "Nombre", "Usuario", "Rol",
            "Estado", "Bloqueado", "Acciones"
        ])

        # Hacemos flexible la columna del nombre
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setStyleSheet("""
            QTableWidget { border: none; font-size: 13px; }
            QHeaderView::section {
                background: #1A2942; color: #FFFFFF; font-weight: 600;
                padding: 8px; border: none;
            }
            QTableWidget::item:selected { background: #E8F0FE; color: #1A2942; }
            QTableWidget::item:alternate { background: #F8FAFD; }
        """)

        card_layout.addWidget(self.tabla)
        layout.addWidget(card)
        layout.addStretch()

    # ── Carga de datos ─────────────────────────────────────────────────────────
    def _cargar_datos(self):
        """
        Consulta la lista de usuarios en la BD y llena la tabla.
        Se llama al iniciar la vista y después de cada operación CRUD.
        """
        usuarios = listar_usuarios()   # Consultamos todos los usuarios con sus roles
        self.tabla.setRowCount(0)      # Limpiamos la tabla antes de rellenar

        # Obtenemos el ID del usuario logueado para no permitir auto-edición crítica
        usuario_activo = get_usuario_activo()

        for usuario in usuarios:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)

            # Col 0: cédula del usuario; guardamos el ID como dato oculto
            item_ced = QTableWidgetItem(usuario["cedula"])
            item_ced.setData(Qt.UserRole, usuario["id"])   # ID oculto para acciones
            self.tabla.setItem(fila, 0, item_ced)

            # Col 1: nombre completo
            self.tabla.setItem(fila, 1, QTableWidgetItem(usuario["nombre"]))

            # Col 2: nombre de usuario (username)
            self.tabla.setItem(fila, 2, QTableWidgetItem(usuario["username"]))

            # Col 3: badge del rol con color por tipo de rol
            lbl_rol = QLabel(f"  {usuario['rol']}  ")
            lbl_rol.setAlignment(Qt.AlignCenter)
            lbl_rol.setFont(QFont(FONT_FAMILY, 11))

            bg, fg = _color_rol(usuario["rol"])
            lbl_rol.setStyleSheet(
                f"background: {bg}; color: {fg}; border-radius: 6px; padding: 2px 4px;"
            )
            self.tabla.setCellWidget(fila, 3, lbl_rol)

            # Col 4: estado activo/inactivo con semáforo de color
            estado_txt = "✅ Activo" if usuario["activo"] else "⛔ Inactivo"
            item_estado = QTableWidgetItem(estado_txt)
            item_estado.setForeground(
                QColor("#155724") if usuario["activo"] else QColor("#721C24")
            )
            self.tabla.setItem(fila, 4, item_estado)

            # Col 5: indicador de bloqueo de cuenta
            bloq_txt = "🔒 Bloqueado" if usuario["bloqueado"] else "—"
            item_bloq = QTableWidgetItem(bloq_txt)
            if usuario["bloqueado"]:
                item_bloq.setForeground(QColor("#856404"))  # Texto naranja si bloqueado
            self.tabla.setItem(fila, 5, item_bloq)

            # Col 6: botones de acción (editar + desbloquear si aplica)
            acciones_widget = self._crear_acciones(
                usuario["id"], usuario["bloqueado"],
                es_yo=(usuario["id"] == usuario_activo.id if usuario_activo else False)
            )
            self.tabla.setCellWidget(fila, 6, acciones_widget)

            # Ajustamos la altura de cada fila para el contenido
            self.tabla.setRowHeight(fila, 44)

    def _crear_acciones(self, uid: int, bloqueado: bool, es_yo: bool) -> QWidget:
        """
        Crea un widget con los botones de acción para un usuario.
        Parámetros:
            uid:      ID del usuario de esa fila
            bloqueado: True si la cuenta está bloqueada
            es_yo:    True si el usuario es el mismo que está logueado
        """
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(4, 4, 4, 4)
        row.setSpacing(6)

        # Botón editar (siempre disponible)
        btn_edit = QPushButton("✏️ Editar")
        btn_edit.setObjectName("btn_table_edit")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.clicked.connect(lambda _, u=uid: self._abrir_dialogo_editar(u))
        row.addWidget(btn_edit)

        # Botón desbloquear (solo visible si la cuenta está bloqueada)
        if bloqueado:
            btn_desbloq = QPushButton("🔓 Desbloquear")
            btn_desbloq.setObjectName("btn_table_confirm")
            btn_desbloq.setCursor(Qt.PointingHandCursor)
            btn_desbloq.clicked.connect(lambda _, u=uid: self._desbloquear(u))
            row.addWidget(btn_desbloq)

        row.addStretch()
        return container

    # ── Acciones ───────────────────────────────────────────────────────────────
    def _abrir_dialogo_crear(self):
        """Abre el diálogo para crear un nuevo usuario."""
        dialogo = DialogoUsuario(modo="crear", parent=self)
        if dialogo.exec() == QDialog.Accepted:
            self._cargar_datos()  # Recargamos la tabla para mostrar el nuevo usuario

    def _abrir_dialogo_editar(self, uid: int):
        """Abre el diálogo de edición precargado con los datos del usuario."""
        # Buscamos el usuario en la lista actual para pasar sus datos al diálogo
        usuarios = listar_usuarios()
        usuario = next((u for u in usuarios if u["id"] == uid), None)
        if not usuario:
            return

        dialogo = DialogoUsuario(modo="editar", usuario=usuario, parent=self)
        if dialogo.exec() == QDialog.Accepted:
            self._cargar_datos()  # Recargamos para reflejar los cambios

    def _desbloquear(self, uid: int):
        """Desbloquea la cuenta de un usuario después de confirmar la acción."""
        resp = QMessageBox.question(
            self, "Desbloquear usuario",
            "¿Estás seguro de que deseas desbloquear esta cuenta?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            ok, msg = desbloquear_usuario(uid)  # Llamamos al modelo
            if ok:
                QMessageBox.information(self, "Éxito", msg)
            else:
                QMessageBox.warning(self, "Error", msg)
            self._cargar_datos()  # Actualizamos la tabla


class DialogoUsuario(QDialog):
    """
    Diálogo modal compartido para crear o editar un usuario.
    El parámetro 'modo' controla si es 'crear' o 'editar'.
    """

    def __init__(self, modo: str, usuario: dict = None, parent=None):
        super().__init__(parent)
        self._modo = modo        # 'crear' o 'editar'
        self._usuario = usuario  # Datos del usuario (solo en modo editar)

        # Título del diálogo según el modo
        self.setWindowTitle("Nuevo Usuario" if modo == "crear" else "Editar Usuario")
        self.setMinimumWidth(440)
        self._setup_ui()

    def _setup_ui(self):
        """Construye el formulario del diálogo."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Título interior del diálogo
        icono = "➕" if self._modo == "crear" else "✏️"
        texto = "Crear nuevo usuario" if self._modo == "crear" else "Editar usuario"
        titulo = QLabel(f"{icono}  {texto}")
        titulo.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLORS['primary']};")
        layout.addWidget(titulo)

        # ── Formulario con QFormLayout ────────────────────────────────────────
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        def inp(placeholder, max_len=100):
            """Helper que crea un QLineEdit estilizado con placeholder."""
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setMaxLength(max_len)
            field.setFixedHeight(36)
            field.setStyleSheet("""
                QLineEdit {
                    border: 1.5px solid #D1D9E6; border-radius: 8px;
                    padding: 0 12px; font-size: 13px; background: white;
                }
                QLineEdit:focus { border-color: #1A2942; }
            """)
            return field

        # Campo cédula (solo editable al crear; en edición se muestra deshabilitado)
        self.inp_cedula = inp("Número de cédula", max_len=20)
        if self._modo == "editar" and self._usuario:
            # En modo editar, mostramos la cédula pero no la dejamos cambiar
            self.inp_cedula.setText(self._usuario["cedula"])
            self.inp_cedula.setEnabled(False)  # Solo lectura para la cédula
        form.addRow("Cédula *", self.inp_cedula)

        # Campo nombre completo
        self.inp_nombre = inp("Nombre completo")
        if self._modo == "editar" and self._usuario:
            self.inp_nombre.setText(self._usuario["nombre"])
        form.addRow("Nombre *", self.inp_nombre)

        # Campo username (solo en modo crear; no se permite cambiar el username)
        self.inp_username = inp("Nombre de usuario para login", max_len=50)
        if self._modo == "editar":
            self.inp_username.setText(self._usuario["username"] if self._usuario else "")
            self.inp_username.setEnabled(False)  # El username no se puede cambiar
        form.addRow("Usuario *", self.inp_username)

        # Campo contraseña (en editar es opcional: si se deja vacío, no cambia)
        placeholder_pwd = "Contraseña" if self._modo == "crear" else "Nueva contraseña (dejar vacío para no cambiar)"
        self.inp_pwd = inp(placeholder_pwd, max_len=128)
        self.inp_pwd.setEchoMode(QLineEdit.Password)  # Oculta el texto con asteriscos
        form.addRow("Contraseña", self.inp_pwd)

        # ComboBox para seleccionar el rol
        self.combo_rol = QComboBox()
        self.combo_rol.setFixedHeight(36)
        self.combo_rol.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #D1D9E6; border-radius: 8px;
                padding: 0 12px; font-size: 13px; background: white;
            }
        """)
        # Cargamos los roles desde la BD
        for rol in listar_roles():
            self.combo_rol.addItem(rol)
        # Preseleccionamos el rol actual en modo editar
        if self._modo == "editar" and self._usuario:
            idx = self.combo_rol.findText(self._usuario["rol"])
            if idx >= 0:
                self.combo_rol.setCurrentIndex(idx)
        form.addRow("Rol *", self.combo_rol)

        # Checkbox para activar/desactivar la cuenta (solo en modo editar)
        if self._modo == "editar":
            self.chk_activo = QCheckBox("Cuenta activa")
            self.chk_activo.setChecked(self._usuario.get("activo", True) if self._usuario else True)
            form.addRow("Estado", self.chk_activo)
        else:
            self.chk_activo = None  # No existe en modo crear (siempre activo)

        layout.addLayout(form)

        # ── Botones Aceptar / Cancelar ────────────────────────────────────────
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_ok_txt = "Crear Usuario" if self._modo == "crear" else "Guardar Cambios"
        botones.button(QDialogButtonBox.Ok).setText(btn_ok_txt)
        botones.button(QDialogButtonBox.Ok).setObjectName("btn_primary")
        botones.accepted.connect(self._confirmar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _confirmar(self):
        """
        Valida los campos y llama al modelo para crear o editar el usuario.
        Si hay errores de validación, muestra un mensaje y no cierra el diálogo.
        """
        nombre = self.inp_nombre.text().strip()
        password = self.inp_pwd.text().strip()
        rol = self.combo_rol.currentText()

        if self._modo == "crear":
            # En modo crear todos los campos son obligatorios
            cedula = self.inp_cedula.text().strip()
            username = self.inp_username.text().strip()

            if not cedula or not nombre or not username or not password:
                QMessageBox.warning(self, "Campos obligatorios",
                                    "Completa todos los campos marcados con *.")
                return

            # Llamamos al modelo para crear el usuario
            ok, msg = crear_usuario(cedula, nombre, username, password, rol)

        else:
            # En modo editar, la contraseña es opcional
            if not nombre:
                QMessageBox.warning(self, "Campo obligatorio",
                                    "El nombre no puede estar vacío.")
                return

            # Estado activo del checkbox (solo existe en modo editar)
            activo = self.chk_activo.isChecked() if self.chk_activo else True

            # Llamamos al modelo para editar el usuario
            ok, msg = editar_usuario(
                uid=self._usuario["id"],
                nombre=nombre,
                rol_nombre=rol,
                activo=activo,
                nueva_password=password   # Puede ser vacío; el modelo lo maneja
            )

        if ok:
            QMessageBox.information(self, "Éxito", msg)
            self.accept()  # Cierra con resultado Accepted para refrescar la tabla
        else:
            QMessageBox.warning(self, "Error", msg)
