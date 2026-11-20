"""Irisan 1 — enkode data.

Jangkar emas tutorial Thonky (HELLO WORLD 1-Q,
dibaca langsung dari halaman enkode data) +
pemilihan mode/versi vs segno pada korpus.
"""
import qr

DATA_EMAS = [0x20, 0x5B, 0x0B, 0x78, 0xD1, 0x72, 0xDC,
             0x4D, 0x43, 0x40, 0xEC, 0x11, 0xEC]

if __name__ == "__main__":
    cek = 0
    v, mode, cw = qr.enkode_data("HELLO WORLD", "Q")
    assert (v, mode) == (1, "alfa"), (v, mode)
    assert cw == DATA_EMAS, cw
    cek += 1
    # mode otomatis
    assert qr.pilih_mode("0123456789") == "numerik"
    assert qr.pilih_mode("HELLO $WORLD") == "alfa"
    assert qr.pilih_mode("halo dunia") == "byte"
    assert qr.pilih_mode("") == "byte"
    cek += 4
    # numerik: "123" -> mode 0001, jumlah 0000000011,
    # data 0001111011; tiga byte pertama aliran:
    # 00010000 00001100 01111011
    v, mode, cw = qr.enkode_data("123", "L", versi=1)
    assert cw[0] == 0b00010000 and cw[1] == 0b00001100
    assert cw[2] == 0b01111011
    cek += 1
    # byte: 'a' = 0x61 sesudah mode 0100 + jumlah
    # 8 bit (00000001): aliran 01000000 00010110 ...
    v, mode, cw = qr.enkode_data("a", "L", versi=1)
    assert mode == "byte"
    assert cw[0] == 0b01000000 and cw[1] == 0b00010110
    cek += 2
    # kapasitas: versi naik tepat saat perlu
    v, _, _ = qr.enkode_data("A" * 16, "Q")
    assert v == 1  # 16 karakter alfa muat di 1-Q
    v, _, _ = qr.enkode_data("A" * 17, "Q")
    assert v == 2
    cek += 2
    # terlalu panjang -> galat, bukan diam-diam salah
    try:
        qr.enkode_data("x" * 3000, "L")
        raise SystemExit("harusnya GalatQR")
    except qr.GalatQR:
        cek += 1
    print("irisan 1: %d pemeriksaan LULUS" % cek)
