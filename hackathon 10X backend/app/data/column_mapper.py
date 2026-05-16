import pandas as pd

def normalize_glid_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes variations of GLID column names to 'glusr_usr_id'.
    """
    glid_variants = ['glid', 'seller_id', 'fk_glusr_usr_id', 'GluserId']
    
    # Check if any variant exists and rename it
    for col in glid_variants:
        if col in df.columns:
            df.rename(columns={col: 'glusr_usr_id'}, inplace=True)
            break # Assume only one variant per file
            
    return df
