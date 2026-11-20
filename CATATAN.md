# CATATAN — Build 25: QR Code Generator

Satu halaman per irisan: konsep inti + temuan.
Panduan: Thonky QR Code Tutorial. Wasit: segno
dan pustaka qrcode (dua implementasi independen),
dipasang di venv referensi lokal.

## Irisan 1 — Enkode data (11)

**Konsep.** Tiga mode dengan kepadatan berbeda:
numerik 10 bit per 3 digit, alfanumerik 11 bit per
2 karakter dari tabel 45, byte 8 bit per byte
UTF-8. Sesudah indikator mode + jumlah: terminator
maksimal 4 nol, ratakan ke byte, lalu pad berganti
`EC 11` sampai kapasitas versi/level penuh.

**Temuan.** Jangkar tutorial lolos pada percobaan
pertama — `HELLO WORLD` 1-Q menghasilkan persis
13 codeword yang dicetak tutorial. Yang justru
salah dua kali adalah aritmetika bit di *ujiku
sendiri* (posisi indikator jumlah numerik, dan
huruf `A` yang kukira byte padahal alfanumerik);
pola berulang seri ini: curigai dulu alat ukurnya.

## Irisan 2 — Reed-Solomon (108)

**Konsep.** GF(256) dengan polinom primitif
0x11D: penjumlahan adalah XOR, perkalian memakai
tabel log/antilog α=2. EC adalah sisa pembagian
polinom data×xⁿ oleh polinom generator ∏(x−αⁱ),
i = 0…n−1.

**Temuan.** Bug paling berbahaya seri ini: saat
membangun generator, suku x dan suku tetapan αⁱ
tertulis tertukar — hasilnya generator berakar
α⁻ⁱ. Semua codeword data tetap benar, semua EC
salah, dan kode tetap *tampak* seperti QR. Yang
menangkapnya bukan contoh melainkan pembuktian:
generator derajat n wajib bernilai 0 di α⁰…αⁿ⁻¹
dan tidak di αⁿ, dan data+EC wajib bersindrom
nol. Kedua uji aljabar itu sekarang permanen di
irisan ini, ditambah jangkar EC HELLO WORLD.

## Irisan 3 — Blok, interleaving, geometri (161)

**Konsep.** Versi/level besar memecah data ke dua
grup blok (grup 2 selalu satu codeword lebih
panjang per blok), EC dihitung per blok, lalu
pesan akhir disusun selang-seling per kolom blok:
semua data dulu, lalu semua EC.

**Temuan.** Tabel EC 160 entri dari tutorial tidak
dipercaya begitu saja: total codeword tiap entri
dibuktikan sama dengan jumlah modul data yang
dihitung dari geometri kerangka matriks versi itu
— 160/160 cocok, jadi tabel dan kerangka saling
mengunci. Di irisan ini juga ditemukan artefak
wasit pertama (lihat irisan 5).

## Irisan 4 — Masker, penalti, format (68)

**Konsep.** Delapan pola masker diterapkan hanya
ke wilayah data; yang dipilih adalah yang
berpenalti ISO 18004 Tabel 11 (N1 run, N2 blok
2×2, N3 pola mirip finder, N4 proporsi gelap)
terendah. Info format 15 bit dan info versi 18
bit keduanya *dihitung* dengan BCH (generator
0x537 + topeng 0x5412; 0x1F25), bukan dihafal.

**Temuan.** Dua koreksi dari membaca sumber wasit:
(1) penilaian masker spek dilakukan pada matriks
**tanpa** info format/versi — menilainya sesudah
format ditulis membuat skor dan pilihan maskerku
menyimpang dari segno; (2) aturan N3 menghitung
pola 1:1:3:1:1 yang menempel tepi matriks (zona
tenang virtual melengkapi sisi terangnya) dan
pola yang sisi terangnya kurang dari 4 modul di
dalam matriks tetapi utuh di tepi. Sesudah kedua
koreksi itu, skorku sama persis dengan evaluator
segno pada semua masker yang diuji. Bug kecil
lain: sel (8,6) dan (6,8) adalah modul timing,
bukan format — cadangannya tidak boleh ditimpa 0.

## Irisan 5 — Diferensial penuh (180)

**Konsep.** Sapuan 40 versi × 4 level dengan
masker paksa bergilir melawan segno (160 matriks
identik), korpus otomatis penuh, pendapat ketiga
pustaka qrcode, dan tepi kapasitas: 2953 byte pas
di 40-L, 2954 ditolak.

**Temuan.** Tiga, semuanya berharga:
(1) Tabel alignment-ku salah di lima versi
(30–34) — kupelajari dari kegagalan sapuan di
v30: barisan pusatnya bukan deret mulus yang
kutulis dari ingatan (v30 yang benar
6, 26, 52, 78, 104, 130). Sesudah dikoreksi dari
Annex E spek, seluruh sapuan hijau.
(2) Pola alignment berpusat di garis timing
sempat terlewat oleh aturan "pusat sudah fungsi"
— 40 modul hilang di v≥7; aturan yang benar hanya
melewatkan tiga kombinasi pojok finder.
(3) **Artefak wasit**: bila data + terminator
berakhir *persis* di batas codeword dan padding
masih diperlukan, segno menyisipkan satu codeword
`0x00` ekstra sebelum pad `EC 11…` — menyimpang
dari aturan padding spek. Dua kasus korpus kena
(5-Q byte dan sebuah kasus v3). Pustaka qrcode
dan teks spek sepakat dengan build ini; kasus
tepi itu diverifikasi ke qrcode pada masker
pilihannya + pilihan masker build ini dibuktikan
sama dengan argmin evaluator ISO segno atas
kandidatku sendiri. Kodenya tetap bisa dipindai
(penyisipan ada di wilayah padding), jadi ini
penyimpangan jinak — tetapi diferensial yang
jujur harus mencatatnya, bukan menyembunyikannya.
