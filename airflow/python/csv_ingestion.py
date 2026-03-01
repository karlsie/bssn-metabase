import pandas as pd
from sqlalchemy import create_engine

# Load Excel
df = pd.read_csv('file.csv', header=True)

# Connect to Postgres
engine = create_engine('postgresql://username:password@localhost:5432/yourdb')

# Write to Table
df.to_sql('table_name', engine, if_exists='append', index=False)
