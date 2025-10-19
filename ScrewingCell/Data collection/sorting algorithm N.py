import os
import pandas as pd
import xml.etree.ElementTree as ET
import shutil
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






taskdata_dir = r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Task data"
intrinsic_dir = r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Intrinsic data"
extrinsic_dir = r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Extrinsic data"


# Input types of screwdrivings
miss = int(input("Type number of missing screws:"))
miss_s = []
no = int(input("Type the number of no-screws:"))
no_s = []
bent = int(input("Type number of out-of-plane screws:"))
bent_s = []

ut = int(input("Type number of under-tightened screws:"))
ut_s = []

# Loop through n times and get an input from the user each time
for i in range(miss):
    input_miss = input("Enter mising pins #" + str(i+1) + ": ")
    miss_s.append(input_miss)
    
for i in range(no):
    input_no = input("Enter no pins #" + str(i+1) + ": ")
    no_s.append(input_no)
    
for i in range(bent):
    input_bent = input("Enter bent pins #" + str(i+1) + ": ")
    bent_s.append(input_bent)
    

for i in range(ut):
    input_ut = input("Enter under-tightened pins #" + str(i+1) + ": ")
    ut_s.append(input_ut)

print(miss_s)
print(bent_s)

print(ut_s)

# Make sure 'N' folders exist
os.makedirs(r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Task data\N", exist_ok=True)
os.makedirs(r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Extrinsic data\N", exist_ok=True)
os.makedirs(r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Intrinsic data\N", exist_ok=True)

# Function that will move the files
def move_files(number_list, source_dir, dest_dir):
    files = os.listdir(source_dir)
    os.makedirs(dest_dir, exist_ok=True)  # Ensure destination folder exists
    for filename in files:
        for number in number_list:
            if filename.endswith(number + ".csv") or filename.endswith(number + ".wav"):
                src_path = os.path.join(source_dir, filename)
                dest_path = os.path.join(dest_dir, filename)
                shutil.move(src_path, dest_path)
                print(f"Moved {filename} to {dest_dir}")

#Task data
move_files(miss_s, taskdata_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Task data\M")
move_files(no_s, taskdata_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Task data\NS")
move_files(bent_s, taskdata_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Task data\B")

move_files(ut_s, taskdata_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Task data\UT")
files_t = os.listdir(taskdata_dir)
for filename in files_t:
    if "csv" in filename:
        # Construct the full paths for the source and destination files
        src_path_t = os.path.join(taskdata_dir, filename)
        dest_path_t = os.path.join(r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Task data\N", filename)
        # Move the good screw files to N
        shutil.move(src_path_t, dest_path_t)



#Extrinsic data
move_files(miss_s, extrinsic_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Extrinsic data\M")
move_files(no_s, extrinsic_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Extrinsic data\NS")
move_files(bent_s, extrinsic_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Extrinsic data\B")

move_files(ut_s, extrinsic_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Extrinsic data\UT")
files_e = os.listdir(extrinsic_dir)
for filename in files_e:
    if "wav" in filename:
        src_path_e = os.path.join(extrinsic_dir, filename)
        dest_path_e = os.path.join(r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Extrinsic data\N", filename)
        # Move the good screw files to N
        shutil.move(src_path_e, dest_path_e)



#Intrinsic data
move_files(miss_s, intrinsic_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Intrinsic data\M")
move_files(no_s, intrinsic_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Intrinsic data\NS")
move_files(bent_s, intrinsic_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Intrinsic data\B")

move_files(ut_s, intrinsic_dir, r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Intrinsic data\UT")
files_i = os.listdir(intrinsic_dir)
for filename in files_i:
    if "csv" in filename:
        src_path_i = os.path.join(intrinsic_dir, filename)
        dest_path_i = os.path.join(r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Intrinsic data\N", filename)
        # Move the good screw files to N
        shutil.move(src_path_i, dest_path_i)






