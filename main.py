# main.py (Fixed Import Error - Complete Version)

import kivy
import os
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
from kivy.graphics import Color, Rotate, PushMatrix, PopMatrix, Rectangle
# CORRECT IMPORTS: Use Mesh and Line for drawing shapes
from kivy.graphics.vertex_instructions import Mesh, Line
from kivy.core.window import Window

# Import the correct function from your backend
from plume_model import calculate_full_plume
from dose_decay import generate_dose_data

Window.size = (1000, 700)

class PlumeDrawingWidget(Widget):
    """A custom widget for drawing the fallout plume polygons."""
    def __init__(self, contours, angle, **kwargs):
        super().__init__(**kwargs)
        self.contours = contours
        self.angle = angle
        # This dictionary maps dose levels to colors (R, G, B, Alpha)
        self.dose_colors = {
            '1000_rad_hr': (1, 0, 0, 0.8),    # Red
            '300_rad_hr':  (1, 0.5, 0, 0.7),  # Orange
            '100_rad_hr':  (1, 1, 0, 0.6),    # Yellow
            '30_rad_hr':   (0.5, 1, 0, 0.5),  # Lime Green
            '10_rad_hr':   (0, 1, 0, 0.4),    # Green
        }
        # Call the drawing function when the widget size is known
        self.bind(size=self.draw_plume)

    def triangulate_polygon(self, points):
        """
        Simple triangulation for convex polygons (fan triangulation from first vertex)
        Returns vertices and indices for Mesh rendering
        """
        if len(points) < 3:
            return [], []
        
        # Convert to vertices format [x, y, u, v, x2, y2, u2, v2, ...]
        vertices = []
        for i, (x, y) in enumerate(points):
            # u, v are texture coordinates (we'll use 0,0 for solid colors)
            vertices.extend([x, y, 0, 0])
        
        # Create triangle indices (fan triangulation)
        indices = []
        for i in range(1, len(points) - 1):
            indices.extend([0, i, i + 1])  # Triangle from vertex 0 to consecutive vertices
        
        return vertices, indices

    def draw_plume(self, *args):
        self.canvas.clear()
        
        # Scaling factor to make the plume visible (miles -> pixels)
        SCALE_FACTOR = 2.0 
        
        center_x = self.width / 2
        center_y = self.height / 2
        
        with self.canvas:
            PushMatrix()
            # Rotate the entire canvas around the center point
            Rotate(angle=self.angle, origin=(center_x, center_y))
            
            # Draw the contours from highest dose to lowest
            sorted_dose_keys = sorted(self.contours.keys(), key=lambda x: int(x.split('_')[0]), reverse=True)
            
            for dose_key in sorted_dose_keys:
                points = self.contours[dose_key]
                if len(points) < 3:  # Need at least 3 points for a polygon
                    continue
                    
                color = self.dose_colors.get(dose_key, (1, 1, 1, 0.3))
                Color(*color)
                
                # Scale and translate points
                scaled_points = []
                for x, y in points:
                    scaled_x = x * SCALE_FACTOR + center_x
                    scaled_y = y * SCALE_FACTOR + center_y
                    scaled_points.append((scaled_x, scaled_y))

                # Create filled polygon using Mesh
                vertices, indices = self.triangulate_polygon(scaled_points)
                if vertices and indices:
                    Mesh(vertices=vertices, indices=indices, mode='triangles')
                
                # Draw outline for better visibility
                outline_points = []
                for x, y in scaled_points:
                    outline_points.extend([x, y])
                
                # Draw a darker outline
                Color(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, color[3])
                Line(points=outline_points, width=1, close=True)
            
            PopMatrix()


class NuclearApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation='horizontal')
        
        self.map_area = Widget(size_hint_x=0.7)
        with self.map_area.canvas.before:
            Color(0.2, 0.2, 0.2)
            self.map_rect = Rectangle(size=self.map_area.size, pos=self.map_area.pos)
        self.map_area.bind(size=self._update_rect, pos=self._update_rect)
        
        self.controls = GridLayout(cols=1, spacing=10, padding=10, size_hint_x=0.3)
        self.controls.add_widget(Label(text='Nuclear Fallout Simulator', size_hint_y=None, height=40, font_size='20sp'))

        # Input fields
        self.controls.add_widget(Label(text='Location:', size_hint_y=None, height=30))
        self.location_input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.lat_input = TextInput(text='28.6', hint_text='Lat', multiline=False)
        self.lon_input = TextInput(text='77.2', hint_text='Lon', multiline=False)
        self.location_input_layout.add_widget(self.lat_input)
        self.location_input_layout.add_widget(self.lon_input)
        self.controls.add_widget(self.location_input_layout)
        
        self.controls.add_widget(Label(text='Yield (kilotons):', size_hint_y=None, height=30))
        self.yield_input = TextInput(text='150', multiline=False, size_hint_y=None, height=30)
        self.controls.add_widget(self.yield_input)
        
        self.controls.add_widget(Label(text='Wind Speed (km/h):', size_hint_y=None, height=30))
        self.wind_speed_input = TextInput(text='24', multiline=False, size_hint_y=None, height=30)
        self.controls.add_widget(self.wind_speed_input)
        
        self.controls.add_widget(Label(text='Wind Direction:', size_hint_y=None, height=30))
        self.wind_direction_spinner = Spinner(
            text='E', values=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
            size_hint_y=None, height=40
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

    def _update_rect(self, instance, value):
        self.map_rect.pos = instance.pos
        self.map_rect.size = instance.size

    def run_simulation(self, instance):
        try:
            yield_kt = float(self.yield_input.text)
            wind_speed = float(self.wind_speed_input.text)
            wind_direction = self.wind_direction_spinner.text

            # Call the backend function
            plume_data = calculate_full_plume(yield_kt, wind_speed, wind_direction)
            
            # Remove the old plume widget if it exists
            if hasattr(self, 'plume_widget'):
                self.map_area.remove_widget(self.plume_widget)
            
            # Create an instance of our new drawing widget
            # Pass the contours and angle from the plume_data dictionary
            self.plume_widget = PlumeDrawingWidget(
                contours=plume_data['contours'], 
                angle=plume_data['angle']
            )
            self.map_area.add_widget(self.plume_widget)

        except ValueError:
            popup = Popup(title='Input Error',
                          content=Label(text='Please enter valid numbers for yield and wind speed.'),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
        except Exception as e:
            print(f"An error occurred: {e}")

    def show_dose_graph(self, instance):
        try:
            time_points, dose_data = generate_dose_data(1000)
            
            plt.style.use('dark_background')
            plt.figure(figsize=(6, 4))
            plt.plot(time_points, dose_data, color='cyan')
            plt.title('Dose Rate vs. Time', color='white')
            plt.xlabel('Time (hours)', color='white')
            plt.ylabel('Dose Rate (rad/hr)', color='white')
            plt.grid(True, linestyle='--', alpha=0.6)
            
            plot_path = os.path.join(os.getcwd(), 'dose_graph.png')
            plt.savefig(plot_path, transparent=True)
            plt.close()
            
            content = BoxLayout(orientation='vertical')
            graph_image = KivyImage(source=plot_path, reload=True, nocache=True)
            close_button = Button(text='Close', size_hint_y=None, height=50)
            
            content.add_widget(graph_image)
            content.add_widget(close_button)
            
            popup = Popup(title='Dose Rate Graph', content=content, size_hint=(0.8, 0.8), auto_dismiss=False)
            close_button.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            print(f"Could not generate graph: {e}")

if __name__ == '__main__':
    NuclearApp().run()