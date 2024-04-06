import os
import regex
from glob import glob
import matplotlib.axes
import matplotlib.text
import matplotlib.font_manager as fm

def install_fonts():
    font_manager: fm.FontManager = fm.fontManager
    for file in glob(os.path.join('assets/fonts', '*.[ot]tf')):
        print(f"Installing font {file}")
        font_manager.addfont(file)


def change_fonts(ax: matplotlib.axes.Axes):
    for child in ax.get_children():
        if isinstance(child, matplotlib.text.Annotation):
            a: matplotlib.text.Annotation = child
            a.set_fontfamily(determine_font(a.get_text()))

    y_axis = ax.get_yaxis()
    for text in y_axis.get_ticklabels():
        text.set_fontfamily(determine_font(text.get_text()))    


def determine_font(text: str):
    if regex.search(r'\p{IsHangul}', text):
        return 'Noto Sans KR'
    if regex.search(r'[\p{IsBopo}\p{IsHira}\p{IsKatakana}]', text):
        return 'Noto Sans JP'
    if regex.search(r'\p{Han}', text):
        return 'Noto Sans SC'
    if regex.search(r'\p{IsHebrew}', text):
        return 'Noto Sans Hebrew Condensed'
    return 'DejaVu Sans'
