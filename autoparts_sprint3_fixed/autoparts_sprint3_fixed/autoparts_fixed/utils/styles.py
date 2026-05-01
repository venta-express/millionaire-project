"""
AutoParts Express - Estilos globales de la aplicación
Sprint 3: Botones rediseñados con fondos sólidos y texto blanco
          para máxima visibilidad en todos los contextos.
          Nuevos estilos: QTabWidget, QProgressBar, btn_table_*.

Paleta principal:
  PRIMARY  #1A2942  azul marino oscuro
  ACCENT   #FF6B2B  naranja vibrante
  SUCCESS  #27AE60  verde
  DANGER   #E74C3C  rojo
  WARNING  #F39C12  amarillo-naranja
  INFO     #2980B9  azul informativo
  SURFACE  #F4F6FA  fondo gris muy claro
"""

APP_STYLE = """
/* ═══════════════════════════════════════════════════════════════════
   BASE
═══════════════════════════════════════════════════════════════════ */
QWidget {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
    color: #1A2942;
    background-color: transparent;
}
QMainWindow,
QMainWindow > QWidget,
QStackedWidget,
QStackedWidget > QWidget {
    background-color: #F4F6FA;
}

/* ═══════════════════════════════════════════════════════════════════
   BOTONES — fondo sólido + texto blanco para máximo contraste
═══════════════════════════════════════════════════════════════════ */

/* PRIMARIO (naranja) — acción principal de cada pantalla */
QPushButton#btn_primary {
    background-color: #FF6B2B;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 14px;
    min-width: 120px;
}
QPushButton#btn_primary:hover   { background-color: #E55A1E; }
QPushButton#btn_primary:pressed { background-color: #C94D18; }
QPushButton#btn_primary:disabled {
    background-color: #B0B8C8;
    color: #FFFFFF;
}

/* SECUNDARIO (blanco + borde azul) */
QPushButton#btn_secondary {
    background-color: #FFFFFF;
    color: #1A2942;
    border: 2px solid #1A2942;
    border-radius: 8px;
    padding: 9px 20px;
    font-weight: 700;
    font-size: 14px;
    min-width: 120px;
}
QPushButton#btn_secondary:hover {
    background-color: #1A2942;
    color: #FFFFFF;
}
QPushButton#btn_secondary:pressed {
    background-color: #0D1B2E;
    color: #FFFFFF;
}
QPushButton#btn_secondary:disabled {
    background-color: #F0F2F5;
    color: #9BAABB;
    border-color: #C5CFE0;
}

/* PELIGRO (rojo) */
QPushButton#btn_danger {
    background-color: #E74C3C;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 14px;
    min-width: 120px;
}
QPushButton#btn_danger:hover   { background-color: #C0392B; }
QPushButton#btn_danger:pressed { background-color: #A93226; }

/* ÉXITO (verde) */
QPushButton#btn_success {
    background-color: #27AE60;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 14px;
    min-width: 120px;
}
QPushButton#btn_success:hover   { background-color: #1E8449; }
QPushButton#btn_success:pressed { background-color: #196F3D; }

/* ADVERTENCIA (amarillo) */
QPushButton#btn_warning {
    background-color: #E67E22;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 14px;
    min-width: 120px;
}
QPushButton#btn_warning:hover   { background-color: #CA6F1E; }
QPushButton#btn_warning:pressed { background-color: #B9770E; }

/* INFO (azul) */
QPushButton#btn_info {
    background-color: #2980B9;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 14px;
    min-width: 120px;
}
QPushButton#btn_info:hover   { background-color: #2471A3; }
QPushButton#btn_info:pressed { background-color: #1F618D; }

/* ── Botones compactos dentro de tablas ─────────────────────────── */
/* Editar — azul */
QPushButton#btn_table_edit {
    background-color: #2980B9;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 5px 12px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#btn_table_edit:hover { background-color: #2471A3; }

/* Eliminar — rojo */
QPushButton#btn_table_delete {
    background-color: #E74C3C;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 5px 12px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#btn_table_delete:hover { background-color: #C0392B; }

/* Ver — gris azulado */
QPushButton#btn_table_view {
    background-color: #5D6D7E;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 5px 12px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#btn_table_view:hover { background-color: #424F5E; }

/* Confirmar/Recibir — verde */
QPushButton#btn_table_confirm {
    background-color: #27AE60;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 5px 12px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#btn_table_confirm:hover { background-color: #1E8449; }

/* Cancelar (tabla) — naranja */
QPushButton#btn_table_cancel {
    background-color: #E67E22;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 5px 12px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#btn_table_cancel:hover { background-color: #CA6F1E; }

/* ── Botón NAV del sidebar ───────────────────────────────────────── */
QPushButton#btn_nav {
    background-color: transparent;
    color: #8FA4BE;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
}
QPushButton#btn_nav:hover {
    background-color: rgba(255,255,255,0.10);
    color: #FFFFFF;
}
QPushButton#btn_nav[active="true"],
QPushButton#btn_nav:checked {
    background-color: rgba(255,107,43,0.22);
    color: #FF6B2B;
    font-weight: 700;
}

/* ═══════════════════════════════════════════════════════════════════
   INPUTS
═══════════════════════════════════════════════════════════════════ */
QLineEdit {
    background-color: #FFFFFF;
    border: 1.5px solid #D8E0EC;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 14px;
    color: #1A2942;
    selection-background-color: #FF6B2B;
    selection-color: #FFFFFF;
}
QLineEdit:focus        { border-color: #FF6B2B; }
QLineEdit:disabled     { background-color: #F0F2F5; color: #AAAAAA; }
QLineEdit[error="true"]{ border-color: #E74C3C; }

QTextEdit {
    background-color: #FFFFFF;
    border: 1.5px solid #D8E0EC;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    color: #1A2942;
}
QTextEdit:focus { border-color: #FF6B2B; }

/* ═══════════════════════════════════════════════════════════════════
   COMBOBOX / DATE / SPINBOX
═══════════════════════════════════════════════════════════════════ */
QComboBox {
    background-color: #FFFFFF;
    border: 1.5px solid #D8E0EC;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 14px;
    color: #1A2942;
    min-width: 120px;
}
QComboBox:focus { border-color: #FF6B2B; }
QComboBox::drop-down { border: none; width: 30px; }
QComboBox::down-arrow { image: none; width: 0; }
QComboBox QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #D8E0EC;
    border-radius: 6px;
    selection-background-color: #FF6B2B;
    selection-color: #FFFFFF;
    padding: 4px;
}

QDateEdit {
    background-color: #FFFFFF;
    border: 1.5px solid #D8E0EC;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 14px;
    color: #1A2942;
}
QDateEdit:focus { border-color: #FF6B2B; }
QDateEdit::drop-down { border: none; width: 30px; }

QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1.5px solid #D8E0EC;
    border-radius: 8px;
    padding: 9px 12px;
    font-size: 14px;
    color: #1A2942;
}
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #FF6B2B; }
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    width: 22px;
    background: #F0F4FA;
    border: none;
    border-radius: 4px;
}

/* ═══════════════════════════════════════════════════════════════════
   TABLA
═══════════════════════════════════════════════════════════════════ */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E0E6F0;
    border-radius: 10px;
    gridline-color: #F0F4FA;
    outline: none;
    alternate-background-color: #F8FAFD;
}
QTableWidget::item {
    padding: 10px 12px;
    border-bottom: 1px solid #F0F4FA;
}
QTableWidget::item:selected {
    background-color: #FFF0E8;
    color: #1A2942;
}
QHeaderView::section {
    background-color: #1A2942;
    color: #FFFFFF;
    padding: 10px 12px;
    border: none;
    font-weight: 700;
    font-size: 13px;
}
QHeaderView::section:first { border-top-left-radius: 10px; }
QHeaderView::section:last  { border-top-right-radius: 10px; }

/* ═══════════════════════════════════════════════════════════════════
   CARD (QFrame#card)
═══════════════════════════════════════════════════════════════════ */
QFrame#card {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E0E6F0;
}

/* ═══════════════════════════════════════════════════════════════════
   TABWIDGET (Módulo de Reportes)
═══════════════════════════════════════════════════════════════════ */
QTabWidget::pane {
    border: 1px solid #E0E6F0;
    border-radius: 0 10px 10px 10px;
    background: #FFFFFF;
    padding: 8px;
}
QTabBar::tab {
    background-color: #EDF1F7;
    color: #7B8A9E;
    border: 1px solid #E0E6F0;
    border-bottom: none;
    padding: 9px 22px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    margin-right: 3px;
}
QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #1A2942;
    border-bottom: 3px solid #FF6B2B;
}
QTabBar::tab:hover:!selected {
    background-color: #DDE5F0;
    color: #1A2942;
}

/* ═══════════════════════════════════════════════════════════════════
   PROGRESSBAR (exportación reportes)
═══════════════════════════════════════════════════════════════════ */
QProgressBar {
    background-color: #E0E6F0;
    border-radius: 6px;
    height: 10px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #FF6B2B;
    border-radius: 6px;
}

/* ═══════════════════════════════════════════════════════════════════
   SCROLLBARS
═══════════════════════════════════════════════════════════════════ */
QScrollBar:vertical {
    background: #F4F6FA; width: 8px; margin: 0; border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #C5CFE0; border-radius: 4px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #A0AFCA; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #F4F6FA; height: 8px; border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #C5CFE0; border-radius: 4px; min-width: 30px;
}

/* ═══════════════════════════════════════════════════════════════════
   DIALOG
═══════════════════════════════════════════════════════════════════ */
QDialog { background-color: #F4F6FA; }

QDialogButtonBox QPushButton {
    background-color: #FF6B2B;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 22px;
    font-weight: 700;
    font-size: 13px;
    min-width: 110px;
}
QDialogButtonBox QPushButton:hover { background-color: #E55A1E; }

/* Botón Cancel/Cancelar dentro de QDialogButtonBox */
QDialogButtonBox QPushButton[text="Cancel"],
QDialogButtonBox QPushButton[text="Cancelar"] {
    background-color: #FFFFFF;
    color: #1A2942;
    border: 2px solid #C5CFE0;
}
QDialogButtonBox QPushButton[text="Cancel"]:hover,
QDialogButtonBox QPushButton[text="Cancelar"]:hover {
    background-color: #1A2942;
    color: #FFFFFF;
    border-color: #1A2942;
}

/* ═══════════════════════════════════════════════════════════════════
   TOOLTIP
═══════════════════════════════════════════════════════════════════ */
QToolTip {
    background-color: #1A2942;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

# ── Diccionario de colores para uso directo en código Python ─────────────────
COLORS = {
    "primary":   "#1A2942",
    "accent":    "#FF6B2B",
    "surface":   "#F4F6FA",
    "card":      "#FFFFFF",
    "text":      "#1A2942",
    "muted":     "#7B8A9E",
    "success":   "#27AE60",
    "danger":    "#E74C3C",
    "warning":   "#E67E22",
    "info":      "#2980B9",
    "border":    "#E0E6F0",
}
