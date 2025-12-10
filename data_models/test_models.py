import pandas as pd
from models import *

df = pd.read_csv("data/doctor_availability.csv")

for i, row in df.iterrows():
    try:
        model = DoctorAvailabilityModel(**row.to_dict())
        print(f"Row {i} OK")
    except Exception as e:
        print(f"Row {i} ERROR: {e}")
