import kivy
import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage  # Import Kivy's Image widget
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
import matplotlib.pyplot as plt

# Import your backend logic from Day 2
from plume_model import calculate_plume
from dose_decay import generate_dose_data

# Set a fixed window size for consistent look
Window.size = (800, 600)

class PlumeDrawingWidget(Widget):
    """A custom widget for drawing the fallout plume."""
    def __init__(self, plume_length, plume_width, **kwargs):
        super().__init__(**kwargs)
        self.plume_length = plume_length
        self.plume_width = plume_width
        self.draw_plume()

    def draw_plume(self):
        self.canvas.clear()
        
        center_x = self.width / 2
        center_y = self.height / 2

        with self.canvas:
            # Outer zone (Yellow)
            Color(1, 1, 0, 0.5)
            Ellipse(pos=(center_x - self.plume_length/2, center_y - self.plume_width/2), 
                    size=(self.plume_length, self.plume_width))

            # Inner zone (Red)
            Color(1, 0, 0, 0.8)
            inner_length = self.plume_length * 0.4
            inner_width = self.plume_width * 0.4
            Ellipse(pos=(center_x - inner_length/2, center_y - inner_width/2), 
                    size=(inner_length, inner_width))

class NuclearApp(App):
    def build(self):
        self.layout = FloatLayout()
        
        # --- UI ELEMENTS ---
        self.yield_label = Label(text='Yield (MT):', size_hint=(None, None), size=(100, 40), pos_hint={'x': .1, 'y': .9})
        self.wind_label = Label(text='Wind (km/h):', size_hint=(None, None), size=(100, 40), pos_hint={'x': .1, 'y': .8})
        
        self.yield_input = TextInput(text='15', multiline=False, size_hint=(None, None), size=(200, 40), pos_hint={'x': .4, 'y': .9})
        self.wind_input = TextInput(text='20', multiline=False, size_hint=(None, None), size=(200, 40), pos_hint={'x': .4, 'y': .8})
        
        self.simulate_button = Button(text='Simulate Fallout', size_hint=(None, None), size=(200, 50), pos_hint={'center_x': .5, 'y': .7})
        self.simulate_button.bind(on_press=self.run_simulation)
        
        self.plume_container = Widget(size_hint=(.5, .6), pos_hint={'x': 0, 'y': 0})
        self.graph_container = Widget(size_hint=(.5, .6), pos_hint={'x': .5, 'y': 0})
        
        self.layout.add_widget(self.yield_label)
        self.layout.add_widget(self.wind_label)
        self.layout.add_widget(self.yield_input)
        self.layout.add_widget(self.wind_input)
        self.layout.add_widget(self.simulate_button)
        self.layout.add_widget(self.plume_container)
        self.layout.add_widget(self.graph_container)

        return self.layout

    def run_simulation(self, instance):
        try:
            yield_mt = float(self.yield_input.text)
            wind_speed = float(self.wind_input.text)

            # Plume visualization
            plume_dimensions = calculate_plume(yield_mt, wind_speed)
            if hasattr(self, 'plume_widget'):
                self.plume_container.remove_widget(self.plume_widget)
            self.plume_widget = PlumeDrawingWidget(plume_dimensions['length'] * 10, plume_dimensions['width'] * 10)
            self.plume_container.add_widget(self.plume_widget)

            # Graph visualization
            self.plot_graph(yield_mt)

        except ValueError:
            # Handle non-numeric input gracefully
            pass

    def plot_graph(self, yield_mt):
        # 1. Generate the data points
        time_points, dose_data = generate_dose_data(yield_mt)

        # 2. Create the Matplotlib plot
        plt.style.use('dark_background')
        plt.figure(figsize=(4, 3))
        plt.plot(time_points, dose_data, color='cyan')
        plt.title('Dose Rate vs. Time', color='white')
        plt.xlabel('Time (hours)', color='white')
        plt.ylabel('Dose Rate (rad/hr)', color='white')
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # 3. Save the plot to a temporary file
        plot_path = os.path.join(os.getcwd(), 'dose_graph.png')
        plt.savefig(plot_path, transparent=True)
        plt.close() # Close the plot to free up memory

        # 4. Display the image in Kivy
        if hasattr(self, 'graph_widget'):
            self.graph_container.remove_widget(self.graph_widget)
        self.graph_widget = KivyImage(source=plot_path, allow_stretch=True, keep_ratio=True)
        self.graph_container.add_widget(self.graph_widget)


if __name__ == '__main__':
    NuclearApp().run()