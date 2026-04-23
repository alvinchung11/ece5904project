from dataclasses import dataclass, field, asdict
import json

# Class to hold patient data

@dataclass
class Diagnosis:
    date_month : int = 1
    date_day : int = 1
    date_year : int = 1970

    primary_diagnosis : str = ""
    icd_10_code : str = ""
    treatment_protocols : str = ""

    primary_site : str = ""
    tissue_organ_origin : str = ""

    inss_stage : str = ""
    inpc_grade : str = ""
    cog_risk_group : str = ""

    mki : str = ""

    molecular_test_result : str = ""
    molecular_test_ploidy : str = ""

    pathology_necrosis_percent : float = 0.0
    pathology_percent_tumor_nuclei : float = 0.0

@dataclass
class Patient:
    first_name : str = ""
    last_name : str = ""
    
    gender : str = "Unknown"
    ethnicity : str = "Unknown"
    race : str = "Unknown"

    birth_month : int = 1
    birth_day : int = 1
    birth_year : int = 1970

    diagnosis : Diagnosis = None
    # diagnoses : list[Diagnosis] = field(default_factory=list)

    def get_diagnosis_asdict(self):
        return asdict(self.diagnosis)

def save_patient_data(patient, filepath):
    file = open(filepath, "w")
    patient_dict = asdict(patient)
    json.dump(patient_dict, file)
    file.close()
    
def load_patient_data(filepath):
    file = open(filepath, "r")
    data = json.load(file)

    patient = Patient(**data)

    if(patient.diagnosis != None):
        patient.diagnosis = Diagnosis(**patient.diagnosis)

    return patient

def load_encoded_labels(filepath):
    file = open(filepath, "r")
    data = json.load(file)

    return data