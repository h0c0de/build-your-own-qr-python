"""Generator QR Code (ISO/IEC 18004) dalam Python.

Mengikuti Thonky QR Code Tutorial langkah demi
langkah: enkode data (numerik/alfanumerik/byte),
Reed-Solomon di GF(256), interleaving blok,
penempatan modul, 8 masker dengan penilaian
penalti spek, dan info format/versi terhitung
dengan BCH — tanpa tabel hafalan untuk keduanya.
"""

# ----------------------------------------------------------------
# GF(256): primitif 0x11D (x^8+x^4+x^3+x^2+1), generator 2
# ----------------------------------------------------------------

GF_EXP = [0] * 512
GF_LOG = [0] * 256
_x = 1
for _i in range(255):
    GF_EXP[_i] = _x
    GF_LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D
for _i in range(255, 512):
    GF_EXP[_i] = GF_EXP[_i - 255]


def gf_kali(a, b):
    if a == 0 or b == 0:
        return 0
    return GF_EXP[GF_LOG[a] + GF_LOG[b]]


def rs_generator(n):
    """Polinom generator derajat n:
    hasil kali (x - a^i) untuk i = 0..n-1.
    Koefisien dari pangkat tertinggi ke terendah."""
    hasil = [1]
    for i in range(n):
        baru = [0] * (len(hasil) + 1)
        for j, koef in enumerate(hasil):
            # kali (x + a^i): suku x tetap di indeks j,
            # suku tetapan a^i * koef di indeks j + 1
            baru[j] ^= koef
            baru[j + 1] ^= gf_kali(koef, GF_EXP[i])
        hasil = baru
    return hasil


def rs_ec(data, n):
    """Codeword koreksi: sisa pembagian
    data * x^n oleh polinom generator derajat n."""
    gen = rs_generator(n)
    sisa = [0] * n
    for b in data:
        faktor = b ^ sisa.pop(0)
        sisa.append(0)
        for j in range(n):
            sisa[j] ^= gf_kali(gen[j + 1], faktor)
    return sisa


# ----------------------------------------------------------------
# Tabel EC: per (versi, level) ->
# (ec per blok, ((blok grup1, data per blok),
#                (blok grup2, data per blok)))
# Sumber: tabel Thonky; konsistensinya dibuktikan
# silang vs geometri matriks di uji_irisan3.
# ----------------------------------------------------------------

TABEL_EC = {
    1:  {"L": (7,  ((1, 19),)),  "M": (10, ((1, 16),)),
         "Q": (13, ((1, 13),)),  "H": (17, ((1, 9),))},
    2:  {"L": (10, ((1, 34),)),  "M": (16, ((1, 28),)),
         "Q": (22, ((1, 22),)),  "H": (28, ((1, 16),))},
    3:  {"L": (15, ((1, 55),)),  "M": (26, ((1, 44),)),
         "Q": (18, ((2, 17),)),  "H": (22, ((2, 13),))},
    4:  {"L": (20, ((1, 80),)),  "M": (18, ((2, 32),)),
         "Q": (26, ((2, 24),)),  "H": (16, ((4, 9),))},
    5:  {"L": (26, ((1, 108),)), "M": (24, ((2, 43),)),
         "Q": (18, ((2, 15), (2, 16))),
         "H": (22, ((2, 11), (2, 12)))},
    6:  {"L": (18, ((2, 68),)),  "M": (16, ((4, 27),)),
         "Q": (24, ((4, 19),)),  "H": (28, ((4, 15),))},
    7:  {"L": (20, ((2, 78),)),  "M": (18, ((4, 31),)),
         "Q": (18, ((2, 14), (4, 15))),
         "H": (26, ((4, 13), (1, 14)))},
    8:  {"L": (24, ((2, 97),)),
         "M": (22, ((2, 38), (2, 39))),
         "Q": (22, ((4, 18), (2, 19))),
         "H": (26, ((4, 14), (2, 15)))},
    9:  {"L": (30, ((2, 116),)),
         "M": (22, ((3, 36), (2, 37))),
         "Q": (20, ((4, 16), (4, 17))),
         "H": (24, ((4, 12), (4, 13)))},
    10: {"L": (18, ((2, 68), (2, 69))),
         "M": (26, ((4, 43), (1, 44))),
         "Q": (24, ((6, 19), (2, 20))),
         "H": (28, ((6, 15), (2, 16)))},
    11: {"L": (20, ((4, 81),)),
         "M": (30, ((1, 50), (4, 51))),
         "Q": (28, ((4, 22), (4, 23))),
         "H": (24, ((3, 12), (8, 13)))},
    12: {"L": (24, ((2, 92), (2, 93))),
         "M": (22, ((6, 36), (2, 37))),
         "Q": (26, ((4, 20), (6, 21))),
         "H": (28, ((7, 14), (4, 15)))},
    13: {"L": (26, ((4, 107),)),
         "M": (22, ((8, 37), (1, 38))),
         "Q": (24, ((8, 20), (4, 21))),
         "H": (22, ((12, 11), (4, 12)))},
    14: {"L": (30, ((3, 115), (1, 116))),
         "M": (24, ((4, 40), (5, 41))),
         "Q": (20, ((11, 16), (5, 17))),
         "H": (24, ((11, 12), (5, 13)))},
    15: {"L": (22, ((5, 87), (1, 88))),
         "M": (24, ((5, 41), (5, 42))),
         "Q": (30, ((5, 24), (7, 25))),
         "H": (24, ((11, 12), (7, 13)))},
    16: {"L": (24, ((5, 98), (1, 99))),
         "M": (28, ((7, 45), (3, 46))),
         "Q": (24, ((15, 19), (2, 20))),
         "H": (30, ((3, 15), (13, 16)))},
    17: {"L": (28, ((1, 107), (5, 108))),
         "M": (28, ((10, 46), (1, 47))),
         "Q": (28, ((1, 22), (15, 23))),
         "H": (28, ((2, 14), (17, 15)))},
    18: {"L": (30, ((5, 120), (1, 121))),
         "M": (26, ((9, 43), (4, 44))),
         "Q": (28, ((17, 22), (1, 23))),
         "H": (28, ((2, 14), (19, 15)))},
    19: {"L": (28, ((3, 113), (4, 114))),
         "M": (26, ((3, 44), (11, 45))),
         "Q": (26, ((17, 21), (4, 22))),
         "H": (26, ((9, 13), (16, 14)))},
    20: {"L": (28, ((3, 107), (5, 108))),
         "M": (26, ((3, 41), (13, 42))),
         "Q": (30, ((15, 24), (5, 25))),
         "H": (28, ((15, 15), (10, 16)))},
    21: {"L": (28, ((4, 116), (4, 117))),
         "M": (26, ((17, 42),)),
         "Q": (28, ((17, 22), (6, 23))),
         "H": (30, ((19, 16), (6, 17)))},
    22: {"L": (28, ((2, 111), (7, 112))),
         "M": (28, ((17, 46),)),
         "Q": (30, ((7, 24), (16, 25))),
         "H": (24, ((34, 13),))},
    23: {"L": (30, ((4, 121), (5, 122))),
         "M": (28, ((4, 47), (14, 48))),
         "Q": (30, ((11, 24), (14, 25))),
         "H": (30, ((16, 15), (14, 16)))},
    24: {"L": (30, ((6, 117), (4, 118))),
         "M": (28, ((6, 45), (14, 46))),
         "Q": (30, ((11, 24), (16, 25))),
         "H": (30, ((30, 16), (2, 17)))},
    25: {"L": (26, ((8, 106), (4, 107))),
         "M": (28, ((8, 47), (13, 48))),
         "Q": (30, ((7, 24), (22, 25))),
         "H": (30, ((22, 15), (13, 16)))},
    26: {"L": (28, ((10, 114), (2, 115))),
         "M": (28, ((19, 46), (4, 47))),
         "Q": (28, ((28, 22), (6, 23))),
         "H": (30, ((33, 16), (4, 17)))},
    27: {"L": (30, ((8, 122), (4, 123))),
         "M": (28, ((22, 45), (3, 46))),
         "Q": (30, ((8, 23), (26, 24))),
         "H": (30, ((12, 15), (28, 16)))},
    28: {"L": (30, ((3, 117), (10, 118))),
         "M": (28, ((3, 45), (23, 46))),
         "Q": (30, ((4, 24), (31, 25))),
         "H": (30, ((11, 15), (31, 16)))},
    29: {"L": (30, ((7, 116), (7, 117))),
         "M": (28, ((21, 45), (7, 46))),
         "Q": (30, ((1, 23), (37, 24))),
         "H": (30, ((19, 15), (26, 16)))},
    30: {"L": (30, ((5, 115), (10, 116))),
         "M": (28, ((19, 47), (10, 48))),
         "Q": (30, ((15, 24), (25, 25))),
         "H": (30, ((23, 15), (25, 16)))},
    31: {"L": (30, ((13, 115), (3, 116))),
         "M": (28, ((2, 46), (29, 47))),
         "Q": (30, ((42, 24), (1, 25))),
         "H": (30, ((23, 15), (28, 16)))},
    32: {"L": (30, ((17, 115),)),
         "M": (28, ((10, 46), (23, 47))),
         "Q": (30, ((10, 24), (35, 25))),
         "H": (30, ((19, 15), (35, 16)))},
    33: {"L": (30, ((17, 115), (1, 116))),
         "M": (28, ((14, 46), (21, 47))),
         "Q": (30, ((29, 24), (19, 25))),
         "H": (30, ((11, 15), (46, 16)))},
    34: {"L": (30, ((13, 115), (6, 116))),
         "M": (28, ((14, 46), (23, 47))),
         "Q": (30, ((44, 24), (7, 25))),
         "H": (30, ((59, 16), (1, 17)))},
    35: {"L": (30, ((12, 121), (7, 122))),
         "M": (28, ((12, 47), (26, 48))),
         "Q": (30, ((39, 24), (14, 25))),
         "H": (30, ((22, 15), (41, 16)))},
    36: {"L": (30, ((6, 121), (14, 122))),
         "M": (28, ((6, 47), (34, 48))),
         "Q": (30, ((46, 24), (10, 25))),
         "H": (30, ((2, 15), (64, 16)))},
    37: {"L": (30, ((17, 122), (4, 123))),
         "M": (28, ((29, 46), (14, 47))),
         "Q": (30, ((49, 24), (10, 25))),
         "H": (30, ((24, 15), (46, 16)))},
    38: {"L": (30, ((4, 122), (18, 123))),
         "M": (28, ((13, 46), (32, 47))),
         "Q": (30, ((48, 24), (14, 25))),
         "H": (30, ((42, 15), (32, 16)))},
    39: {"L": (30, ((20, 117), (4, 118))),
         "M": (28, ((40, 47), (7, 48))),
         "Q": (30, ((43, 24), (22, 25))),
         "H": (30, ((10, 15), (67, 16)))},
    40: {"L": (30, ((19, 118), (6, 119))),
         "M": (28, ((18, 47), (31, 48))),
         "Q": (30, ((34, 24), (34, 25))),
         "H": (30, ((20, 15), (61, 16)))},
}


def kapasitas_data(versi, level):
    """Total codeword data untuk (versi, level)."""
    _, grup = TABEL_EC[versi][level]
    return sum(nb * dc for nb, dc in grup)


# ----------------------------------------------------------------
# Enkode data
# ----------------------------------------------------------------

ALFANUMERIK = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
_MODE_BITS = {"numerik": 0b0001, "alfa": 0b0010,
              "byte": 0b0100}
# panjang indikator jumlah per grup versi (1-9, 10-26, 27-40)
_PANJANG_JUMLAH = {
    "numerik": (10, 12, 14),
    "alfa": (9, 11, 13),
    "byte": (8, 16, 16),
}


class GalatQR(Exception):
    pass


def pilih_mode(teks):
    if teks and all(c in "0123456789" for c in teks):
        return "numerik"
    if teks and all(c in ALFANUMERIK for c in teks):
        return "alfa"
    return "byte"


def _grup_versi(versi):
    return 0 if versi <= 9 else (1 if versi <= 26 else 2)


def _bit_data(teks, mode):
    """Bit data saja (tanpa indikator mode/jumlah)."""
    bit = []
    if mode == "numerik":
        for j in range(0, len(teks), 3):
            potong = teks[j:j + 3]
            lebar = {1: 4, 2: 7, 3: 10}[len(potong)]
            v = int(potong)
            bit.extend((v >> k) & 1
                       for k in range(lebar - 1, -1, -1))
    elif mode == "alfa":
        nilai = [ALFANUMERIK.index(c) for c in teks]
        for j in range(0, len(nilai) - 1, 2):
            v = nilai[j] * 45 + nilai[j + 1]
            bit.extend((v >> k) & 1
                       for k in range(10, -1, -1))
        if len(nilai) % 2:
            v = nilai[-1]
            bit.extend((v >> k) & 1
                       for k in range(5, -1, -1))
    else:  # byte: UTF-8
        for b in teks.encode("utf-8"):
            bit.extend((b >> k) & 1
                       for k in range(7, -1, -1))
    return bit


def _jumlah_karakter(teks, mode):
    if mode == "byte":
        return len(teks.encode("utf-8"))
    return len(teks)


def enkode_data(teks, level, versi=None, mode=None):
    """-> (versi, mode, daftar codeword data penuh
    termasuk terminator + padding)."""
    if not teks:
        raise GalatQR("teks kosong")
    mode = mode or pilih_mode(teks)
    data_bit = _bit_data(teks, mode)
    jumlah = _jumlah_karakter(teks, mode)

    def muat(v):
        pj = _PANJANG_JUMLAH[mode][_grup_versi(v)]
        return 4 + pj + len(data_bit) <= \
            kapasitas_data(v, level) * 8

    if versi is None:
        for v in range(1, 41):
            if muat(v):
                versi = v
                break
        else:
            raise GalatQR("teks terlalu panjang")
    elif not muat(versi):
        raise GalatQR("tidak muat di versi %d" % versi)
    pj = _PANJANG_JUMLAH[mode][_grup_versi(versi)]
    if jumlah >= (1 << pj):
        raise GalatQR("jumlah karakter meluap")
    bit = []
    bit.extend((_MODE_BITS[mode] >> k) & 1
               for k in range(3, -1, -1))
    bit.extend((jumlah >> k) & 1
               for k in range(pj - 1, -1, -1))
    bit.extend(data_bit)
    kapasitas = kapasitas_data(versi, level) * 8
    # terminator s.d. 4 nol, lalu ratakan ke byte
    bit.extend([0] * min(4, kapasitas - len(bit)))
    while len(bit) % 8:
        bit.append(0)
    codeword = []
    for j in range(0, len(bit), 8):
        b = 0
        for bitke in bit[j:j + 8]:
            b = (b << 1) | bitke
        codeword.append(b)
    pad = (0xEC, 0x11)
    i = 0
    while len(codeword) < kapasitas // 8:
        codeword.append(pad[i % 2])
        i += 1
    return versi, mode, codeword


# ----------------------------------------------------------------
# Blok + interleaving
# ----------------------------------------------------------------

def susun_blok(codeword, versi, level):
    """-> (blok_data, blok_ec) mengikuti grup tabel."""
    ec_per, grup = TABEL_EC[versi][level]
    blok_data = []
    pos = 0
    for nb, dc in grup:
        for _ in range(nb):
            blok_data.append(codeword[pos:pos + dc])
            pos += dc
    assert pos == len(codeword)
    blok_ec = [rs_ec(b, ec_per) for b in blok_data]
    return blok_data, blok_ec


def interleave(blok_data, blok_ec):
    """Codeword akhir: data selang-seling per kolom
    blok, lalu EC selang-seling dengan cara sama."""
    hasil = []
    for daftar in (blok_data, blok_ec):
        for kol in range(max(len(b) for b in daftar)):
            for blok in daftar:
                if kol < len(blok):
                    hasil.append(blok[kol])
    return hasil


# ----------------------------------------------------------------
# Matriks
# ----------------------------------------------------------------

# koordinat pusat pola alignment per versi (spek)
ALIGNMENT = {
    1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30],
    6: [6, 34], 7: [6, 22, 38], 8: [6, 24, 42],
    9: [6, 26, 46], 10: [6, 28, 50], 11: [6, 30, 54],
    12: [6, 32, 58], 13: [6, 34, 62],
    14: [6, 26, 46, 66], 15: [6, 26, 48, 70],
    16: [6, 26, 50, 74], 17: [6, 30, 54, 78],
    18: [6, 30, 56, 82], 19: [6, 30, 58, 86],
    20: [6, 34, 62, 90], 21: [6, 28, 50, 72, 94],
    22: [6, 26, 50, 74, 98], 23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106], 25: [6, 32, 58, 84, 110],
    26: [6, 30, 58, 86, 114], 27: [6, 34, 62, 90, 118],
    28: [6, 26, 50, 74, 98, 122],
    29: [6, 30, 54, 78, 102, 126],
    30: [6, 26, 52, 78, 104, 130],
    31: [6, 30, 56, 82, 108, 134],
    32: [6, 34, 60, 86, 112, 138],
    33: [6, 30, 58, 86, 114, 142],
    34: [6, 34, 62, 90, 118, 146],
    35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154],
    37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162],
    39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170],
}

# bit sisa per versi 1..40
SISA_BIT = ([0] + [7] * 5 + [0] * 7 + [3] * 7 + [4] * 7
            + [3] * 7 + [0] * 6)
assert len(SISA_BIT) == 40

_BIT_EC_FORMAT = {"L": 1, "M": 0, "Q": 3, "H": 2}


def _bit(v, i):
    return (v >> i) & 1


def info_format(level, mask):
    """15 bit info format, terhitung via BCH (0x537)
    lalu ditopeng 0x5412 — bukan tabel hafalan."""
    data = (_BIT_EC_FORMAT[level] << 3) | mask
    sisa = data
    for _ in range(10):
        sisa = (sisa << 1) ^ ((sisa >> 9) * 0x537)
    return ((data << 10) | sisa) ^ 0x5412


def info_versi(versi):
    """18 bit info versi (v >= 7) via BCH 0x1F25."""
    sisa = versi
    for _ in range(12):
        sisa = (sisa << 1) ^ ((sisa >> 11) * 0x1F25)
    return (versi << 12) | sisa


def _kerangka(versi):
    """Matriks + peta fungsi. Nilai awal modul fungsi
    diisi; info format ditulis belakangan (tergantung
    masker). Mengembalikan (matriks, fungsi)."""
    n = 17 + 4 * versi
    m = [[0] * n for _ in range(n)]
    fungsi = [[False] * n for _ in range(n)]

    def taruh(r, c, v):
        if 0 <= r < n and 0 <= c < n:
            m[r][c] = v
            fungsi[r][c] = True

    # timing lebih dulu (akan ditimpa finder/alignment)
    for i in range(n):
        v = 1 if i % 2 == 0 else 0
        taruh(6, i, v)
        taruh(i, 6, v)
    # pola finder + separator
    for r0, c0 in ((0, 0), (0, n - 7), (n - 7, 0)):
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                gelap = (0 <= dr <= 6 and dc in (0, 6)) or \
                    (0 <= dc <= 6 and dr in (0, 6)) or \
                    (2 <= dr <= 4 and 2 <= dc <= 4)
                taruh(r0 + dr, c0 + dc, 1 if gelap else 0)
    # pola alignment — lewati hanya tiga kombinasi
    # pojok finder; pusat di garis timing (6, x) /
    # (x, 6) TETAP digambar (menimpa timing)
    koord = ALIGNMENT[versi]
    for r in koord:
        for c in koord:
            if (r == koord[0] and c == koord[0]) or \
                    (r == koord[0] and c == koord[-1]) or \
                    (r == koord[-1] and c == koord[0]):
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    gelap = max(abs(dr), abs(dc)) != 1
                    taruh(r + dr, c + dc, 1 if gelap else 0)
    # cadangan info format (nilai sementara 0);
    # (8,6) dan (6,8) adalah modul timing — jangan
    # ditimpa
    for i in range(9):
        if i != 6:
            taruh(8, i, 0)
            taruh(i, 8, 0)
    for i in range(8):
        taruh(8, n - 1 - i, 0)
        taruh(n - 1 - i, 8, 0)
    taruh(n - 8, 8, 1)  # modul gelap
    # area info versi (v >= 7) dicadangkan sebagai
    # fungsi bernilai 0 — isinya ditulis di akhir,
    # sesudah masker dipilih (penilaian masker spek
    # dilakukan TANPA info format & versi)
    if versi >= 7:
        for i in range(18):
            taruh(i // 3, n - 11 + i % 3, 0)
            taruh(n - 11 + i % 3, i // 3, 0)
    return m, fungsi


def _tulis_versi(m, n, versi):
    if versi < 7:
        return
    for i in range(18):
        v = _bit(info_versi(versi), i)
        m[i // 3][n - 11 + i % 3] = v
        m[n - 11 + i % 3][i // 3] = v


def _tulis_format(m, n, level, mask):
    f = info_format(level, mask)
    for i in range(6):
        m[i][8] = _bit(f, i)
    m[7][8] = _bit(f, 6)
    m[8][8] = _bit(f, 7)
    m[8][7] = _bit(f, 8)
    for i in range(9, 15):
        m[8][14 - i] = _bit(f, i)
    for i in range(8):
        m[8][n - 1 - i] = _bit(f, i)
    for i in range(8, 15):
        m[n - 15 + i][8] = _bit(f, i)
    m[n - 8][8] = 1


_MASker = [
    lambda r, c: (r + c) % 2 == 0,
    lambda r, c: r % 2 == 0,
    lambda r, c: c % 3 == 0,
    lambda r, c: (r + c) % 3 == 0,
    lambda r, c: (r // 2 + c // 3) % 2 == 0,
    lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
    lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
    lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
]


def penalti(m):
    """Skor penalti spek ISO 18004 Tabel 11 (N1-N4),
    dinilai atas matriks TANPA info format/versi.

    N1: run >= 5 sewarna di baris/kolom: 3 + lebihnya.
    N2: tiap jendela 2x2 sewarna: 3.
    N3: pola 1:1:3:1:1 yang didahului ATAU diikuti
        area terang selebar 4 modul: 40. Di tepi
        matriks, zona tenang virtual ikut dihitung —
        pola yang menempel tepi dengan sisi dalamnya
        terang tetap kena.
    N4: proporsi gelap: 10 per kelipatan 5% menjauhi
        50%.
    """
    n = len(m)
    skor = 0
    garis = [list(baris) for baris in m] + \
        [[m[r][c] for r in range(n)] for c in range(n)]
    pola = [1, 0, 1, 1, 1, 0, 1]
    for g in garis:
        run = 1
        for i in range(1, n):
            if g[i] == g[i - 1]:
                run += 1
            else:
                if run >= 5:
                    skor += run - 2
                run = 1
        if run >= 5:
            skor += run - 2
        # N3 dengan aturan tepi spek
        i = 0
        while i <= n - 7:
            if g[i:i + 7] == pola:
                sebelum = g[max(i - 4, 0):i]
                sesudah = g[i + 7:i + 11]
                if i == 0 or i == n - 7 or \
                        not any(sebelum) or \
                        not any(sesudah):
                    skor += 40
                    i += 7
                else:
                    i += 4
            else:
                i += 1
    for r in range(n - 1):
        for c in range(n - 1):
            if m[r][c] == m[r][c + 1] == m[r + 1][c] == \
                    m[r + 1][c + 1]:
                skor += 3
    gelap = sum(sum(baris) for baris in m)
    persen = gelap * 100.0 / (n * n)
    skor += 10 * int(abs(persen - 50) / 5)
    return skor


def buat(teks, level="M", versi=None, mode=None,
         mask=None):
    """-> matriks modul (list baris, 1 = gelap),
    tanpa zona tenang."""
    versi, mode, codeword = enkode_data(
        teks, level, versi, mode)
    blok_data, blok_ec = susun_blok(codeword, versi,
                                    level)
    akhir = interleave(blok_data, blok_ec)
    bit = []
    for b in akhir:
        bit.extend((b >> k) & 1 for k in range(7, -1, -1))
    bit.extend([0] * SISA_BIT[versi - 1])
    n = 17 + 4 * versi
    kandidat = []
    for mk in range(8):
        if mask is not None and mk != mask:
            continue
        m, fungsi = _kerangka(versi)
        i = 0
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
                        v = bit[i] if i < len(bit) else 0
                        if _MASker[mk](r, c):
                            v ^= 1
                        m[r][c] = v
                        i += 1
            kanan -= 2
        # nilai dulu (tanpa format/versi), tulis
        # info versi + format hanya pada yang terpilih
        kandidat.append((penalti(m), mk, m))
    kandidat.sort(key=lambda t: (t[0], t[1]))
    terbaik = kandidat[0][2]
    _tulis_versi(terbaik, n, versi)
    _tulis_format(terbaik, n, level, kandidat[0][1])
    return terbaik


def render_ascii(matriks, tenang=2):
    """Render teks: dua karakter per modul."""
    n = len(matriks)
    luar = ["  " * (n + 2 * tenang)]
    for baris in matriks:
        luar.append("  " * tenang + "".join(
            "██" if v else "  " for v in baris)
            + "  " * tenang)
    luar.extend(["  " * (n + 2 * tenang)] * tenang)
    luar[0:0] = ["  " * (n + 2 * tenang)] * (tenang - 1)
    return "\n".join(luar)
