-- CREATE TABLE statement for PostgreSQL

CREATE TABLE public.aset_tik (
    id_stakeholder VARCHAR(10) PRIMARY KEY,
    no_registrasi_csirt VARCHAR(50),
    nama_stakeholder VARCHAR(100),
    jenis_perangkat VARCHAR(50),
    merk VARCHAR(50),
    jumlah INTEGER,
    created_at TIMESTAMP
);

-- convert above values to INSERT statements for PostgreSQL, add created_at with random timestamps within first 3 months in 2026 

INSERT INTO public.aset_tik (id_stakeholder, no_registrasi_csirt, nama_stakeholder, jenis_perangkat, merk, jumlah, created_at) VALUES
('001', '083/CSIRT.01.10/BSSN/07/2022', 'Lembaga AAAA', 'PC', 'Lenovo', 30, '2026-01-15 10:30:00'),
('002', '123/CSIRT.01.10/BSSN/11/2022', 'Lembaga BBBB', 'Laptop', 'Asus', 4, '2026-02-20 14:45:00'),
('003', '156/CSIRT.01.05/BSSN/04/2023', 'Lembaga CCCC', 'Server', 'HP', 2, '2026-03-10 09:15:00'),
('004', '236/CSIRT.0105/BSSN/08/2023', 'Lembaga DDDD', 'Server', 'Asus', 5, '2026-01-25 11:20:00'),
('005', '146/CSIRT.01.05/BSSN/02/2023', 'Lembaga EEEE', 'Server', 'MSI', 6, '2026-02-18 13:35:00'),
('006', '130/CSIRT.01.05/BSSN/12/2022', 'Lembaga FFFF', 'Server', 'Gigabyte', 15, '2026-03-05 16:45:00'),
('007', '168/CSIRT.01.05/BSSN/05/2023', 'Lembaga GGGG', 'Server', 'Asus', 35, '2026-01-30 14:55:00'),
('008', '227/CSIRT.01.05/BSSN/08/2023', 'Lembaga HHHH', 'Core Switch', 'MSI', 5, '2026-02-25 11:20:00');