import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib import pyplot as plt

WINDOW_TITLE = "System Name"

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
    def __init__(self, parent, controller, label_text,):
        super().__init__(parent)

        self.label = ttk.Label(self, text=label_text, font="")
        self.label.pack(side="top", anchor="w")

        self.calendar = DateEntry(self, selectmode="day", state="readonly")
        self.calendar.pack(side="top", anchor="w")

class PatientDataInputFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.title = ttk.Label(self, text="Patient Information")
        self.title.pack(side="top", anchor="w", padx=10, pady=10)

        self.names_frame = ttk.Frame(self)
        self.names_frame.pack(side="top", fill="x")

        self.first_name_entry = LabeledEntry(self.names_frame, controller, "First Name")
        self.first_name_entry.pack(side="left", padx=10, pady=10)

        self.last_name_entry = LabeledEntry(self.names_frame, controller, "Last Name")
        self.last_name_entry.pack(side="left", padx=10, pady=10)

        GENDER_VALUES = ["Unknown", "Male", "Female"]

        self.gender_dropdown = LabeledDropdown(self, controller, "Gender", GENDER_VALUES)
        self.gender_dropdown.pack(side="top", fill="x", padx=10, pady=10)

        self.race_eth_frame = ttk.Frame(self)
        self.race_eth_frame.pack(side="top", fill="x")

        ETHNICITY_VALUES = ["Unknown", "Not Hispanic or Latino", "Hispanic or Latino"]
        RACE_VALUES = ["Unknown", "Asian", "Black", "White", "Native American", "Pacific Islander", "Other"]

        self.ethnicity_dropdown = LabeledDropdown(self.race_eth_frame, controller, "Ethnicity", ETHNICITY_VALUES)
        self.ethnicity_dropdown.pack(side="left", padx=10, pady=10)

        self.race_dropdown = LabeledDropdown(self.race_eth_frame, controller, "Race", RACE_VALUES)
        self.race_dropdown.pack(side="left", padx=10, pady=10)

        # TODO Fix bug with calendar coarse month/year selection
        self.birth_date_frame = LabeledCalendar(self, controller, "Birth Date")
        self.birth_date_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        self.button = ttk.Button(self, text="Save", command=self.save_patient_info)
        self.button.pack(anchor="w", padx=10, pady=10)
    
    def calendar_fix(self, event):
        event.widget._top_cal.overrideredirect(False)
        print("what")

    def save_patient_info(self):
        patient_info = dict()

        patient_info["first_name"] = self.first_name_entry.entry.get()
        patient_info["last_name"] = self.last_name_entry.entry.get()

        patient_info["gender"] = self.gender_dropdown.combo.get()

        patient_info["race"] = self.race_dropdown.combo.get()
        patient_info["ethnicity"] = self.ethnicity_dropdown.combo.get()

        birth_date = self.birth_date_frame.calendar.get_date()
        patient_info["birth_year"] = birth_date.year
        patient_info["birth_month"] = birth_date.month
        patient_info["birth_day"] = birth_date.day

        print(patient_info)

class DiagnosesInputFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.title = ttk.Label(self, text="Diagnosis Data")
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



class GuiRoot(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title(WINDOW_TITLE)
        self.geometry("800x600")
        
        self.container = ttk.Frame()
        self.container.pack(fill="both")
        
        # self.test_notebook = ttk.Notebook(self.container)
        # self.test_notebook.pack(fill="both", expand=True)

        # self.patient_data = PatientDataInputFrame(self.container, self)
        # self.patient_data.pack(fill="both")

        # self.diagnoses_data = DiagnosesInputFrame(self.container, self)
        # self.diagnoses_data.pack(fill="both")

        # self.test_plot = PlotFrame(self.container, self)


        # self.test_notebook.add(self.patient_data, text="Patient Information")
        # self.test_notebook.add(self.diagnoses_data, text="Diagnosis Information")
        # self.test_notebook.add(self.test_plot, text="Test Plot")