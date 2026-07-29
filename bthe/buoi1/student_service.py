from validators import validate_id, validate_name, validate_email, validate_age

students = []

def check_duplicate_id(student_id):
    student_id_clean = student_id.strip().lower()
    return any(s['id'].lower() == student_id_clean for s in students)

def check_duplicate_email(email):
    email_clean = email.strip().lower()
    return any(s['email'].lower() == email_clean for s in students)

def add_student(student_id, name, age_input, email):
    valid_id, msg_id = validate_id(student_id)
    if not valid_id:
        return False, msg_id

    valid_name, msg_name = validate_name(name)
    if not valid_name:
        return False, msg_name

    valid_email, msg_email = validate_email(email)
    if not valid_email:
        return False, msg_email

    valid_age, age_or_msg = validate_age(age_input)
    if not valid_age:
        return False, age_or_msg

    if check_duplicate_id(student_id):
        return False, f"Ma sinh vien '{student_id.strip()}' da ton tai!"

    if check_duplicate_email(email):
        return False, f"Email '{email.strip()}' da duoc su dung!"

    student = {
        "id": student_id.strip(),
        "name": name.strip(),
        "age": age_or_msg,
        "email": email.strip()
    }
    students.append(student)
    return True, "Them sinh vien thanh cong!"

def get_all_students():
    return students

def find_student_by_id(student_id):
    student_id_clean = student_id.strip().lower()
    for student in students:
        if student['id'].lower() == student_id_clean:
            return student
    return None

def filter_students_by_age(min_age=None, max_age=None):
    filtered = []
    for s in students:
        match_min = (min_age is None) or (s['age'] >= min_age)
        match_max = (max_age is None) or (s['age'] <= max_age)
        if match_min and match_max:
            filtered.append(s)
    return filtered