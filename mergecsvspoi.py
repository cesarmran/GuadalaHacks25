import pandas as pd

# Load the CSV files
file1 = pd.read_csv("C:/Users/52312/Downloads/Guadalahacks25/nav1.csv")
file2 = pd.read_csv("C:/Users/52312/Downloads/Guadalahacks25/POIs/POI_4815075.csv")
file1.columns = file1.columns.str.lower()
file2.columns = file2.columns.str.lower()
# Define the common column and the columns to extract
common_column = "link_id"
file1_column = "geometry"
file2_column = "poi_id"

# Merge the files based on the common column
merged = pd.merge(file1[[common_column, file1_column]],
                  file2[[common_column, file2_column]],
                  on=common_column,
                  how='inner')  # or 'left', 'right', 'outer' depending on what you want

# Save or display the result
print(merged)
merged.to_csv("merged_output.csv", index=False)
