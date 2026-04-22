from dataclasses import dataclass, field, asdict
import json

# Class to hold patient data

@dataclass
class Diagnosis:
    date_month : int
    date_day : int
    date_year : int


@dataclass
class Patient:
    first_name : str
    last_name : str
    
    gender : str = "Unknown"
    ethnicity : str = "Unknown"
    race : str = "Unknown"

    birth_month : int = 1
    birth_day : int = 1
    birth_year : int = 1970

    diagnoses : list[Diagnosis] = field(default_factory=list)

    def save_data(self, filepath):
        file = open(filepath, "w")
        patient_dict = asdict(self)
        json.dump(patient_dict, file)
        file.close()