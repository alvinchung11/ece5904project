import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib import pyplot as plt
from datetime import date
import calendar

from patient_data import Patient
from patient_data import Diagnosis
from patient_data import save_patient_data, load_patient_data, load_encoded_labels

WINDOW_TITLE = "System Name"
TITLE_FONT = ("TkDefaultFont", 24)
H1_FONT = ("TkDefaultFont", 12)
H2_FONT = ("TkDefaultFont", 10)

MONTH_VALUES = list(range(1,12+1))
EARLIEST_YEAR = 1970

GENDER_VALUES = ["Not Specified", "Male", "Female"]
ETHNICITY_VALUES = ["Not Specified", "Not Hispanic or Latino", "Hispanic or Latino"]
RACE_VALUES = ["Not Specified", "Asian", "Black", "White", "Native American", "Pacific Islander", "Other"]

PATIENT_SAVE_FILETYPE = ("JSON Files", "*.json")

ENCODED_LABELS_FILEPATH = "../data/encoded_labels.json"

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

    def get(self):
        return self.entry.get()

class LabeledDropdown(ttk.Frame):
    def __init__(self, parent, controller, label_text, dropdown_values, width=None):
        super().__init__(parent)

        self.label = ttk.Label(self, text=label_text, font="")
        self.label.pack(side="top", anchor="w")

        self.combo = ttk.Combobox(self, values=dropdown_values, state="readonly", width=width)
        self.combo.set(dropdown_values[0])
        self.combo.pack(side="top", anchor="w")

    def get(self):
        return self.combo.get()
    
class LabeledSpinbox(ttk.Frame):
    def __init__(self, parent, controller, label_text, min, max, width=None):
        super().__init__(parent)

        self.label = ttk.Label(self, text=label_text, font="")
        self.label.pack(side="top", anchor="w")

        self.spin = ttk.Spinbox(self, from_=min, to=max, width=width)
        self.spin.set(min)
        self.spin.pack(side="top", anchor="w")

    def get(self):
        return self.spin.get()

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

        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()

        # if(len(first_name) < 1 or len(last_name) < 1):
        #     print("Please fill out first and last name")
        #     return

        gender = self.gender_dropdown.get()
        race = self.race_dropdown.get()
        ethnicity = self.ethnicity_dropdown.get()

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

        save_filepath = filedialog.asksaveasfilename(parent=self, filetypes=[PATIENT_SAVE_FILETYPE], defaultextension=".json", title="Save Patient Data")
        save_patient_data(patient, save_filepath)

        self.controller.set_patient_filepath(save_filepath)
        self.controller.set_current_patient(patient)
        self.controller.show_patient_diagnosis_split()

        self.grab_release()
        self.destroy()

    def cancel_callback(self):
        self.grab_release()
        self.destroy()

class DiagnosesInputWindow(tk.Toplevel):
    def __init__(self, parent, controller, new_diagnosis=True):
        super().__init__(parent)
        self.grab_set() # Prevent other interactions until window is closed 

        self.parent = parent
        self.controller = controller

        """ Window size and placement """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = 450
        window_height = 850

        placement_x, placement_y = get_window_placement(screen_width, screen_height, window_width, window_height)

        self.geometry("{}x{}+{}+{}".format(window_width, window_height, placement_x, placement_y))

        """ Title label """

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.title = ttk.Label(self.container, text="Diagnosis Data", font=TITLE_FONT)
        self.title.pack(anchor="w")

        """ Load in Encoded Labels """
        encoded_labels = load_encoded_labels(ENCODED_LABELS_FILEPATH)

        encoded_labels["cases.primary_site"]

        PRIMARY_SITE_VALUES = encoded_labels["cases.primary_site"]
        PRIMARY_SITE_VALUES.insert(0, "Unknown")
        primary_site_width = len(max(PRIMARY_SITE_VALUES, key=len))

        PRIMARY_DIAGNOSIS_VALUES = encoded_labels["diagnoses.primary_diagnosis"]
        PRIMARY_DIAGNOSIS_VALUES.insert(0, "Unknown")

        TISSUE_OR_ORGAN_ORIGIN_VALUES = encoded_labels["diagnoses.tissue_or_organ_of_origin"]
        TISSUE_OR_ORGAN_ORIGIN_VALUES.insert(0, "Unknown")

        TREATMENT_VALUES = encoded_labels["treatments.protocol_identifier"]
        TREATMENT_VALUES.insert(0, "Unknown")
        
        INSS_STAGE_VALUES = ["Unknown", "Stage 1", "Stage 2A", "Stage 2B", "Stage 3", "Stage 4", "Stage 4S"]
        INPC_GRADE_VALUES = ["Unknown", "Undifferentiated or Poorly Differentiated", "Differentiating"]
        COG_NBL_RISK_GROUP_VALUES = ["Unknown", "Low Risk", "Intermediate Risk", "High Risk"]
        MKI_VALUES = ["Unknown", "Low", "Intermediate", "High"]

        ICD_10_VALUES = encoded_labels["diagnoses.icd_10_code"]
        ICD_10_VALUES.insert(0, "Unknown")

        MOLECULAR_TEST_RESULT_VALUES = ["Unknown", "Abnormal", "Amplified", "Normal", "Not Amplified"]
        MOLECULAR_TEST_PLOIDY_VALUES = ["Unknown", "Diploid", "Hyperdiploid"]

        self.date = LabeledCalendar(self.container, controller, "Date of Diagnoses")
        self.date.pack(side="top", fill="x", padx=10, pady=10)

        self.primary_diagnosis = LabeledDropdown(self.container, controller, label_text="Primary Diagnosis", dropdown_values=PRIMARY_DIAGNOSIS_VALUES, width=primary_site_width)
        self.primary_diagnosis.pack(anchor="w", padx=10, pady=5)

        # TODO will need to allow manual input
        self.icd10 = LabeledDropdown(self.container, controller, label_text="ICD-10 Code", dropdown_values=ICD_10_VALUES, width=primary_site_width)
        self.icd10.pack(anchor="w", padx=10, pady=5)

        # TODO will need to allow individual inputs of treatments
        self.treatment_protocols = LabeledDropdown(self.container, controller, label_text="Treatment Protocols", dropdown_values=TREATMENT_VALUES, width=primary_site_width)
        self.treatment_protocols.pack(anchor="w", padx=10, pady=5)

        self.primary_site = LabeledDropdown(self.container, controller, label_text="Primary Site", dropdown_values=PRIMARY_SITE_VALUES, width=primary_site_width)
        self.primary_site.pack(anchor="w", padx=10, pady=5)

        self.tissue_organ_origin = LabeledDropdown(self.container, controller, label_text="Tissue/Organ of Origin", dropdown_values=TISSUE_OR_ORGAN_ORIGIN_VALUES, width=primary_site_width)
        self.tissue_organ_origin.pack(anchor="w", padx=10, pady=5)

        self.inss_stage = LabeledDropdown(self.container, controller, label_text="INSS Stage", dropdown_values=INSS_STAGE_VALUES, width=primary_site_width)
        self.inss_stage.pack(anchor="w", padx=10, pady=5)

        self.inpc_grade = LabeledDropdown(self.container, controller, label_text="INPC Grade", dropdown_values=INPC_GRADE_VALUES, width=primary_site_width)
        self.inpc_grade.pack(anchor="w", padx=10, pady=5)

        self.cog_nbl_risk_group = LabeledDropdown(self.container, controller, label_text="COG Risk Group", dropdown_values=COG_NBL_RISK_GROUP_VALUES, width=primary_site_width)
        self.cog_nbl_risk_group.pack(anchor="w", padx=10, pady=5)

        self.mki = LabeledDropdown(self.container, controller, label_text="Mitosis Karyorrhexis Index", dropdown_values=MKI_VALUES, width=primary_site_width)
        self.mki.pack(anchor="w", padx=10, pady=5)

        self.molecular_test_result = LabeledDropdown(self.container, controller, label_text="MYCN Molecular Test Result", dropdown_values=MOLECULAR_TEST_RESULT_VALUES, width=primary_site_width)
        self.molecular_test_result.pack(anchor="w", padx=10, pady=5)

        self.molecular_test_ploidy = LabeledDropdown(self.container, controller, label_text="Molecular Test Ploidy", dropdown_values=MOLECULAR_TEST_PLOIDY_VALUES, width=primary_site_width)
        self.molecular_test_ploidy.pack(anchor="w", padx=10, pady=5)
        
        self.pathology_necrosis_percent = LabeledSpinbox(self.container, controller, label_text="Pathology Necrosis Percent", min=0, max=100)
        self.pathology_necrosis_percent.pack(anchor="w", padx=10, pady=5)

        self.pathology_percent_tumor_nuclei = LabeledSpinbox(self.container, controller, label_text="Pathology Percent Tumor Nuclei", min=0, max=100)
        self.pathology_percent_tumor_nuclei.pack(anchor="w", padx=10, pady=5)

        self.save_button = ttk.Button(self, text="Save", command=self.save_callback)
        self.save_button.pack(side="left", padx=10, pady=5)

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel_callback)
        self.cancel_button.pack(side="left", padx=10, pady=5)

    def save_callback(self):
        # TODO Add checking for valid values
        diagnosis = Diagnosis()

        month, day, year = self.date.get_date()

        diagnosis.date_month = month
        diagnosis.date_day = day
        diagnosis.date_year = year

        diagnosis.primary_diagnosis = self.primary_diagnosis.get()
        diagnosis.icd_10_code = self.icd10.get()
        diagnosis.treatment_protocols = self.treatment_protocols.get()

        diagnosis.primary_site = self.primary_site.get()
        diagnosis.tissue_organ_origin = self.tissue_organ_origin.get()

        diagnosis.inss_stage = self.inss_stage.get()
        diagnosis.inpc_grade = self.inpc_grade.get()
        diagnosis.cog_risk_group = self.cog_nbl_risk_group.get()

        diagnosis.mki = self.mki.get()
        diagnosis.molecular_test_result = self.molecular_test_result.get()
        diagnosis.molecular_test_ploidy = self.molecular_test_ploidy.get()

        diagnosis.pathology_necrosis_percent = float(self.pathology_necrosis_percent.get()) / 100.0
        diagnosis.pathology_percent_tumor_nuclei = float(self.pathology_percent_tumor_nuclei.get()) / 100.0
        
        # Save to disk
        self.controller.add_diagnosis(diagnosis)
        
        # Update display
        self.parent.show_info()

        self.grab_release()
        self.destroy()

    def cancel_callback(self):
        self.grab_release()
        self.destroy()

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

        self.load_patient_button = ttk.Button(self, text="Load Patient", padding=10, width=20, command=self.load_patient_callback)
        self.load_patient_button.pack(pady=5)

    def new_patient_callback(self):
        patient_input_window = PatientDataInputWindow(self, self.controller)

    def load_patient_callback(self):
        filepath = filedialog.askopenfilename(parent=self, filetypes=[PATIENT_SAVE_FILETYPE], defaultextension=".json")
        patient = load_patient_data(filepath)

        self.controller.set_patient_filepath(filepath)
        self.controller.set_current_patient(patient)
        self.controller.show_patient_diagnosis_split()

class PatientInfoFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.title_label = ttk.Label(self, text="Patient Information", font=TITLE_FONT)
        self.title_label.pack(anchor="center", padx=10, pady=10)

        patient = controller.get_current_patient()

        name_str = "Name: {}, {}".format(patient.last_name, patient.first_name)
        gender_str = "Gender: {}".format(patient.gender)
        ethnicity_str = "Ethnicity: {}".format(patient.ethnicity)
        race_str = "Race: {}".format(patient.race)

        birth_month = calendar.month_name[patient.birth_month]

        date_of_birth_str = "Date of Birth: {} {}, {}".format(birth_month, patient.birth_day, patient.birth_year)

        self.edit_button = ttk.Button(self, text="Edit")
        self.edit_button.pack(anchor="center", padx=10)

        self.name = ttk.Label(self, text=name_str, font=H1_FONT)
        self.name.pack(anchor="w", padx=10, pady=5)

        self.date_of_birth = ttk.Label(self, text=date_of_birth_str, font=H1_FONT)
        self.date_of_birth.pack(anchor="w", padx=10, pady=5)

        self.gender = ttk.Label(self, text=gender_str, font=H1_FONT)
        self.gender.pack(anchor="w", padx=10, pady=5)

        self.ethnicity = ttk.Label(self, text=ethnicity_str, font=H1_FONT)
        self.ethnicity.pack(anchor="w", padx=10, pady=5)

        self.race = ttk.Label(self, text=race_str, font=H1_FONT)
        self.race.pack(anchor="w", padx=10, pady=5)

class DiagnosesInfoFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.title_label = ttk.Label(self, text="Diagnoses", font=TITLE_FONT)
        self.title_label.pack(anchor="center", padx=10, pady=10)

        self.add_button = ttk.Button(self, text="Add Entry", command=self.add_button_callback)
        self.add_button.pack(anchor="center", padx=10)

        if(self.controller.get_current_patient().diagnosis != None):
            self.show_info()

    def add_button_callback(self):
        diagnosis_input_window = DiagnosesInputWindow(self, self.controller)
    
    def show_info(self):
        self.add_button.pack_forget()

        patient = self.controller.get_current_patient()
        diagnosis = patient.diagnosis

        month = calendar.month_name[diagnosis.date_month]
        day = diagnosis.date_day
        year = diagnosis.date_year

        primary_diagnosis_str = "Primary Diagnosis: {}".format(diagnosis.primary_diagnosis)
        icd_10_code_str = "ICD-10 Code: {}".format(diagnosis.icd_10_code)
        treatment_protocols_str = "Treatment Protocol IDs:\n{}".format(diagnosis.treatment_protocols)

        primary_site_str = "Primary Site: {}".format(diagnosis.primary_site)
        tissue_organ_origin_str = "Tissue/Organ of Origin: {}".format(diagnosis.tissue_organ_origin)

        inss_stage_str = "INSS Stage: {}".format(diagnosis.inss_stage)
        inpc_grade_str = "INPC Grade: {}".format(diagnosis.inpc_grade)
        cog_risk_group_str = "COG Neuroblastoma Risk Group: {}".format(diagnosis.cog_risk_group)

        mki_str = "Mitosis Karyorrhexis Index: {}".format(diagnosis.mki)

        molecular_test_result_str = "Molecular Test Result (MYCN Gene): {}".format(diagnosis.molecular_test_result)
        molecular_test_ploidy_str = "Molecular Test Ploidy: {}".format(diagnosis.molecular_test_ploidy)

        pathology_necrosis_percent_str = "Pathology Necrosis Percent: {}%".format(diagnosis.pathology_necrosis_percent * 100)
        pathology_percent_tumor_nuclei_str = "Pathology Percent Tumor Nuclei: {}%".format(diagnosis.pathology_necrosis_percent * 100)

        date_str = "Date of Record: {} {}, {}".format(month, day, year)
        self.date = ttk.Label(self, text=date_str, font=H2_FONT)
        self.date.pack(anchor="w", padx=10, pady=5)

        self.primary_diagnosis = ttk.Label(self, text=primary_diagnosis_str, font=H2_FONT)
        self.primary_diagnosis.pack(anchor="w", padx=10, pady=5)

        self.icd10 = ttk.Label(self, text=icd_10_code_str, font=H2_FONT)
        self.icd10.pack(anchor="w", padx=10, pady=5)
        
        self.treatments = ttk.Label(self, text=treatment_protocols_str, font=H2_FONT, wraplength=300)
        self.treatments.pack(anchor="w", padx=10, pady=5)

        self.primary_site = ttk.Label(self, text=primary_site_str, font=H2_FONT, wraplength=300)
        self.primary_site.pack(anchor="w", padx=10, pady=5)

        self.tissue_organ_origin = ttk.Label(self, text=tissue_organ_origin_str, font=H2_FONT, wraplength=300)
        self.tissue_organ_origin.pack(anchor="w", padx=10, pady=5)

        self.inss_stage = ttk.Label(self, text=inss_stage_str, font=H2_FONT)
        self.inss_stage.pack(anchor="w", padx=10, pady=5)

        self.inpc_grade = ttk.Label(self, text=inpc_grade_str, font=H2_FONT)
        self.inpc_grade.pack(anchor="w", padx=10, pady=5)

        self.cog_risk_group = ttk.Label(self, text=cog_risk_group_str, font=H2_FONT)
        self.cog_risk_group.pack(anchor="w", padx=10, pady=5)

        self.mki = ttk.Label(self, text=mki_str, font=H2_FONT)
        self.mki.pack(anchor="w", padx=10, pady=5)

        self.molecular_test_result = ttk.Label(self, text=molecular_test_result_str, font=H2_FONT)
        self.molecular_test_result.pack(anchor="w", padx=10, pady=5)

        self.molecular_test_ploidy = ttk.Label(self, text=molecular_test_ploidy_str, font=H2_FONT)
        self.molecular_test_ploidy.pack(anchor="w", padx=10, pady=5)

        self.pathology_necrosis_percent = ttk.Label(self, text=pathology_necrosis_percent_str, font=H2_FONT)
        self.pathology_necrosis_percent.pack(anchor="w", padx=10, pady=5)

        self.pathology_percent_tumor_nuclei = ttk.Label(self, text=pathology_percent_tumor_nuclei_str, font=H2_FONT)
        self.pathology_percent_tumor_nuclei.pack(anchor="w", padx=10, pady=5)


class GuiRoot(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.current_patient = None
        self.patient_filepath = None

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

        self.patient_diagnosis_split = ttk.PanedWindow(self.left_pane_frame, orient="vertical")
        self.patient_diagnosis_split.pack(fill="both", expand=True)

        self.patient_info = PatientInfoFrame(self.patient_diagnosis_split, self)
        self.patient_diagnosis_split.add(self.patient_info, weight=1)

        self.diagnoses_info = DiagnosesInfoFrame(self.patient_diagnosis_split, self)
        self.patient_diagnosis_split.add(self.diagnoses_info, weight=2)

    def set_current_patient(self, patient : Patient):
        self.current_patient = patient

    def get_current_patient(self):
        return self.current_patient
    
    def set_patient_filepath(self, filepath):
        self.patient_filepath = filepath

    def get_patient_filepath(self, filepath):
        return self.patient_filepath

    def add_diagnosis(self, diagnosis):
        self.current_patient.diagnosis = diagnosis
        save_patient_data(self.current_patient, self.patient_filepath)

if __name__ == "__main__":
    test_root = tk.Tk()
    window = DiagnosesInputWindow(test_root, test_root)

    test_root.mainloop()
