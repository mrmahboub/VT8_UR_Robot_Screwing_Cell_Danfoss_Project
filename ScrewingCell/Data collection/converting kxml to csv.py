import os
import pandas as pd
import xml.etree.ElementTree as ET
import datetime

# User input
wood = input("Wood number: ").zfill(3)  # Ensure 3-digit wood number

# Date for filename
today = datetime.date.today().strftime('%d%m%Y')

# Paths
input_folder_KXML = r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Intrinsic data\KXML"
output_folder_CSV = r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Intrinsic data"

# Counter for filenames
counter = 0

for filename in sorted(os.listdir(input_folder_KXML)):
    if filename.lower().endswith(".kxml"):
        try:
            file_path = os.path.join(input_folder_KXML, filename)
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Header
            version = root.find('Wsk3Header/Version').text
            date_xml = root.find('Wsk3Header/Date').text
            time_xml = root.find('Wsk3Header/Time').text
            title = root.find('Wsk3Header/Title').text
            num_y_axes = int(root.find('Wsk3Header/NumberofYAxes').text)

            # X-axis
            x_axis = root.find('Wsk3Vectors/X_Axis')
            x_values = [float(x.text) for x in x_axis.find('Values').iter('float')]

            # Y-axis
            y_axes = root.find('Wsk3Vectors/Y_AxesList')
            y_data = {}
            for axis in y_axes.iter('AxisData'):
                y_index = int(axis.find('_Index').text)
                y_name = axis.find('Header/Name').text
                y_unit = axis.find('Header/Unit').text
                y_values = [float(x.text) for x in axis.find('Values').iter('float')]
                y_data[y_index] = {'name': y_name, 'unit': y_unit, 'values': y_values}

            # DataFrame
            data = {'Time (ms)': x_values}
            for i in range(num_y_axes):
                col_name = f"{y_data[i]['name']} ({y_data[i]['unit']})"
                data[col_name] = y_data[i]['values']
            df = pd.DataFrame(data)

            # File naming: i{date}{wood}{counter:03}.csv
            output_filename = f"i{today}{wood}{counter:03}.csv"
            output_path = os.path.join(output_folder_CSV, output_filename)
            df.to_csv(output_path, index=False)

            print(f"✔ Converted {filename} → {output_filename} | Title: {title}, Time: {time_xml}")
            counter += 1

        except Exception as e:
            print(f"⚠ Error converting {filename}: {e}")
