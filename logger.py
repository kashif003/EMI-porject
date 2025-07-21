 

import asyncio
import os
from bleak import BleakClient, BleakScanner
import pandas as pd
from datetime import datetime



# UUIDs for service and characteristic
SERVICE_UUID = "19077010-1234-5678-1234-56789abcdef0"
CHAR_UUID = "fedcba01-1234-5678-1234-56789abcdef0"

data_log = []

# Store RSSI values for all scanned devices
rssi_dict = {}

# Callback when data is received
def notification_handler(sender, data):
    try:
        line = data.decode("utf-8").strip()
        print("Received:", line)
        parts = line.split(",")

        if len(parts) == 14:
            entry = {
                "Time1": int(parts[0]),
                "sequence": int(parts[1]),
                "acc_x": float(parts[3]),
                "acc_y": float(parts[4]),
                "acc_z": float(parts[5]),
                "gyro_x": float(parts[7]),
                "gyro_y": float(parts[8]),
                "gyro_z": float(parts[9]),
                "mag_x": float(parts[11]),
                "mag_y": float(parts[12]),
                "mag_z": float(parts[13]),
            }

            # Include RSSI values from nearby beacons
            for device_name, rssi in rssi_dict.items():
                entry[f"{device_name}_rssi"] = rssi

            data_log.append(entry)
    except Exception as e:
        print("Error decoding data:", e)

# Main BLE task
async def run():
    global rssi_dict
    print("Scanning for devices...")
    devices = await BleakScanner.discover()

    target_device = None
    for d in devices:
        print(f"Device found: {d.address}, Name: {d.name}, RSSI: {d.rssi}")
        name = d.name or f"Unknown_{d.address[-4:]}"
        rssi_dict[name] = d.rssi

        if d.name and "Nitesh_Nano33BLE_IMU" in d.name:
            target_device = d

    if not target_device:
        print("Target IMU device not found!")
        return

    print(f"Connecting to {target_device.name}")
    async with BleakClient(target_device.address) as client:
        await client.start_notify(CHAR_UUID, notification_handler)

        print("Receiving data... Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopped by user.")
        finally:
            parent_directory = r"C:\Users\Nitesh Morem\OneDrive\Desktop\3rd-sem\EMBEDDED INTELLIGENCE\Task5"
            filename = f"imu_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = os.path.join(parent_directory, filename)

            print(f"Saving data to: {file_path}")
            df = pd.DataFrame(data_log)
            df.to_csv(file_path, index=False)
            print(f"Saved {len(data_log)} entries to {file_path}")

# Run it
asyncio.run(run())
