import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch

class StudentDataEntry:
    def __init__(self, root):
        self.root = root
        self.root.title("Academic Records Management System")
        self.root.geometry("800x800")
        
        # Configure custom styles with new colors
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", 
                           font=("Calibri", 28, "bold"),
                           padding=20,
                           foreground="#2E4053")
        
        self.style.configure("Header.TLabel", 
                           font=("Calibri", 14, "bold"),
                           foreground="#566573",
                           padding=(0, 10))
        
        self.style.configure("Custom.TEntry", 
                           padding=8,
                           fieldbackground="#F8F9F9")
        
        self.style.configure("Custom.TButton", 
                           font=("Calibri", 11),
                           padding=12,
                           background="#3498DB",
                           foreground="white")
        
        # Set theme and configure colors
        self.style.theme_use('clam')
        self.root.configure(bg="#ECF0F1")
        
        # Create main container with gradient effect
        self.container = ttk.Frame(root, padding="30")
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with custom scrollbar
        self.canvas = tk.Canvas(self.container, bg="#ECF0F1")
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", 
                                     command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack with modern spacing
        self.canvas.pack(side="left", fill="both", expand=True, padx=5)
        self.scrollbar.pack(side="right", fill="y")
        
        # Initialize variables
        self.entries = {}
        self.create_widgets()
        
        # Configure grid weights
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

    def validate_admin_no(self, value):
        if not value:
            return True, ""
        
        try:
            number_part, year_part = value.split('/')
            
            if not number_part.isdigit():
                return False, "Admin number format should be: number/year-year (e.g., 150/2012-13)"
            
            years = year_part.split('-')
            if len(years) != 2:
                return False, "Year format should be: year-year (e.g., 2012-13)"
            
            if not (len(years[0]) == 4 and len(years[1]) == 2):
                return False, "Year format should be: YYYY-YY (e.g., 2012-13)"
            
            if not (years[0].isdigit() and years[1].isdigit()):
                return False, "Years should be numbers"
            
            full_year = int(years[0])
            short_year = int(years[1])
            if short_year != (full_year + 1) % 100:
                return False, "Second year should be one year after first year"
            
        except ValueError:
            return False, "Admin number format should be: number/year-year (e.g., 150/2012-13)"
            
        return True, ""

    def validate_name(self, value):
        if not value:
            return True, ""
        if not all(x.isalpha() or x.isspace() for x in value):
            return False, "Name should contain only letters and spaces"
        return True, ""

    def validate_class(self, value):
        if not value:
            return True, ""
        try:
            class_num = int(value)
            if not (1 <= class_num <= 12):
                return False, "Class should be between 1 and 12"
        except ValueError:
            return False, "Class should be a number"
        return True, ""

    def validate_roll_no(self, value):
        if not value:
            return True, ""
        try:
            roll_no = int(value)
            if roll_no <= 0:
                return False, "Roll number should be positive"
        except ValueError:
            return False, "Roll number should be a number"
        return True, ""

    def validate_marks(self, value):
        if not value:
            return True, ""
        try:
            marks = float(value)
            if not (0 <= marks <= 100):
                return False, "Marks should be between 0 and 100"
        except ValueError:
            return False, "Marks should be a number"
        return True, ""

    def validate_field(self, event, field):
        value = self.entries[field].get()
        if self.fields[field].get("validate"):
            valid, message = self.fields[field]["validate"](value)
            if not valid:
                messagebox.showerror("Validation Error", message)
                return False
        return True

    def create_widgets(self):
        # Title with decorative elements
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 40))
        
        title_label = ttk.Label(title_frame, 
                              text="Academic Records Management", 
                              style="Title.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                 text="Student Information System",
                                 font=("Calibri", 14, "italic"),
                                 foreground="#7F8C8D")
        subtitle_label.pack()
        
        # Field definitions
        self.fields = {
            "Admin No": {"required": True, "validate": self.validate_admin_no, "section": "Personal Details"},
            "Name": {"required": True, "validate": self.validate_name, "section": "Personal Details"},
            "Class": {"required": True, "validate": self.validate_class, "section": "Personal Details"},
            "Roll No": {"required": True, "validate": self.validate_roll_no, "section": "Personal Details"},
            "English 1": {"required": False, "validate": self.validate_marks, "section": "Academic Details"},
            "English 2": {"required": False, "validate": self.validate_marks, "section": "Academic Details"},
            "Science": {"required": False, "validate": self.validate_marks, "section": "Academic Details"},
            "Hindi": {"required": False, "validate": self.validate_marks, "section": "Academic Details"},
            "SST": {"required": False, "validate": self.validate_marks, "section": "Academic Details"},
            "Maths": {"required": False, "validate": self.validate_marks, "section": "Academic Details"},
            "Optional Subject": {"required": False, "section": "Academic Details"}
        }
        
        current_row = 2
        current_section = None
        
        for field, properties in self.fields.items():
            if properties["section"] != current_section:
                current_section = properties["section"]
                section_label = ttk.Label(self.scrollable_frame, text=current_section,
                                        style="Header.TLabel")
                section_label.grid(row=current_row, column=0, columnspan=2,
                                 pady=(20, 10), sticky="w")
                current_row += 1
            
            field_frame = ttk.Frame(self.scrollable_frame)
            field_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew",
                           padx=20, pady=5)
            field_frame.grid_columnconfigure(1, weight=1)
            
            label_text = f"{field}{'*' if properties['required'] else ''}"
            label = ttk.Label(field_frame, text=label_text)
            label.grid(row=0, column=0, padx=(0, 10), sticky="w")
            
            entry = ttk.Entry(field_frame, style="Custom.TEntry", width=40)
            entry.grid(row=0, column=1, sticky="ew")
            self.entries[field] = entry
            
            if "validate" in properties:
                entry.bind('<FocusOut>', 
                          lambda e, f=field: self.validate_field(e, f))
            
            current_row += 1
        
        ttk.Separator(self.scrollable_frame, orient='horizontal').grid(
            row=current_row, column=0, columnspan=3, sticky='ew', pady=20)
        current_row += 1
        
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.grid(row=current_row, column=0, columnspan=2, pady=30)
        
        save_btn = ttk.Button(button_frame, text="✓ Save", style="Custom.TButton",
                             command=self.save_to_csv)
        save_btn.pack(side=tk.LEFT, padx=12)
        
        clear_btn = ttk.Button(button_frame, text="⟲ Clear", style="Custom.TButton",
                              command=self.clear_entries)
        clear_btn.pack(side=tk.LEFT, padx=12)
        
        view_btn = ttk.Button(button_frame, text="👁 View Records", 
                             style="Custom.TButton",
                             command=self.view_records)
        view_btn.pack(side=tk.LEFT, padx=12)
        
        report_btn = ttk.Button(button_frame, text="📄 Generate Report", 
                               style="Custom.TButton",
                               command=self.generate_report_card)
        report_btn.pack(side=tk.LEFT, padx=12)

    def check_scholarship_eligibility(self, tree):
        selected_items = tree.selection()
        
        if not selected_items:
            messagebox.showerror("Error", "Please select a student record first!")
            return
            
        student_data = tree.item(selected_items[0])['values']
        
        try:
            # Get the marks from the selected student
            subject_indices = [4, 5, 6, 7, 8, 9, 10]  # Indices for subject marks
            total_marks = 0
            subjects_counted = 0
            
            for index in subject_indices:
                marks = student_data[index]
                if marks:
                    try:
                        marks_float = float(marks)
                        total_marks += marks_float
                        subjects_counted += 1
                    except ValueError:
                        continue
            
            if subjects_counted > 0:
                average = total_marks / subjects_counted
                
                # Check scholarship eligibility (80% or above)
                if average >= 80:
                    message = (f"Student {student_data[1]} is ELIGIBLE for scholarship!\n\n"
                             f"Average Marks: {average:.2f}%\n"
                             "Criteria: ≥80% for scholarship eligibility")
                    messagebox.showinfo("Scholarship Eligibility", message)
                else:
                    message = (f"Student {student_data[1]} is NOT ELIGIBLE for scholarship.\n\n"
                             f"Average Marks: {average:.2f}%\n"
                             "Criteria: ≥80% for scholarship eligibility")
                    messagebox.showwarning("Scholarship Eligibility", message)
            else:
                messagebox.showerror("Error", "No marks data found for this student!")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while checking scholarship eligibility: {e}")

    def save_to_csv(self):
        for field, properties in self.fields.items():
            value = self.entries[field].get()
            if properties["required"] and not value:
                messagebox.showerror("Error", f"{field} is required!")
                self.entries[field].focus()
                return
            
            if value and properties.get("validate"):
                valid, message = properties["validate"](value)
                if not valid:
                    messagebox.showerror("Error", message)
                    self.entries[field].focus()
                    return

        try:
            file_exists = os.path.isfile("student_data.csv")
            with open("student_data.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                
                if not file_exists:
                    writer.writerow(list(self.fields.keys()) + ["Timestamp"])
                
                row_data = [self.entries[field].get() for field in self.fields]
                row_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                writer.writerow(row_data)
                
            messagebox.showinfo("Success", "Student data saved successfully!")
            self.clear_entries()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving data: {e}")

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def view_records(self):
        try:
            if not os.path.exists("student_data.csv"):
                messagebox.showinfo("Info", "No records found!")
                return

            records_window = tk.Toplevel(self.root)
            records_window.title("Student Records")
            records_window.geometry("1000x600")

            container = ttk.Frame(records_window, padding="10")
            container.pack(fill=tk.BOTH, expand=True)

            tree_frame = ttk.Frame(container)
            tree_frame.pack(fill=tk.BOTH, expand=True)

            tree = ttk.Treeview(tree_frame)
            
            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

            tree.grid(column=0, row=0, sticky='nsew')
            vsb.grid(column=1, row=0, sticky='ns')
            hsb.grid(column=0, row=1, sticky='ew')

            tree_frame.grid_columnconfigure(0, weight=1)
            tree_frame.grid_rowconfigure(0, weight=1)

            with open("student_data.csv", mode="r") as file:
                reader = csv.reader(file)
                headers = next(reader)
                
                tree["columns"] = headers
                tree["show"] = "headings"
                
                for header in headers:
                    tree.heading(header, text=header)
                    tree.column(header, width=100, minwidth=50)
                
                for row in reader:
                    tree.insert("", tk.END, values=row)

            button_frame = ttk.Frame(container)
            button_frame.pack(pady=10)

            generate_btn = ttk.Button(
                button_frame, 
                text="Generate Selected Report Card", 
                style="Custom.TButton",
                command=lambda: self.generate_saved_report_card(tree)
            )
            generate_btn.pack(side=tk.LEFT, padx=5)

            # Scholarship Check Button
            scholarship_btn = ttk.Button(
                button_frame,
                text="Check Scholarship Eligibility",
                style="Custom.TButton",
                command=lambda: self.check_scholarship_eligibility(tree)
            )
            scholarship_btn.pack(side=tk.LEFT, padx=5)

            close_btn = ttk.Button(
                button_frame, 
                text="Close", 
                command=records_window.destroy,
                style="Custom.TButton"
            )
            close_btn.pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while viewing records: {e}")

    def generate_report_card(self):
        admin_no = self.entries["Admin No"].get()
        name = self.entries["Name"].get()
        class_val = self.entries["Class"].get()
        
        if not all([admin_no, name, class_val]):
            messagebox.showerror("Error", "Please enter at least Admin No, Name, and Class!")
            return
            
        try:
            filename = f"report_card_{admin_no.replace('/', '_')}.pdf"
            
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            
            try:
                c.drawImage("school_logo.png", 50, height - 120, width=60, height=60)
            except:
                pass
                
            c.setFont("Helvetica-Bold", 24)
            c.drawString(130, height - 80, "REPORT CARD")
            c.setFont("Helvetica", 16)
            c.drawString(130, height - 100, "Salford High School")
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 150, "Student Details:")
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 170, f"Name: {name}")
            c.drawString(50, height - 190, f"Admin No: {admin_no}")
            c.drawString(50, height - 210, f"Class: {class_val}")
            c.drawString(300, height - 170, f"Roll No: {self.entries['Roll No'].get()}")
            c.drawString(300, height - 190, f"Date: {datetime.now().strftime('%d-%m-%Y')}")
            
            subjects = ["English 1", "English 2", "Science", "Hindi", "SST", "Maths", "Optional Subject"]
            y_position = height - 260
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, "Subject")
            c.drawString(200, y_position, "Marks")
            c.drawString(300, y_position, "Grade")
            
            y_position -= 5
            c.line(50, y_position, 400, y_position)
            y_position -= 20
            
            c.setFont("Helvetica", 12)
            total_marks = 0
            subjects_counted = 0
            
            for subject in subjects:
                marks = self.entries[subject].get()
                if marks:
                    try:
                        marks_float = float(marks)
                        total_marks += marks_float
                        subjects_counted += 1
                        
                        grade = self.calculate_grade(marks_float)
                        
                        c.drawString(50, y_position, subject)
                        c.drawString(200, y_position, str(marks))
                        c.drawString(300, y_position, grade)
                        
                        y_position -= 20
                    except ValueError:
                        pass
            
            if subjects_counted > 0:
                average = total_marks / subjects_counted
                y_position -= 20
                c.line(50, y_position, 400, y_position)
                y_position -= 20
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, f"Average: {average:.2f}%")
                c.drawString(300, y_position, f"Grade: {self.calculate_grade(average)}")
            
            y_position -= 50
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, "Grading Scale:")
            c.setFont("Helvetica", 10)
            y_position -= 20
            c.drawString(50, y_position, "A = 90% - 100% (Excellent)")
            y_position -= 15
            c.drawString(50, y_position, "B = 80% - 89% (Very Good)")
            y_position -= 15
            c.drawString(50, y_position, "C = 60% - 79% (Good)")
            y_position -= 15
            c.drawString(50, y_position, "D = Below 60% (Needs Improvement)")
            
            y_position -= 40
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, "Remarks:")
            c.line(120, y_position, 400, y_position)
            
            y_position -= 60
            c.line(50, y_position, 200, y_position)
            c.drawString(50, y_position - 20, "Class Teacher Signature")
            c.line(250, y_position, 400, y_position)
            c.drawString(250, y_position - 20, "Principal Signature")
            
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(50, 30, "This is a computer-generated report card.")
            c.drawString(50, 20, f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            
            c.save()
            messagebox.showinfo("Success", f"Report card generated successfully as {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating report card: {e}")

    def generate_saved_report_card(self, tree):
        selected_items = tree.selection()
        
        if not selected_items:
            messagebox.showerror("Error", "Please select a student record first!")
            return
            
        student_data = tree.item(selected_items[0])['values']
        
        try:
            admin_no = student_data[0]
            filename = f"report_card_{admin_no.replace('/', '_')}.pdf"
            
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            
            try:
                c.drawImage("school_logo.png", 50, height - 120, width=60, height=60)
            except:
                pass
                
            c.setFont("Helvetica-Bold", 24)
            c.drawString(130, height - 80, "REPORT CARD")
            c.setFont("Helvetica", 16)
            c.drawString(130, height - 100, "Salford High School")
            
            name = student_data[1]
            class_val = student_data[2]
            roll_no = student_data[3]
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 150, "Student Details:")
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 170, f"Name: {name}")
            c.drawString(50, height - 190, f"Admin No: {admin_no}")
            c.drawString(50, height - 210, f"Class: {class_val}")
            c.drawString(300, height - 170, f"Roll No: {roll_no}")
            c.drawString(300, height - 190, f"Date: {datetime.now().strftime('%d-%m-%Y')}")
            
            subjects = ["English 1", "English 2", "Science", "Hindi", "SST", "Maths", "Optional Subject"]
            subject_indices = [4, 5, 6, 7, 8, 9, 10]
            y_position = height - 260
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, "Subject")
            c.drawString(200, y_position, "Marks")
            c.drawString(300, y_position, "Grade")
            
            y_position -= 5
            c.line(50, y_position, 400, y_position)
            y_position -= 20
            
            c.setFont("Helvetica", 12)
            total_marks = 0
            subjects_counted = 0
            
            for subject, index in zip(subjects, subject_indices):
                marks = student_data[index]
                if marks:
                    try:
                        marks_float = float(marks)
                        total_marks += marks_float
                        subjects_counted += 1
                        
                        grade = self.calculate_grade(marks_float)
                        
                        c.drawString(50, y_position, subject)
                        c.drawString(200, y_position, str(marks))
                        c.drawString(300, y_position, grade)
                        
                        y_position -= 20
                    except ValueError:
                        pass
            
            if subjects_counted > 0:
                average = total_marks / subjects_counted
                y_position -= 20
                c.line(50, y_position, 400, y_position)
                y_position -= 20
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, f"Average: {average:.2f}%")
                c.drawString(300, y_position, f"Grade: {self.calculate_grade(average)}")
            
            y_position -= 50
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, "Grading Scale:")
            c.setFont("Helvetica", 10)
            y_position -= 20
            c.drawString(50, y_position, "A = 90% - 100% (Excellent)")
            y_position -= 15
            c.drawString(50, y_position, "B = 80% - 89% (Very Good)")
            y_position -= 15
            c.drawString(50, y_position, "C = 60% - 79% (Good)")
            y_position -= 15
            c.drawString(50, y_position, "D = Below 60% (Needs Improvement)")
            
            y_position -= 40
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, "Remarks:")
            c.line(120, y_position, 400, y_position)
            
            y_position -= 60
            c.line(50, y_position, 200, y_position)
            c.drawString(50, y_position - 20, "Class Teacher Signature")
            c.line(250, y_position, 400, y_position)
            c.drawString(250, y_position - 20, "Principal Signature")
            
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(50, 30, "This is a computer-generated report card.")
            c.drawString(50, 20, f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            
            c.save()
            messagebox.showinfo("Success", f"Report card generated successfully as {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating report card: {e}")

    def calculate_grade(self, marks):
        if marks >= 90:
            return "A"
        elif marks >= 80:
            return "B"
        elif marks >= 60:
            return "C"
        else:
            return "D"

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentDataEntry(root)
    root.mainloop()