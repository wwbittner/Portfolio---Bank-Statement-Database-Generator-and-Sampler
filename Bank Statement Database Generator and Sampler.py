###
# SET-UP
###


import pandas as pd #Used to interact with spreadsheets
from pdf2image import convert_from_path #Used to turn our pdfs into images so the OCR system can read them
import pytesseract  #OCR (occular character recognition) system, used to "read" text in images and turn them into regular text
import re   #Used for clean-up of text
import cv2  #Used in OCR
import numpy as np  #Used in OCR
from tkinter import *   #Used to build UI
from tkinter import ttk, filedialog #Used for the file upload function
import os   #Used for file access
import random #Used for random sampling

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" #Loads Pytesseract, our OCR tool

root = Tk() #Creates the root of our app UI
root.title("PDF Transaction Extractor")
root.geometry("1000x700")
root.configure(bg="light blue")

blue_style = ttk.Style()    #Creates the blue color scheme that I use for the app UI
blue_style.configure("Blue.TFrame", background = "light blue")

main_frame = ttk.Frame(root, padding=10, style="Blue.TFrame")   #Creates the main frame where all the UI shows up
main_frame.grid()

display_frame = ttk.Frame(main_frame, padding=10, style="Blue.TFrame")  #Creates a display frame where we actually put stuff
display_frame.grid()

#Creates messages to pop up when the user generates a spreadsheet or samples from it
process_complete_message = ttk.Label(display_frame, text="Sent to transactions.xlsx\n\nWarning: Dates may be changed\nto the current year,\nso be sure to check them." )
sample_complete_message = ttk.Label(display_frame, text="Sent to PCard Sample.xlsx\n\nWarning: Dates may be changed\nto the current year,\nso be sure to check them.")
process_complete_message.grid(column=5, row=1, padx=10)
process_complete_message.grid_remove()
sample_complete_message.grid(column=5, row=7, padx=10)
sample_complete_message.grid_remove()

#Creates tracker so the user knows what pdf is being processed at any given time
progress_label = ttk.Label(display_frame, text="", style="Blue.TFrame")
progress_label.grid(column=5, row=2, padx=10, sticky=W)

#Creates a frame below the display frame where I put the instructions to use the app
instructions_frame = ttk.Frame(root)
instructions_frame.grid(row=1)
instructions = ttk.Label(instructions_frame, text="How to use this app:\n" \
"1. In MAGIC, download the UMB bank statement for each line item in the PCard Contractual and PCard Commodities categories.\n" \
"2. Upload each bank statement using the 'Browse' button.\n" \
"3. Write the document number (found on MAGIC) next to each pdf.\n" \
"4. Click 'Process PDFs.' A spreadsheet called 'transactions.xsls' will be automatically created.\n" \
"5. Open transactions.xlsx. Make sure the information is correct, then paste the data from the US Bank statement spreadsheet below the UMB bank statement data.\nUse the Transaction ID in place of the Document ID. Some columns might be empty - that's ok.\n" \
"6. Type the number of rows you want to sample, then hit 'Sample from PDF.'\n" \
"7. Your Procurement Card sample is now in a spreadsheet called 'PCard Sample.xlsx!")
instructions.grid(column=0, row=10, padx=10, sticky=W)

def browse_file(entry_box): #This function allows the user to select files manually through the app
    file_path = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        entry_box.delete(0, END)
        entry_box.insert(0, file_path)

file_entries = []   #List of the paths of the files the user selected
id_entries = []     #List of the MAGIC document IDs the user selected

for i in range(10):     #Creates ten boxes where user can select a file
    ttk.Label(display_frame, text=f"File Path {i+1}").grid(column=0, row=i, padx=5, pady=5)
    file_entry = ttk.Entry(display_frame, width=60)
    file_entry.grid(column=1, row=i, padx=5)
    file_entries.append(file_entry)     #Adds the user's file selection to the list of file paths
    browse_button = ttk.Button(display_frame,text="Browse",command=lambda e=file_entry: browse_file(e))
    browse_button.grid(column=2, row=i, padx=5)
    ttk.Label(display_frame,text=f"Document ID {i+1}").grid(column=3, row=i, padx=5)
    id_entry = ttk.Entry(display_frame, width=20)
    id_entry.grid(column=4, row=i, padx=5)
    id_entries.append(id_entry)     #Adds the matching document ID to the list of file paths


###
# Core pdf-processing function
###


def process_pdf():
    pdf_files = []      #This is the list of pdf files the user wants to process
    for i in range(10): #We update pdf_files to include matched pairs of document ids and file paths
        pdf_id = id_entries[i].get().strip()
        pdf_path = file_entries[i].get().strip()
        if not pdf_path:
            continue
        pdf_files.append({"id": pdf_id, "path": pdf_path})
    total_pdfs = len(pdf_files)     #We need the total number of PDFs to run our tracker
    processed_count = 0     #This is the basis for our tracker
    root.update_idletasks()
    all_rows = []   #This is the list where the pdf reader will put all the rows of text it finds
    for pdf_info in pdf_files:  #This is where the magic happens: the function converts pdfs to images and then reads the text in those images
        input_pdf = pdf_info["path"]
        pdf_id = pdf_info["id"]
        print(f"\nProcessing: {input_pdf}")     #DEBUGGING TOOL
        progress_label.config(text=f"Processing PDF {processed_count + 1} of {total_pdfs}...")  #This is the progress tracker the user actually sees
        root.update_idletasks()     #We have to update idle tasks to ensure the UI shows updates to the progress tracker, because otherwise the UI is simply frozen
        pdf_name = os.path.basename(input_pdf)
        #We convert each pdf to an image so it can be read by OCR
        images = convert_from_path(input_pdf,first_page=1,last_page=10,poppler_path=r"C:\Users\wbittner\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin")
        lines = []  #This is where we store the lines of text that OCR finds
        for i, image in enumerate(images):  #This loop is where pytesseract (the OCR software) turns image text into "real" text
            img = np.array(image)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray,150,255,cv2.THRESH_BINARY)
            text = pytesseract.image_to_string(thresh,config='--psm 6')
            page_lines = [line.strip()for line in text.split("\n")if line.strip()]
            lines.extend(page_lines)
            print(f"OCR processed page {i+1}")  #DEBUGGING TOOL
        capture = False #Tells the program not to worry about any old line, but only the ones we specify
        filtered_lines = [] #This stores the lines that actually have transaction data
        for line in lines:  #This loop filters out lines of text that are not transactions
            if "Cardholder Transaction" in line:    #Since the pdfs always start showing transactions at "Cardholder Transactions" or "Cardholder Transactions Continued", this code will start capturing lines only once we reach that section
                capture = True
                continue
            if "Interest Charge Calculation" in line:   #The pdfs always stop showing transactions at "Interest Charge Calculation", so that is where we want to stop capturing lines of text
                capture = False
            if capture: #Adds any captured lines to our list of filtered lines
                filtered_lines.append(line)
        clean_lines = []    #This stores the lines we care about, minus headers
        for line in filtered_lines: #This removes the headers from our lines of text
            if "Date Date" in line:
                continue
            if "Description Amount" in line:
                continue
            clean_lines.append(line)
        date_pattern = r"^\d{1,2}/\d{1,2}"
        transactions = []
        current = []
        for line in clean_lines:    #Further filters our text rows by making sure that we only keep lines that start with a date
            if re.match(date_pattern, line):
                if current:
                    transactions.append(current)
                current = [line]
            else:
                current.append(line)
        if current:
            transactions.append(current)
        parsed_rows = []
        for t in transactions:  #For each saved row of text, we determine what elements are date, amount, description, etc.
            if not t:
                continue
            first_line = t[0]
            match = re.match(r"(\d{1,2}/\d{1,2})\s+(\d{1,2}/\d{1,2})\s+(\d+)",first_line)
            if not match:
                continue
            transaction_date = match.group(1)
            amount_matches = re.findall(r"-?\$?\d+\.\d{2}",first_line)
            amount = amount_matches[-1] if amount_matches else None
            if amount:
                amount = amount.replace("$", "")
            description = " ".join(t)
            description = description.replace(transaction_date, "")
            if amount:
                description = description.replace(amount, "")
            description = description.strip()
            if "PAYMENT - THANK YOU" in description.upper():
                continue
            parsed_rows.append({"Bank": "UMB", "MAGIC ID/Transaction ID": pdf_id, "Transaction Date": transaction_date, #These are our columns
                                "Amount": amount, "Vendor/Description" : description})
        print(f"Parsed rows from {pdf_name}: {len(parsed_rows)}")   #DEBUGGING TOOL
        all_rows.extend(parsed_rows)
        processed_count += 1
        progress_label.config(text=f"Completed {processed_count} of {total_pdfs} PDFs")
        root.update_idletasks()
    df = pd.DataFrame(all_rows).drop_duplicates()   #Creates a dataframe where we will store our text
    df["Transaction Date"] = df["Transaction Date"].astype(str) #We need this if we later copy-paste the data into another Excel sheet, which we sometimes do during compliance audits. Unless we put the date as a string, Excel tries to give it a year, usually the current year, which is inaccurate if the transaction is from a prior year.
    with pd.ExcelWriter("transactions.xlsx", engine="openpyxl") as writer:  #Writes our dataframe to an Excel spreadsheet
        df.to_excel(writer, index=False)
        ws = writer.sheets["Sheet1"]
        headers = {}
        for cell in ws[1]:
            headers[cell.value] = cell.column_letter
        for col_name in ["Transaction Date"]:
            col_letter = headers[col_name]
            for cell in ws[col_letter]:
                cell.number_format = "@"
                if cell.row != 1 and cell.value:
                    cell.value = str(cell.value)
        print("\nDone. Output saved to transactions.xlsx")  #DEBUGGING TOOL
        process_complete_message.grid()
        progress_label.config(text="All PDFs processed successfully.")
        root.after(10000, process_complete_message.grid_remove)


###
# Core data sampler function
###


number_of_rows_to_sample_label = ttk.Label(display_frame, text="How many rows do\nyou want to sample?") #Allows user to decide their sample size
number_of_rows_to_sample_label.grid(column=5, row=4, padx=5, sticky=W)
number_of_rows_to_sample = ttk.Entry(display_frame, width=20)
number_of_rows_to_sample.grid(column=5, row=5, padx=5, sticky=W)

def sample_from_spreadsheet():  #This function will take the Excel spreadsheet we just generated and randomly sample it, sending a random sample of rows to a new Excel sheet.
    full_sheet = pd.read_excel(r"transactions.xlsx")
    full_sheet = full_sheet[full_sheet["Amount"] != 0]
    sample_size = int(number_of_rows_to_sample.get())
    random_rows = random.sample(range(len(full_sheet)), sample_size)
    sampled_sheet = full_sheet.iloc[random_rows]
    sampled_sheet.to_excel("PCard Sample.xlsx", index=False)
    sample_complete_message.grid()
    root.after(10000, sample_complete_message.grid_remove)

run_process_pdf = ttk.Button(display_frame,text="Process PDFs",command=process_pdf) #Buttons that allow user to run the pdf reader and pdf sampler functions
run_sample_from_pdf = ttk.Button(display_frame, text="Sample from PDF", command=sample_from_spreadsheet)
run_process_pdf.grid(column=5, row=0, padx=10, sticky=W)
run_sample_from_pdf.grid(column=5, row=6, padx=10, sticky=W)

root.mainloop()