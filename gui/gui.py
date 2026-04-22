import tkinter as tk
from tkinter import ttk
from matplotlib import pyplot as plt
from datetime import date
import calendar

from patient_data import Patient
from patient_data import Diagnosis

WINDOW_TITLE = "System Name"
TITLE_FONT = ("TkDefaultFont", 24)

MONTH_VALUES = list(range(1,12+1))
EARLIEST_YEAR = 1970

GENDER_VALUES = ["Not Specified", "Male", "Female"]
ETHNICITY_VALUES = ["Not Specified", "Not Hispanic or Latino", "Hispanic or Latino"]
RACE_VALUES = ["Not Specified", "Asian", "Black", "White", "Native American", "Pacific Islander", "Other"]

def get_window_placement(screen_width, screen_height, window_width, window_height):
    placement_x = int(screen_width / 2) - int(window_width / 2)
    placement_y = int(screen_height / 2) - int(window_height / 2)
    
    return placement_x, placement_y

class LabeledEntry(ttk.Frame):
    def __init__(self, parent, controller, label_text):
        super().__init__(parent)

        self.label = ttk.Label(self, text=label_text, font="")
        self.label.pack(side="top", anchor="w")

        self.entry = ttk.Entry(self)
        self.entry.pack(side="top", anchor="w")

class LabeledDropdown(ttk.Frame):
    def __init__(self, parent, controller, label_text, dropdown_values):
        super().__init__(parent)

        self.label = ttk.Label(self, text=label_text, font="")
        self.label.pack(side="top", anchor="w")

        self.combo = ttk.Combobox(self, values=dropdown_values, state="readonly")
        self.combo.set(dropdown_values[0])
        self.combo.pack(side="top", anchor="w")

class LabeledCalendar(ttk.Frame):
    def __init__(self, parent, controller, label_text, initial_month=None, initial_day=None, initial_year=None):
        super().__init__(parent)
        
        self.label = ttk.Label(self, text=label_text, font="")
        self.label.pack(side="top", anchor="w")

        current_date = date.today()
        year_values = list(reversed(range(EARLIEST_YEAR, current_date.year+1)))

        if(initial_month == None):
            initial_month = current_date.month

        if(initial_year == None):
            initial_year = current_date.year

        initial_day_range = calendar.monthrange(initial_year, initial_month)[1]
        initial_day_values = list(range(1, initial_day_range+1))

        if(initial_day == None):
            initial_day = current_date.day

        if(initial_day > initial_day_values[-1]):
            initial_day = initial_day_values[-1]
        elif(initial_day < 1):
            initial_day = 1

        """ Month """
        self.month_frame = ttk.Frame(self)
        self.month_frame.pack(side="left")

        self.month_label = ttk.Label(self.month_frame, text="Month")
        self.month_label.pack(side="top", anchor="w")

        self.month_combo = ttk.Combobox(self.month_frame, width=5, values=MONTH_VALUES, state="readonly")
        self.month_combo.set(initial_month)
        self.month_combo.bind("<<ComboboxSelected>>", self.update_day_values)
        self.month_combo.pack(side="top", anchor="w")

        """ Day """
        self.day_frame = ttk.Frame(self)
        self.day_frame.pack(side="left", padx=10)

        self.day_label = ttk.Label(self.day_frame, text="Day")
        self.day_label.pack(side="top", anchor="w")
        
        self.day_combo = ttk.Combobox(self.day_frame, width=5, values=initial_day_values, state="readonly")
        self.day_combo.set(initial_day)
        self.day_combo.pack(side="top", anchor="w")

        """ Year """
        self.year_frame = ttk.Frame(self)
        self.year_frame.pack(side="left")

        self.year_label = ttk.Label(self.year_frame, text="Year")
        self.year_label.pack(side="top", anchor="w")

        self.year_combo = ttk.Combobox(self.year_frame, width=10, values=year_values, state="readonly")
        self.year_combo.set(initial_year)
        self.year_combo.bind("<<ComboboxSelected>>", self.update_day_values)
        self.year_combo.pack(side="top", anchor="w")

    def update_day_values(self, event):
        selected_month = int(self.month_combo.get())
        selected_day = int(self.day_combo.get())
        selected_year = int(self.year_combo.get())

        # Determine the number of days in the month
        num_days = calendar.monthrange(selected_year, selected_month)[1]
        day_range = list(range(1, num_days+1))
        
        # Set possible day values accordingly
        self.day_combo.configure(values=day_range)

        # Set the selected day if it exceeds new range
        if(selected_day > day_range[-1]):
            self.day_combo.set(day_range[-1])

    def get_date(self):
        selected_month = int(self.month_combo.get())
        selected_day = int(self.day_combo.get())
        selected_year = int(self.year_combo.get())

        return selected_month, selected_day, selected_year

class PatientDataInputWindow(tk.Toplevel):
    def __init__(self, parent, controller, new_patient=True):
        super().__init__(parent)
        self.grab_set() # Prevent other interactions until window is closed 
        
        self.controller = controller
        self.new_patient = new_patient

        """ Window size and placement """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()

        placement_x, placement_y = get_window_placement(screen_width, screen_height, window_width, window_height)

        self.geometry("+{}+{}".format(placement_x, placement_y))

        """ Title label """
        if(new_patient):
            title_text = "New Patient Information"
        else:
            title_text = "Edit Patient Information"

        self.title = ttk.Label(self, text=title_text, font=TITLE_FONT)
        self.title.pack(side="top", anchor="w", padx=10, pady=10)

        """ First and last name """
        self.names_frame = ttk.Frame(self)
        self.names_frame.pack(side="top", fill="x")

        self.first_name_entry = LabeledEntry(self.names_frame, controller, "First Name")
        self.first_name_entry.pack(side="left", padx=10, pady=10)

        self.last_name_entry = LabeledEntry(self.names_frame, controller, "Last Name")
        self.last_name_entry.pack(side="left", padx=10, pady=10)

        """ Gender """
        self.gender_dropdown = LabeledDropdown(self, controller, "Gender", GENDER_VALUES)
        self.gender_dropdown.pack(side="top", fill="x", padx=10, pady=10)

        """ Race and ethnicity """
        self.race_eth_frame = ttk.Frame(self)
        self.race_eth_frame.pack(side="top", fill="x")

        self.ethnicity_dropdown = LabeledDropdown(self.race_eth_frame, controller, "Ethnicity", ETHNICITY_VALUES)
        self.ethnicity_dropdown.pack(side="left", padx=10, pady=10)

        self.race_dropdown = LabeledDropdown(self.race_eth_frame, controller, "Race", RACE_VALUES)
        self.race_dropdown.pack(side="left", padx=10, pady=10)

        """ Date of Birth """
        self.birth_date_frame = LabeledCalendar(self, controller, "Date of Birth")
        self.birth_date_frame.pack(side="top", fill="x", padx=10, pady=10)

        self.save_button = ttk.Button(self, text="Save", command=self.save_callback)
        self.save_button.pack(side="left", padx=10, pady=10)

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel_callback)
        self.cancel_button.pack(side="left", padx=10, pady=10)

    def save_callback(self):

        first_name = self.first_name_entry.entry.get()
        last_name = self.last_name_entry.entry.get()

        # if(len(first_name) < 1 or len(last_name) < 1):
        #     print("Please fill out first and last name")
        #     return

        gender = self.gender_dropdown.combo.get()
        race = self.race_dropdown.combo.get()
        ethnicity = self.ethnicity_dropdown.combo.get()

        birth_month, birth_day, birth_year = self.birth_date_frame.get_date()

        patient = Patient(first_name, last_name)
        # if(not self.new_patient):
        #     pass

        patient.gender = gender
        patient.race = race
        patient.ethnicity = ethnicity

        patient.birth_month = birth_month
        patient.birth_day = birth_day
        patient.birth_year = birth_year

        self.controller.set_current_patient(patient)
    
        self.grab_release()
        self.destroy()

    def cancel_callback(self):
        self.grab_release()
        self.destroy()

class DiagnosesInputWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.title = ttk.Label(self, text="Diagnosis Data", font=TITLE_FONT)
        self.title.grid(row=0, sticky="nsew", padx=10, pady=10)

        PRIMARY_DIAGNOSIS_VALUES = ["Unknown", "Stage 1", "Stage 2A", "Stage 2B", "Stage 3", "Stage 4", "Stage 4S"]
        self.primary_diagnosis = LabeledDropdown(self, controller, label_text="Primary Diagnosis", dropdown_values=PRIMARY_DIAGNOSIS_VALUES)

        self.primary_site = LabeledEntry(self, controller, label_text="Primary Site")
        self.primary_site.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.tissue_organ_origin = LabeledEntry(self, controller, label_text="Tissue or Organ of Origin")
        self.tissue_organ_origin.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        INSS_STAGE_VALUES = ["Unknown", "Stage 1", "Stage 2A", "Stage 2B", "Stage 3", "Stage 4", "Stage 4S"]
        self.inss_stage = LabeledDropdown(self, controller, label_text="INSS Stage", dropdown_values=INSS_STAGE_VALUES)
        self.inss_stage.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        COG_NBL_RISK_GROUP_VALUES = ["Unknown", "Low Risk", "Intermediate Risk", "High Risk"]
        self.cog_nbl_risk_group = LabeledDropdown(self, controller, label_text="COG Risk Group", dropdown_values=COG_NBL_RISK_GROUP_VALUES)
        self.cog_nbl_risk_group.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        MKI_VALUES = ["Unknown", "Low", "Intermediate", "High"]
        self.mki = LabeledDropdown(self, controller, label_text="Mitosis Karyorrhexis Index", dropdown_values=MKI_VALUES)
        self.mki.grid(row=3, column=0, padx=10, pady=10)

class PlotFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.title = ttk.Label(self, text="Plot Data", font=TITLE_FONT)
        self.title.pack()

class PatientSelectFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.title_label = ttk.Label(self, text="Patient Data", font=TITLE_FONT)
        self.title_label.pack(pady=10)

        self.new_patient_button = ttk.Button(self, text="Add New Data", padding=10, width=20, command=self.new_patient_callback)
        self.new_patient_button.pack(pady=5)

        # self.load_patient_button = ttk.Button(self, text="Load Patient", padding=10, width=20)
        # self.load_patient_button.pack(pady=5)

    def new_patient_callback(self):
        patient_info_window = PatientDataInputWindow(self, self.controller)

class PatientInfoFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)


class GuiRoot(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.current_patient = None
        
        self.title(WINDOW_TITLE)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width*0.8)
        window_height = int(screen_height*0.8)

        placement_x, placement_y = get_window_placement(screen_width, screen_height, window_width, window_height)

        self.geometry("{}x{}+{}+{}".format(window_width, window_height, placement_x, placement_y))
        
        self.minsize(width=600, height=400)

        # self.frames = dict()

        self.style = ttk.Style()
        # self.style.theme_use("default")
        self.style.configure("TPanedwindow",
                             background="gray")

        self.container = ttk.Frame()
        self.container.pack(fill="both", expand=True)

        # Main horizontal layout, left and right
        self.main_hor_pane = ttk.PanedWindow(self.container, orient="horizontal")
        self.main_hor_pane.pack(fill="both", expand=True)

        # Add frame to left pane
        self.left_pane_frame = ttk.Frame(self.main_hor_pane)
        self.main_hor_pane.add(self.left_pane_frame, weight=1)

        # TODO implement the split info
        # self.patient_diagnosis_split = ttk.PanedWindow(self.left_pane_frame, orient="vertical")

        # self.patient_info = ttk.Frame(self.left_pane_frame)
        # self.patient_diagnosis_split.add(self.patient_info, weight=1)

        # label = ttk.Label(self.patient_info, text="Patient")
        # label.pack()

        # self.diagnoses_info = ttk.Frame(self.patient_diagnosis_split)
        # self.patient_diagnosis_split.add(self.diagnoses_info, weight=1)

        # label2 = ttk.Label(self.diagnoses_info, text="Diagnosis")
        # label2.pack()

        self.patient_select = PatientSelectFrame(self.left_pane_frame, self)
        self.patient_select.pack(expand=True)

        # Add a vertical layout to the right side
        self.right_vert_pane = ttk.PanedWindow(self.main_hor_pane, orient="vertical")
        self.main_hor_pane.add(self.right_vert_pane, weight=5)

        # Frames within right side
        self.test_plot = PlotFrame(self.right_vert_pane, self)
        self.right_vert_pane.add(self.test_plot, weight=5)
        
        # self.diagnoses_data = DiagnosesInputFrame(self.righ_vert_pane, self)
        # self.righ_vert_pane.add(self.diagnoses_data, weight=1)

        # self.test_notebook = ttk.Notebook(self.container)
        # self.test_notebook.pack(fill="both", expand=True)

        # self.patient_data.grid(row=0, column=0)
        # self.test_notebook.add(self.patient_data, text="Patient Information")
        # self.test_notebook.add(self.diagnoses_data, text="Diagnosis Information")
        # self.test_notebook.add(self.test_plot, text="Test Plot")

    def show_patient_diagnosis_split(self):
        self.patient_select.pack_forget()
        self.patient_diagnosis_split.pack(fill="both", expand=True)

    def set_current_patient(self, patient : Patient):
        self.current_patient = patient

        print(self.current_patient.first_name)
        print(self.current_patient.last_name)
        print(self.current_patient.birth_month)
        print(self.current_patient.birth_day)
        print(self.current_patient.birth_year)

if __name__ == "__main__":
    test_root = tk.Tk()
    window = PatientDataInputWindow(test_root, test_root) 

    test_root.mainloop()
