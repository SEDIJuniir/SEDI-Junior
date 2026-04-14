[app]
title = SEDI Master
package.name = sedimaster
package.domain = org.sedi
source.dir = .
source.include_exts = py,png,jpg,kv,db
version = 1.0

# Requisitos necesarios para tu código
requirements = python3, kivy==2.3.0, kivymd==1.2.0, pyjnius, sqlite3, pillow

orientation = portrait

# --- ANDROID ---
android.permissions = INTERNET
android.api = 33
android.minapi = 21

# ESTO ES LO MÁS IMPORTANTE PARA QUE ABRA WHATSAPP
android.manifest.queries = com.whatsapp, com.whatsapp.w4b

# Arquitecturas para celulares modernos
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
