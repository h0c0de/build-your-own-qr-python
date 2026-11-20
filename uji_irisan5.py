"""Irisan 5 — final: diferensial matriks penuh.

(1) Sapuan versi 1-40 x level L/M/Q/H dengan masker
    paksa bergilir: matriks identik segno.
(2) Korpus otomatis penuh (mode/versi/masker
    dipilih sendiri oleh kedua pihak): identik.
(3) Pendapat ketiga: pustaka qrcode pada sampel.
(4) Tepi kapasitas versi 40-L byte.
"""
import qrcode as qrlib

from uji_bersama import matriks_segno, beda
import qr

KORPUS = [
    ("HELLO WORLD", "Q"), ("12345678901234567890", "L"),
    ("Proyek QR 130y.tech — v2!", "M"),
    ("https://github.com/h0c0de", "Q"),
    ("a", "H"), ("Z" * 100, "M"),
    ("Campur 123 dan huruf kecil é", "L"),
    ("0123456789" * 50, "Q"),
    ("BYTE mode dengan unicode ✓✓✓", "H"),
    ("Teks sedang untuk memaksa versi belasan " * 3, "M"),
    ("x" * 500, "L"), ("9" * 1500, "M"),
]

if __name__ == "__main__":
    cek = 0
    # (1) sapuan versi/level, masker paksa bergilir
    for v in range(1, 41):
        for j, level in enumerate("LMQH"):
            mk = (v + j) % 8
            teks = "UJI%d" % v
            m = qr.buat(teks, level, versi=v, mask=mk)
            s = matriks_segno(teks, level, v, "alfa", mk)
            assert beda(m, s) == 0, (v, level, mk)
            cek += 1
    # (2) otomatis penuh. Pengecualian terdokumentasi:
    # bila data+terminator berakhir PERSIS di batas
    # codeword, segno menyisipkan satu byte 0x00
    # sebelum padding EC/11 — menyimpang dari spek;
    # kasus tepi itu diverifikasi ke pustaka qrcode.
    def kasus_tepi(teks, level):
        versi, mode, _ = qr.enkode_data(teks, level)
        pj = qr._PANJANG_JUMLAH[mode][qr._grup_versi(versi)]
        pakai = 4 + pj + len(qr._bit_data(teks, mode))
        kap = qr.kapasitas_data(versi, level) * 8
        term = min(4, kap - pakai)
        return (pakai + term) % 8 == 0 and \
            pakai + term < kap

    for teks, level in KORPUS:
        m = qr.buat(teks, level)
        versi, mode, _ = qr.enkode_data(teks, level)
        if kasus_tepi(teks, level):
            # kasus tepi segno: verifikasi (a) matriks
            # identik pustaka qrcode pada masker yang
            # qrcode pilih, (b) pilihan masker otomatis
            # build ini == argmin evaluator ISO segno
            # atas kandidat pra-format milikku sendiri
            q = qrlib.QRCode(
                version=versi,
                error_correction={
                    "L": qrlib.constants.ERROR_CORRECT_L,
                    "M": qrlib.constants.ERROR_CORRECT_M,
                    "Q": qrlib.constants.ERROR_CORRECT_Q,
                    "H": qrlib.constants.ERROR_CORRECT_H}[level],
                box_size=1, border=0)
            from qrcode.util import QRData, MODE_NUMBER, \
                MODE_ALPHA_NUM, MODE_8BIT_BYTE
            q.add_data(QRData(teks, mode={
                "numerik": MODE_NUMBER, "alfa": MODE_ALPHA_NUM,
                "byte": MODE_8BIT_BYTE}[mode]))
            q.make(fit=False)
            qm = q.get_matrix()
            bitf = [0] * 15
            for i in range(6):
                bitf[i] = qm[i][8]
            bitf[6] = qm[7][8]
            bitf[7] = qm[8][8]
            bitf[8] = qm[8][7]
            for i in range(9, 15):
                bitf[i] = qm[8][14 - i]
            fval = sum(b << i for i, b in enumerate(bitf))
            mk_q = next(k for k in range(8)
                        if qr.info_format(level, k) == fval)
            assert beda(qr.buat(teks, level, mask=mk_q),
                        qm) == 0, (teks[:20], level,
                                   "tepi: beda dari qrcode")
            import segno.encoder as _enc
            _, fungsi = qr._kerangka(versi)
            n = 17 + 4 * versi
            skor = []
            for k in range(8):
                mm = qr.buat(teks, level, mask=k)
                pra = [[mm[r][c] if not (fungsi[r][c] and
                        (r == 8 or c == 8 or
                         (versi >= 7 and
                          (r < 6 and c >= n - 11 or
                           c < 6 and r >= n - 11))))
                        else 0 for c in range(n)]
                       for r in range(n)]
                skor.append(_enc.evaluate_mask(
                    tuple(bytes(x) for x in pra), n, n))
            mk_iso = min(range(8), key=lambda k: (skor[k], k))
            assert m == qr.buat(teks, level, mask=mk_iso), \
                (teks[:20], level, "tepi: masker ISO")
        else:
            s = matriks_segno(teks, level, versi, mode,
                              None)
            assert beda(m, s) == 0, (teks[:20], level)
        cek += 1
    # (3) pendapat ketiga: pustaka qrcode
    for teks, level in KORPUS[:6]:
        versi, mode, _ = qr.enkode_data(teks, level)
        mk = 3
        m = qr.buat(teks, level, versi=versi, mask=mk)
        q = qrlib.QRCode(
            version=versi, error_correction={
                "L": qrlib.constants.ERROR_CORRECT_L,
                "M": qrlib.constants.ERROR_CORRECT_M,
                "Q": qrlib.constants.ERROR_CORRECT_Q,
                "H": qrlib.constants.ERROR_CORRECT_H}[level],
            box_size=1, border=0, mask_pattern=mk)
        q.add_data(teks)
        q.make(fit=False)
        lain = q.get_matrix()
        assert beda(m, lain) == 0, (teks[:20], level)
        cek += 1
    # (4) tepi kapasitas 40-L byte: 2953 pas, 2954 gagal
    m = qr.buat("y" * 2953, "L")
    assert len(m) == 177
    cek += 1
    try:
        qr.buat("y" * 2954, "L")
        raise SystemExit("2954 harusnya GalatQR")
    except qr.GalatQR:
        cek += 1
    print("irisan 5: %d pemeriksaan LULUS" % cek)
