# Classes to hold patient data

from dataclasses import dataclass, field, asdict
from datetime import date
import json
import numpy as np
import calendar

FEATURE_VECTOR_LENGTH = 34

ENCODED_LABELS_FILEPATH = "../data/encoded_labels.json"

COG_RISK_ENCODING = {"Unknown":0.0, "Low Risk":1, "Intermediate Risk":2, "High Risk":3}
INSS_STAGE_ENCODING = {"Unknown":0.0, "Stage 1":1, "Stage 2A":2, "Stage 2B":3, "Stage 3":4, "Stage 4":5, "Stage 4S": 6}
MKI_ENCODING = {"Unknown":0.0, "Low":1, "Intermediate":2, "High":3}

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

    def get_diagnosis_in_english(self):
        ret = "Record Date: {} {}, {} ".format(calendar.month_name[self.date_month], self.date_day, self.date_year)

        ret += "Primary Diagnosis: {} ".format(self.primary_diagnosis)
        ret += "ICD-10 Code: {} ".format(self.icd_10_code)
        ret += "Treatment Protocols: {} ".format(self.treatment_protocols)

        ret += "Primary Site: {} ".format(self.primary_site)
        ret += "Tissue or Organ of Origin: {} ".format(self.tissue_organ_origin)

        ret += "International Neuroblastoma Staging System (INSS) Stage: {} ".format(self.inss_stage)
        ret += "International Neuroblastoma Pathology Classification (INPC) Grade: {} ".format(self.inpc_grade)
        ret += "Children's Oncology Group (COG) Neuroblastoma Risk Group: {} ".format(self.cog_risk_group)
        ret += "Mitosis Karyorrhexis Index (MKI): {} ".format(self.mki)

        ret += "Molecular Test Result, MYCN Gene: {} ".format(self.molecular_test_result)
        ret += "Molecular Test Ploidy: {} ".format(self.molecular_test_ploidy)

        ret += "Sample Pathology Necrosis Percent: {} ".format(self.pathology_necrosis_percent)
        ret += "Sample Pathology Percent Tumor Nuclei: {} ".format(self.pathology_percent_tumor_nuclei)

        return ret

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

    def get_feature_vector(self):
        feature_vector = np.zeros(FEATURE_VECTOR_LENGTH)
        
        encoded_labels = load_encoded_labels()

        feature_vector[0] = encoded_labels["cases.primary_site"].index(self.diagnosis.primary_site)

        patient_birth = date(self.birth_year, self.birth_month, self.birth_day)
        diagnosis_date = date(self.diagnosis.date_year, self.diagnosis.date_month, self.diagnosis.date_day)
        diff = diagnosis_date - patient_birth
        age_at_diagnosis = diff.days

        feature_vector[1] = age_at_diagnosis

        feature_vector[2] = COG_RISK_ENCODING[self.diagnosis.cog_risk_group]
        feature_vector[3] = encoded_labels["diagnoses.icd_10_code"].index(self.diagnosis.icd_10_code)
        feature_vector[4] = INSS_STAGE_ENCODING[self.diagnosis.inss_stage]
        feature_vector[5] = MKI_ENCODING[self.diagnosis.mki]
        feature_vector[6] = encoded_labels["diagnoses.primary_diagnosis"].index(self.diagnosis.primary_diagnosis)
        feature_vector[7] = encoded_labels["diagnoses.tissue_or_organ_of_origin"].index(self.diagnosis.tissue_organ_origin)
        feature_vector[8] = encoded_labels["treatments.protocol_identifier"].index(self.diagnosis.treatment_protocols)

        match self.gender:
            case "Female":
                feature_vector[9] = 1.0
            case "Male":
                feature_vector[10] = 1.0
            case _:
                feature_vector[11] = 1.0

        match self.ethnicity:
            case "Hispanic or Latino":
                feature_vector[12] = 1.0
            case "Not Hispanic or Latino":
                feature_vector[13] = 1.0
            case _:
                feature_vector[14] = 1.0

        match self.race:
            case "Native American":
                feature_vector[15] = 1.0
            case "Asian":
                feature_vector[16] = 1.0
            case "Black":
                feature_vector[17] = 1.0
            case "Pacific Islander":
                feature_vector[18] = 1.0
            case "White":
                feature_vector[19] = 1.0
            case _:
                feature_vector[20] = 1.0

        match self.diagnosis.inpc_grade:
            case "Differentiating":
                feature_vector[21] = 1.0
            case "Undifferentiated or Poorly Differentiated":
                feature_vector[22] = 1.0
            case _:
                feature_vector[23] = 1.0

        match self.diagnosis.molecular_test_ploidy:
            case "Diploid":
                feature_vector[24] = 1.0
            case "Hyperdiploid":
                feature_vector[25] = 1.0
            case _:
                feature_vector[26] = 1.0

        match self.diagnosis.molecular_test_result:
            case "Abnormal":
                feature_vector[27] = 1.0
            case "Amplified":
                feature_vector[28] = 1.0
            case "Normal":
                feature_vector[29] = 1.0
            case "Not Amplified":
                feature_vector[30] = 1.0
            case _:
                feature_vector[31] = 1.0

        feature_vector[32] = self.diagnosis.pathology_necrosis_percent
        feature_vector[33] = self.diagnosis.pathology_percent_tumor_nuclei

        # Add batch dimension
        feature_vector = np.expand_dims(feature_vector, axis=0)

        return feature_vector

        """
        Ordering
        0 'cases.primary_site',
        1 'diagnoses.age_at_diagnosis',
        2 'diagnoses.cog_neuroblastoma_risk_group',
        3 'diagnoses.icd_10_code',
        4 'diagnoses.inss_stage',
        5 'diagnoses.mitosis_karyorrhexis_index',
        6 'diagnoses.primary_diagnosis',
        7 'diagnoses.tissue_or_organ_of_origin',
        8 'treatments.protocol_identifier',

        9 'demographic.gender_female',
        10 'demographic.gender_male',
        11 'demographic.gender_nan',

        12 'demographic.ethnicity_hispanic or latino',
        13 'demographic.ethnicity_not hispanic or latino',
        14 'demographic.ethnicity_nan',

        15 'demographic.race_american indian or alaska native',
        16 'demographic.race_asian',
        17 'demographic.race_black or african american',
        18 'demographic.race_native hawaiian or other pacific islander',
        19 'demographic.race_white',
        20 'demographic.race_nan',

        21 'diagnoses.inpc_grade_Differentiating',
        22 'diagnoses.inpc_grade_Undifferentiated or Poorly Differentiated',
        23 'diagnoses.inpc_grade_nan',
        
        24 'molecular_tests.ploidy_Diploid',
        25 'molecular_tests.ploidy_Hyperdiploid',
        26 'molecular_tests.ploidy_nan',

        27 'molecular_tests.test_result_Abnormal, NOS',
        28 'molecular_tests.test_result_Amplified',
        29 'molecular_tests.test_result_Normal',
        30 'molecular_tests.test_result_Not Amplified',
        31 'molecular_tests.test_result_nan',

        32 'pathology_details.necrosis_percent',
        33 'pathology_details.percent_tumor_nuclei',
        """

    def get_patient_data_in_english(self):
        ret = "Patient Name: {} {} ".format(self.first_name, self.last_name)

        ret += "Gender: {} ".format(self.gender)
        ret += "Ethnicity: {} ".format(self.ethnicity)
        ret += "Race: {} ".format(self.race)

        ret += "Date of Birth: {} {}, {}".format(calendar.month_name[self.birth_month], self.birth_day, self.birth_year)

        ret += "Diagnosis 1: [{}] ".format(self.diagnosis.get_diagnosis_in_english())

        return ret

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

def load_encoded_labels(filepath=ENCODED_LABELS_FILEPATH):

    file = open(filepath, "r")
    data = json.load(file)

    return data
