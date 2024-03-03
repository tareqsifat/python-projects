from ftplib import FTP_TLS
from audio_split import *
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def ftp_download_split(delay = None, now = None):
    # Specify the desired directory
    desired_directory = os.getenv("FTP_DIRECTORY")

    # Create the directory if it doesn't exist
    if not os.path.exists(desired_directory):
        os.makedirs(desired_directory)

    # Define FTP server details
    ftp_host = os.getenv("FTP_HOST")
    ftp_port = int(os.getenv("FTP_PORT"))
    ftp_username = os.getenv("FTP_USERNAME")
    ftp_password = os.getenv("FTP_PASSWORD")
    # delay_hours = int(os.getenv("DELAY_HOURS"))
    delay_hours = delay


    # # Connect to the FTP server using FTP_TLS
    ftp = FTP_TLS()
    ftp.connect(ftp_host, ftp_port)
    ftp.login(ftp_username, ftp_password)
    ftp.prot_p()  # Enable secure data transfer

    # Define the remote file path on the FTP server
    # print(delay)
    # now = datetime.now()
    time = now - timedelta(hours = delay_hours)
    this_date = time.strftime("%Y%m%d")
    this_time = time.strftime("%H")
    remote_directory_path = f"/master_audios/{this_date}/{this_time}/"
    # remote_directory_path = f"/master_audios/20230618/{hour}"


    file_names = ftp.nlst(remote_directory_path)

    #save and split every audio file by loop
    if len(file_names) != 0:
        for file_name in file_names:
            
            local_file_path = os.path.join(desired_directory, os.path.basename(file_name)) # Adjust this line
            
            print(f"Downloading {file_name}...")
            with open(local_file_path, 'wb') as local_file:
                ftp.retrbinary('RETR ' + file_name, local_file.write)
                local_file_name = local_file.name
                print(f"{file_name} downloaded, saved and splitting")
                split_master_audio(local_file_name)


            print(f"{file_name} downloaded and slitted saved.")
            os.remove(f"{local_file_path}")

        print("All files have been downloaded and saved.")
    else:
        print("File Not found In FTP server")
        

    # Close the FTP connection
    ftp.quit()


if __name__ == "__main__":
    start_index = 117
    end_index = 105
    now = datetime.now()

    for x in range(start_index, end_index, -1):
        time = now - timedelta(hours = x)
        this_date = time.strftime("%Y%m%d")
        this_time = time.strftime("%H")
        print(f"date: {this_date}, time: {this_time}")
    for x in range(start_index, end_index, -1):
        hour = "{:02d}".format(int(x))
        ftp_download_split(x, now)
    # ftp_download_split(12)
