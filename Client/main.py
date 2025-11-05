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

kivy.require("2.1.0")

KV = """
<ImageButton@ButtonBehavior+Image>:
    # Un widget que combina un botón con una imagen
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

        # Imagen clicable para el Softphone de Origen
        ImageButton:
            id: softphone_origen
            name: 'softphone_origen'
            source: 'assets/softphone.png'
            on_press: root.handle_button_press(self.name)

        # Imagen clicable para la Red de Transporte
        ImageButton:
            id: red_transporte
            name: 'red_transporte'
            source: 'assets/network.png'
            on_press: root.handle_button_press(self.name)

        # Imagen clicable para el Softphone de Destino
        ImageButton:
            id: softphone_destino
            name: 'softphone_destino'
            source: 'assets/softphone.png'
            on_press: root.handle_button_press(self.name)

    # Botón para configuración global
    Button:
        text: 'Parámetros Globales (GoS/Costes)'
        size_hint_y: 0.15
        font_size: '18sp'
        on_press: root.open_global_popup()

    # Área de Resultados y Alertas
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
    """Panel principal de la aplicación"""

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
        form.add_widget(
            Spinner(
                text="Buena",
                values=("Excelente", "Buena", "Normal", "Pobre", "Mala"),
            )
        )
        form.add_widget(Label(text="Codec (elegido) [Paso 2]:"))
        form.add_widget(
            Spinner(text="G.711", values=("G.711", "G.729", "G.723.1 (6.3)", "..."))
        )
        form.add_widget(Label(text="BW Softphone (Kbps) [Paso 3]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        popup = ConfigPopup(
            title_text="Configuración Softphone (Origen)", content_widget=form
        )
        popup.open()

    def open_red_popup(self):
        form = GridForm()
        form.add_widget(Label(text="Encapsulación WAN (Tcwan):"))
        form.add_widget(
            Spinner(text="Ethernet", values=("Ethernet", "Ethernet+802.1q", "PPPoE"))
        )
        form.add_widget(Label(text="Reserva BW (BWres %):"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        form.add_widget(Label(text="Tipo RTP [Paso 5]:"))
        form.add_widget(Spinner(text="RTP", values=("RTP", "cRTP")))
        form.add_widget(Label(text="Secuencia PLR [Paso 7]:"))
        form.add_widget(TextInput(multiline=False))
        form.add_widget(Label(text="O cargar PLR desde .txt:"))
        form.add_widget(Button(text="Abrir Fichero"))
        popup = ConfigPopup(
            title_text="Configuración Red de Transporte", content_widget=form
        )
        popup.open()

    def open_destino_popup(self):
        form = GridForm(cols=1)
        form.add_widget(Label(text="Este panel mostrará resultados."))
        form.add_widget(
            Label(text="(p.ej. Tamaño Buffer Anti-Jitter, Retardo Decodif.)")
        )
        form.add_widget(Label(text="No requiere configuración de entrada."))
        popup = ConfigPopup(
            title_text="Softphone (Destino) - Resultados", content_widget=form
        )
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
        popup = ConfigPopup(
            title_text="Parámetros Globales, GoS y Costes", content_widget=form
        )
        popup.open()


class VoIPApp(App):
    def build(self):
        return MainPanel()


if __name__ == "__main__":
    VoIPApp().run()
