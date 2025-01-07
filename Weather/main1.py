import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import requests
from typing import Dict, List
import threading
from ttkthemes import ThemedTk

class EnvironmentSystem:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Environment Monitoring System - India")
        self.root.geometry("1000x700")
        
        # Dictionary of Indian cities with their coordinates
        self.indian_cities = {
            "Mumbai": {"lat": 19.07, "lon": 72.87},
            "Delhi": {"lat": 28.61, "lon": 77.21},
            "Bangalore": {"lat": 12.97, "lon": 77.59},
            "Hyderabad": {"lat": 17.38, "lon": 78.48},
            "Chennai": {"lat": 13.08, "lon": 80.27},
            "Kolkata": {"lat": 22.57, "lon": 88.36},
            "Pune": {"lat": 18.52, "lon": 73.86},
            "Ahmedabad": {"lat": 23.03, "lon": 72.58},
            "Jaipur": {"lat": 26.91, "lon": 75.79},
            "Lucknow": {"lat": 26.85, "lon": 80.95}
        }
        
        # API Configuration
        self.weather_api = "https://api.open-meteo.com/v1/forecast"
        self.air_quality_api = "https://air-quality-api.open-meteo.com/v1/air-quality"
        
        # Data storage
        self.city_data: Dict[str, Dict] = {}
        
        self.setup_styles()
        self.create_header()
        self.create_main_content()
        self.setup_footer()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Helvetica', 24, 'bold'))
        style.configure('SubHeader.TLabel', font=('Helvetica', 16))
        style.configure('Data.TLabel', font=('Helvetica', 12))
        style.configure('Custom.TButton', font=('Helvetica', 11))
        
        self.root.configure(bg='#f0f0f0')
        style.configure('Custom.TFrame', background='#ffffff')

    def create_header(self):
        header_frame = ttk.Frame(self.root, style='Custom.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(20,10))
        
        ttk.Label(
            header_frame, 
            text="Environmental Monitoring Dashboard", 
            style='Header.TLabel'
        ).pack(pady=10)

    def create_main_content(self):
        content_frame = ttk.Frame(self.root, style='Custom.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel
        left_panel = ttk.Frame(content_frame, style='Custom.TFrame')
        left_panel.pack(side='left', fill='y', padx=(0,10))
        
        ttk.Label(
            left_panel, 
            text="Select City:", 
            style='SubHeader.TLabel'
        ).pack(pady=(0,5))
        
        self.city_var = tk.StringVar()
        city_dropdown = ttk.Combobox(
            left_panel, 
            textvariable=self.city_var,
            values=list(self.indian_cities.keys()),
            state='readonly',
            width=30
        )
        city_dropdown.pack(pady=(0,20))
        city_dropdown.bind('<<ComboboxSelected>>', self.fetch_city_data)
        
        # Control buttons
        ttk.Button(
            left_panel,
            text="Refresh Data",
            style='Custom.TButton',
            command=self.fetch_city_data
        ).pack(fill='x', pady=5)
        
        ttk.Button(
            left_panel,
            text="Temperature Forecast",
            style='Custom.TButton',
            command=self.show_temperature_forecast
        ).pack(fill='x', pady=5)
        
        ttk.Button(
            left_panel,
            text="Air Quality Data",
            style='Custom.TButton',
            command=self.show_air_quality
        ).pack(fill='x', pady=5)
        
        # Right panel
        right_panel = ttk.Frame(content_frame, style='Custom.TFrame')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Main data display
        self.data_display = ttk.Label(
            right_panel,
            text="Select a city to view data",
            style='Data.TLabel',
            wraplength=500
        )
        self.data_display.pack(pady=20)
        
        # Detailed data display
        self.detailed_display = tk.Text(
            right_panel,
            height=15,
            width=50,
            wrap=tk.WORD,
            font=('Helvetica', 11)
        )
        self.detailed_display.pack(pady=20, padx=20, fill='both', expand=True)

    def setup_footer(self):
        self.footer_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.footer_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = ttk.Label(
            self.footer_frame,
            text="Ready to fetch data",
            style='Data.TLabel'
        )
        self.status_label.pack(side='left')

    def fetch_city_data(self, event=None):
        city = self.city_var.get()
        if not city:
            return
            
        self.status_label.config(text="Fetching data...")
        threading.Thread(target=self._fetch_data, args=(city,)).start()

    def _fetch_data(self, city):
        try:
            coords = self.indian_cities[city]
            
            # Fetch weather data
            weather_params = {
                'latitude': coords['lat'],
                'longitude': coords['lon'],
                'current_weather': True,
                'hourly': 'temperature_2m,relative_humidity_2m,precipitation_probability'
            }
            weather_response = requests.get(self.weather_api, params=weather_params)
            weather_data = weather_response.json()
            
            # Fetch air quality data
            air_params = {
                'latitude': coords['lat'],
                'longitude': coords['lon'],
                'current': True,
                'hourly': 'pm10,pm2_5,carbon_monoxide'
            }
            air_response = requests.get(self.air_quality_api, params=air_params)
            air_data = air_response.json()
            
            # Combine the data
            self.city_data[city] = {
                'temperature': weather_data['current_weather']['temperature'],
                'windspeed': weather_data['current_weather']['windspeed'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'hourly_temp': weather_data['hourly']['temperature_2m'][:24],  # Next 24 hours
                'hourly_humidity': weather_data['hourly']['relative_humidity_2m'][:24],
                'precipitation_prob': weather_data['hourly']['precipitation_probability'][:24],
                'pm10': air_data['current']['pm10'],
                'pm2_5': air_data['current']['pm2_5'],
                'co': air_data['current']['carbon_monoxide']
            }
            
            self.root.after(0, self.update_display, city)
            self.root.after(0, self.status_label.config, 
                          {"text": f"Last updated: {self.city_data[city]['timestamp']}"})
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", 
                          f"Failed to fetch data: {str(e)}")
            self.root.after(0, self.status_label.config, 
                          {"text": "Error fetching data"})

    def update_display(self, city):
        data = self.city_data[city]
        
        # Update main display
        main_text = f"""
Current Weather Conditions for {city}:
Temperature: {data['temperature']}°C
Wind Speed: {data['windspeed']} km/h
Air Quality:
  PM10: {data['pm10']} μg/m³
  PM2.5: {data['pm2_5']} μg/m³
  CO: {data['co']} μg/m³
"""
        self.data_display.configure(text=main_text)
        
        # Update detailed display
        detailed_text = "Hourly Forecast:\n\n"
        for i in range(24):
            detailed_text += f"Hour {i}:\n"
            detailed_text += f"  Temperature: {data['hourly_temp'][i]}°C\n"
            detailed_text += f"  Humidity: {data['hourly_humidity'][i]}%\n"
            detailed_text += f"  Rain Probability: {data['precipitation_prob'][i]}%\n\n"
        
        self.detailed_display.delete('1.0', tk.END)
        self.detailed_display.insert('1.0', detailed_text)

    def show_temperature_forecast(self):
        if not self.city_data:
            messagebox.showinfo("Info", "No data available")
            return
            
        city = self.city_var.get()
        if city not in self.city_data:
            messagebox.showinfo("Info", "Please fetch data for this city first")
            return
            
        # Create forecast window
        forecast_window = tk.Toplevel(self.root)
        forecast_window.title(f"Temperature Forecast - {city}")
        forecast_window.geometry("600x400")
        
        # Add forecast content
        text_widget = tk.Text(forecast_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill='both', expand=True)
        
        data = self.city_data[city]
        forecast_text = f"24-Hour Temperature Forecast for {city}:\n\n"
        
        for i in range(24):
            forecast_text += f"Hour {i}: {data['hourly_temp'][i]}°C\n"
            forecast_text += f"Rain Probability: {data['precipitation_prob'][i]}%\n\n"
            
        text_widget.insert('1.0', forecast_text)
        text_widget.configure(state='disabled')

    def show_air_quality(self):
        if not self.city_data:
            messagebox.showinfo("Info", "No data available")
            return
            
        city = self.city_var.get()
        if city not in self.city_data:
            messagebox.showinfo("Info", "Please fetch data for this city first")
            return
            
        data = self.city_data[city]
        
        # Create air quality window
        aq_window = tk.Toplevel(self.root)
        aq_window.title(f"Air Quality - {city}")
        aq_window.geometry("600x400")
        
        # Add air quality content
        text_widget = tk.Text(aq_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill='both', expand=True)
        
        # Analyze air quality
        pm25_status = "Good" if data['pm2_5'] <= 10 else "Moderate" if data['pm2_5'] <= 25 else "Poor"
        pm10_status = "Good" if data['pm10'] <= 20 else "Moderate" if data['pm10'] <= 50 else "Poor"
        
        aq_text = f"""Air Quality Analysis for {city}

PM2.5: {data['pm2_5']} μg/m³
Status: {pm25_status}
(WHO guideline: 10 μg/m³ annual mean)

PM10: {data['pm10']} μg/m³
Status: {pm10_status}
(WHO guideline: 20 μg/m³ annual mean)

Carbon Monoxide: {data['co']} μg/m³

Last Updated: {data['timestamp']}

Health Implications:
- PM2.5: Fine particulate matter that can penetrate deep into the lungs
- PM10: Coarse particulate matter that can affect the respiratory system
- CO: Carbon monoxide can reduce oxygen delivery to organs

Recommendations:
- {pm25_status.lower()} PM2.5 levels: {'Outdoor activities are safe' if pm25_status == 'Good' else 'Consider reducing outdoor activities' if pm25_status == 'Moderate' else 'Avoid prolonged outdoor activities'}
- {pm10_status.lower()} PM10 levels: {'Outdoor activities are safe' if pm10_status == 'Good' else 'Consider reducing outdoor activities' if pm10_status == 'Moderate' else 'Avoid prolonged outdoor activities'}
"""
        text_widget.insert('1.0', aq_text)
        text_widget.configure(state='disabled')

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = EnvironmentSystem()
    app.run()