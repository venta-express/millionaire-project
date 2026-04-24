"""
AutoParts Express - UI de Auditoria del Sistema
Sprint 4: Panel que muestra el log de acciones realizadas en el sistema.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QLineEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor
from models.auditoria import obtener_auditoria


MODULOS = ["Todos", "Ventas", "Inventario", "Compras", "Clientes",
           "Usuarios", "Reportes", "Promociones", "Sistema"]

COLORES_MODULO = {
    "Ventas":      "#27AE60",
    "Inventario":  "#2980B9",
    "Compras":     "#8E44AD",
    "Clientes":    "#16A085",
    "Usuarios":    "#E74C3C",
    "Reportes":    "#F39C12",
    "Promociones": "#E67E22",
    "Sistema":     "#7F8C8D",
}


class _CargaThread(QThread):
    terminado = Signal(list)

    def __init__(self, modulo, parent=None):
        super().__init__(parent)
        self.modulo = modulo

    def run(self):
        modulo = None if self.modulo == "Todos" else self.modulo
        try:
            datos = obtener_auditoria(modulo=modulo, limit=300)
        except Exception:
            datos = []
        self.terminado.emit(datos)


class AuditoriaWidget(QWidget):
    """Panel de auditoria del sistema."""

    def __init__(self, usuario_actual: dict, parent=None):
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self._datos = []
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Encabezado
        titulo = QLabel("Auditoria del Sistema")
        titulo.setStyleSheet("font-size:20px; font-weight:bold; color:#1A2942;")
        layout.addWidget(titulo)

        # Barra de filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(10)

        self.cmb_modulo = QComboBox()
        self.cmb_modulo.addItems(MODULOS)
        self.cmb_modulo.setFixedWidth(160)
        self.cmb_modulo.currentTextChanged.connect(self._cargar)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por usuario o accion...")
        self.txt_buscar.textChanged.connect(self._filtrar)

        btn_refresh = QPushButton("Actualizar")
        btn_refresh.setObjectName("btn_primary")
        btn_refresh.clicked.connect(self._cargar)
        btn_refresh.setFixedWidth(120)

        self.lbl_total = QLabel("0 registros")
        self.lbl_total.setStyleSheet("color:#7F8C8D;")

        filtros.addWidget(QLabel("Modulo:"))
        filtros.addWidget(self.cmb_modulo)
        filtros.addWidget(self.txt_buscar, 1)
        filtros.addWidget(btn_refresh)
        filtros.addWidget(self.lbl_total)
        layout.addLayout(filtros)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Fecha/Hora", "Usuario", "Modulo", "Accion", "Detalle", "IP"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla)

    def _cargar(self):
        self.tabla.setRowCount(0)
        self.lbl_total.setText("Cargando...")
        modulo = self.cmb_modulo.currentText()
        self._thread = _CargaThread(modulo, self)
        self._thread.terminado.connect(self._mostrar_datos)
        self._thread.start()

    def _mostrar_datos(self, datos: list):
        self._datos = datos
        self._filtrar()

    def _filtrar(self):
        texto = self.txt_buscar.text().lower()
        datos = self._datos

        if texto:
            datos = [
                d for d in datos
                if texto in (d.get("usuario") or "").lower()
                or texto in (d.get("accion") or "").lower()
                or texto in (d.get("detalle") or "").lower()
            ]

        self.tabla.setRowCount(len(datos))
        for row, d in enumerate(datos):
            fecha = d["fecha_hora"]
            if hasattr(fecha, "strftime"):
                fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S")
            else:
                fecha_str = str(fecha)

            modulo = d.get("modulo", "")
            color = COLORES_MODULO.get(modulo, "#7F8C8D")

            items = [
                fecha_str,
                d.get("username") or d.get("usuario") or "—",
                modulo,
                d.get("accion", ""),
                (d.get("detalle") or "")[:120],
                d.get("ip") or "—",
            ]

            for col, val in enumerate(items):
                item = QTableWidgetItem(str(val))
                if col == 2:
                    item.setForeground(QColor(color))
                self.tabla.setItem(row, col, item)

        self.lbl_total.setText(f"{len(datos)} registros")
