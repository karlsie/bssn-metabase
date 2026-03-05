-- CREATE TABLE statement for PostgreSQL

CREATE TABLE kinerja_keamanan_siber (
    id_stakeholder VARCHAR(10) PRIMARY KEY,
    no_registrasi_csirt VARCHAR(50),
    nama_stakeholder VARCHAR(100),
    nilai_akhir_indeks_kami INTEGER,
    nilai_akhir_csm FLOAT,
    nilai_akhir_tmpi FLOAT,
    nilai_ikas FLOAT,
    rekomendasi FLOAT,
    created_at TIMESTAMP
);

-- convert above values to INSERT statements for PostgreSQL, add created_at with random timestamps within first 3 months in 2026 

INSERT INTO kinerja_keamanan_siber (id_stakeholder, no_registrasi_csirt, nama_stakeholder, nilai_akhir_indeks_kami, nilai_akhir_csm, nilai_akhir_tmpi, nilai_ikas, rekomendasi, created_at) VALUES
('001', '083/CSIRT.01.10/BSSN/07/2022', 'Lembaga AAAA', 918, 3.412, 4.3, 4.1, 0.8866666667, '2026-01-15 10:30:00'),
('002', '123/CSIRT.01.10/BSSN/11/2022', 'Lembaga BBBB', 823, 3.476, 3.2, 3.15, 0.9366666667, '2026-02-20 14:45:00'),
('003', '156/CSIRT.01.05/BSSN/04/2023', 'Lembaga CCCC', 788, 3.772, 2.5, 2.45, 0.9866666667, '2026-03-10 09:15:00'),
('004', '236/CSIRT.0105/BSSN/08/2023', 'Lembaga DDDD', 678, 3.852, 2.3, 2.35, 1.036666667, '2026-01-25 11:20:00'),
('005', '146/CSIRT.01.05/BSSN/02/2023', 'Lembaga EEEE', 876, 3.93, 3.3, 3.33, 1.086666667, '2026-02-18 13:35:00'),
('006', '130/CSIRT.01.05/BSSN/12/2022', 'Lembaga FFFF', 773, 3.956, 2.5, 2.6, 1.136666667, '2026-03-05 16:45:00'),
('007', '168/CSIRT.01.05/BSSN/05/2023', 'Lembaga GGGG', 721, 4.348, 2.5, 2.57, 1.186666667, '2026-01-30 14:55:00'),
('008', '227/CSIRT.01.05/BSSN/08/2023', 'Lembaga HHHH', 678, 3.406, 2.3, 2.67, 1.236666667, '2026-02-25 11:20:00');