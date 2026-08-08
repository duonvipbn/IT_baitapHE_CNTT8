CREATE DATABASE IF NOT EXISTS connect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE connect_db;

DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    age INT NOT NULL,
    major VARCHAR(50) NOT NULL,
    gpa FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO students (student_code, full_name, email, age, major, gpa) VALUES
('SV001', 'Nguyễn Văn A', 'nguyenvana@gmail.com', 20, 'Software Engineering', 3.5),
('SV002', 'Trần Thị B', 'tranthib@gmail.com', 21, 'Computer Science', 3.8),
('SV003', 'Lê Văn C', 'levanc@gmail.com', 19, 'Information Technology', 2.9),
('SV004', 'Phạm Minh D', 'phamminhd@gmail.com', 22, 'Software Engineering', 3.2),
('SV005', 'Hoàng Anh E', 'hoanganhe@gmail.com', 20, 'Data Science', 3.9);