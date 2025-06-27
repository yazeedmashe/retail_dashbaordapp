import pandas as pd
import sqlite3
from datetime import datetime

# === Paths ===
file1 = r"Data/product_catalog.csv"
file2 = r"Data/sales_data.csv"
file3 = r"Data/store_data.csv"
log_path = r"Output/etl_log.txt"
db_path = r"Database/retail_analytics.db"

# === Extract ===
def extract(file1, file2, file3, log_file):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    df3 = pd.read_csv(file3)

    log_file.write("✅ Extract Step Started\n")
    log_file.write(f"🔹 {len(df1)} rows extracted from product_catalog\n")
    log_file.write(f"🔹 {len(df2)} rows extracted from sales_data\n")
    log_file.write(f"🔹 {len(df3)} rows extracted from store_data\n")
    log_file.write(f"✅ Extract Step Completed at {datetime.now()}\n\n")

    return df1, df2, df3

# === Clean ===
def clean_data(df1, df2, df3, log_file):
    df1 = df1.drop_duplicates().dropna()
    df2 = df2.drop_duplicates().dropna()
    df3 = df3.drop_duplicates().dropna()

    log_file.write("✅ Clean Step Started\n")
    log_file.write(f"🔹 {len(df1)} rows remain in product_catalog after cleaning\n")
    log_file.write(f"🔹 {len(df2)} rows remain in sales_data after cleaning\n")
    log_file.write(f"🔹 {len(df3)} rows remain in store_data after cleaning\n")
    log_file.write(f"✅ Clean Step Completed at {datetime.now()}\n\n")

    return df1, df2, df3

# === Transform ===
def transform(merged_df, log_file):
    log_file.write("✅ Transform Step Started\n")

    merged_df['Profit'] = (merged_df['Price'] - merged_df['Cost_Price']) * merged_df['Quantity']

    def categorize_profit(p):
        if p < 0:
            return "Loss"
        elif p < 100:
            return "Low Profit"
        else:
            return "High Profit"

    merged_df['Profitability'] = merged_df['Profit'].apply(categorize_profit)

    merged_df['Month'] = pd.to_datetime(merged_df['Sale_Date']).dt.month
    merged_df['Quarter'] = pd.to_datetime(merged_df['Sale_Date']).dt.quarter
    merged_df['Weekday'] = pd.to_datetime(merged_df['Sale_Date']).dt.day_name()

    log_file.write(f"✅ Transform Step Completed at {datetime.now()}\n\n")

    return merged_df

# === Summarize ===
def summarize(df, log_file):
    summary_df = df.groupby(['Region', 'Brand', 'Category', 'Profitability'])['Profit'].sum().reset_index()

    log_file.write("✅ Summarize Step Completed\n\n")
    return summary_df

# === Load ===
def load(df1, df2, db_path, log_file):
    db = sqlite3.connect(db_path)

    df1.to_sql('cleaned_data', db, if_exists='replace', index=False)
    df2.to_sql('summary_data', db, if_exists='replace', index=False)

    db.commit()
    db.close()

    log_file.write("✅ Load Step Completed: Data written to SQLite\n\n")

# === Main ETL Runner ===
def run_etl():
    with open(log_path, 'a') as log_file:
        log_file.write(f"\n🟡 ETL Job Started: {datetime.now()}\n\n")
        try:
            df1, df2, df3 = extract(file1, file2, file3, log_file)
            df1, df2, df3 = clean_data(df1, df2, df3, log_file)

            merged_df = df2.merge(df1, on='ProductID').merge(df3, on='StoreID')
            log_file.write(f"✅ Merging Completed: {len(merged_df)} rows\n\n")

            df_transformed = transform(merged_df, log_file)
            df_summary = summarize(df_transformed, log_file)

            load(df_transformed, df_summary, db_path, log_file)

            log_file.write(f"🟢 ETL Job Finished Successfully at {datetime.now()}\n")
        except Exception as e:
            log_file.write(f"🔴 ERROR during ETL: {str(e)} at {datetime.now()}\n")

# === Run the ETL Job ===
if __name__ == "__main__":
    run_etl()
