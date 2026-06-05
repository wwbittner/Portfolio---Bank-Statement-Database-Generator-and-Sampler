**Bank Statement Database Generator and Sampler**



*Problem:* Mississippi state agencies use UMB Bank for their official credit cards. The Office of the State Auditor received their statements as pdf scans, not spreadsheets. To build an Excel database, auditors must manually enter transactions into Excel, which takes hours for even small agencies.



*How the Code Solves the Problem:* Uses ocular character recognition (OCR) to transform transaction data from pdf to Excel.



*Tech Stack:*

* Python

  * pandas
  * pytesseract (Occular Character Recognition)
  * tkinter (UI)



*Installation:*





*Screenshots:*





*Challenges:*

* The bank statement pdfs are scans of printed statements, meaning they cannot be read directly by pdf reader software (requires text-based pdfs, not scans) or by image reader software (requires true images). I solved this problem by adding code that transforms pdf scans to true images as part of the pdf reading process.



*Future Improvements:*

* Expand code to be able to process statements from other banks, as the state is moving away from UMB Bank.
* Use APIs to make the code download bank statements directly from the state's servers rather than downloading pdfs manually.

