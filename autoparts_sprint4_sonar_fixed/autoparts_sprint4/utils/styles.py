"""
AutoParts Express - Estilos globales (blanco suavizado)
"""

APP_STYLE = """
QWidget {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
    color: #2C3E50;
    background-color: transparent;
}
QMainWindow,
QMainWindow > QWidget,
QStackedWidget,
QStackedWidget > QWidget {
    background-color: #EAECEE;
}

/* Botón primario */
QPushButton#btn_primary {
    background-color: #FF6B2B;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 700;
}
QPushButton#btn_primary:hover { background-color: #E55A1E; }

/* Botón secundario */
QPushButton#btn_secondary {
    background-color: #F8F9FA;
    color: #2C3E50;
    border: 1.5px solid #BDC3C7;
    border-radius: 8px;
    padding: 9px 20px;
    font-weight: 700;
}
QPushButton#btn_secondary:hover {
    background-color: #E2E6E9;
    color: #1A252F;
}

/* Navegación sidebar */
QPushButton#btn_nav {
    background-color: transparent;
    color: #8FA4BE;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
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

/* Inputs */
QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox {
    background-color: #F8F9FA;
    border: 1.5px solid #D5D8DC;
    border-radius: 8px;
    padding: 9px 14px;
    color: #2C3E50;
}
QLineEdit:focus { border-color: #FF6B2B; }

/* Tablas */
QTableWidget {
    background-color: #F8F9FA;
    alternate-background-color: #F2F3F4;
    border: 1px solid #E5E7E9;
}
QTableWidget::item:selected {
    background-color: #FFF0E8;
    color: #2C3E50;
}
QHeaderView::section {
    background-color: #1A2942;
    color: #FFFFFF;
    padding: 10px;
    font-weight: 700;
}

/* Cards */
QFrame#card {
    background-color: #F8F9FA;
    border-radius: 12px;
    border: 1px solid #E5E7E9;
}

/* Tabs */
QTabWidget::pane {
    background-color: #F8F9FA;
    border: 1px solid #E5E7E9;
}
QTabBar::tab {
    background-color: #E8ECEF;
    color: #7B8A9E;
    padding: 9px 22px;
}
QTabBar::tab:selected {
    background-color: #F8F9FA;
    color: #2C3E50;
    border-bottom: 3px solid #FF6B2B;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #EAECEE;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #BDC3C7;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #95A5A6;
}
"""

COLORS = {
    "primary": "#1A2942",
    "accent": "#FF6B2B",
    "surface": "#EAECEE",
    "card": "#F8F9FA",
    "text": "#2C3E50",
    "muted": "#7B8A9E",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "warning": "#E67E22",
    "info": "#2980B9",
    "border": "#D5D8DC",
}