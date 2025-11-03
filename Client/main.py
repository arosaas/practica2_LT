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

# --- Kivy Language String (para Estilos) ---
KV = """
<MainPanel>:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    BoxLayout:
        orientation: 'horizontal'
        spacing: 10
        size_hint_y: 0.4 # 40% de la altura para los 3 botones

        # Botones para los 3 elementos de la topología
        TopologyButton:
            id: softphone_origen
            text: '1. Softphone (Origen)'
            on_press: root.open_softphone_popup()
        TopologyButton:
            id: red_transporte
            text: '2. Red de Transporte'
            on_press: root.open_red_popup()
        TopologyButton:
            id: softphone_destino
            text: '3. Softphone (Destino)'
            on_press: root.open_destino_popup()

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

<TopologyButton@Button>:
    # Widget personalizado para los 3 botones principales
    status_text: 'Sin configurar'
    BoxLayout:
        orientation: 'vertical'
        pos: self.pos
        size: self.size
        padding: 10
        
        Label:
            text: root.text # El texto del botón (p.ej. '1. Softphone')
            font_size: '18sp'
            bold: True
            size_hint_y: 0.7
        Label:
            text: f"Estado: {root.status_text}"
            font_size: '14sp'
            color: (1, 0.8, 0.8, 1) # Color por defecto (rojo claro)
            size_hint_y: 0.3

<ConfigPopup>:
    title: root.title_text
    size_hint: (0.9, 0.9)
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        # El ScrollView contendrá el formulario (GridForm)
        ScrollView:
            id: scroll_content
            size_hint_y: 0.85

        # Botón para cerrar el popup
        Button:
            text: 'Guardar y Cerrar'
            size_hint_y: 0.15
            font_size: '16sp'
            on_press: root.dismiss()

<GridForm>:
    # Layout reutilizable para los formularios
    cols: 2
    spacing: 10
    size_hint_y: None
    height: self.minimum_height  # <--- ESTA ES LA LÍNEA CORREGIDA
    row_default_height: 40
    row_force_default: True
"""

# --- Clases de Python ---

Builder.load_string(KV)


class GridForm(GridLayout):
    """Un GridLayout que se auto-ajusta en altura para el ScrollView."""

    pass


class ConfigPopup(Popup):
    """Popup genérico para configuración."""

    title_text = StringProperty("Configuración")
    content_widget = ObjectProperty(None)

    def __init__(self, title_text, content_widget, **kwargs):
        super().__init__(**kwargs)
        self.title_text = title_text
        # Añadimos el widget de contenido (el formulario) al ScrollView
        self.ids.scroll_content.add_widget(content_widget)


class MainPanel(BoxLayout):
    """El widget raíz de la aplicación."""

    def open_softphone_popup(self):
        # 1. Crear el layout del formulario
        form = GridForm()

        # 2. Añadir los widgets específicos de "Softphone"
        form.add_widget(Label(text="Calidad Voz (QoE) [Paso 2]:"))
        form.add_widget(
            Spinner(
                text="Buena", values=("Excelente", "Buena", "Normal", "Pobre", "Mala")
            )
        )

        form.add_widget(Label(text="Codec (elegido) [Paso 2]:"))
        form.add_widget(
            Spinner(text="G.711", values=("G.711", "G.729", "G.723.1 (6.3)", "..."))
        )  # etc.

        form.add_widget(Label(text="BW Softphone (Kbps) [Paso 3]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))

        # 3. Crear y abrir el Popup
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
        form.add_widget(Button(text="Abrir Fichero"))  # Lógica no implementada

        popup = ConfigPopup(
            title_text="Configuración Red de Transporte", content_widget=form
        )
        popup.open()

    def open_destino_popup(self):
        # El Softphone de destino tiene pocos *inputs* y más *resultados*
        # (Jitter buffer, retardo decodificación)
        form = GridForm(cols=1)  # 1 sola columna
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
