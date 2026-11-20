"""Mesin diferensial build 25 vs segno (wasit
independen) — matriks dibandingkan modul demi modul.
Jalankan dengan python dari venv referensi:
~/workspace/build-your-own-x/qr-ref/venv/bin/python
"""
import segno

import qr

MODE_SEGNO = {"numerik": "numeric", "alfa": "alphanumeric",
              "byte": "byte"}


def matriks_segno(teks, level, versi, mode, mask):
    q = segno.make(teks, error=level.lower(),
                   version=versi, mode=MODE_SEGNO[mode],
                   mask=mask, boost_error=False,
                   micro=False)
    return [list(baris) for baris in q.matrix]


def beda(a, b):
    if len(a) != len(b):
        return -1
    return sum(1 for r in range(len(a))
               for c in range(len(a)) if a[r][c] != b[r][c])
