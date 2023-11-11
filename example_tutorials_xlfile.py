import openpyxl

# Create a new workbook and select the active sheet
workbook = openpyxl.Workbook()
sheet = workbook.active

# Add column headers
sheet['A1'] = 'logo'
sheet['B1'] = 'title'
sheet['C1'] = 'description'
sheet['D1'] = 'details'
sheet['E1'] = 'content_type'
sheet['F1'] = 'level_id'
sheet['G1'] = 'category_id'
sheet['H1'] = 'status'

# Sample data
data = [
    ('logo1.jpg', 'Tutorial 1', 'Description 1', 'Details 1', 'Video', 1, 1, 'Active'),
    ('logo2.jpg', 'Tutorial 2', 'Description 2', 'Details 2', 'Article', 2, 2, 'Inactive'),
    ('logo3.jpg', 'Tutorial 3', 'Description 3', 'Details 3', 'PDF', 1, 2, 'Active'),
]

# Add sample data to the sheet
for row_idx, row_data in enumerate(data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        sheet.cell(row=row_idx, column=col_idx, value=value)

# Save the workbook to a file
workbook.save('tutorial_example.xlsx')
