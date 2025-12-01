# -*- coding: utf-8 -*-
import subprocess

def post_init_hook(cr, registry):
    pkgs = [
        'pytesseract',
        'pdf2image',
        'Pillow',
        'PyPDF2<3.0.0'
    ]
    try:
        subprocess.check_call(['pip3', 'install'] + pkgs)
    except Exception as e:
        print(f"[EAZYNOVA ACHAT OCR] Erreur installation dépendances OCR : {e}")
