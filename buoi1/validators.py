import re

def validate_id(student_id):
    if not student_id or not student_id.strip():
        return False, "Ma sinh vien khong duoc de rong!"
    return True, ""

def validate_name(name):
    if not name or not name.strip():
        return False, "Ten sinh vien khong duoc de rong hoac chi chua khoang trang!"
    return True, ""

def validate_email(email):
    if not email or not email.strip():
        return False, "Email khong duoc de rong!"
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email.strip()):
        return False, "Dinh dang email khong hop le!"
    return True, ""

def validate_age(age_input):
    try:
        age = int(age_input)
        if age < 16 or age > 100:
            return False, "Tuoi phai trong khoang tu 16 den 100!"
        return True, age
    except ValueError:
        return False, "Tuoi phai la mot so nguyen hop le!"