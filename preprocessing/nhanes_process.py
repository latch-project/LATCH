import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import tempfile
import os
import requests
import pyreadstat
import io
from tqdm import tqdm
from sqlalchemy import create_engine, text
import sys
from pathlib import Path

import sys
from pathlib import Path

# sys.path.append(str(Path.cwd().parents[0]))
sys.path.append(str(Path.cwd()))
from config import other_config, data_config, config


def get_unique_file_year_combinations(
    df, file_col="Data File Name", year_col="Begin Year"
):
    """
    Extracts unique combinations of 'Data File Name' and 'BEgin Year' from a pandas DataFrame.

    Args:
      df: pandas DataFrame containing the data.
      file_col: Name of the column containing file names. Defaults to 'Data File Name'.
      year_col: Name of the column containing years. Defaults to 'BEgin Year'.

    Returns:
      pandas DataFrame with unique combinations of file names and years.
    """

    if file_col not in df.columns or year_col not in df.columns:
        raise ValueError(
            f"Columns '{file_col}' and '{year_col}' must be present in the DataFrame."
        )

    unique_combinations = df[[file_col, year_col]].drop_duplicates()
    return unique_combinations


def get_all_variables(component: "str"):
    base_url = "https://wwwn.cdc.gov"
    varlist_url = f"https://wwwn.cdc.gov/nchs/nhanes/search/variablelist.aspx?Component={component}&Cycle="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    r = requests.get(varlist_url, headers=headers)
    if not r.ok:
        print("Failed to get variable list page")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", id="GridView1")
    if not table:
        print("Variable table not found")
        return None

    df = pd.read_html(io.StringIO(str(table)))[0]
    return df


def get_all_tables(component: "str"):
    base_url = "https://wwwn.cdc.gov"
    varlist_url = (
        f"https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component={component}"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    r = requests.get(varlist_url, headers=headers)
    if not r.ok:
        print("Failed to get variable list page")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", id="GridView1")
    if not table:
        print("Variable table not found")
        return None

    df = pd.read_html(io.StringIO(str(table)))[0]
    return df


def nhanes_codebook_from_url(url):
    """
    Download and parse NHANES codebook from a full documentation URL.
    Returns a dict with variable names as keys and codebook entries as values.
    """
    if not isinstance(url, str):
        raise ValueError("'url' must be a string")

    # Fix relative paths
    if url.lower().startswith("/nchs/"):
        url = "https://wwwn.cdc.gov" + url

    soup = fetch_html(url)
    if soup is None:
        raise Exception(f"Could not find a web page at: {url}")

    try:
        var_info = get_var_names(soup)
        colnames = var_info.get("VarNames", [])
    except Exception as e:
        # print(f"Error parsing variable names: {e}")
        print("")
        return None

    if not colnames:
        print("No variables found on page.")
        return None

    result = {}
    for var in colnames:
        codebook = codebook_helper(var, soup)
        if codebook:
            result[var] = codebook

    return result if result else None


def get_var_names(doc):
    var_names = []
    var_descs = []

    # Try Codebook TOC list approach first
    codebook_section = None
    for tag in doc.find_all(True):  # all tags
        if tag.name and tag.get_text(strip=True).lower().find("codebook") != -1:
            codebook_section = tag
            break

    if codebook_section:
        li_tags = codebook_section.find_all("li")
        for li in li_tags:
            text = li.get_text(strip=True)
            parts = text.split(" - ", 1)
            if len(parts) == 2:
                var_names.append(parts[0].strip())
                var_descs.append(parts[1].strip())

    # Fallback: scan for <h3><a name="..."> blocks
    if not var_names:
        h3_tags = doc.find_all("h3")
        for h3 in h3_tags:
            a = h3.find("a")
            if a and a.has_attr("name"):
                full_text = h3.get_text(strip=True)
                parts = full_text.split(" - ", 1)
                if len(parts) == 2:
                    var_names.append(parts[0].strip())
                    var_descs.append(parts[1].strip())

    return {"VarNames": var_names, "VarDesc": var_descs}


def fetch_html(url):
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None
        return BeautifulSoup(res.content, "html.parser")
    except Exception:
        return None


def codebook_helper(colname, soup):
    """
    Extract variable codebook section for a given column name from HTML soup.
    Tries to handle CDC's inconsistent capitalization in variable anchors.
    """
    if soup is None:
        return None

    section = test_locations(colname, soup)

    # Try common capitalization variants
    if section is None:
        name_parts = list(colname)
        upper_flags = [c.isupper() for c in name_parts]
        nc = len(name_parts)

        lcnm = colname

        # Lowercase last char
        if nc > 0 and upper_flags[-1]:
            lcnm = colname[:-1] + colname[-1].lower()
            section = test_locations(lcnm, soup)

        # Lowercase second to last if still not found
        if section is None and nc > 1 and upper_flags[-2]:
            lcnm = colname[:-2] + colname[-2].lower() + colname[-1]
            section = test_locations(lcnm, soup)

        # Try second last lower, last upper combo
        if section is None and nc > 1 and not upper_flags[-2]:
            lcnm = colname[:-1] + colname[-1].upper()
            section = test_locations(lcnm, soup)

    # If still nothing, return None
    if section is None:
        # print(f'Warning: Column "{colname}" not found in HTML.')
        return None

    # Extract description fields from <dl>
    desc = {}
    entry = section.find_next_sibling("dl")
    if entry:
        dts = entry.find_all("dt")
        dds = entry.find_all("dd")
        for dt, dd in zip(dts, dds):
            desc[dt.get_text(strip=True)] = dd.get_text(strip=True)

    # Extract value mappings from <table>
    table = section.find_next("table")
    if table:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        rows = []
        for tr in table.find_all("tr")[1:]:
            tds = tr.find_all("td")
            row = [td.get_text(strip=True) for td in tds]
            if row:
                rows.append(dict(zip(headers, row)))
        if rows:
            desc["values"] = rows

    return desc if desc else None


def test_locations(colname, soup):
    """
    Try to locate the section in the HTML for the given variable name.
    """
    # Try to find <h3><a name="...">
    section = soup.find("a", attrs={"name": colname})
    if section:
        return section.find_parent("h3")

    # Fallback: try <h3 id="...">
    section = soup.find("h3", attrs={"id": colname})
    if section:
        return section

    return None


def nhanes_from_url(
    url,
    translated=True,
    cleanse_numeric=False,
    nchar=128,
    includelabels=False,
    adjust_timeout=True,
):
    """Download NHANES .XPT table and return as a DataFrame."""
    try:
        timeout = estimate_timeout(url, factor=adjust_timeout)
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        df = pd.read_sas(io.BytesIO(response.content), format="xport")
        return df

    except Exception as e:
        print("")
        # print(f"Error downloading {url}: {e}")
        return None


def estimate_timeout(url, factor=True):
    """
    Estimate timeout duration based on file size.

    Args:
        url (str): URL to request.
        factor (bool or float): If True, use default multiplier;
                                if a number, use it as a multiplier.
    Returns:
        int: Estimated timeout in seconds.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        size = int(response.headers.get("Content-Length", 0))  # in bytes
        base_timeout = 30  # default fallback

        if factor is True:
            multiplier = 0.00001  # 10 seconds per MB
        elif isinstance(factor, (int, float)):
            multiplier = factor
        else:
            multiplier = 0.00001

        estimated = int(size * multiplier)
        return max(base_timeout, estimated)

    except Exception:
        return 60  # Fallback if estimation fails


def count_xpt_files(category):
    url = f"https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component={category}"
    """Counts the number of .XPT files on an NHANES data page."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        soup = BeautifulSoup(response.content, "html.parser")

        links = soup.find_all("a")

        xpt_count = 0
        for link in links:
            href = link.get("href")
            if href and href.lower().endswith(".xpt"):
                xpt_count += 1

        return xpt_count

    except requests.exceptions.RequestException as e:
        print("")
        # print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print("")
        # print(f"An unexpected error occurred: {e}")
        return None


import pandas as pd
from tqdm import tqdm


def check_nhanes_files_from_tablename_year(df):
    """
    Checks the existence of codebook and data files for each row in the DataFrame and
    returns separate counts and lists of URLs that caused errors for codebooks and data.

    Args:
        df (pd.DataFrame): DataFrame containing 'Data File Name' and 'Begin Year' columns.
        nhanes_codebook_from_url (function): Function to retrieve codebook from URL.
        nhanes_from_url (function): Function to retrieve data DataFrame from URL.

    Returns:
        tuple: A tuple containing:
            - codebook_error_count (int): Number of codebook errors.
            - codebook_error_urls (list): List of codebook error URLs.
            - data_error_count (int): Number of data errors.
            - data_error_urls (list): List of data error URLs.
    """
    codebook_error_count = 0
    codebook_error_urls = []
    data_error_count = 0
    data_error_urls = []

    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        file_name = row["Data File Name"]
        year = row["Begin Year"]

        codebookurl = f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{year}/DataFiles/{file_name}.htm"
        dataurl = f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{year}/DataFiles/{file_name}.XPT"

        codebook_exists = True
        data_exists = True

        try:
            codebook = nhanes_codebook_from_url(codebookurl)
            if codebook is None:
                print("")
                # print(f"Codebook URL exists, but returned None: {codebookurl}")
                codebook_exists = False
                codebook_error_urls.append(codebookurl)
                codebook_error_count += 1
        except Exception as e:
            print("")
            # print(f"Codebook URL does not exist or error: {codebookurl}, {e}")
            codebook_exists = False
            codebook_error_urls.append(codebookurl)
            codebook_error_count += 1

        try:
            data_df = nhanes_from_url(dataurl)
            if data_df is None:
                print("")
                # print(f"Data URL exists, but returned None: {dataurl}")
                data_exists = False
                data_error_urls.append(dataurl)
                data_error_count += 1
        except Exception as e:
            print("")
            # print(f"Data URL does not exist or error: {dataurl}, {e}")
            data_exists = False
            data_error_urls.append(dataurl)
            data_error_count += 1

        if not codebook_exists or not data_exists:
            print("One or more files do not exist.")
            print("-" * 20)
        else:
            print("-" * 20)

    return codebook_error_count, codebook_error_urls, data_error_count, data_error_urls


db_config = {
    "database": config.DB_NAME,
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "port": config.DB_PORT,
}


def create_db_engine(db_config):
    user = db_config.get("user", "")
    password = db_config.get("password")
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 5432)
    database = db_config.get("database", "")

    auth = user
    if password is not None:
        auth += f":{password}"
    conn_str = f"postgresql+psycopg2://{auth}@{host}:{port}/{database}"
    return create_engine(conn_str)


from sqlalchemy import text
import pandas as pd


def extract_schema_and_samples(engine, table, schema_name):
    schema_data = []

    with engine.connect() as connection:
        try:
            # Get column names and data types
            columns_query = text(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = :schema 
                AND table_name = :table
                """
            )
            columns_info = connection.execute(
                columns_query, {"schema": schema_name, "table": table}
            ).fetchall()

            # Structure the data
            table_schema = {"table": f"{schema_name}.{table}", "columns": {}}

            for col_name, col_type in columns_info:
                # Get up to 10 distinct non-null values from the column
                sample_values_query = text(
                    f"""
                SELECT DISTINCT "{col_name}"
                FROM {schema_name}.{table}
                WHERE "{col_name}" IS NOT NULL
                LIMIT 20
                """
                )
                try:
                    sample_values = [
                        str(row[0])
                        for row in connection.execute(sample_values_query).fetchall()
                    ]
                except Exception as e:
                    sample_values = [f"[Error: {e}]"]
                    print("")
                    # print(
                    #     f"Error fetching sample values for column '{col_name}' in table '{table}': {e}"
                    # )

                # Pad to exactly 10 items if needed
                while len(sample_values) < 10:
                    sample_values.append("")

                table_schema["columns"][col_name] = {
                    "data_type": col_type,
                    "sample_values": sample_values,
                }

            schema_data.append(table_schema)

        except Exception as e:
            print("")
            # print(f"Error processing table {table}: {e}")

    return schema_data


def april_3_save_extract_schema_and_samples(engine, table, schema_name):
    schema_data = []

    with engine.connect() as connection:
        try:
            # Get column names and data types
            columns_query = text(
                f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = :schema 
                AND table_name = :table
            """
            )
            columns_info = connection.execute(
                columns_query, {"schema": schema_name, "table": table}
            ).fetchall()

            # Get up to 10 random sample rows
            sample_query = text(
                f"SELECT * FROM {schema_name}.{table} ORDER BY RANDOM() LIMIT 10"
            )
            rows_df = pd.read_sql(sample_query, connection)

            # Structure the data
            table_schema = {"table": f"{schema_name}.{table}", "columns": {}}

            for col_name, col_type in columns_info:
                non_null_values = (
                    rows_df[col_name].dropna().astype(str).unique().tolist()
                )

                # Get up to 5 unique sample values
                sample_values = non_null_values[:5]

                # Pad with empty strings if fewer than 5
                while len(sample_values) < 5:
                    sample_values.append("")

                table_schema["columns"][col_name] = {
                    "data_type": col_type,
                    "sample_values": sample_values,
                }

            schema_data.append(table_schema)
        except Exception as e:
            print("")
            # print(f"Error processing table {table}: {e}")

    return schema_data
