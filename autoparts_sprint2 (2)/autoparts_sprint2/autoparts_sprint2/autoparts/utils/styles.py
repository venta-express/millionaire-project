"""
AutoParts Express - Estilos globales de la aplicación
Paleta: Azul oscuro profesional + naranja vibrante como acento
"""

APP_STYLE = """
/* ── Variables de color simuladas con comentarios ────────────────────── */
/* PRIMARY   : #1A2942  (azul marino oscuro)                             */
/* ACCENT    : #FF6B2B  (naranja vibrante)                               */
/* SURFACE   : #F4F6FA  (gris muy claro)                                 */
/* CARD      : #FFFFFF                                                   */
/* TEXT      : #1A2942                                                   */
/* MUTED     : #7B8A9E                                                   */
/* SUCCESS   : #27AE60                                                   */
/* DANGER    : #E74C3C                                                   */
/* WARNING   : #F39C12                                                   */

QWidget {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
    color: #1A2942;
    background-color: transparent;
}

QMainWindow, QMainWindow > QWidget,
QStackedWidget, QStackedWidget > QWidget {
    background-color: #F4F6FA;
}

/* ── Botón primario ────────────────────────────────────────────────── */
QPushButton#btn_primary {
    background-color: #FF6B2B;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.3px;
}
QPushButton#btn_primary:hover {
    background-color: #E55A1E;
}
QPushButton#btn_primary:pressed {
    background-color: #CC4D15;
}
QPushButton#btn_primary:disabled {
    background-color: #CCCCCC;
    color: #888888;
}

/* ── Botón secundario ──────────────────────────────────────────────── */
QPushButton#btn_secondary {
    background-color: transparent;
    color: #1A2942;
    border: 2px solid #1A2942;
    border-radius: 8px;
    padding: 9px 22px;
    font-weight: 600;
    font-size: 14px;
}
QPushButton#btn_secondary:hover {
    background-color: #1A2942;
    color: white;
}

/* ── Botón peligro ──────────────────────────────────────────────────── */
QPushButton#btn_danger {
    background-color: #E74C3C;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 14px;
}
QPushButton#btn_danger:hover {
    background-color: #C0392B;
}

/* ── Botón éxito ────────────────────────────────────────────────────── */
QPushButton#btn_success {
    background-color: #27AE60;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 14px;
}
QPushButton#btn_success:hover {
    background-color: #1E8449;
}

/* ── Botón ghost (sidebar nav) ─────────────────────────────────────── */
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
    background-color: rgba(255,255,255,0.08);
    color: white;
}
QPushButton#btn_nav[active="true"] {
    background-color: rgba(255,107,43,0.18);
    color: #FF6B2B;
    font-weight: 700;
}

/* ── Inputs ────────────────────────────────────────────────────────── */
QLineEdit {
    background-color: white;
    border: 1.5px solid #D8E0EC;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    color: #1A2942;
    selection-background-color: #FF6B2B;
}
QLineEdit:focus {
    border-color: #FF6B2B;
    outline: none;
}
QLineEdit:disabled {
    background-color: #F0F2F5;
    color: #AAAAAA;
}
QLineEdit[error="true"] {
    border-color: #E74C3C;
}

/* ── ComboBox ───────────────────────────────────────────────────────── */
QComboBox {
    background-color: white;
    border: 1.5px solid #D8E0EC;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    color: #1A2942;
    min-width: 120px;
}
QComboBox:focus { border-color: #FF6B2B; }
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox::down-arrow {
    image: none;
    width: 0;
}
QComboBox QAbstractItemView {
    background: white;
    border: 1px solid #D8E0EC;
    border-radius: 6px;
    selection-background-color: #FF6B2B;
    selection-color: white;
    padding: 4px;
}

/* ── Tabla ──────────────────────────────────────────────────────────── */
QTableWidget {
    background-color: white;
    border: 1px solid #E8ECF4;
    border-radius: 10px;
    gridline-color: #F0F4FA;
    outline: none;
    selection-background-color: #FFF0E8;
    selection-color: #1A2942;
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
    color: white;
    padding: 10px 12px;
    border: none;
    font-weight: 600;
    font-size: 13px;
}
QHeaderView::section:first {
    border-top-left-radius: 10px;
}
QHeaderView::section:last {
    border-top-right-radius: 10px;
}

/* ── Scroll bars ─────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #F4F6FA;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #C5CFE0;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #A0AFCA; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #F4F6FA;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #C5CFE0;
    border-radius: 4px;
    min-width: 30px;
}

/* ── Labels ─────────────────────────────────────────────────────────── */
QLabel#label_title {
    font-size: 22px;
    font-weight: 700;
    color: #1A2942;
}
QLabel#label_subtitle {
    font-size: 13px;
    color: #7B8A9E;
}
QLabel#label_error {
    color: #E74C3C;
    font-size: 12px;
    font-weight: 500;
}
QLabel#label_success {
    color: #27AE60;
    font-size: 12px;
    font-weight: 500;
}
QLabel#badge_alta {
    background-color: #FDEDEC;
    color: #E74C3C;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 12px;
}
QLabel#badge_media {
    background-color: #FEF9E7;
    color: #F39C12;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 12px;
}

/* ── Card (QFrame) ───────────────────────────────────────────────────── */
QFrame#card {
    background-color: white;
    border-radius: 12px;
    border: 1px solid #E8ECF4;
}

/* ── Sidebar ────────────────────────────────────────────────────────── */
QFrame#sidebar {
    background-color: #1A2942;
    border-radius: 0px;
}

/* ── SpinBox ────────────────────────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {
    background-color: white;
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
    background: #F4F6FA;
    border: none;
    border-radius: 4px;
}

/* ── MessageBox / Dialog ─────────────────────────────────────────────── */
QDialog {
    background-color: #F4F6FA;
}

/* ── ToolTip ─────────────────────────────────────────────────────────── */
QToolTip {
    background-color: #1A2942;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

# Colores como constantes Python para uso en widgets
COLORS = {
    "primary":   "#1A2942",
    "accent":    "#FF6B2B",
    "surface":   "#F4F6FA",
    "card":      "#FFFFFF",
    "text":      "#1A2942",
    "muted":     "#7B8A9E",
    "success":   "#27AE60",
    "danger":    "#E74C3C",
    "warning":   "#F39C12",
    "border":    "#D8E0EC",
}
