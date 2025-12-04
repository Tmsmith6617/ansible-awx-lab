#!/usr/bin/env python3
import os
import glob
import xml.etree.ElementTree as ET
import pandas as pd

# Change this if needed
XML_INPUT_DIR = "./scap_outputs"   # where your fetched XMLs live
OUTPUT_FILE = "scap_results.xlsx"

def parse_scap_xml(xml_file):
    """
    Parse a SCAP XCCDF result XML file.
    Returns a list of dicts: each dict = one Rule result.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # In SCAP XCCDF results, rule results are under nodes <Rule> or <TestResult>/<RuleResult>
    rows = []
    # Try generic way: find all <Rule> elements
    for rule in root.findall(".//Rule"):
        title = rule.findtext("title")
        result = rule.findtext("result")
        ident = rule.findtext("ident")
        # you can add more fields (severity, fixtext, etc.) if present in your XML
        rows.append({
            "Rule_Title": title,
            "Result": result,
            "CCE/ID": ident
        })
    return rows

def main():
    writer = pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl")

    xml_files = glob.glob(os.path.join(XML_INPUT_DIR, "*.xml"))
    if not xml_files:
        print("No XML files found in", XML_INPUT_DIR)
        return

    for xml_file in xml_files:
        hostname = os.path.basename(xml_file).replace(".xml", "")
        print("Processing:", hostname)
        rows = parse_scap_xml(xml_file)
        if not rows:
            print("  WARNING: no <Rule> entries parsed from", xml_file)
            continue
        df = pd.DataFrame(rows)
        # Excel sheet names max 31 chars
        sheet_name = hostname[:31]
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    writer.save()
    print("Wrote all results to", OUTPUT_FILE)

if __name__ == "__main__":
    main()
