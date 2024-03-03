import os

# Define the output directory
output_directory = '/tmp/text_save'

# Check if the directory exists
if not os.path.exists(output_directory):
    # If it doesn't exist, create it
    os.makedirs(output_directory)

# Define the content to be written (100MB of '0' and space)
content = '0' * 100000000  # 100MB of '0'
content += ' ' * (100000000 - 1)  # Add a space at the end to make it 100MB

# Create 100 files with the specified content
for i in range(1, 101):
    file_name = f'{output_directory}/file_{i}.txt'
    print(file_name)
    with open(file_name, 'w') as file:
        file.write(content)

print("100 text files created and saved to", output_directory)
