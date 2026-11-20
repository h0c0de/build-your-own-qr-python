# RENCANA — Build 25: QR Code Generator

Sumber: **Thonky QR Code Tutorial** (thonky.com)
sebagai panduan langkah demi langkah + contoh
terhitungnya sebagai jangkar emas; **segno** dan
**qrcode** (dua implementasi Python independen)
sebagai wasit diferensial matriks penuh.

Bukti emas pra-kode (dibaca langsung dari tutorial,
20 Nov 2026):
- `HELLO WORLD`, alfanumerik, versi 1-Q: codeword
  data persis `20 5B 0B 78 D1 72 DC 4D 43 40 EC 11
  EC` (13 codeword, termasuk terminator + padding
  EC 11 EC).
- Tabel EC lengkap 40 versi x 4 level terbaca dari
  halaman tabel tutorial; konsistensinya dibuktikan
  silang melawan geometri matriks (total codeword
  per versi dihitung dari jumlah modul data) untuk
  160/160 entri sebelum dipercaya.

## Lingkup

MASUK:
- Mode numerik, alfanumerik, byte (UTF-8); satu
  segmen; pemilihan mode & versi otomatis terkecil.
- Versi 1-40, level L/M/Q/H: tabel blok EC dua
  grup, Reed-Solomon GF(256) primitif 0x11D,
  interleaving data + EC.
- Matriks penuh: finder, timing, alignment
  (semua versi), modul gelap, info versi (v>=7,
  BCH 18 bit terhitung), 8 masker + penilaian
  4 aturan penalti spek, info format (BCH 15 bit
  terhitung, bukan tabel hafalan).

DILUAR (tercatat):
- Mode Kanji (perlu tabel Shift-JIS) & ECI.
- Segmentasi multi-mode teroptimasi (satu segmen
  per kode; wasit dipaksa mode yang sama).
- Micro QR, kode terstruktur/append, FNC1.
- Gambar (PNG/SVG) — keluarannya matriks modul;
  renderer ASCII hanya untuk catatan.

## Irisan

- [x] Irisan 1 — Enkode data: mode, indikator
  jumlah, terminator/padding; jangkar HELLO WORLD.
- [x] Irisan 2 — Reed-Solomon: GF(256), polinom
  generator, EC per blok; bukti sindrom nol +
  jangkar contoh tutorial.
- [x] Irisan 3 — Blok & interleaving + penempatan
  modul: fungsi pola dasar versi 1-7.
- [x] Irisan 4 — Masker, penalti, info format &
  versi; matriks akhir versi rendah utuh.
- [x] Irisan 5 — Final: diferensial matriks penuh
  vs segno (dan qrcode) lintas versi/level/mode/
  masker paksa + acak; kapasitas tepi versi 40.

## Pagar selesai

- [x] `uji_irisan1.py` … `uji_irisan5.py` hijau.
- [x] `CATATAN.md` satu halaman per irisan.
- [x] Repo GitHub publik
  `build-your-own-qr-python` terbit dan
  terverifikasi (SHA blob lokal == remote, halaman
  publik terbaca).
