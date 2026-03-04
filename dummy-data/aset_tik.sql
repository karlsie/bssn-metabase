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

-- convert above values to INSERT statements for PostgreSQL

INSERT INTO public.aset_tik (id_stakeholder, no_registrasi_csirt, nama_stakeholder, jenis_perangkat, merk, jumlah) VALUES
('001', '083/CSIRT.01.10/BSSN/07/2022', 'Lembaga AAAA', 'PC', 'Lenovo', 30),
('002', '123/CSIRT.01.10/BSSN/11/2022', 'Lembaga BBBB', 'Laptop', 'Asus', 4),
('003', '156/CSIRT.01.05/BSSN/04/2023', 'Lembaga CCCC', 'Server', 'HP', 2),
('004', '236/CSIRT.0105/BSSN/08/2023', 'Lembaga DDDD', 'Server', 'Asus', 5),
('005', '146/CSIRT.01.05/BSSN/02/2023', 'Lembaga EEEE', 'Server', 'MSI', 6),
('006', '130/CSIRT.01.05/BSSN/12/2022', 'Lembaga FFFF', 'Server', 'Gigabyte', 15),
('007', '168/CSIRT.01.05/BSSN/05/2023', 'Lembaga GGGG', 'Server', 'Asus', 35),
('008', '227/CSIRT.01.05/BSSN/08/2023', 'Lembaga HHHH', 'Core Switch', 'MSI', 5);