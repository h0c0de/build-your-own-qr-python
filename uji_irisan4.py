"""Irisan 4 — info format/versi terhitung + penalti.

32 nilai info format (4 level x 8 masker) hasil
BCH dibandingkan dengan yang terbaca dari matriks
segno; info versi v>=7 hal yang sama; skor penalti
samaku persis dengan evaluator segno pada matriks
pra-format untuk seluruh korpus contoh.
"""
import segno.encoder as enc

from uji_bersama import matriks_segno
import qr


def baca_format(m):
    """Baca 15 bit info format dari salinan kiri-atas
    matriks jadi (urutan penempatan spek)."""
    bit = [0] * 15
    for i in range(6):
        bit[i] = m[i][8]
    bit[6] = m[7][8]
    bit[7] = m[8][8]
    bit[8] = m[8][7]
    for i in range(9, 15):
        bit[i] = m[8][14 - i]
    return sum(b << i for i, b in enumerate(bit))


def baca_versi(m, n):
    bit = [m[i // 3][n - 11 + i % 3] for i in range(18)]
    return sum(b << i for i, b in enumerate(bit))


if __name__ == "__main__":
    cek = 0
    for level in "LMQH":
        for mk in range(8):
            m = matriks_segno("FORMAT", level, 2, "alfa",
                              mk)
            assert baca_format(m) == \
                qr.info_format(level, mk), (level, mk)
            cek += 1
    for v in (7, 10, 25, 40):
        m = matriks_segno("VERSI", "M", v, "alfa", 0)
        n = 17 + 4 * v
        assert baca_versi(m, n) == qr.info_versi(v), v
        cek += 1
    # penalti: samaku == evaluator segno (pra-format)
    contoh = [("HELLO WORLD", "Q"), ("1234567890", "M"),
              ("uji penalti versi besar", "H"),
              ("https://iniurl.my.id/x", "L")]
    for teks, level in contoh:
        versi, mode, _ = qr.enkode_data(teks, level)
        _, fungsi = qr._kerangka(versi)
        n = 17 + 4 * versi
        for mk in range(8):
            m = qr.buat(teks, level, mask=mk)
            pra = [[m[r][c] if not (fungsi[r][c] and
                    (r == 8 or c == 8 or
                     (versi >= 7 and
                      (r < 6 and c >= n - 11 or
                       c < 6 and r >= n - 11))))
                    else 0 for c in range(n)]
                   for r in range(n)]
            skor_s = enc.evaluate_mask(
                tuple(bytes(x) for x in pra), n, n)
            assert qr.penalti(pra) == skor_s, \
                (teks, mk)
            cek += 1
    print("irisan 4: %d pemeriksaan LULUS" % cek)
