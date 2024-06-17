# import camelot

# # Path to the PDF file
# pdf_path = "static/1/66692a1ce42db66e9513eda90.pdf"

# # Extract tables from the PDF
# tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')

# # Function to convert table to text
# def table_to_text(table):
#     output = []
#     # Get the table as a pandas DataFrame
#     df = table.df
#     for index, row in df.iterrows():
#         row_text = "\t".join(row)
#         output.append(row_text)
#     return "\n".join(output)

# # Process each table and output the text
# for i, table in enumerate(tables):
#     table_text = table_to_text(table)
#     with open(f"table_{i}.txt", "w", encoding="utf-8") as f:
#         f.write(table_text)
#     print(f"Table {i} extracted and saved as table_{i}.txt")

# print("Tables extracted and saved as text.")


import tabula

# Path to the PDF file
pdf_path = "static/1/66692a1ce42db66e9513eda90.pdf"

# Extract tables from the PDF
tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

# Function to convert table to text
def table_to_text(df):
    output = []
    for index, row in df.iterrows():
        row_text = "\t".join(map(str, row))
        output.append(row_text)
    return "\n".join(output)

# Process each table and output the text
for i, table in enumerate(tables):
    table_text = table_to_text(table)
    with open(f"table_{i}.txt", "w", encoding="utf-8") as f:
        f.write(table_text)
    print(f"Table {i} extracted and saved as table_{i}.txt")

print("Tables extracted and saved as text.")


# import pdfplumber
# import camelot
# import os

# # Path to the PDF file
# pdf_path = "static/1/66692a1ce42db66e9513eda90.pdf"
# output_folder = "extracted_text"

# # Ensure the output folder exists
# os.makedirs(output_folder, exist_ok=True)

# # Extract non-table text using pdfplumber
# with pdfplumber.open(pdf_path) as pdf:
#     all_text = []
#     for i, page in enumerate(pdf.pages):
#         text = page.extract_text()
#         with open(os.path.join(output_folder, f"page_{i+1}_text.txt"), "w", encoding="utf-8") as f:
#             f.write(text)
#         all_text.append(text)

# # Extract tables using Camelot
# tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')

# # Function to convert table to text
# def table_to_text(table):
#     output = []
#     df = table.df
#     for index, row in df.iterrows():
#         row_text = "\t".join(row)
#         output.append(row_text)
#     return "\n".join(output)

# # Process each table and output the text
# for i, table in enumerate(tables):
#     table_text = table_to_text(table)
#     with open(os.path.join(output_folder, f"table_{i+1}.txt"), "w", encoding="utf-8") as f:
#         f.write(table_text)
#     print(f"Table {i+1} extracted and saved as table_{i+1}.txt")

# print("Non-table text and tables extracted and saved as text.")
