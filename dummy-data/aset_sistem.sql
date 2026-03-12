-- CREATE TABLE statement for PostgreSQL

CREATE TABLE aset_sistem (
    Id_stakeholder VARCHAR(10) PRIMARY KEY,
    No_Registrasi_CSIRT VARCHAR(50),
    Nama_Stakeholder VARCHAR(100),
    Id_Sistem VARCHAR(10),
    Nama VARCHAR(100),
    Jenis_Se VARCHAR(20),
    Sektor_IIV VARCHAR(10),
    Kategori_SE VARCHAR(20),
    created_at TIMESTAMP
);

-- convert above values to INSERT statements for PostgreSQL, add created_at with random timestamps within first 3 months in 2026 

INSERT INTO aset_sistem (id_stakeholder, No_Registrasi_CSIRT, Nama_Stakeholder, Id_Sistem, Nama, Jenis_Se, Sektor_IIV, Kategori_SE, created_at) VALUES
('001', '083/CSIRT.01.10/BSSN/07/2022', 'Lembaga AAAA', 'A001', 'Sistem A', 'Publik', 'Ya', 'Strategis', '2026-01-15 10:30:00'),
('002', '123/CSIRT.01.10/BSSN/11/2022', 'Lembaga BBBB', 'B001', 'Sistem B', 'Privat', 'Tidak', 'Tinggi', '2026-02-20 14:45:00'),
('003', '156/CSIRT.01.05/BSSN/04/2023', 'Lembaga CCCC', 'C001', 'Sistem C', 'Publik', 'Ya', 'Rendah', '2026-03-10 09:15:00'),
('004', '236/CSIRT.0105/BSSN/08/2023', 'Lembaga DDDD', 'D001', 'Sistem D', 'Privat', 'Tidak', 'Strategis', '2026-01-25 11:20:00'),
('005', '146/CSIRT.01.05/BSSN/02/2023', 'Lembaga EEEE', 'E001', 'Sistem E', 'Privat', 'Ya', 'Tinggi', '2026-02-18 13:35:00'),
('006', '130/CSIRT.01.05/BSSN/12/2022', 'Lembaga FFFF', 'F001', 'Sistem F', 'Privat', 'Ya', 'Rendah', '2026-03-05 16:45:00'),
('007', '168/CSIRT.01.05/BSSN/05/2023', 'Lembaga GGGG', 'G001', 'Sistem G', 'Privat', 'Ya', 'Rendah', '2026-01-30 14:55:00'),
('008', '227/CSIRT.01.05/BSSN/08/2023', 'Lembaga HHHH', 'H001', 'Sistem H', 'Privat', 'Ya', 'Rendah', '2026-02-25 11:20:00');