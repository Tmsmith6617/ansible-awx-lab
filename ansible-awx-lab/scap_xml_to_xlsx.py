#!/usr/bin/env python3
import os
import glob
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# --------------------------
# Configurable variables
# --------------------------
XML_INPUT_DIR = "/home/awxuser/scap_outputs"   # folder where your SCAP XMLs are stored
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE = f"/home/awxuser/scap_results/scap_results_{TIMESTAMP}.xlsx"
# avoids overwriting previous runs

# --------------------------
# Functions
# --------------------------
def parse_scap_xml(xml_file):
    """
    Parse a SCAP XCCDF result XML file.
    Returns a list of dicts: each dict = one Rule result.
    """
    rows = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Generic find for all <Rule> elements
        for rule in root.findall(".//Rule"):
            title = rule.findtext("title", default="N/A")
            result = rule.findtext("result", default="N/A")
            ident = rule.findtext("ident", default="N/A")
            
            # Optional: add more fields if present in XML
            rows.append({
                "Rule_Title": title,
                "Result": result,
                "CCE/ID": ident,
                "Source_File": os.path.basename(xml_file)
            })
    except ET.ParseError:
        print(f"  ERROR: Failed to parse {xml_file}")
    return rows

# --------------------------
# Main execution
# --------------------------
def main():
    xml_files = glob.glob(os.path.join(XML_INPUT_DIR, "*.xml"))
    if not xml_files:
        print(f"No XML files found in {XML_INPUT_DIR}")
        return

    total_rules = 0
    total_hosts = 0

    # Use context manager for ExcelWriter so file is saved automatically
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        for xml_file in xml_files:
            hostname = os.path.basename(xml_file).replace(".xml", "")
            print(f"Processing host: {hostname}")

            rows = parse_scap_xml(xml_file)
            if not rows:
                print(f"  WARNING: No <Rule> entries parsed from {xml_file}")
                continue

            df = pd.DataFrame(rows)
            total_rules += len(df)
            total_hosts += 1
            # Excel sheet name max 31 chars
            sheet_name = hostname[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"\n✅ Finished processing {total_hosts} host(s), {total_rules} rules total")
    print(f"Results written to {OUTPUT_FILE}")

# --------------------------
if __name__ == "__main__":
    main()
