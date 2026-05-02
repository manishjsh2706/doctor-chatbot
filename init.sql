CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    specialty VARCHAR(100)
);

CREATE TABLE availability (
    id SERIAL PRIMARY KEY,
    doctor_id INT REFERENCES doctors(id),
    date DATE,
    time TIME,
    is_booked BOOLEAN DEFAULT FALSE
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    doctor_id INT REFERENCES doctors(id),
    patient_name VARCHAR(100),
    date DATE,
    time TIME
);

INSERT INTO doctors (name, specialty) VALUES
('Dr. Arjun Mehta', 'General Physician'),
('Dr. Priya Sharma', 'Dermatologist'),
('Dr. Rohan Kapoor', 'Orthopedic'),
('Dr. Sneha Iyer', 'Cardiologist'),
('Dr. Vivek Rao', 'Orthopedic'),
('Dr. Anjali Desai', 'General Physician'),
('Dr. Karan Malhotra', 'Dermatologist'),
('Dr. Neha Gupta', 'Cardiologist'),
('Dr. Sanjay Patel', 'Orthopedic'),
('Dr. Meera Joshi', 'General Physician');

INSERT INTO availability (doctor_id, date, time, is_booked) VALUES
(1, '2026-02-19', '10:00:00', FALSE),
(1, '2026-02-19', '11:00:00', FALSE),
(2, '2026-02-19', '14:00:00', FALSE),
(2, '2026-02-20', '15:00:00', FALSE),
(3, '2026-02-19', '09:30:00', FALSE),
(3, '2026-02-20', '10:30:00', FALSE),
(4, '2026-02-19', '16:00:00', FALSE),
(4, '2026-02-21', '11:00:00', FALSE),
(5, '2026-02-19', '12:00:00', FALSE),
(5, '2026-02-20', '13:00:00', FALSE),
(6, '2026-02-21', '09:00:00', FALSE),
(7, '2026-02-21', '10:00:00', FALSE),
(8, '2026-02-21', '11:00:00', FALSE),
(9, '2026-02-22', '14:00:00', FALSE),
(10, '2026-02-22', '15:00:00', FALSE);

INSERT INTO appointments (doctor_id, patient_name, date, time) VALUES
(1, 'Rahul Verma', '2026-02-19', '10:00:00'),
(2, 'Sneha Kulkarni', '2026-02-19', '14:00:00'),
(3, 'Amit Singh', '2026-02-19', '09:30:00'),
(4, 'Pooja Nair', '2026-02-19', '16:00:00'),
(5, 'Ravi Kumar', '2026-02-19', '12:00:00');