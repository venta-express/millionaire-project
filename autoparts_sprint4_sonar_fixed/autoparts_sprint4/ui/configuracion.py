"""
AutoParts Express - UI de Configuracion del Sistema
Sprint 4: Panel para editar parametros globales y gestionar backups.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QFileDialog, QGroupBox, QFormLayout, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from models.configuracion import obtener_todas, actualizar_config, obtener_config
from models.backup import generar_backup, listar_backups


class _BackupThread(QThread):
    terminado = Signal(bool, str)

    def __init__(self, directorio, parent=None):
        super().__init__(parent)
        self.directorio = directorio

    def run(self):
        ok, msg = generar_backup(self.directorio)
        self.terminado.emit(ok, msg)


class ConfiguracionWidget(QWidget):
    """Panel de configuracion del sistema."""

    def __init__(self, usuario_actual: dict, parent=None):
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self.directorio_backup = os.path.join(
            os.path.expanduser("~"), "autoparts_backups"
        )
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("Configuracion del Sistema")
        titulo.setStyleSheet("font-size:20px; font-weight:bold; color:#1A2942;")
        layout.addWidget(titulo)

        # ── Seccion empresa ──
        grp_empresa = QGroupBox("Datos de la Empresa")
        grp_empresa.setStyleSheet(
            "QGroupBox { font-weight:bold; border:1px solid #CBD5E0;"
            "border-radius:6px; margin-top:8px; padding:10px; }"
            "QGroupBox::title { subcontrol-origin:margin; left:10px; }"
        )
        form = QFormLayout(grp_empresa)

        self.campos = {}
        campos_empresa = [
            ("empresa_nombre",    "Nombre empresa:"),
            ("empresa_nit",       "NIT:"),
            ("empresa_telefono",  "Telefono:"),
            ("empresa_email",     "Email:"),
            ("empresa_direccion", "Direccion:"),
            ("factura_prefijo",   "Prefijo factura:"),
        ]
        for clave, etiqueta in campos_empresa:
            campo = QLineEdit()
            campo.setObjectName(clave)
            self.campos[clave] = campo
            form.addRow(etiqueta, campo)

        btn_guardar = QPushButton("Guardar Configuracion")
        btn_guardar.setObjectName("btn_success")
        btn_guardar.clicked.connect(self._guardar)
        form.addRow("", btn_guardar)
        layout.addWidget(grp_empresa)

        # ── Seccion backup ──
        grp_backup = QGroupBox("Respaldo de Base de Datos")
        grp_backup.setStyleSheet(
            "QGroupBox { font-weight:bold; border:1px solid #CBD5E0;"
            "border-radius:6px; margin-top:8px; padding:10px; }"
            "QGroupBox::title { subcontrol-origin:margin; left:10px; }"
        )
        bk_layout = QVBoxLayout(grp_backup)

        dir_row = QHBoxLayout()
        self.lbl_directorio = QLabel(self.directorio_backup)
        self.lbl_directorio.setStyleSheet(
            "background:#F4F6FA; padding:6px; border-radius:4px; color:#555;"
        )
        btn_dir = QPushButton("Cambiar carpeta")
        btn_dir.setObjectName("btn_secondary")
        btn_dir.clicked.connect(self._cambiar_directorio)
        dir_row.addWidget(QLabel("Carpeta:"))
        dir_row.addWidget(self.lbl_directorio, 1)
        dir_row.addWidget(btn_dir)
        bk_layout.addLayout(dir_row)

        self.btn_backup = QPushButton("Generar Backup Ahora")
        self.btn_backup.setObjectName("btn_primary")
        self.btn_backup.clicked.connect(self._generar_backup)
        bk_layout.addWidget(self.btn_backup)

        self.lbl_estado_backup = QLabel("")
        self.lbl_estado_backup.setWordWrap(True)
        bk_layout.addWidget(self.lbl_estado_backup)

        # Lista de backups existentes
        self.tabla_backups = QTableWidget()
        self.tabla_backups.setColumnCount(3)
        self.tabla_backups.setHorizontalHeaderLabels(["Archivo", "Fecha", "Tamano"])
        self.tabla_backups.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_backups.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_backups.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla_backups.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_backups.verticalHeader().setVisible(False)
        self.tabla_backups.setMaximumHeight(180)
        bk_layout.addWidget(QLabel("Backups existentes:"))
        bk_layout.addWidget(self.tabla_backups)

        layout.addWidget(grp_backup)
        layout.addStretch()

    def _cargar(self):
        configs = obtener_todas()
        mapa = {c["clave"]: c["valor"] for c in configs}
        for clave, campo in self.campos.items():
            campo.setText(mapa.get(clave, ""))
        self._actualizar_lista_backups()

    def _guardar(self):
        for clave, campo in self.campos.items():
            actualizar_config(clave, campo.text().strip())
        QMessageBox.information(self, "Exito", "Configuracion guardada correctamente.")

    def _cambiar_directorio(self):
        d = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de backups")
        if d:
            self.directorio_backup = d
            self.lbl_directorio.setText(d)
            self._actualizar_lista_backups()

    def _generar_backup(self):
        self.btn_backup.setEnabled(False)
        self.btn_backup.setText("Generando...")
        self.lbl_estado_backup.setText("Generando backup, por favor espere...")
        self._thread = _BackupThread(self.directorio_backup, self)
        self._thread.terminado.connect(self._backup_terminado)
        self._thread.start()

    def _backup_terminado(self, ok: bool, mensaje: str):
        self.btn_backup.setEnabled(True)
        self.btn_backup.setText("Generar Backup Ahora")
        if ok:
            self.lbl_estado_backup.setStyleSheet("color:#27AE60; font-weight:bold;")
            self.lbl_estado_backup.setText(f"Backup generado: {mensaje}")
            self._actualizar_lista_backups()
        else:
            self.lbl_estado_backup.setStyleSheet("color:#E74C3C; font-weight:bold;")
            self.lbl_estado_backup.setText(f"Error: {mensaje}")

    def _actualizar_lista_backups(self):
        backups = listar_backups(self.directorio_backup)
        self.tabla_backups.setRowCount(len(backups))
        for row, b in enumerate(backups):
            self.tabla_backups.setItem(row, 0, QTableWidgetItem(b["nombre"]))
            fecha_str = b["fecha"].strftime("%Y-%m-%d %H:%M")
            self.tabla_backups.setItem(row, 1, QTableWidgetItem(fecha_str))
            self.tabla_backups.setItem(row, 2, QTableWidgetItem(f"{b['tamano_kb']} KB"))
