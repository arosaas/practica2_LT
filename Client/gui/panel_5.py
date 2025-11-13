from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from .popups import ConfigPopup, GridForm
from kivy.app import App
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from .message_sender import MessageSender

# Configuración de campos para Simulación PLR (Paso 5)
PLR_PARAMS_FIELDS = [
    ("Paquetes Enviados:", "int", "100000", "Paquetes Enviados"),
    ("Paquetes Perdidos (Red):", "int", "50", "Paquetes Perdidos"),
]


class Step5Panel(BoxLayout):
    """Panel para Paso 5: Simulación PLR (PLR_REQUEST)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10
        self.section = "Parámetros de PLR"

    def handle_button_press(self, button_name):
        if button_name == "softphone_destino":
            self.show_plr_results()

    def open_config_popup(self):
        """Abre popup para configurar Parámetros de PLR."""
        form = GridForm()

        for label_text, input_type, default, field_name in PLR_PARAMS_FIELDS:
            widget = self._create_input_field(form, label_text, default, input_type)
            widget.bind(
                text=lambda i, v, lt=label_text: self._on_field_change(i, v, lt)
            )
            # Inicializar valor por defecto
            self._on_field_change(widget, default, label_text)

        popup = ConfigPopup(
            title_text="Parámetros de PLR - Simulación", content_widget=form
        )
        popup.open()

    def send_plr_data(self):
        """Envía PLR_REQUEST al servidor."""
        app = App.get_running_app()
        plr_data = getattr(app, "summary_data", {}).get(self.section, {})

        try:
            # Recoger datos de app.summary_data
            # Necesitamos 'jitter' de los parámetros del Softphone (Paso 1)
            jitter_ms = (
                getattr(app, "summary_data", {})
                .get("Softphone (Origen)", {})
                .get("Jitter (ms)", 30)
            )

            payload = {
                "packetsSent": int(plr_data.get("Paquetes Enviados", 100000)),
                "packetsLost": int(plr_data.get("Paquetes Perdidos", 50)),
                "jitterMs": float(jitter_ms),  # Enviar jitter de Paso 1
            }
            MessageSender.send("PLR_REQUEST", payload, callback=self._on_plr_response)
        except (ValueError, KeyError) as e:
            self._show_error_popup(
                f"Valores inválidos o faltan datos de Jitter (Paso 1): {str(e)}"
            )

    def _on_plr_response(self, response):
        """Callback para procesar la respuesta PLR_RESPONSE."""
        try:
            plr_data = response if isinstance(response, dict) else {}

            app = App.get_running_app()
            if not hasattr(app, "plr_results_data"):
                app.plr_results_data = {}

            # Asumiendo que el servidor devuelve {"packetLossRate": X, "jitterDiscards": Y, "totalLoss": Z}
            app.plr_results_data["PLR Red (%)"] = plr_data.get("packetLossRate", "---")
            app.plr_results_data["Descartes Jitter"] = plr_data.get(
                "jitterDiscards", "---"
            )
            app.plr_results_data["Pérdida Total (%)"] = plr_data.get("totalLoss", "---")

            MessageSender._show_popup_success("PLR_REQUEST", {}, response)
        except Exception as e:
            self._show_error_popup(f"Error procesando respuesta PLR: {str(e)}")

    def show_plr_results(self):
        """Muestra los resultados de PLR guardados."""
        app = App.get_running_app()
        form = GridForm(cols=2)

        results = getattr(
            app,
            "plr_results_data",
            {
                "PLR Red (%)": "---",
                "Descartes Jitter": "---",
                "Pérdida Total (%)": "---",
            },
        )

        for key, value in results.items():
            form.add_widget(Label(text=f"{key}:"))
            form.add_widget(Label(text=str(value), color=(1, 1, 1, 1), size_hint_x=1))

        popup = ConfigPopup(
            title_text="Softphone (Destino) - Resultados PLR", content_widget=form
        )
        popup.open()

    # --- Métodos Helper (idénticos a paneles anteriores) ---

    def _create_input_field(self, form, label_text, default_value, input_type):
        form.add_widget(Label(text=label_text))
        widget = TextInput(multiline=False, text=default_value)
        if input_type == "float":
            widget.input_filter = "float"
        elif input_type == "int":
            widget.input_filter = "int"
        form.add_widget(widget)
        return widget

    def _on_field_change(self, instance, value, label_text):
        field_name = self._get_field_name(label_text)
        if field_name:
            self._update_data(field_name, value)
            self._update_summary_display()

    def _get_field_name(self, label_text):
        for label, _, _, field_name in PLR_PARAMS_FIELDS:
            if label == label_text:
                return field_name
        return None

    def _update_data(self, field_name, value):
        app = App.get_running_app()
        if not hasattr(app, "summary_data"):
            app.summary_data = {}
        if self.section not in app.summary_data:
            app.summary_data[self.section] = {}

        if value:
            app.summary_data[self.section][field_name] = value
        elif field_name in app.summary_data[self.section]:
            del app.summary_data[self.section][field_name]

    def _update_summary_display(self):
        app = App.get_running_app()
        data = getattr(app, "summary_data", {}).get(self.section, {})

        if not data:
            summary_str = "Sin parámetros configurados aún."
        else:
            summary_str = f"{self.section.upper()}:\n"
            for field_name, value in data.items():
                summary_str += f"   • {field_name}: {value}\n"

        if hasattr(self, "ids") and "panel_resultados" in self.ids:
            self.ids.panel_resultados.text = summary_str

    def _show_error_popup(self, message):
        form = GridForm()
        form.add_widget(Label(text=f"Error: {message}"))
        popup = ConfigPopup(title_text="Error de Entrada", content_widget=form)
        popup.open()
