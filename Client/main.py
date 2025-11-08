import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
# import os <-- Ya no es necesario

# --- DEFINICIÓN DE KIVY LANG (KV) ---
# (Indentación corregida)
KV = """
<ImageButton@ButtonBehavior+Image>:
    allow_stretch: True
    keep_ratio: True

<MainPanel>:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    BoxLayout:
        orientation: 'horizontal'
        spacing: 10
        size_hint_y: 0.4
        ImageButton:
            id: softphone_origen
            name: 'softphone_origen'
            on_press: root.handle_button_press(self.name)
            source: 'assets/softphone.png' 
        ImageButton:
            id: red_transporte
            name: 'red_transporte'
            on_press: root.handle_button_press(self.name)
            source: 'assets/network.png' 
        ImageButton:
            id: softphone_destino
            name: 'softphone_destino'
            on_press: root.handle_button_press(self.name)
            source: 'assets/softphone.png' 

    # --- ¡CORREGIDO! ---
    # (Este bloque estaba fuera de <MainPanel>)
    Button:
        text: 'Parámetros Globales (GoS/Costes)'
        size_hint_y: 0.15
        font_size: '18sp'
        on_press: root.open_global_popup()
    Label:
        id: panel_resultados
        text: 'Resultados y Alertas se mostrarán aquí.'
        size_hint_y: 0.45
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.1, 1
            Rectangle:
                pos: self.pos
                size: self.size
    # --- FIN DE LA CORRECCIÓN ---

<ConfigPopup>:
    title: root.title_text
    size_hint: (0.9, 0.9)
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        ScrollView:
            id: scroll_content
            size_hint_y: 0.85
        Button:
            text: 'Guardar y Cerrar'
            size_hint_y: 0.15
            font_size: '16sp'
            on_press: root.dismiss()

<GridForm>:
    cols: 2
    spacing: 10
    size_hint_y: None
    height: self.minimum_height
    row_default_height: 40
    row_force_default: True
"""

Builder.load_string(KV)


# --- CLASES DE LA APP VOIP ---

class GridForm(GridLayout):
    pass

class ConfigPopup(Popup):
    title_text = StringProperty("Configuración")
    content_widget = ObjectProperty(None)
    def __init__(self, title_text, content_widget, **kwargs):
        super().__init__(**kwargs)
        self.title_text = title_text
        self.ids.scroll_content.add_widget(content_widget)

class MainPanel(BoxLayout):
    # El 'on_kv_post' se ha eliminado porque las 'source'
    # están ahora en el string KV.
    
    def handle_button_press(self, button_name):
        if button_name == "softphone_origen":
            self.open_softphone_popup()
        elif button_name == "red_transporte":
            self.open_red_popup()
        elif button_name == "softphone_destino":
            self.open_destino_popup()

    def open_softphone_popup(self):
        form = GridForm()
        form.add_widget(Label(text="Calidad Voz (QoE) [Paso 2]:"))
        form.add_widget(Spinner(text="Buena", values=("Excelente", "Buena", "Normal", "Pobre", "Mala")))
        form.add_widget(Label(text="Codec (elegido) [Paso 2]:"))
        form.add_widget(Spinner(text="G.711", values=("G.711", "G.729", "G.723.1 (6.3)", "...")))
        form.add_widget(Label(text="BW Softphone (Kbps) [Paso 3]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        popup = ConfigPopup(title_text="Configuración Softphone (Origen)", content_widget=form)
        popup.open()

    def open_red_popup(self):
        form = GridForm()
        form.add_widget(Label(text="Encapsulación WAN (Tcwan):"))
        form.add_widget(Spinner(text="Ethernet", values=("Ethernet", "Ethernet+802.1q", "PPPoE")))
        form.add_widget(Label(text="Reserva BW (BWres %):"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        form.add_widget(Label(text="Tipo RTP [Paso 5]:"))
        form.add_widget(Spinner(text="RTP", values=("RTP", "cRTP")))
        form.add_widget(Label(text="Secuencia PLR [Paso 7]:"))
        form.add_widget(TextInput(multiline=False))
        form.add_widget(Label(text="O cargar PLR desde .txt:"))
        form.add_widget(Button(text="Abrir Fichero"))
        popup = ConfigPopup(title_text="Configuración Red de Transporte", content_widget=form)
        popup.open()

    def open_destino_popup(self):
        form = GridForm(cols=1)
        form.add_widget(Label(text="Este panel mostrará resultados."))
        form.add_widget(Label(text="(p.ej. Tamaño Buffer Anti-Jitter, Retardo Decodif.)"))
        form.add_widget(Label(text="No requiere configuración de entrada."))
        popup = ConfigPopup(title_text="Softphone (Destino) - Resultados", content_widget=form)
        popup.open()

    def open_global_popup(self):
        form = GridForm()
        form.add_widget(Label(text="Num. Empresas (Nc):"))
        form.add_widget(TextInput(multiline=False, input_filter="int"))
        form.add_widget(Label(text="Líneas / Cliente (Nl):"))
        form.add_widget(TextInput(multiline=False, input_filter="int"))
        form.add_widget(Label(text="T. Medio Llamada (Tpll):"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        form.add_widget(Label(text="Prob. Bloqueo (Pb) [GoS]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float", text="0.01"))
        form.add_widget(Label(text="Precio / Mbps [Costes]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        form.add_widget(Label(text="Precio Máx. Total [Costes]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        form.add_widget(Label(text="Email para Informe [Paso 8]:"))
        form.add_widget(TextInput(multiline=False))
        popup = ConfigPopup(title_text="Parámetros Globales, GoS y Costes", content_widget=form)
        popup.open()


# --- CLASES DEL SCREENMANAGER (5 PANTALLAS) ---

class MainWindow(Screen):
    """Pantalla 1: Solo botón NEXT"""
    def __init__(self, **kwargs):
        Screen.__init__(self,**kwargs)
        panel_voip = MainPanel()
        self.add_widget(panel_voip)
        button_next = Button(
            text='NEXT', 
            size_hint=(None,None), 
            size=(100,100), 
            pos_hint={'x': 0.875, 'y': 0},
            background_color=(0.2, 0.6, 1, 1)
        )
        button_next.bind(on_release=self.go)
        self.add_widget(button_next)

    def go(self, w):
        self.manager.switch_to(MainApp.second_window, direction='left') 

class SecondWindow(Screen):
    """Pantalla 2: Botones BACK y NEXT"""
    def __init__(self, **kwargs):
        Screen.__init__(self,**kwargs)
        
        panel_voip = MainPanel()
        self.add_widget(panel_voip)
        
        button_back = Button(
            text='BACK', 
            size_hint=(None,None), 
            size=(100,100), 
            pos_hint={'x': 0, 'y': 0},
            background_color=(1, 0.5, 0.2, 1)
        )
        button_back.bind(on_release=self.go_back)
        self.add_widget(button_back)

        button_next = Button(
            text='NEXT', 
            size_hint=(None,None), 
            size=(100,100), 
            pos_hint={'x': 0.875, 'y': 0},
            background_color=(0.2, 0.6, 1, 1)
        )
        button_next.bind(on_release=self.go_next)
        self.add_widget(button_next)

    def go_back(self, w):
        self.manager.switch_to(MainApp.main_window, direction='right')
        
    def go_next(self, w):
        self.manager.switch_to(MainApp.third_window, direction='left')


class ThirdWindow(Screen):
    """Pantalla 3: Botones BACK y NEXT"""
    def __init__(self, **kwargs):
        Screen.__init__(self,**kwargs)
        
        panel_voip = MainPanel()
        self.add_widget(panel_voip)
        
        button_back = Button(
            text='BACK', 
            size_hint=(None,None), 
            size=(100,100), 
            pos_hint={'x': 0, 'y': 0},
            background_color=(1, 0.5, 0.2, 1)
        )
        button_back.bind(on_release=self.go_back)
        self.add_widget(button_back)

        button_next = Button(
            text='NEXT', 
            size_hint=(None,None), 
            size=(100,100), 
            pos_hint={'x': 0.875, 'y': 0},
            background_color=(0.2, 0.6, 1, 1)
        )
        button_next.bind(on_release=self.go_next)
        self.add_widget(button_next)

    def go_back(self, w):
        self.manager.switch_to(MainApp.second_window, direction='right')

    def go_next(self, w):
        self.manager.switch_to(MainApp.fourth_window, direction='left')

class FourthWindow(Screen):
    """Pantalla 4: Botones BACK y NEXT"""
    def __init__(self, **kwargs):
        Screen.__init__(self,**kwargs)
        
        panel_voip = MainPanel()
        self.add_widget(panel_voip)
        
        button_back = Button(
            text='BACK', 
            size_hint=(None,None), 
            size=(100,100), 
            pos_hint={'x': 0, 'y': 0},
            background_color=(1, 0.5, 0.2, 1)
        )
        button_back.bind(on_release=self.go_back)
        self.add_widget(button_back)

        button_next = Button(
            text='NEXT', 
            size_hint=(None,None), 
            size=(100,100), 
            pos_hint={'x': 0.875, 'y': 0},
            background_color=(0.2, 0.6, 1, 1)
        )
        button_next.bind(on_release=self.go_next)
        self.add_widget(button_next)

    def go_back(self, w):
        self.manager.switch_to(MainApp.third_window, direction='right')

    def go_next(self, w):
        self.manager.switch_to(MainApp.fifth_window, direction='left')

class FifthWindow(Screen):
    """Pantalla 5: Solo botón BACK"""
    def __init__(self, **kwargs):
        Screen.__init__(self,**kwargs)
        
        panel_voip = MainPanel()
        self.add_widget(panel_voip)
        
        button_back = Button(
            text='BACK', 
            size_hint=(None,None), 
            size=(100,100), 
            pos_hint={'x': 0, 'y': 0},
            background_color=(1, 0.5, 0.2, 1)
        )
        button_back.bind(on_release=self.go_back)
        self.add_widget(button_back)

    def go_back(self, w):
        self.manager.switch_to(MainApp.fourth_window, direction='right')


# --- CLASE PRINCIPAL DE LA APP (5 PANTALLAS) ---

class MainApp(App):
    def build(self):
        screen_manager = ScreenManager()
        
        MainApp.main_window = MainWindow(name='main')
        MainApp.second_window = SecondWindow()
        MainApp.third_window = ThirdWindow()
        MainApp.fourth_window = FourthWindow()
        MainApp.fifth_window = FifthWindow()
        
        screen_manager.add_widget(MainApp.main_window)
        screen_manager.add_widget(MainApp.second_window)
        screen_manager.add_widget(MainApp.third_window)
        screen_manager.add_widget(MainApp.fourth_window)
        screen_manager.add_widget(MainApp.fifth_window)

        return screen_manager


# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    MainApp().run()