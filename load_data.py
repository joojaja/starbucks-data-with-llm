## Data Loading

# possible issues
# missing data or wrong data (string input, null input)
# inconsistent formatting (file format all in one column, encoding)

# Helper functions to validate the inputs

import pandas as pd
import csv

def clean_null_values(df):
    """
    Remove columns and rows with null values.
    - Drops columns where all values are null
    - Drops rows where any value is null
    """
    # Drop column if all values are null
    df.dropna(axis=1, how='all', inplace=True)
    
    # Drop row if one of the values is null
    df.dropna(inplace=True)
    
    return df

def strip_column_and_row_whitespace(df):
    """
    Strip whitespace from all column names and rows
    """
    df.columns = df.columns.str.strip() # strip column
    
    # Strip whitespace from row index only if it's a string index
    if df.index.dtype == 'object':
        df.index = df.index.str.strip()
    
    return df

def convert_to_numeric(df):
    """
    Convert all columns to numeric types.
    Drops rows containing string values that cannot be converted.
    """
    # Try to convert each column to numeric, mark non-numeric values as NaN
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Drop rows that now contain NaN (were strings)
    df.dropna(inplace=True)
    
    return df

def standardise_units_to_grams(df):
    """
    Convert columns ending with (kg) or (mg) to (g) with appropriate value conversions.
    - (kg) columns: multiply values by 1000
    - (mg) columns: divide values by 1000
    """
    new_columns = {}
    
    for col in df.columns:
        if col.endswith('(kg)'):
            # Convert kg to g (multiply by 1000)
            new_col_name = col[:-5]  # Remove (kg)
            df[col] = df[col] * 1000
            new_columns[col] = new_col_name
        elif col.endswith('(mg)'):
            # Convert mg to g (divide by 1000)
            new_col_name = col[:-5]  # Remove (mg)
            df[col] = df[col] / 1000
            new_columns[col] = new_col_name
        elif col.endswith('(g)'):
            # Remove (g) in name
            new_col_name = col[:-4]  # Remove (g)
            new_columns[col] = new_col_name
    
    # Rename the columns
    if new_columns:
        df.rename(columns=new_columns, inplace=True)
    
    return df

def detect_and_fix_single_column_csv(filepath):
    """
    Detect if CSV has all data in a single column (comma-separated within that column).
    If so, reparse it properly by splitting on commas.
    Returns a properly formatted DataFrame or None if file needs standard parsing.
    """
    try:
        with open(filepath, 'r', encoding='utf-16') as f:
            lines = f.readlines()
        if lines and lines[0].startswith(','):
            data = []
            for line in lines:
                line = line.strip()
                if line:
                    row = next(csv.reader([line]))
                    # Remove leading empty element
                    if row[0] == '':
                        row = row[1:]
                    data.append(row)
            if len(data) > 1:
                headers = data[0]
                rows = [x[1:] for x in data[1:]]
                index = [x[0].strip() for x in data[1:]]
                df = pd.DataFrame(rows, columns=headers, index=index)
                return df
        return None
        
    except Exception as e:
        # Ignore UTF-16 error
        if 'does not start with BOM' in str(e):
            return None
        else:
            print(f"Error parsing single column csv {filepath}: {e}")
            return None

def load_csv_file_into_dataframe(filepath):
    """
    Load a CSV file into a pandas DataFrame.
    Validation done:
        1. Detects and fixes CSV files with all data in a single column
        2. Handles missing or null values and drops bad rows/columns
        3. Strips whitespace from column names and row indices
        4. Converts all data to numeric and drops rows with non-numeric values
        5. Converts columns ending with (kg) or (mg) to (g) with value adjustments
        6. Add Fat-to-Protein Ratio computed per row
    """
    try:
        # First, check if this is a single-column CSV
        df = detect_and_fix_single_column_csv(filepath)
        
        # If not a single-column issue, load normally
        if df is None:
            df = pd.read_csv(filepath,
                            na_values=["NA", "", "-"], # these values are considered null
                            index_col=0,
                            encoding='utf-8')
        
        # Apply validations
        df = strip_column_and_row_whitespace(df)
        df = convert_to_numeric(df)
        df = clean_null_values(df)
        df = standardise_units_to_grams(df)

        # Calculate Fat-to-Protein Ratio column safely
        # Avoid division by zero: where protein == 0, set ratio to 0
        df['Fat-to-Protein Ratio'] = df.apply(
            lambda row: round(row['Fat'] / row['Protein'], 3) if row['Protein'] != 0 else 0,
            axis=1
        )

        return df
    
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None
