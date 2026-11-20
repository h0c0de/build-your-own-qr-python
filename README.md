# Build Your Own — QR Code Generator

Generator **QR Code** lengkap (versi 1–40, level
L/M/Q/H) dalam Python murni, dibangun mengikuti
**Thonky QR Code Tutorial** langkah demi langkah
dan dibuktikan melawan dua implementasi independen:
matriks identik modul-demi-modul dengan **segno**
pada sapuan 160 kombinasi versi×level dan korpus
otomatis, dengan **pustaka qrcode** sebagai pendapat
ketiga — termasuk dua kasus tepi terdokumentasi di
mana segno menyimpang dari spek dan build ini
mengikuti spek (lihat `CATATAN.md` irisan 5).

Jangkar emasnya berasal dari tutorial itu sendiri:
`HELLO WORLD` pada 1-Q harus menghasilkan codeword
data persis `20 5B 0B 78 D1 72 DC 4D 43 40 EC 11 EC`
— dan memang begitu.

## Isi

| Berkas | Isi |
| --- | --- |
| `qr.py` | Generatornya: GF(256) + Reed-Solomon, tabel EC 160 entri, enkode 3 mode, blok + interleaving, matriks + 8 masker + penalti ISO, info format/versi BCH |
| `uji_bersama.py` | Pembanding matriks vs segno |
| `uji_irisan1.py` … `uji_irisan5.py` | Uji per irisan (perlu segno + qrcode terpasang untuk irisan 3–5) |

## Memakai

```python
from qr import buat, render_ascii

m = buat("HELLO WORLD", level="Q")   # matriks 21x21
print(render_ascii(m))
```

`buat()` memilih mode (numerik/alfanumerik/byte
UTF-8), versi terkecil, dan masker berpenalti
terendah secara otomatis; ketiganya bisa dipaksa
lewat parameter `mode=`, `versi=`, `mask=`.

## Tiga hal yang menentukan

1. **Generator Reed-Solomon adalah ∏(x − αⁱ).**
   Menukar tempat suku x dan suku tetapan saat
   membangunnya menghasilkan generator yang akarnya
   α⁻ⁱ — tetap Reed-Solomon yang sah, tetapi bukan
   QR. Gejalanya khas: codeword data cocok semua,
   codeword EC berbeda semua. Bukti yang dipakai di
   sini bukan hafalan: polinom derajat n harus
   berakar persis di α⁰…αⁿ⁻¹ dan data+EC harus
   bersindrom nol.

2. **Penalti masker dinilai TANPA info format &
   versi** (ISO 18004 §7.8). Menilainya sesudah
   format ditulis mengubah skor dan bisa mengubah
   masker terpilih. Aturan N3 juga menghitung pola
   yang menempel tepi matriks — zona tenang virtual
   di luar simbol ikut berperan.

3. **Pusat alignment di garis timing tetap
   digambar.** Pola yang pusatnya di (6, x) atau
   (x, 6) menimpa timing; yang dilewati hanya tiga
   kombinasi pojok finder. Melewatkan semuanya yang
   "pusatnya sudah fungsi" menghapus 40 modul dari
   versi ≥7 dan menggeser seluruh aliran data.

## Di luar lingkup

Mode Kanji/ECI, segmentasi multi-mode teroptimasi
(satu segmen per kode), Micro QR, dan keluaran
gambar — matriks modul adalah keluarannya.

## Lisensi

Kode: MIT. Tutorial © Thonky; segno (BSD) dan
qrcode (BSD) hanya wasit uji, tidak disertakan.
