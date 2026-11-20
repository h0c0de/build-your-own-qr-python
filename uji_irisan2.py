"""Irisan 2 — Reed-Solomon di GF(256).

Bukti aljabar (bukan hafalan): polinom generator
derajat n punya akar persis a^0..a^(n-1), dan
data+EC selalu bersindrom nol (habis dibagi
generator). Jangkar silang: EC HELLO WORLD yang
terekstrak dari matriks segno.
"""
import random

import qr

EC_EMAS = [168, 72, 22, 82, 217, 54, 156, 0, 46, 15,
           180, 122, 16]
DATA_EMAS = [0x20, 0x5B, 0x0B, 0x78, 0xD1, 0x72, 0xDC,
             0x4D, 0x43, 0x40, 0xEC, 0x11, 0xEC]


def nilai_poli(koef, x):
    """Evaluasi polinom (koefisien pangkat tertinggi
    dulu) di titik x dalam GF(256)."""
    hasil = 0
    for k in koef:
        hasil = qr.gf_kali(hasil, x) ^ k
    return hasil


if __name__ == "__main__":
    cek = 0
    # GF: a^255 = 1, log/exp saling balik
    assert qr.GF_EXP[255] == 1
    for v in range(1, 256):
        assert qr.GF_EXP[qr.GF_LOG[v]] == v
    cek += 2
    # akar generator
    for n in (7, 10, 13, 18, 30):
        g = qr.rs_generator(n)
        assert len(g) == n + 1 and g[0] == 1
        for i in range(n):
            assert nilai_poli(g, qr.GF_EXP[i]) == 0, (n, i)
        assert nilai_poli(g, qr.GF_EXP[n]) != 0
        cek += 1
    # jangkar contoh tutorial
    assert qr.rs_ec(DATA_EMAS, 13) == EC_EMAS
    cek += 1
    # sindrom nol pada data acak berbagai derajat
    acak = random.Random(25)
    for n in (7, 16, 22, 30):
        for _ in range(25):
            data = [acak.randrange(256)
                    for _ in range(acak.randrange(1, 60))]
            penuh = data + qr.rs_ec(data, n)
            g = qr.rs_generator(n)
            for i in range(n):
                assert nilai_poli(penuh,
                                  qr.GF_EXP[i]) == 0
            cek += 1
    print("irisan 2: %d pemeriksaan LULUS" % cek)
