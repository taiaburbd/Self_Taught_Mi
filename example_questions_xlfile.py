import pandas as pd

# Create a DataFrame with demo data
data = {
    'Question': ['What is 2 + 2?', 'Capital of France', 'Who wrote Hamlet?'],
    'Option1': [3, 'Paris', 'Dickens'],
    'Option2': [4, 'London', 'Shakespeare'],
    'Option3': [5, 'Berlin', 'Twain'],
    'Option4': [6, 'Madrid', 'Austen'],
    'Answer': [4, 'Paris', 'Shakespeare'],
    'Level': [1, 2, 3],
    'Category': ['Mathematics', 'Geography', 'Literature'],
    'Created_by': ['User1', 'User2', 'User3']
}

df = pd.DataFrame(data)

# Export the DataFrame to an Excel file
excel_file = "static/questions_example.xlsx"
df.to_excel(excel_file, index=False)

print(f"Demo Excel file '{excel_file}' has been created.")
