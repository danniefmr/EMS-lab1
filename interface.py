from tkinter import *
import serial
import threading
import time

def button_relay(relay_btn):
    global relay
    # Only allow manual control if auto control is disabled
    if not auto_control_var.get():
        if relay == "OFF":
            relay = "ON"
            relay_btn.config(text="Relay ON", bg="green", fg="white")
        else:
            relay = "OFF"
            relay_btn.config(text="Relay OFF", bg="red", fg="white")
        
        send_relay_command()
        print("Manual relay control:", relay)
    else:
        print("Manual control disabled - Auto control active")

def send_relay_command():
    if ser and ser.is_open:
        ser.write((relay + '\n').encode('utf-8'))
    else:
        print("Serial port not available")

def auto_relay_control(ds18b20_temp):
    global relay
    
    if not auto_control_var.get():
        return 
    
    try:
        threshold = float(threshold_entry.get())
        
        if ds18b20_temp > threshold:
            if relay != "OFF":
                relay = "OFF"
                relay_btn.config(text="Relay OFF (Auto)", bg="red", fg="white")
                send_relay_command()
                print(f"Auto control: Temperature {ds18b20_temp}°C > {threshold}°C - Relay OFF")
        else:
            if relay != "ON":
                relay = "ON"
                relay_btn.config(text="Relay ON (Auto)", bg="green", fg="white")
                send_relay_command()
                print(f"Auto control: Temperature {ds18b20_temp}°C <= {threshold}°C - Relay ON")
                
    except ValueError:
        print("Invalid threshold value")

SERIAL_PORT = 'COM5'
BAUD_RATE = 115200

ser = serial.Serial()
ser.port = SERIAL_PORT
ser.baudrate = BAUD_RATE
ser.timeout = 1
relay = "OFF"

try:
    ser.open()
    print(f"Serial port {SERIAL_PORT} opened successfully")
except Exception as e:
    print(f"Failed to open serial port {SERIAL_PORT}: {e}")
    ser = None

root = Tk()
root.title("Temperature Sensors")

labelsT = {
"NTC-Temp": Label(root, text="NTC Temperature:", font=("Arial", 14)),
"LM35-Temp": Label(root, text="LM35 Temperature:", font=("Arial", 14)),
"DS18B20-Temp": Label(root, text="DS18B20 Temperature:", font=("Arial", 14))
}

valuesT = {
"NTC-Temp": Label(root, text="-- °C", font=("Arial", 16), fg="blue"),
"LM35-Temp": Label(root, text="-- °C", font=("Arial", 16), fg="blue"),
"DS18B20-Temp": Label(root, text="-- °C", font=("Arial", 16), fg="blue")
}

labelsV = {
"NTC-Volt": Label(root, text="NTC Voltage:", font=("Arial", 14)),
"LM35-Volt": Label(root, text="LM35 Voltage:", font=("Arial", 14)),
}

valuesV = {
"NTC-Volt": Label(root, text="-- V", font=("Arial", 16), fg="blue"),
"LM35-Volt": Label(root, text="-- V", font=("Arial", 16), fg="blue"),
}


labelsT["NTC-Temp"].grid(row=0, column=0, padx=10, pady=5, sticky="w")
valuesT["NTC-Temp"].grid(row=0, column=1, padx=10, pady=5, sticky="w")
labelsV["NTC-Volt"].grid(row=0, column=2, padx=10, pady=5, sticky="w")
valuesV["NTC-Volt"].grid(row=0, column=3, padx=10, pady=5, sticky="w")

labelsT["LM35-Temp"].grid(row=1, column=0, padx=10, pady=5, sticky="w")
valuesT["LM35-Temp"].grid(row=1, column=1, padx=10, pady=5, sticky="w")
labelsV["LM35-Volt"].grid(row=1, column=2, padx=10, pady=5, sticky="w")
valuesV["LM35-Volt"].grid(row=1, column=3, padx=10, pady=5, sticky="w")

labelsT["DS18B20-Temp"].grid(row=2, column=0, padx=10, pady=5, sticky="w")
valuesT["DS18B20-Temp"].grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Add temperature threshold input
threshold_label = Label(root, text="Temperature Threshold:", font=("Arial", 14))
threshold_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

threshold_entry = Entry(root, font=("Arial", 14), width=10)
threshold_entry.insert(0, "30.0")  # Default threshold
threshold_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

threshold_unit = Label(root, text="°C", font=("Arial", 14))
threshold_unit.grid(row=3, column=2, padx=5, pady=5, sticky="w")

# Add auto control checkbox
auto_control_var = BooleanVar()
auto_control_checkbox = Checkbutton(root, text="Auto Relay Control", font=("Arial", 12), 
                                   variable=auto_control_var)
auto_control_checkbox.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")


relay_btn = Button(root, text="Relay OFF", padx=10, pady=5, bg="red", fg="white", command=lambda:button_relay(relay_btn))
relay_btn.grid(row=5, column=0, padx=10, pady=5, columnspan=4)


def read_raspberry():
    while True:
        try:
            if ser and ser.is_open:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    # Check if it's sensor data (comma-separated values)
                    if ',' in line:
                        parts = line.split(',')
                        if len(parts) == 5:  # Expected: ntc_temp, ntc_volt, lm35_temp, lm35_volt, ds18b20_temp
                            valuesT["NTC-Temp"].config(text=f"{parts[0]} °C")
                            valuesV["NTC-Volt"].config(text=f"{parts[1]} V")
                            valuesT["LM35-Temp"].config(text=f"{parts[2]} °C")
                            valuesV["LM35-Volt"].config(text=f"{parts[3]} V")
                            valuesT["DS18B20-Temp"].config(text=f"{parts[4]} °C")
                            
                            # Automatic relay control based on DS18B20 temperature
                            try:
                                ds18b20_temp = float(parts[4])
                                auto_relay_control(ds18b20_temp)
                            except ValueError:
                                pass  # Invalid temperature value
                    # Check if it's a relay confirmation message
                    elif line.startswith("Relay:"):
                        print(f"Arduino confirmed: {line}")
        except Exception as e:
            print(f"Serial read error: {e}")
        time.sleep(0.1)  # Reduced delay for more responsive reading

# Run serial reading in background
thread = threading.Thread(target=read_raspberry, daemon=True)
thread.start()

root.mainloop()
  

    