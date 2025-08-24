import kivy
import os
import math
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Ellipse, Rotate, PushMatrix, PopMatrix
from kivy.core.window import Window

# Import your backend logic
from plume_model import calculate_plume
from dose_decay import generate_dose_data

Window.size = (1000, 700)

class PlumeDrawingWidget(Widget):
    """A custom widget for drawing the fallout plume."""
    def __init__(self, plume_length, plume_width, plume_angle, **kwargs):
        super().__init__(**kwargs)
        self.plume_length = plume_length
        self.plume_width = plume_width
        self.plume_angle = plume_angle
        self.draw_plume()

    def draw_plume(self):
        self.canvas.clear()
        
        center_x = self.width / 2
        center_y = self.height / 2
        
        with self.canvas:
            PushMatrix()
            # Rotate the canvas based on the plume's angle
            rotate = Rotate(angle=self.plume_angle, origin=(center_x, center_y))
            
            # Draw a semi-transparent yellow outer zone
            Color(1, 1, 0, 0.5)
            Ellipse(pos=(center_x - self.plume_length / 2, center_y - self.plume_width / 2),
                    size=(self.plume_length, self.plume_width))

            # Draw a more opaque inner red zone
            Color(1, 0, 0, 0.8)
            inner_length = self.plume_length * 0.4
            inner_width = self.plume_width * 0.4
            Ellipse(pos=(center_x - inner_length / 2, center_y - inner_width / 2),
                    size=(inner_length, inner_width))
            
            PopMatrix()


class NuclearApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation='horizontal')
        
        # Left-side layout for map and plume
        self.map_area = Widget(size_hint_x=0.7)
        self.map_area.canvas.add(Color(0.2, 0.2, 0.2))
        self.map_area.canvas.add(kivy.graphics.Rectangle(pos=self.map_area.pos, size=self.map_area.size))
        
        # Controls panel on the right
        self.controls = GridLayout(cols=1, spacing=10, padding=10, size_hint_x=0.3)
        self.controls.add_widget(Label(text='Nuclear Fallout Simulator', size_hint_y=None, height=40))

        self.controls.add_widget(Label(text='Location:', size_hint_y=None, height=30))
        self.location_input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.lat_input = TextInput(text='28.6', hint_text='Lat', multiline=False)
        self.lon_input = TextInput(text='77.2', hint_text='Lon', multiline=False)
        self.location_input_layout.add_widget(self.lat_input)
        self.location_input_layout.add_widget(self.lon_input)
        self.controls.add_widget(self.location_input_layout)
        
        self.controls.add_widget(Label(text='Yield (kilotons):', size_hint_y=None, height=30))
        self.yield_input = TextInput(text='15', multiline=False, size_hint_y=None, height=30)
        self.controls.add_widget(self.yield_input)
        
        self.controls.add_widget(Label(text='Wind Speed (km/h):', size_hint_y=None, height=30))
        self.wind_speed_input = TextInput(text='20', multiline=False, size_hint_y=None, height=30)
        self.controls.add_widget(self.wind_speed_input)
        
        self.controls.add_widget(Label(text='Wind Direction:', size_hint_y=None, height=30))
        self.wind_direction_spinner = Spinner(
            text='NE', values=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
            size_hint=(None, None), size=(100, 40)
        )
        self.controls.add_widget(self.wind_direction_spinner)
        
        self.detonate_button = Button(text='Simulate Fallout', size_hint_y=None, height=50)
        self.detonate_button.bind(on_press=self.run_simulation)
        self.controls.add_widget(self.detonate_button)
        
        self.show_graph_button = Button(text='Show Dose Graph', size_hint_y=None, height=50)
        self.show_graph_button.bind(on_press=self.show_dose_graph)
        self.controls.add_widget(self.show_graph_button)

        self.main_layout.add_widget(self.map_area)
        self.main_layout.add_widget(self.controls)
        
        return self.main_layout

    def run_simulation(self, instance):
        try:
            yield_mt = float(self.yield_input.text)
            wind_speed = float(self.wind_speed_input.text)
            wind_direction = self.wind_direction_spinner.text

            plume_dimensions = calculate_plume(yield_mt, wind_speed, wind_direction)
            
            if hasattr(self, 'plume_widget'):
                self.map_area.remove_widget(self.plume_widget)
            
            # Pass the calculated dimensions to your drawing widget
            plume_length_scaled = plume_dimensions['length'] * 10
            plume_width_scaled = plume_dimensions['width'] * 10
            plume_angle = plume_dimensions['angle']
            
            self.plume_widget = PlumeDrawingWidget(plume_length_scaled, plume_width_scaled, plume_angle)
            self.map_area.add_widget(self.plume_widget)

        except ValueError:
            pass

    def show_dose_graph(self, instance):
        # 1. Generate the data points
        time_points, dose_data = generate_dose_data(1000)
        
        # 2. Create the Matplotlib plot
        plt.style.use('dark_background')
        plt.figure(figsize=(6, 4))
        plt.plot(time_points, dose_data, color='cyan')
        plt.title('Dose Rate vs. Time', color='white')
        plt.xlabel('Time (hours)', color='white')
        plt.ylabel('Dose Rate (rad/hr)', color='white')
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # 3. Save the plot to a temporary file
        plot_path = os.path.join(os.getcwd(), 'dose_graph.png')
        plt.savefig(plot_path, transparent=True)
        plt.close()
        
        # 4. Display the image in a Popup
        content = BoxLayout(orientation='vertical')
        graph_image = KivyImage(source=plot_path, allow_stretch=True, keep_ratio=True)
        close_button = Button(text='Close', size_hint_y=None, height=50)
        
        content.add_widget(graph_image)
        content.add_widget(close_button)
        
        popup = Popup(title='Dose Rate Graph', content=content, size_hint=(0.8, 0.8), auto_dismiss=False)
        close_button.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    NuclearApp().run()