import pandas as pd
from datetime import datetime
from numpy import uint
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import struct
import math
import os, time
import snap7
from snap7 import util
from snap7.types import *
from snap7.util import *
import pyaudio
import wave
import threading
import time

wood = input("Enter wood number: ")
today = datetime.today().strftime('%d%m%Y')




# Function that provides the signal for the start of the screwdriving and connects to modbus_______________

def PLCsignal(db_number, start_offset, bit_offset):
    reading = client.db_read(db_number, start_offset, 1)
    a = snap7.util.get_bool(reading, 0, bit_offset)
    #print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
    return a

try:
    client = snap7.client.Client()
    client.connect('172.20.1.148', 0, 1)
    db_number = 19
    start_offset = 0
    bit_offset = 0

    if client.get_connected():
        print("Connected to PLC")
    else:
        print("Could not connect to PLC (get_connected returned False)")

except Exception as e:
    print("Error while connecting to PLC:", e)




#_________________________________________________________________________________________________________


class ModbusReader(threading.Thread):
    def __init__(self, host, port, registers):
        threading.Thread.__init__(self)
        self.daemon = True
        self.c = ModbusClient(host=host, port=port, auto_open=True, debug=False)
        self.registers = registers
        self.register_values = {}

    def run(self):
        while True:
            try:
                # Read the values of the specified registers from the UR10
                reg_TCP_x = self.c.read_holding_registers(self.registers['TCP_x'])
                reg_TCP_y = self.c.read_holding_registers(self.registers['TCP_y'])
                reg_TCP_z = self.c.read_holding_registers(self.registers['TCP_z'])
                reg_TCP_rx = self.c.read_holding_registers(self.registers['TCP_rx'])
                reg_TCP_ry = self.c.read_holding_registers(self.registers['TCP_ry'])
                reg_TCP_rz = self.c.read_holding_registers(self.registers['TCP_rz'])
                reg_Robot_I = self.c.read_holding_registers(self.registers['Robot_I'])

                # Store the register values in a dictionary
                self.register_values = {
                    'TCP_x': reg_TCP_x[0],
                    'TCP_y': reg_TCP_y[0],
                    'TCP_z': reg_TCP_z[0],
                    'TCP_rx': reg_TCP_rx[0],
                    'TCP_ry': reg_TCP_ry[0],
                    'TCP_rz': reg_TCP_rz[0],
                    'Robot_I': reg_Robot_I[0]
                }
            except:
                print("Error reading register values")


    def get_register_values(self):
        return self.register_values

# Connect to Modbus
try:
    c = ModbusClient(host='172.20.1.50', port=502, auto_open=True, debug=False)
    print("connected",c.open())
except ValueError:
    print("Error with host or port params")

# Setting up the task data parameters
registers = {
    'TCP_x': 400,
    'TCP_y': 401,
    'TCP_z': 402,
    'TCP_rx': 403,
    'TCP_ry': 404,
    'TCP_rz': 405,
    'Robot_I': 450
}

# Create a ModbusReader thread and start it
modbus_reader = ModbusReader('172.20.1.50', 502, registers)
modbus_reader.start()





# Initialize the dataframe
df = pd.DataFrame(columns=['Time', 'TCP_x', 'TCP_y', 'TCP_z', 'TCP_rx', 'TCP_ry', 'TCP_rz', 'Robot_I'])

#function for unsigned integers
def unsigned(a):
    if a > 32767:
        a = a - 65535
    else:
        a = a
    return a
#_______________________________________________________________________________________

""" Setting up the microphone recording class as a thread.
    It will run in the background, during the data collection.
"""


class SoundRecorderThread(threading.Thread):
    def __init__(self):
        # Call the constructor of the parent class (threading.Thread)
        threading.Thread.__init__(self)
        
        # Initialize some default parameters for recording audio
        self.frames = []
        self.should_stop = False
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100

    def run(self):
        audio = pyaudio.PyAudio()
        # Open a stream for recording audio with the default input device
        stream = audio.open(format=self.FORMAT, channels=self.CHANNELS,
                            rate=self.RATE, input=True,
                            frames_per_buffer=self.CHUNK)
        # Continuously read audio data from the stream and append it to self.frames
        while not self.should_stop:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            
        # Stop the stream and close it
        stream.stop_stream()
        stream.close()
        audio.terminate()

    # Set the should_stop flag to True, which will cause the recording loop to exit
    def stop_recording(self):
        self.should_stop = True

    # Return the list of recorded audio frames
    def get_frames(self):
        return self.frames

# Function that saves recordings
def save_recording(frames, filename):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))



#________________________________________________________________________________________
"""
Main loop that monitors the PLC signal and decides when will the data be recorded and where will it be saved.
"""

# Set the desired recording frequency
desired_frequency = 400  # 400 ms
desired_period = desired_frequency / 1000  # Convert to seconds


# Set up the variables for the sound recording
recorder = None
frames = []

# Set up the variables for the PLC signal monitoring
flag = False
counter = 0
directory = os.path.expanduser(r'C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Extrinsic data')
    
# Start the main loop
while True:
    
    start_time_loop = time.time()
    register_values = modbus_reader.get_register_values()
    # Check the PLC signal
    result = PLCsignal(db_number, start_offset, bit_offset)

    # If the function returns True, set the flag to True and start recording
    if result and not flag:
        print("Recording started")
        flag = True
        start_time = datetime.now()
        #For recording task data
        data = []
        
        #Recording audio
        recorder = SoundRecorderThread()
        recorder.start()

    # If the flag is True, record audio until the PLC signal goes back to False
    if flag:
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).total_seconds() * 1000
        data.append([elapsed_time, register_values['TCP_x'], register_values['TCP_y'], register_values['TCP_z'], register_values['TCP_rx'], register_values['TCP_ry'], register_values['TCP_rz'], register_values['Robot_I']])
        
        # If the PLC signal is False or if the recording has reached its maximum duration, stop recording
        if not result:
            flag = False
            print("Recording stopped")
            

            
            
            df = pd.DataFrame(data=data, columns=['Time', 'TCP_x', 'TCP_y', 'TCP_z','TCP_rx', 'TCP_ry', 'TCP_rz', 'Robot_I'])
            df = df.applymap(unsigned)
            df[['TCP_x', 'TCP_y', 'TCP_z']] = df[['TCP_x', 'TCP_y', 'TCP_z']] / 10
            df[['TCP_rx', 'TCP_ry', 'TCP_rz', 'Robot_I']] = df[['TCP_rx', 'TCP_ry', 'TCP_rz', 'Robot_I']] / 1000
            df = df.rename(columns={'Time': 'Time (ms)', 'TCP_x': 'TCP_x (mm)', 'TCP_y': 'TCP_y (mm)', 'TCP_z': 'TCP_z (mm)', 'TCP_rx': 'TCP_rx (mm)', 'TCP_ry': 'TCP_ry (mm)', 'TCP_rz': 'TCP_rz (mm)', 'Robot_I': 'Robot_I (A)'})

            sf = len(df.index)/int(elapsed_time/1000)
            print("Sampling frequency is:", round(sf),"Hz")
            print(elapsed_time)
            print(len(df.index))
            print(df)
            filename_t = os.path.join(r'C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Screwcell dataset\Task data', f"t{today}{wood}{counter:03}.csv")
            df.to_csv(filename_t, index=False)
            
            
            recorder.stop_recording()
            frames = recorder.get_frames()

            # Save the recorded audio as a WAV file
            filename = os.path.join(directory, f"e{today}{wood}{counter:03}.wav")
            save_recording(frames, filename)

            counter += 1
        

            




    
    
    


