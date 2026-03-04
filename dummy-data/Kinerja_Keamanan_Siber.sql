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

-- convert above values to INSERT statements for PostgreSQL, removed created_at

INSERT INTO kinerja_keamanan_siber (id_stakeholder, no_registrasi_csirt, nama_stakeholder, nilai_akhir_indeks_kami, nilai_akhir_csm, nilai_akhir_tmpi, nilai_ikas, rekomendasi) VALUES
('001', '083/CSIRT.01.10/BSSN/07/2022', 'Lembaga AAAA', 918, 3.412, 4.3, 4.1, 0.8866666667),
('002', '123/CSIRT.01.10/BSSN/11/2022', 'Lembaga BBBB', 823, 3.476, 3.2, 3.15, 0.9366666667),
('003', '156/CSIRT.01.05/BSSN/04/2023', 'Lembaga CCCC', 788, 3.772, 2.5, 2.45, 0.9866666667),
('004', '236/CSIRT.0105/BSSN/08/2023', 'Lembaga DDDD', 678, 3.852, 2.3, 2.35, 1.036666667),
('005', '146/CSIRT.01.05/BSSN/02/2023', 'Lembaga EEEE', 876, 3.93, 3.3, 3.33, 1.086666667),
('006', '130/CSIRT.01.05/BSSN/12/2022', 'Lembaga FFFF', 773, 3.956, 2.5, 2.6, 1.136666667),
('007', '168/CSIRT.01.05/BSSN/05/2023', 'Lembaga GGGG', 721, 4.348, 2.5, 2.57, 1.186666667),
('008', '227/CSIRT.01.05/BSSN/08/2023', 'Lembaga HHHH', 678, 3.406, 2.3, 2.67, 1.236666667);