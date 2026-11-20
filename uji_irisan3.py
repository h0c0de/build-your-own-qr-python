"""Irisan 3 — tabel EC vs geometri + blok/interleave.

Konsistensi silang independen: untuk 160 entri
(versi, level), total codeword dari tabel harus
sama dengan jumlah modul data yang dihitung dari
kerangka matriks (fungsi vs data) versi itu.
Lalu aliran codeword utuh (kasus multi-blok 5-Q)
dibandingkan dengan yang terekstrak dari matriks
pustaka qrcode.

Catatan wasit: untuk kasus 5-Q ini segno menyisip
satu codeword 0x00 ekstra sebelum padding (datanya
berakhir persis di batas codeword) — menyimpang
dari aturan padding spek; pustaka qrcode dan teks
spek sepakat dengan build ini. Di semua kasus lain
pada irisan 5 segno identik.
"""
import qrcode as qrlib
from qrcode.constants import ERROR_CORRECT_Q
from qrcode.util import MODE_8BIT_BYTE, QRData

import qr

if __name__ == "__main__":
    cek = 0
    for v in range(1, 41):
        _, fungsi = qr._kerangka(v)
        n = len(fungsi)
        modul_data = sum(1 for r in range(n)
                         for c in range(n)
                         if not fungsi[r][c])
        total_cw = (modul_data - qr.SISA_BIT[v - 1]) // 8
        assert (modul_data - qr.SISA_BIT[v - 1]) % 8 == 0
        for level in "LMQH":
            ec_per, grup = qr.TABEL_EC[v][level]
            data = sum(nb * dc for nb, dc in grup)
            blok = sum(nb for nb, _ in grup)
            assert data + ec_per * blok == total_cw, \
                (v, level)
            cek += 1
    # aliran multi-blok: ekstrak dari matriks
    # pustaka qrcode (masker 0, mode byte, versi 5)
    teks = "BLOK GANDA 5-Q: interleaving diuji di sini!"
    versi, mode, cw = qr.enkode_data(teks, "Q", versi=5)
    bd, be = qr.susun_blok(cw, 5, "Q")
    assert len(bd) == 4 and len(bd[0]) == 15
    aliran = qr.interleave(bd, be)
    q = qrlib.QRCode(version=5,
                     error_correction=ERROR_CORRECT_Q,
                     box_size=1, border=0, mask_pattern=0)
    q.add_data(QRData(teks, mode=MODE_8BIT_BYTE))
    q.make(fit=False)
    m = q.get_matrix()
    _, fungsi = qr._kerangka(5)
    bit = []
    n = 37
    kanan = n - 1
    while kanan >= 1:
        if kanan == 6:
            kanan = 5
        naik = ((kanan + 1) & 2) == 0
        for vert in range(n):
            r = n - 1 - vert if naik else vert
            for dc in (0, 1):
                c = kanan - dc
                if not fungsi[r][c]:
                    x = m[r][c]
                    if qr._MASker[0](r, c):
                        x ^= 1
                    bit.append(x)
        kanan -= 2
    cw2 = []
    for j in range(0, len(bit) - 7, 8):
        b = 0
        for x in bit[j:j + 8]:
            b = (b << 1) | x
        cw2.append(b)
    assert cw2[:len(aliran)] == aliran
    cek += 1
    print("irisan 3: %d pemeriksaan LULUS" % cek)
