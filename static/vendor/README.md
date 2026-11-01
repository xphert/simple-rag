# Library frontend lokal

File berikut disajikan oleh FastAPI melalui `/static/vendor/`. Tidak ada proses npm atau build frontend yang diperlukan.

| Library | Versi | File | Lisensi |
| --- | --- | --- | --- |
| [Marked](https://marked.js.org/) | 18.1.1 | `marked.umd.js` | MIT; lihat `marked-LICENSE` |
| [DOMPurify](https://github.com/cure53/DOMPurify) | 3.4.17 | `purify.min.js` | Apache-2.0 atau MPL-2.0; lihat `DOMPurify-LICENSE` |

Sumber unduhan paket:

- `https://cdn.jsdelivr.net/npm/marked@18.1.1/lib/marked.umd.js`
- `https://cdn.jsdelivr.net/npm/marked@18.1.1/LICENSE`
- `https://cdn.jsdelivr.net/npm/dompurify@3.4.17/dist/purify.min.js`
- `https://cdn.jsdelivr.net/npm/dompurify@3.4.17/LICENSE`

Marked mengubah Markdown menjadi HTML. DOMPurify menyaring hasilnya sebelum dimasukkan ke halaman. Konfigurasi aplikasi membatasi elemen dan atribut yang diperbolehkan; script, event handler, dan CSS arbitrer dari jawaban tidak dijalankan.

Saat memperbarui library, ganti file distribusi beserta lisensinya dan sesuaikan versi pada dokumentasi ini. Browser menggunakan file lokal, bukan CDN saat menampilkan jawaban.
