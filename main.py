import sqlite3
import urllib.parse
import webbrowser
from datetime import datetime

from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.utils import platform

# --- CONFIGURACIÓN PARA ANDROID / PYDROID 3 ---
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Window.softinput_mode = "below_target"

KV = '''
MDScreenManager:
    PantallaInicio:
    PantallaFormulario:

<PantallaInicio>:
    name: "inicio"
    md_bg_color: 0.05, 0.07, 0.1, 1
    
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "15dp"

        MDRaisedButton:
            text: "SALIR"
            md_bg_color: 0.8, 0.2, 0.2, 1
            pos_hint: {"right": 1}
            on_release: app.confirmar_salida()

        MDBoxLayout:
            orientation: "vertical"
            spacing: "5dp"
            adaptive_height: True
            
            MDLabel:
                text: "SEDI Junior"
                halign: "center"
                font_style: "H3"
                bold: True
                theme_text_color: "Custom"
                text_color: 0.8, 0.7, 0.5, 1

            MDLabel:
                text: "Villa 1° de Mayo\\ncalle 3 este # 53"
                halign: "center"
                font_style: "Subtitle1"
                theme_text_color: "Secondary"

        MDCard:
            orientation: "vertical"
            padding: "20dp"
            radius: 15
            elevation: 0
            md_bg_color: 0.11, 0.13, 0.16, 1
            
            MDLabel:
                text: "ESPECIALIDADES"
                halign: "center"
                bold: True
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
            
            MDLabel:
                text: "• Electricidad Domiciliaria e Industrial\\n• Electromecánica Especializada\\n• Línea Blanca y Refrigeración"
                halign: "center"
                theme_text_color: "Secondary"
        
        MDLabel:
            text: "Atención técnica inmediata"
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Hint"

        MDRaisedButton:
            text: "SOLICITAR SERVICIO"
            size_hint_x: 1
            height: "60dp"
            md_bg_color: 0.8, 0.7, 0.5, 1
            text_color: 0, 0, 0, 1
            bold: True
            on_release: root.manager.current = "formulario"

<PantallaFormulario>:
    name: "formulario"
    md_bg_color: 0.05, 0.07, 0.1, 1

    MDBoxLayout:
        orientation: "vertical"
        padding: "15dp"
        spacing: "10dp"

        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            MDRaisedButton:
                text: "VOLVER"
                on_release: root.manager.current = "inicio"
            Widget:
            MDRaisedButton:
                text: "SALIR"
                md_bg_color: 0.8, 0.2, 0.2, 1
                on_release: app.confirmar_salida()

        MDLabel:
            text: "REGISTRO DE CITA"
            halign: "center"
            font_style: "H5"
            bold: True
            theme_text_color: "Custom"
            text_color: 0.8, 0.7, 0.5, 1

        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: "15dp"

                MDTextField:
                    id: cliente
                    hint_text: "Su Nombre"
                    mode: "fill"
                    fill_color_normal: 0.1, 0.12, 0.15, 1

                MDTextField:
                    id: telefono
                    hint_text: "WhatsApp (Sin +591, solo 8 dígitos)"
                    mode: "fill"
                    input_filter: "int"
                    fill_color_normal: 0.1, 0.12, 0.15, 1

                MDRaisedButton:
                    id: btn_servicio
                    text: "ÁREA DE TRABAJO"
                    size_hint_x: 1
                    on_release: app.abrir_menu_principal()

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "10dp"
                    size_hint_y: None
                    height: "50dp"
                    
                    MDRaisedButton:
                        id: btn_fecha
                        text: "FECHA"
                        size_hint_x: 0.5
                        on_release: app.abrir_calendario()
                    
                    MDRaisedButton:
                        id: btn_hora
                        text: "HORA"
                        size_hint_x: 0.5
                        on_release: app.abrir_reloj()

                MDRaisedButton:
                    text: "RESERVAR Y ENVIAR"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.8, 0.7, 0.5, 1
                    text_color: 0, 0, 0, 1
                    bold: True
                    on_release: app.validar_disponibilidad()
'''

class PantallaInicio(MDScreen):
    pass

class PantallaFormulario(MDScreen):
    pass

class SediMasterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        self.num_recepcion = "59178136808" # Número Admin
        self.servicio_detalle = ""
        self.rubro_base = ""
        self.fecha_final = ""
        self.hora_final = ""
        self.dialog = None
        
        self.menu_data = {
            "Electricidad": ["Domiciliaria", "Industrial"],
            "Línea Blanca": ["Lavadoras", "Secadoras", "Aires Acondicionados", "Microondas"],
            "Electromecánica": ["Herramientas de Construcción", "Herramientas de Jardinería"]
        }
        self.crear_db()
        return Builder.load_string(KV)

    def crear_db(self):
        conn = sqlite3.connect("sedi_reservas.db")
        conn.cursor().execute('''CREATE TABLE IF NOT EXISTS citas 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, telefono TEXT, 
             rubro TEXT, servicio TEXT, fecha TEXT, hora TEXT)''')
        conn.commit()
        conn.close()

    def smart_open(self, url):
        if platform == 'android':
            try:
                from jnius import autoclass, cast
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                
                intent = Intent(Intent.ACTION_VIEW)
                intent.setData(Uri.parse(url))
                
                # Forzar apertura externa
                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                currentActivity.startActivity(intent)
            except Exception as e:
                print(f"Error Intent: {e}")
                webbrowser.open(url)
        else:
            webbrowser.open(url)

    def abrir_menu_principal(self):
        caller = self.root.get_screen("formulario").ids.btn_servicio
        items = [{"viewclass": "OneLineListItem", "text": r, "on_release": lambda x=r: self.abrir_sub_menu(x)} for r in self.menu_data.keys()]
        self.menu = MDDropdownMenu(caller=caller, items=items, width=400)
        self.menu.open()

    def abrir_sub_menu(self, rubro):
        self.menu.dismiss()
        caller = self.root.get_screen("formulario").ids.btn_servicio
        sub_items = [{"viewclass": "OneLineListItem", "text": s, "on_release": lambda x=s, r=rubro: self.seleccionar_final(r, x)} for s in self.menu_data[rubro]]
        self.menu = MDDropdownMenu(caller=caller, items=sub_items, width=400)
        self.menu.open()

    def seleccionar_final(self, rubro, sub):
        self.rubro_base, self.servicio_detalle = rubro, f"{rubro}: {sub}"
        self.root.get_screen("formulario").ids.btn_servicio.text = self.servicio_detalle
        self.menu.dismiss()

    def abrir_calendario(self):
        d = MDDatePicker()
        d.bind(on_save=lambda i, v, r: self.set_fecha(v))
        d.open()

    def set_fecha(self, v):
        self.fecha_final = str(v)
        self.root.get_screen("formulario").ids.btn_fecha.text = self.fecha_final

    def abrir_reloj(self):
        t = MDTimePicker()
        t.bind(on_save=lambda i, v: self.set_hora(v))
        t.open()

    def set_hora(self, v):
        self.hora_final = v.strftime("%H:%M")
        self.root.get_screen("formulario").ids.btn_hora.text = self.hora_final

    def confirmar_salida(self):
        self.dialog = MDDialog(
            text="¿Desea cerrar la aplicación?",
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="SALIR", on_release=lambda x: self.stop())
            ],
        )
        self.dialog.open()

    def validar_disponibilidad(self):
        ids = self.root.get_screen("formulario").ids
        cliente = ids.cliente.text
        telf = ids.telefono.text

        if not all([cliente, telf, self.servicio_detalle, self.fecha_final, self.hora_final]):
            self.mostrar_alerta("Por favor, llene todos los campos.")
            return

        try:
            conn = sqlite3.connect("sedi_reservas.db")
            c = conn.cursor()
            c.execute("INSERT INTO citas (cliente, telefono, rubro, servicio, fecha, hora) VALUES (?,?,?,?,?,?)",
                      (cliente, telf, self.rubro_base, self.servicio_detalle, self.fecha_final, self.hora_final))
            conn.commit()
            conn.close()
            
            # Paso 1: Enviar al Admin vía wa.me
            self.enviar_a_whatsapp(self.num_recepcion, cliente, telf, es_admin=True)
            
            # Paso 2: Mostrar diálogo para confirmar al cliente
            self.mostrar_dialogo_exito(cliente, telf)
            
        except Exception as e:
            self.mostrar_alerta(f"Error: {e}")

    def enviar_a_whatsapp(self, numero, cliente, telf, es_admin=False):
        if es_admin:
            msg = (f"*SOLICITUD SEDI JUNIOR*\n\n"
                   f"👤 Cliente: {cliente}\n"
                   f"📞 Telf: {telf}\n"
                   f"🛠️ Servicio: {self.servicio_detalle}\n"
                   f"📅 Fecha: {self.fecha_final}\n"
                   f"⏰ Hora: {self.hora_final}")
        else:
            msg = (f"Hola *{cliente}*, recibimos tu solicitud en *SEDI Junior*.\n\n"
                   f"🛠️ *Servicio:* {self.servicio_detalle}\n"
                   f"📅 *Fecha:* {self.fecha_final}\n"
                   f"⏰ *Hora:* {self.hora_final}\n\n"
                   f"Un técnico te contactará pronto.")

        msg_encoded = urllib.parse.quote(msg)
        # Formato wa.me con https:// explícito
        url = f"https://wa.me/{numero}?text={msg_encoded}"
        self.smart_open(url)

    def mostrar_dialogo_exito(self, cliente, telf):
        self.dialog = MDDialog(
            title="¡Solicitud Registrada!",
            text="Se envió el reporte al administrador. ¿Deseas enviar el comprobante de recibo al cliente ahora?",
            buttons=[
                MDFlatButton(text="NO", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(
                    text="ENVIAR RECIBO",
                    md_bg_color=(0.1, 0.7, 0.3, 1),
                    on_release=lambda x: self.confirmar_al_cliente(cliente, telf)
                )
            ],
        )
        self.dialog.open()

    def confirmar_al_cliente(self, cliente, telf):
        self.dialog.dismiss()
        # Se asume Bolivia (591) + los 8 dígitos ingresados
        self.enviar_a_whatsapp(f"591{telf}", cliente, telf, es_admin=False)

    def mostrar_alerta(self, texto):
        self.dialog = MDDialog(text=texto, buttons=[MDFlatButton(text="CERRAR", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

if __name__ == "__main__":
    SediMasterApp().run()
