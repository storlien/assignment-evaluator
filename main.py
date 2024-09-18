import os
import nbformat
from nbconvert import PythonExporter
from nbconvert.preprocessors import ExecutePreprocessor
from PyPDF2 import PdfReader
from evaluate import grade_text, grade_code
import glob

assignment_number = ""
grade_only_text = ""
usernames_normal = []
usernames_abnormal = []

def extract_text_from_pdf(file_path):
    try:
        text = ""
        with open(file_path, "rb") as file:
            pdf = PdfReader(file)
            for page in range(len(pdf.pages)):
                text += pdf.pages[page].extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def extract_code_from_notebook(file_path):
    try:
        # Open and read the notebook file
        with open(file_path) as f:
            nb = nbformat.read(f, as_version=4)
        
        # Initialize a variable to store the code blocks with numbering
        ipynb_code = ""
        code_block_counter = 1
        
        # Iterate over each cell in the notebook
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':  # Only process code cells
                # Add a label before each code block
                ipynb_code += f"{code_block_counter}. code block\n"
                ipynb_code += ''.join(cell['source']) + "\n\n"  # Append the code block content
                code_block_counter += 1
        
        return ipynb_code
    
    except Exception as e:
        print(f"Error extracting code from notebook: {e}")
        return None
    
def validate_usernames():
    assignment_files = glob.glob(f"assignment-{assignment_number}/*")

    usernames = []
    usernames_abnormal = []
    usernames_normal = []
    filename_errors = []

    for file in assignment_files:
        filename_list = file.split("_")
        
        if filename_list[0].startswith(f"assignment-{assignment_number}/Assignment "):
            usernames.append(filename_list[1])
        else:
            print("Error:")
            print(filename_list, "\n")
            filename_errors.append(filename_list[0])
    
    # print(usernames)

    usernames_set = set(usernames)

    for username in usernames_set:
        user_files = glob.glob(f"assignment-{assignment_number}/Assignment*{username}*")

        if len(glob.glob(f"assignment-{assignment_number}/Assignment*{username}*.txt")) == 0:
            print("Error! No txt file:", username, "\n")
            usernames_abnormal.append(username)

        elif len(glob.glob(f"assignment-{assignment_number}/Assignment*{username}*.pdf")) == 0:
            print("Error! No pdf file:", username, "\n")
            usernames_abnormal.append(username)

        elif len(glob.glob(f"assignment-{assignment_number}/Assignment*{username}*.ipynb")) == 0 and grade_only_text == "n":
            print("Error! No ipynb file:", username, "\n")
            usernames_abnormal.append(username)
        
        else: 
            usernames_normal.append(username)

    return usernames_normal, usernames_abnormal, filename_errors

def exclude_graded(usernames: list):
    usernames_need_grading = []
    usernames_already_graded = []
    usernames_problem_with_grading = []

    for username in usernames:
        with open(glob.glob(f"assignment-{assignment_number}/Assignment*{username}*.txt")[0], "r") as file:
            submission_text_list = file.read().split("\n")
            if submission_text_list[3] == "Current Grade: Needs Grading":
                usernames_need_grading.append(username)
            elif submission_text_list[3] == "Current Grade: 1":
                # print(username, "already graded.")
                usernames_already_graded.append(username)
            else:
                # print(username, "has problem with grading!")
                usernames_problem_with_grading.append(username)

    return usernames_need_grading, usernames_already_graded, usernames_problem_with_grading

def read_pdfs():
    global usernames_normal, usernames_abnormal

    default_value = ""
    user_submissions_dict_pdf = {key: default_value for key in usernames_normal}
    user_submissions_dict_ipynb = {key: default_value for key in usernames_normal}

    usernames_iterator = usernames_normal.copy()

    print("Reading PDFs...")
    for username in usernames_iterator:
        pdf_text = extract_text_from_pdf(glob.glob(f"assignment-{assignment_number}/Assignment*{username}*.pdf")[0])

        if pdf_text == None:
            print("Error reading PDF:", username)
            usernames_abnormal.append(username)
            usernames_normal.remove(username)
            user_submissions_dict_pdf.pop(username)
            user_submissions_dict_ipynb.pop(username)
        elif pdf_text == "":
            print("Empty PDF:", username)
            usernames_abnormal.append(username)
            usernames_normal.remove(username)
            user_submissions_dict_pdf.pop(username)
            user_submissions_dict_ipynb.pop(username)
        else:
            user_submissions_dict_pdf[username] = pdf_text
    
    print("Done reading PDFs. \n")

    return user_submissions_dict_pdf, user_submissions_dict_ipynb

def read_ipynbs(user_submissions_dict_pdf, user_submissions_dict_ipynb):
    global usernames_normal, usernames_abnormal

    usernames_iterator = usernames_normal.copy()

    print("Reading ipynb files...")
    for username in usernames_iterator:
        ipynb_code = extract_code_from_notebook(glob.glob(f"assignment-{assignment_number}/Assignment*{username}*.ipynb")[0])

        if ipynb_code == None:
            print("Error reading ipynb:", username)
            usernames_abnormal.append(username)
            usernames_normal.remove(username)
            user_submissions_dict_pdf.pop(username)
            user_submissions_dict_ipynb.pop(username)
        elif ipynb_code == "":
            print("Empty ipynb:", username)
            usernames_abnormal.append(username)
            user_submissions_dict_pdf.pop(username)
            user_submissions_dict_ipynb.pop(username)
        else:
            user_submissions_dict_ipynb[username] = ipynb_code

    print("Done reading ipynb files.")

    return user_submissions_dict_pdf, user_submissions_dict_ipynb

def main():
    global assignment_number, grade_only_text, usernames_normal, usernames_abnormal

    assignment_number = str(input("Enter assignment number, e.g. 01: "))
    grade_only_text = str(input("Grade only text submissions? (y/n): "))

    if grade_only_text == "y":
        print("Grading only text submissions.")
    elif grade_only_text == "n":
        print("Grading both text and code submissions.")
    else:
        print("Invalid input.")
        return

    print()

    solutions_pdf_path = f"solutions-{assignment_number}/solutions-{assignment_number}.pdf"

    if grade_only_text == "y":
        if not os.path.exists(solutions_pdf_path):
            print("Solutions pdf is missing!")
            return
        
        solutions_pdf_text = extract_text_from_pdf(solutions_pdf_path)

    else:
        solutions_ipynb_path = f"solutions-{assignment_number}/solutions-{assignment_number}.ipynb"
        
        if not os.path.exists(solutions_pdf_path) or not os.path.exists(solutions_ipynb_path):
            print("Solutions pdf or ipynb is missing!")
            return
        
        solutions_pdf_text = extract_text_from_pdf(solutions_pdf_path)
        solutions_ipynb_code = extract_code_from_notebook(solutions_ipynb_path)

    usernames_normal, usernames_abnormal, filename_errors = validate_usernames()

    print("Usernames normal:", len(usernames_normal))
    print("Usernames abnormal:", len(usernames_abnormal))
    print("Filename errors:", len(filename_errors), "\n")

    usernames_normal, usernames_already_graded, usernames_problem_with_grading = exclude_graded(usernames_normal)

    usernames_normal.sort()
    usernames_already_graded.sort()
    usernames_problem_with_grading.sort()
    usernames_abnormal.sort()

    print("Usernames normal after excluding graded:", len(usernames_normal))
    print("Usernames already graded:", len(usernames_already_graded))
    print("Usernames with problem with grading:", len(usernames_problem_with_grading), usernames_problem_with_grading, "\n")

    if grade_only_text == "n":
        user_submissions_dict_pdf, user_submissions_dict_ipynb = read_pdfs()
        user_submissions_dict_pdf, user_submissions_dict_ipynb = read_ipynbs(user_submissions_dict_pdf, user_submissions_dict_ipynb)
    else:
        user_submissions_dict_pdf, user_submissions_dict_ipynb = read_pdfs()

    if len(user_submissions_dict_pdf) != len(user_submissions_dict_ipynb):
        print("Error: Different number of submissions in pdf and ipynb files.")
        return

    print("Processing submissions... \n")

    students = {}

    for username, submission_text in user_submissions_dict_pdf.items():
            print(f"Grading text submission for {username}...")
            result = grade_text(submission_text, solutions_pdf_text)
            
            if result is None:
                print(f"Error grading text submission for {username}. Result: {result} \n")
                students[username] = -1
            elif result.lower() == "passed":
                print(f"{username} passed the assignment. \n")
                students[username] = 0.5
            elif result.lower() == "failed":
                print(f"{username} failed the assignment. Result: {result} \n")
                students[username] = 0
            else:
                print(f"Error grading text submission for {username}. Result: {result} \n")
                students[username] = -1

    if grade_only_text == "n":
        for username, submission_code in user_submissions_dict_ipynb.items():
            print(f"Grading code submission for {username}...")
            result = grade_code(submission_code, solutions_ipynb_code)
            
            if result is None:
                print(f"Error grading code submission for {username}. Result: {result} \n")
                students[username] = -1
            elif result.lower() == "passed":
                print(f"{username} passed the assignment. \n")
                students[username] = -1 if students[username] == -1 else students[username] + 0.5
            elif result.lower() == "failed":
                print(f"{username} failed the assignment. Result: {result} \n")
                students[username] = -1 if students[username] == -1 else students[username]
            else:
                print(f"Error grading code submission for {username}. Result: {result} \n")
                students[username] = -1

    passed_students = [student for student in students if students[student] == 1]
    half_passed_students = [student for student in students if students[student] == 0.5]
    failed_students = [student for student in students if students[student] == 0]
    error_students = [student for student in students if students[student] == -1]

    if grade_only_text == "y":
        passed_students = half_passed_students
        half_passed_students = []

    print("Total number of students:", len(students))
    print("Passed Students:", len(passed_students), passed_students)
    print("Half Passed Students:", len(half_passed_students), half_passed_students)
    print("Failed Students:", len(failed_students), failed_students)
    print("Error Students:", len(error_students), error_students)

if __name__ == "__main__":
    main()