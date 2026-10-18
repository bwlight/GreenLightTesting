"""Offline Green Light visual theme. UI styling only; no calculation logic."""
import tkinter as tk
from tkinter import ttk

CHARCOAL = '#171B1A'
PANEL = '#252C29'
PANEL_RAISED = '#303A34'
ELECTRIC_GREEN = '#A8F22B'
TEXT = '#F2F5F1'
MUTED = '#C4D0C7'
DARK_TEXT = '#17200C'
WARNING = '#FFCC80'


def apply_theme(root):
    """Apply a high-contrast, consistent dark theme using bundled Tk/ttk only."""
    style = ttk.Style(root)
    style.theme_use('clam')
    root.configure(bg=CHARCOAL)
    style.configure('.', background=CHARCOAL, foreground=TEXT, font=('Segoe UI', 10))
    style.configure('TFrame', background=CHARCOAL)
    style.configure('TLabel', background=CHARCOAL, foreground=TEXT)
    style.configure('Muted.TLabel', foreground=MUTED)
    style.configure('Warning.TLabel', foreground=WARNING, font=('Segoe UI', 10, 'bold'))
    style.configure('Header.TLabel', foreground=ELECTRIC_GREEN, font=('Segoe UI Semibold', 17, 'bold'))
    style.configure('TLabelframe', background=PANEL, foreground=ELECTRIC_GREEN, bordercolor=PANEL_RAISED)
    style.configure('TLabelframe.Label', background=PANEL, foreground=ELECTRIC_GREEN, font=('Segoe UI', 11, 'bold'))
    style.configure('TEntry', fieldbackground=PANEL_RAISED, foreground=TEXT, insertcolor=TEXT, bordercolor=MUTED, padding=4)
    style.map('TEntry', fieldbackground=[('readonly', PANEL_RAISED), ('disabled', PANEL)], foreground=[('disabled', MUTED), ('readonly', TEXT)])
    style.configure('TCombobox', fieldbackground=PANEL_RAISED, background=PANEL_RAISED, foreground=TEXT, arrowcolor=ELECTRIC_GREEN, padding=4)
    style.map('TCombobox', fieldbackground=[('readonly', PANEL_RAISED)], foreground=[('readonly', TEXT)], selectbackground=[('readonly', PANEL_RAISED)], selectforeground=[('readonly', TEXT)])
    style.configure('TSpinbox', fieldbackground=PANEL_RAISED, background=PANEL_RAISED, foreground=TEXT, arrowcolor=ELECTRIC_GREEN, padding=4)
    style.configure('TButton', background=PANEL_RAISED, foreground=TEXT, bordercolor=MUTED, padding=(10, 7), font=('Segoe UI Semibold', 10))
    style.map('TButton', background=[('active', '#435347'), ('pressed', '#526550'), ('disabled', PANEL)], foreground=[('disabled', MUTED)])
    style.configure('Primary.TButton', background=ELECTRIC_GREEN, foreground=DARK_TEXT, bordercolor=ELECTRIC_GREEN, font=('Segoe UI Semibold', 10, 'bold'))
    style.map('Primary.TButton', background=[('active', '#C1FF5A'), ('pressed', '#8CD21C'), ('disabled', PANEL_RAISED)], foreground=[('active', DARK_TEXT), ('pressed', DARK_TEXT), ('disabled', MUTED)])
    style.configure('TCheckbutton', background=CHARCOAL, foreground=TEXT)
    style.map('TCheckbutton', background=[('active', CHARCOAL)], foreground=[('active', ELECTRIC_GREEN)])
    style.configure('TPanedwindow', background=CHARCOAL)
    style.configure('TNotebook', background=CHARCOAL, bordercolor=PANEL_RAISED)
    style.configure('TNotebook.Tab', background=PANEL_RAISED, foreground=TEXT, padding=(14, 8))
    style.map('TNotebook.Tab', background=[('selected', ELECTRIC_GREEN), ('active', '#435347')], foreground=[('selected', DARK_TEXT), ('active', TEXT)])
    style.configure('Treeview', background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=27, bordercolor=PANEL_RAISED)
    style.map('Treeview', background=[('selected', '#496B31')], foreground=[('selected', '#FFFFFF')])
    style.configure('Treeview.Heading', background=PANEL_RAISED, foreground=ELECTRIC_GREEN, font=('Segoe UI Semibold', 10, 'bold'))
    style.map('Treeview.Heading', background=[('active', '#435347')])
    return style
