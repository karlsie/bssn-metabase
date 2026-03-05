-- CREATE TABLE statement for PostgreSQL

CREATE TABLE nilai_indeks_kami (
    id_stakeholder VARCHAR(10) PRIMARY KEY,
    no_registrasi_csirt VARCHAR(50),
    id_penilaian VARCHAR(10),
    nama_stakeholder VARCHAR(100),
    waktu_penilaian DATE,
    nilai_kerangka_kerja INT,
    nilai_tata_kelola INT,
    nilai_pengelolaan_aset INT,
    nilai_teknologi INT,
    nilai_pdp INT,
    nilai_risiko INT,
    suplemen INT,
    nilai_akhir INT,
    created_at TIMESTAMP
);

-- convert above values to INSERT statements for PostgreSQL, change created_at with random timestamps within first 3 months in 2026 


INSERT INTO nilai_indeks_kami (id_stakeholder, no_registrasi_csirt, id_penilaian, nama_stakeholder, waktu_penilaian, nilai_kerangka_kerja, nilai_tata_kelola, nilai_pengelolaan_aset, nilai_teknologi, nilai_pdp, nilai_risiko, suplemen, nilai_akhir, created_at) VALUES
('001', '083/CSIRT.01.10/BSSN/07/2022', '00001', 'Lembaga AAAA', '2024-01-01', 192, 126, 258, 186, 84, 72, 100, 918, '2026-01-15 10:30:45'),
('002', '123/CSIRT.01.10/BSSN/11/2022', '00002', 'Lembaga BBBB', '2024-01-02', 180, 110, 220, 156, 72, 70, 80, 823, '2026-01-22 14:15:30'),
('003', '156/CSIRT.01.05/BSSN/04/2023', '00003', 'Lembaga CCCC', '2024-01-03', 168, 94, 182, 126, 60, 68, 60, 788, '2026-02-05 09:45:20'),
('004', '236/CSIRT.0105/BSSN/08/2023', '00004', 'Lembaga DDDD', '2024-01-04', 156, 78, 144, 133, 63, 66, 40, 678, '2026-02-12 16:20:10'),
('005', '146/CSIRT.01.05/BSSN/02/2023', '00005', 'Lembaga EEEE', '2024-01-05', 144, 62, 106, 108, 62, 64, 40, 876, '2026-02-28 11:30:50'),
('006', '130/CSIRT.01.05/BSSN/12/2022', '00006', 'Lembaga FFFF', '2024-01-06', 132, 46, 108, 99, 65, 62, 30, 773, '2026-03-08 13:45:15'),
('007', '168/CSIRT.01.05/BSSN/05/2023', '00007', 'Lembaga GGGG', '2024-01-07', 120, 30, 110, 96, 56, 60, 35, 721, '2026-03-18 15:20:40'),
('008', '227/CSIRT.01.05/BSSN/08/2023', '00008', 'Lembaga HHHH', '2024-01-08', 108, 14, 112, 93, 43, 58, 40, 678, '2026-03-25 10:15:25');