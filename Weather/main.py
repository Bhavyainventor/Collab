import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class EnvironmentSystem:
    def __init__(self):
        self.city_data = {}  # Store city environmental data
        
    def store_data(self, city, temperature, pollution_level, month):
        """Store environmental data for a city"""
        if city not in self.city_data:
            self.city_data[city] = {'temperatures': {}, 'pollution': {}}
        self.city_data[city]['temperatures'][month] = temperature
        self.city_data[city]['pollution'][month] = pollution_level
        
    def calculate_average_temperature(self, city):
        """Calculate average temperature for a city across all months"""
        if city in self.city_data:
            temps = self.city_data[city]['temperatures'].values()
            return sum(temps) / len(temps) if temps else 0
        return 0
        
    def summer_temperature_report(self, summer_months=('April', 'May', 'June')):
        """Generate report of summer temperatures for all cities"""
        report = {}
        for city in self.city_data:
            summer_temps = [
                self.city_data[city]['temperatures'].get(month, 0)
                for month in summer_months
            ]
            report[city] = sum(summer_temps) / len(summer_temps) if summer_temps else 0
        return report
        
    def get_temperature(self, city, month):
        """Fetch temperature details for a specific city and month"""
        return self.city_data.get(city, {}).get('temperatures', {}).get(month)
        
    def display_results(self):
        """Display environmental data for all cities"""
        for city, data in self.city_data.items():
            print(f"\nCity: {city}")
            print("Temperatures:", data['temperatures'])
            print("Pollution levels:", data['pollution'])
            print("Average temperature:", self.calculate_average_temperature(city))
            
    def find_temperature_extremes(self):
        """Find cities with maximum and minimum temperatures"""
        if not self.city_data:
            return None, None
            
        max_temp = float('-inf')
        min_temp = float('inf')
        max_city = min_city = None
        
        for city, data in self.city_data.items():
            temps = data['temperatures'].values()
            if temps:  # Check if there are any temperatures
                city_max = max(temps)
                city_min = min(temps)
                
                if city_max > max_temp:
                    max_temp = city_max
                    max_city = city
                if city_min < min_temp:
                    min_temp = city_min
                    min_city = city
                
        return max_city, min_city
        
    def check_pollution_level(self, city, month, threshold=100):  # Adjusted for Indian AQI
        """Check if pollution level exceeds threshold"""
        if city in self.city_data:
            pollution = self.city_data[city]['pollution'].get(month, 0)
            if pollution > threshold:
                return "High pollution alert"
            elif pollution > threshold * 0.7:
                return "Moderate pollution warning"
            else:
                return "Normal pollution levels"
        return "City not found"
        
    def categorize_cities(self):
        """Categorize cities into temperature/pollution slabs"""
        categories = {
            'high_temp': [],
            'medium_temp': [],
            'low_temp': [],
            'high_pollution': [],
            'low_pollution': []
        }
        
        for city, data in self.city_data.items():
            if data['temperatures']:  # Check if there are any temperatures
                avg_temp = self.calculate_average_temperature(city)
                avg_pollution = sum(data['pollution'].values()) / len(data['pollution'])
                
                # Temperature categorization (adjusted for Indian weather)
                if avg_temp >= 35:
                    categories['high_temp'].append(city)
                elif avg_temp >= 25:
                    categories['medium_temp'].append(city)
                else:
                    categories['low_temp'].append(city)
                    
                # Pollution categorization
                if avg_pollution > 100:  # Adjusted for Indian AQI standards
                    categories['high_pollution'].append(city)
                else:
                    categories['low_pollution'].append(city)
                    
        return categories

class EnvironmentSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Indian Cities Environment Monitoring System")
        self.root.geometry("1000x700")  # Increased window size
        
        # Apply a theme
        style = ttk.Style()
        style.theme_use('clam')  # You can try different themes: 'alt', 'default', 'classic'
        
        self.env_system = EnvironmentSystem()
        
        # Available cities
        self.indian_cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", 
            "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
        ]
        
        # Configure grid weight
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.create_gui()
        
    def create_gui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create and style notebook
        style = ttk.Style()
        style.configure("TNotebook", padding=5)
        style.configure("TNotebook.Tab", padding=[12, 4], font=('Helvetica', 10))
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both')
        
        # Create tabs with styled frames
        self.input_frame = ttk.Frame(self.notebook, padding="20")
        self.display_frame = ttk.Frame(self.notebook, padding="20")
        self.analysis_frame = ttk.Frame(self.notebook, padding="20")
        
        self.notebook.add(self.input_frame, text='📝 Data Input')
        self.notebook.add(self.display_frame, text='📊 Display Data')
        self.notebook.add(self.analysis_frame, text='📈 Analysis')
        
        self.setup_input_tab()
        self.setup_display_tab()
        self.setup_analysis_tab()
        
    def setup_input_tab(self):
        # Create a frame for the form
        form_frame = ttk.LabelFrame(self.input_frame, text="Enter City Data", padding="20")
        form_frame.pack(fill='x', padx=10, pady=5)
        
        # City Selection Frame
        city_frame = ttk.Frame(form_frame)
        city_frame.pack(fill='x', pady=5)
        
        ttk.Label(city_frame, text="Select City:").pack(side='left', padx=5)
        self.city_var = tk.StringVar()
        city_combo = ttk.Combobox(city_frame, textvariable=self.city_var, values=self.indian_cities)
        city_combo.pack(side='left', padx=5)
        
        # Custom City Entry
        ttk.Label(city_frame, text="or Add Custom City:").pack(side='left', padx=5)
        self.custom_city_var = tk.StringVar()
        custom_city_entry = ttk.Entry(city_frame, textvariable=self.custom_city_var)
        custom_city_entry.pack(side='left', padx=5)
        
        # Add Custom City Button
        ttk.Button(city_frame, text="Add to List", command=self.add_custom_city).pack(side='left', padx=5)
        
        # Month Selection
        month_frame = ttk.Frame(form_frame)
        month_frame.pack(fill='x', pady=5)
        
        ttk.Label(month_frame, text="Select Month:").pack(side='left', padx=5)
        self.month_var = tk.StringVar()
        months = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
        month_combo = ttk.Combobox(month_frame, textvariable=self.month_var, values=months)
        month_combo.pack(side='left', padx=5)
        
        # Temperature Input
        temp_frame = ttk.Frame(form_frame)
        temp_frame.pack(fill='x', pady=5)
        
        ttk.Label(temp_frame, text="Temperature (°C):").pack(side='left', padx=5)
        self.temp_var = tk.StringVar()
        temp_entry = ttk.Entry(temp_frame, textvariable=self.temp_var)
        temp_entry.pack(side='left', padx=5)
        
        # Pollution Input
        pollution_frame = ttk.Frame(form_frame)
        pollution_frame.pack(fill='x', pady=5)
        
        ttk.Label(pollution_frame, text="Pollution Level (AQI):").pack(side='left', padx=5)
        self.pollution_var = tk.StringVar()
        pollution_entry = ttk.Entry(pollution_frame, textvariable=self.pollution_var)
        pollution_entry.pack(side='left', padx=5)
        
        # Submit Button
        submit_frame = ttk.Frame(form_frame)
        submit_frame.pack(fill='x', pady=10)
        submit_btn = ttk.Button(submit_frame, text="Submit Data", command=self.submit_data)
        submit_btn.pack(pady=10)
        
    def setup_display_tab(self):
        # Create Treeview
        self.tree = ttk.Treeview(self.display_frame, columns=('City', 'Month', 'Temperature', 'Pollution'), show='headings')
        
        # Set column headings
        self.tree.heading('City', text='City')
        self.tree.heading('Month', text='Month')
        self.tree.heading('Temperature', text='Temperature (°C)')
        self.tree.heading('Pollution', text='Pollution (AQI)')
        
        # Set column widths
        self.tree.column('City', width=100)
        self.tree.column('Month', width=100)
        self.tree.column('Temperature', width=100)
        self.tree.column('Pollution', width=100)
        
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.display_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Refresh button
        ttk.Button(self.display_frame, text="Refresh Data", command=self.refresh_display).pack(pady=10)
        
    def setup_analysis_tab(self):
        # Frame for buttons
        button_frame = ttk.Frame(self.analysis_frame)
        button_frame.pack(pady=10)
        
        # Buttons for different analyses
        ttk.Button(button_frame, text="Temperature Extremes", 
                  command=self.show_temperature_extremes).pack(pady=5)
        ttk.Button(button_frame, text="Pollution Levels", 
                  command=self.show_pollution_levels).pack(pady=5)
        ttk.Button(button_frame, text="City Categories", 
                  command=self.show_categories).pack(pady=5)
        
        # Results text area
        self.analysis_text = tk.Text(self.analysis_frame, height=15, width=50)
        self.analysis_text.pack(pady=10, padx=10)
        
        # Add scrollbar to text area
        text_scroll = ttk.Scrollbar(self.analysis_frame, orient=tk.VERTICAL, command=self.analysis_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.analysis_text.configure(yscrollcommand=text_scroll.set)

    def add_custom_city(self):
        custom_city = self.custom_city_var.get().strip()
        if custom_city:
            if custom_city not in self.indian_cities:
                self.indian_cities.append(custom_city)
                self.city_var.set(custom_city)
                messagebox.showinfo("Success", f"Added {custom_city} to the city list!")
                self.custom_city_var.set('')  # Clear the entry
            else:
                messagebox.showwarning("Warning", "This city is already in the list!")
        else:
            messagebox.showwarning("Warning", "Please enter a city name!")
            
    def submit_data(self):
        try:
            city = self.city_var.get()
            month = self.month_var.get()
            temperature = float(self.temp_var.get())
            pollution = float(self.pollution_var.get())
            
            if not all([city, month]):
                messagebox.showerror("Error", "Please fill in all fields!")
                return
                
            self.env_system.store_data(city, temperature, pollution, month)
            messagebox.showinfo("Success", "Data stored successfully!")
            
            # Clear inputs
            self.city_var.set('')
            self.month_var.set('')
            self.temp_var.set('')
            self.pollution_var.set('')
            
            # Refresh display
            self.refresh_display()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for temperature and pollution!")
            
    def refresh_display(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Insert data
        for city, data in self.env_system.city_data.items():
            for month in data['temperatures'].keys():
                self.tree.insert('', 'end', values=(
                    city,
                    month,
                    f"{data['temperatures'][month]:.1f}",
                    f"{data['pollution'][month]:.1f}"
                ))
                
    def show_temperature_extremes(self):
        hottest, coldest = self.env_system.find_temperature_extremes()
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, f"Temperature Extremes:\n\n")
        self.analysis_text.insert(tk.END, f"Hottest City: {hottest}\n")
        self.analysis_text.insert(tk.END, f"Coldest City: {coldest}")
        
    def show_pollution_levels(self):
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "Pollution Levels:\n\n")
        for city in self.env_system.city_data:
            for month in self.env_system.city_data[city]['pollution']:
                status = self.env_system.check_pollution_level(city, month)
                self.analysis_text.insert(tk.END, f"{city} - {month}: {status}\n")
                
    def show_categories(self):
        categories = self.env_system.categorize_cities()
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "City Categories:\n\n")
        for category, cities in categories.items():
            self.analysis_text.insert(tk.END, f"{category}: {', '.join(cities) if cities else 'None'}\n")

    def main():
        root = tk.Tk()
        app = EnvironmentSystemGUI(root)
        root.mainloop()

    if __name__ == "__main__":
        main()