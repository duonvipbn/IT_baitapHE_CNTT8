from student_service import (
    add_student,
    get_all_students,
    find_student_by_id,
    filter_students_by_age
)

def print_student_table(student_list):
    if not student_list:
        print(" -> (Danh sach trong)")
        return
    print(f"{'Ma SV':<10} | {'Ho va Ten':<20} | {'Tuoi':<5} | {'Email':<25}")
    print("-" * 68)
    for s in student_list:
        print(f"{s['id']:<10} | {s['name']:<20} | {s['age']:<5} | {s['email']:<25}")

def run_test_cases():
    print("=" * 60)
    print("CHAY BO KIEM THU TU DONG (5 TEST CASES)")
    print("=" * 60)

    test_cases = [
        (1, "Xu ly ma rong", "   ", "Nguyen Van A", 20, "a@gmail.com", False),
        (2, "Xu ly ten chi chua khoang trang", "SV01", "     ", 20, "a@gmail.com", False),
        (3, "Xu ly email sai dinh dang", "SV01", "Nguyen Van A", 20, "email_sai_dinh_dang", False),
        (4, "Xu ly tuoi sai", "SV01", "Nguyen Van A", "abc", "a@gmail.com", False),
        (5, "Them sinh vien hop le", "SV01", "Nguyen Van A", 20, "a@gmail.com", True)
    ]

    for tc_id, desc, s_id, name, age, email, expected in test_cases:
        success, msg = add_student(s_id, name, age, email)
        status = "PASSED" if success == expected else "FAILED"
        print(f"Test Case {tc_id} [{status}] - {desc}")
        print(f"   Input : ID='{s_id}', Name='{name}', Age={age}, Email='{email}'")
        print(f"   Output: {msg}\n")

    print("=" * 60)

def main():
    run_test_cases()

    while True:
        print("\n--- HE THONG QUAN LY SINH VIEN ---")
        print("1. Them sinh vien")
        print("2. Hien thi tat ca sinh vien")
        print("3. Tim sinh vien theo ma")
        print("4. Loc sinh vien theo khoang tuoi")
        print("0. Thoat")
        
        choice = input("Lua chon cua ban (0-4): ").strip()

        if choice == "1":
            print("\n--- THEM SINH VIEN MOI ---")
            s_id = input("Nhap ma SV: ")
            name = input("Nhap ho ten: ")
            age = input("Nhap tuoi: ")
            email = input("Nhap email: ")
            
            success, msg = add_student(s_id, name, age, email)
            if success:
                print(f"[Thanh cong]: {msg}")
            else:
                print(f"[Loi]: {msg}")

        elif choice == "2":
            print("\n--- DANH SACH SINH VIEN ---")
            print_student_table(get_all_students())

        elif choice == "3":
            print("\n--- TIM SINH VIEN THEO MA ---")
            search_id = input("Nhap ma SV can tim: ")
            student = find_student_by_id(search_id)
            if student:
                print_student_table([student])
            else:
                print(f"Khong tim thay sinh vien co ma '{search_id}'!")

        elif choice == "4":
            print("\n--- LOC SINH VIEN THEO TUOI ---")
            try:
                min_a = input("Nhap tuoi toi thieu (bo trong neu khong ap dung): ").strip()
                max_a = input("Nhap tuoi toi da (bo trong neu khong ap dung): ").strip()
                
                min_age = int(min_a) if min_a else None
                max_age = int(max_a) if max_a else None
                
                result = filter_students_by_age(min_age, max_age)
                print_student_table(result)
            except ValueError:
                print("[Loi]: Tuoi nhap vao phai la so integer hop le!")

        elif choice == "0":
            print("Da thoat chuong trinh. Tam biet!")
            break
        else:
            print("Lua chon khong hop le, vui long thu lai!")

if __name__ == "__main__":
    main()