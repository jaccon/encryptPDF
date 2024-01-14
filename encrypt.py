import os
import shutil
import random
import string
import csv
from PyPDF2 import PdfReader, PdfWriter
import json
from datetime import datetime
from tqdm import tqdm

def load_setup(file_path):
    with open(file_path, 'r') as setup_file:
        setup = json.load(setup_file)
    return setup

def generate_random_password(length=4):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def encrypt_pdf(input_path, output_path, password, progress_bar):
    with open(input_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        pdf_writer = PdfWriter()

        pdf_writer.add_page(pdf_reader.pages[0])
        pdf_writer.encrypt(password)

        with open(output_path, 'wb') as encrypted_file:
            pdf_writer.write(encrypted_file)

    # Manually update tqdm progress bar for the password application
    progress_bar.update(1)

def process_pdfs_one_by_one(setup):
    input_dir = setup["input_directory"]
    output_dir = setup["output_directory"]
    password_length = setup["password_length"]

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # List all PDF files in the input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]
    total_files = len(pdf_files)

    # Create a reports directory
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    # Create a CSV file with a timestamped name
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    csv_filename = f"report-{timestamp}.csv"
    csv_filepath = os.path.join(reports_dir, csv_filename)

    with open(csv_filepath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Filename", "Password"])

        for pdf_file in pdf_files:
            input_path = os.path.join(input_dir, pdf_file)
            output_path = os.path.join(output_dir, pdf_file)
            password = generate_random_password(password_length)

            # Copy the PDF file to the "convert" directory
            shutil.copy(input_path, output_path)

            # Create tqdm progress bar for password application
            with tqdm(total=1, desc=f"Processing: {pdf_file}", unit="file", position=0, leave=True) as progress_bar:
                # Encrypt the PDF file in the "convert" directory
                encrypt_pdf(output_path, output_path, password, progress_bar)

            # Write filename and password to the CSV file
            csv_writer.writerow([pdf_file, password])

    return csv_filepath

def load_report(csv_filepath):
    with open(csv_filepath, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader)
        data = [row for row in csv_reader]
    return header, data

if __name__ == "__main__":
    setup = load_setup("setup.json")
    csv_filepath = process_pdfs_one_by_one(setup)
    
    header, data = load_report(csv_filepath)
    
    print("\nReport Header:", header)
    print("Report Data:")
    for row in data:
        print(row)
