import psutil

def list_external_usb_storage_devices():
    external_usb_storage_devices = []

    partitions = psutil.disk_partitions(all=True)
    for partition in partitions:
        if "usb" in partition.device.lower():
            external_usb_storage_devices.append(partition.device)

    return external_usb_storage_devices

if __name__ == "__main__":
    external_usb_storage_devices = list_external_usb_storage_devices()

    print("External USB Storage Devices:")
    for device in external_usb_storage_devices:
        print(f"  {device}")
