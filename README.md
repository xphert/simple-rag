# RAG Parameter Exploration

## Informasi Eksperimen

| Item | Keterangan |
| --- | --- |
| Nama PDF | `modul-rag-dasar.pdf` |
| Jumlah halaman | 5 halaman (semua berbasis teks, tanpa gambar) |
| Ukuran teks | 11.981 karakter |
| SHA-256 (16 karakter pertama) | `41E451717E7FA311` |
| Topik | Modul praktikum Sistem Temu Kembali Informasi berbasis RAG |

Isi PDF: modul kuliah tujuh bab yang membahas pendahuluan RAG, arsitektur sistem, strategi
chunking, model embedding, basis data vektor dan retrieval, tahap generation beserta
temperature, serta evaluasi dan studi kasus. Angka-angka di dalam modul (384 dimensi,
128 token, 100 token, 20 token, TOP_K 4) sengaja dibuat eksplisit supaya jawaban setiap
pertanyaan uji dapat diperiksa secara objektif.

PDF dibuat dengan `scripts/generate_test_pdf.py` agar seluruh eksperimen memakai dokumen
yang benar-benar identik.

## Lingkungan Eksperimen

| Komponen | Nilai |
| --- | --- |
| OS | Windows 11 |
| Python | 3.13.5 (`venv/`) |
| Embedding model | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensi) |
| Vector database | Qdrant lokal (`qdrant_data/`), metrik COSINE |
| LLM | `Qwen2.5-1.5B-Instruct`, berjalan lokal di CPU (mode offline) |
| Backend LLM | HTTP OpenAI-compatible (`httpx`) ke `{LLM_BASE_URL}/chat/completions` |
| Konfigurasi LLM | `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_TEMPERATURE` di `.env` |
| Top-K default | 4 |
| Chunking | `RecursiveCharacterTextSplitter` berbasis tokenizer model embedding |

Catatan: eksperimen dijalankan **tanpa Groq API key** karena tidak ada kredensial yang
tersedia. Aplikasi tetap memakai jalur kode yang sama di `llm.py` (klien OpenAI-compatible).
Bila `.env` diisi `LLM_API_KEY` beserta `LLM_BASE_URL` dan `LLM_MODEL`, aplikasi otomatis
memakai endpoint tersebut; bila `LLM_API_KEY` dikosongkan, aplikasi memakai `GROQ_API_KEY`
(atau model lokal bila keduanya kosong). Nama model adalah satu-satunya variabel yang
berbeda dari instruksi tugas; PDF, pertanyaan, embedding model, chunking, dan TOP_K tetap
sama persis di seluruh percobaan, sehingga perbandingan antar-parameter tetap sah.

## Pertanyaan Pengujian

Kedua pertanyaan dipakai identik pada **seluruh** percobaan.

**Pertanyaan 1**

> Berapa dimensi vektor dan batas maksimum token model embedding yang digunakan pada modul ini?

Kunci jawaban di PDF: 384 dimensi dan 128 token (Bab 4).

**Pertanyaan 2**

> Berapa nilai chunk size dan chunk overlap default pada modul ini, dan mengapa chunk overlap diperlukan?

Kunci jawaban di PDF: chunk size 100 token, chunk overlap 20 token, dan overlap menjaga
kalimat di perbatasan dua chunk agar tidak terbelah (Bab 3).

## Baseline Configuration

| Parameter | Nilai |
| --- | --- |
| Temperature | 0.2 |
| TOP_K | 4 |
| Chunk Size | 100 |
| Chunk Overlap | 20 |
| Embedding Model | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| LLM Model | `Qwen2.5-1.5B-Instruct` (lokal) |

Hasil ingestion baseline: `pages_read = 5`, `chunks_stored = 38`.

## Catatan Perubahan Kode

Aplikasi asli dipakai apa adanya. Hanya ada dua perubahan di luar parameter eksperimen:

1. `llm.py` — nilai `temperature` dijadikan konstanta `TEMPERATURE` (default tetap `0.2`)
   dan dapat diatur lewat `LLM_TEMPERATURE`. Ditambahkan dukungan endpoint OpenAI-compatible
   (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`) serta fallback model lokal bila API key kosong.
   Variabel `GROQ_*` lama tetap didukung sebagai cadangan. Panggilan ke endpoint dilakukan
   langsung dengan `httpx` ke `{LLM_BASE_URL}/chat/completions`, karena SDK `groq` selalu
   menambahkan prefiks `/openai/v1` pada path sehingga tidak cocok untuk gateway umum.
2. `rag.py` — memperbaiki escape newline ganda pada `build_context`. Sebelumnya konteks
   dikirim ke LLM sebagai teks literal `\n`, bukan baris baru. Perbaikan ini hanya
   menyangkut format prompt dan tidak menyentuh retrieval.

`config.py`, `chunker.py`, `vector_store.py`, `embeddings.py`, dan `pdf_loader.py` tidak diubah.

## Cara Menjalankan Ulang

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

python scripts/generate_test_pdf.py      # membuat PDF uji
python -m uvicorn main:app --reload      # http://127.0.0.1:8000
```

Seluruh eksperimen dijalankan otomatis:

```bash
python scripts/download_local_model.py   # hanya untuk mode offline
python scripts/run_experiments.py        # 12 kasus, hasil di results/*.json
python scripts/summarize_results.py      # tabel rekap di results/summary.md
python scripts/answer_stats.py           # panjang jawaban + konsistensi
python scripts/build_readme.py           # mengisi README dari results/
```

Setiap kasus dijalankan sebagai proses terpisah, setara dengan mematikan lalu menyalakan
ulang server. Khusus eksperimen chunking, folder `qdrant_data/` dihapus lebih dulu sehingga
ingestion benar-benar dimulai dari basis data kosong.

## Konfigurasi LLM (OpenAI-compatible)

Model bahasa diatur sepenuhnya dari `.env`, tanpa mengubah kode:

```env
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=gemini/gemini-3-flash-preview
LLM_TEMPERATURE=0.2

GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b

LLM_LOCAL_MODEL=models/Qwen2.5-1.5B-Instruct
```

Urutan pemakaian:

1. `LLM_API_KEY` terisi → pakai `LLM_BASE_URL` + `LLM_MODEL` (endpoint OpenAI-compatible
   apa pun: Groq, gateway, LiteLLM, OpenRouter, dan sejenisnya). `LLM_BASE_URL` harus
   menunjuk ke root API yang berakhiran `/v1`, contoh `https://9r.xphr.dev/v1`; aplikasi
   akan memanggil `{LLM_BASE_URL}/chat/completions`. Kosongkan `LLM_BASE_URL` untuk memakai
   endpoint default Groq (`https://api.groq.com/openai/v1`).
2. `LLM_API_KEY` kosong tetapi `GROQ_API_KEY` terisi → pakai Groq secara langsung.
3. Keduanya kosong → pakai model lokal `LLM_LOCAL_MODEL` (mode offline, seperti eksperimen
   di README ini).

Cek cepat konfigurasi dan koneksi tanpa membuka server:

```bash
python scripts/check_llm.py    # menampilkan backend aktif + uji satu panggilan
```

`LLM_TEMPERATURE` dibaca `llm.py` sebagai nilai `TEMPERATURE`. Pada eksperimen, skrip
`run_experiments.py` menimpa konstanta itu langsung di `llm.py` agar pengaruh temperature
bisa diuji per kasus.

---

## Experiment 1 - Temperature

Yang diubah hanya `TEMPERATURE` di `llm.py`. Database **tidak** di-ingest ulang.
Konfigurasi retrieval tetap: TOP_K = 4, chunk size = 100, chunk overlap = 20.
Setiap nilai temperature dijalankan **dua kali** dengan pertanyaan yang sama agar
konsistensi jawaban bisa diukur.

### Temperature = 0.0

**Actual Output — Pertanyaan 1 (run 1)**

> Dalam modul ini:
>
> - Dimensi vektor untuk model embedding adalah 384.
> - Batas maksimum token yang digunakan oleh model embedding adalah 128.
>
> Sumber: [Page: 3]

**Actual Output — Pertanyaan 1 (run 2)**

> Dalam modul ini:
>
> - Dimensi vektor untuk model embedding adalah 384.
> - Batas maksimum token yang digunakan oleh model embedding adalah 128.
>
> Sumber: [Page: 3]

**Actual Output — Pertanyaan 2 (run 1)**

> Nilai default untuk chunk size pada modul ini adalah 100 token.
>
> Nilai default untuk chunk overlap juga adalah 20 token.
>
> Chunk overlap diperlukan karena memastikan bahwa kalimat yang berada di perbatasan dua chunk tetap terhubung secara kontinu. Tanpa overlap, sebuah definisi bisa terpisahkan menjadi dua bagian, menyebabkan informasi hilang atau duplikat. Selain itu, dengan menggunakan overlap, kita mencegah potensi fragmentasi data saat proses pemrosesan data dilakukan.

**Actual Output — Pertanyaan 2 (run 2)**

> Nilai default untuk chunk size pada modul ini adalah 100 token.
>
> Nilai default untuk chunk overlap juga adalah 20 token.
>
> Chunk overlap diperlukan karena memastikan bahwa kalimat yang berada di perbatasan dua chunk tetap terhubung secara kontinu. Tanpa overlap, sebuah definisi bisa terpisahkan menjadi dua bagian, menyebabkan informasi hilang atau duplikat. Selain itu, dengan menggunakan overlap, kita mencegah potensi fragmentasi data saat proses pemrosesan data dilakukan.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6811 |
| 2 | hal. 2 | 0.6483 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6678 |
| 2 | hal. 3 | 0.5640 |

**Observation**

- Kedua pengulangan **identik karakter per karakter** (kemiripan 1.000) untuk kedua
  pertanyaan. Greedy decoding memang selalu memilih token paling mungkin.
- Jawaban paling ringkas di antara ketiga nilai: 158 karakter (25 kata) untuk Pertanyaan 1
  dan 476 karakter (66 kata) untuk Pertanyaan 2.
- Format keluaran sangat stabil: daftar berbutir untuk Pertanyaan 1, lalu satu baris
  `Sumber: [Page: 3]`.
- Fakta yang disebutkan benar semua: 384 dimensi, 128 token, chunk size 100, overlap 20,
  beserta alasan overlap yang sesuai isi Bab 3.
- Waktu tanggap 23,5 detik dan 29,0 detik; run kedua hampir sama (22,4 dan 29,2 detik).
- Skor retrieval (0,6811 dan 0,6678) sama persis dengan nilai temperature lain, bukti bahwa
  temperature tidak menyentuh tahap retrieval.

### Temperature = 0.2

**Actual Output — Pertanyaan 1 (run 1)**

> Dalam modul ini:
>
> - Dimensi vektor untuk model embedding adalah 384.
> - Batas maksimum token yang digunakan oleh model embedding adalah 128.
>
> Referensi: [Source: modul-rag-dasar.pdf | Page: 3]

**Actual Output — Pertanyaan 1 (run 2)**

> Dalam modul ini:
>
> - Dimensi vektor untuk model embedding adalah 384.
> - Batas maksimum token yang digunakan oleh model embedding adalah 128.
>
> Sumber: [Page: 3]

**Actual Output — Pertanyaan 2 (run 1)**

> Nilai chunk size pada modul ini adalah 100 token dengan default.
>
> Nilai chunk overlap default adalah 20 token.
>
> Chunk overlap diperlukan untuk mempertahankan konteks antar bagian text (chunk) yang saling bertemu atau berhubungan. Tanpa overlap, setiap partisipan bisa saja menerima informasi yang sangat berbeda karena mereka mungkin mendapatkan fragment text yang berbeda-beda. 
>
> Overlapping juga berguna untuk menjamin bahwa pesan yang ada di batas kedua chunk tetap bersatu dan masih relevan meskipun hanya beberapa kata saja. Ini memberikan kesempatan bagi sistem untuk melihat hubungan antara dua bagian text yang berdekatan secara spesifik.

**Actual Output — Pertanyaan 2 (run 2)**

> Nilai chunk size pada modul ini adalah 100 token dengan nilai default.
>
> Nilai chunk overlap pada modul ini adalah 20 token dengan nilai default.
>
> Chunk overlap diperlukan untuk menjaga kalimat yang berada di perbatasan dua chunk. Tanpa overlap, sebuah definisi dapat terbelah menjadi dua, sehingga memperkecil potensi kesalahan interpretasi. Selain itu, overlap juga berguna untuk mencegah bahwa sebuah chunk bisa terisolasi tanpa pasangannya, yang dapat menyebabkan masalah dalam pemrosesan konteks.

**Sources / Similarity Score**

Sama dengan temperature 0.0 (database tidak berubah):

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6811 |
| 2 | hal. 2 | 0.6483 |

**Observation**

- Isi jawaban tetap benar, tetapi wording sudah mulai bervariasi.
- Pertanyaan 1: kemiripan run 1 vs run 2 sebesar 0,883. Bedanya hanya pada label sitasi
  (`Referensi: [Source: modul-rag-dasar.pdf | Page: 3]` versus `Sumber: [Page: 3]`),
  panjang 191 karakter vs 158 karakter.
- Pertanyaan 2: kemiripan turun tajam menjadi 0,255. Run 1 menghasilkan 646 karakter
  (91 kata), run 2 hanya 500 karakter (70 kata). Keduanya menyebut angka yang sama, tetapi
  run 1 menambahkan analogi yang agak melenceng ("setiap partisipan bisa saja menerima
  informasi yang sangat berbeda") yang tidak ada di dokumen.
- Artinya nilai default 0,2 sudah memberi variasi yang cukup besar pada model kecil ini,
  meskipun masih dalam batas fakta yang benar.

### Temperature = 0.8

**Actual Output — Pertanyaan 1 (run 1)**

> Dari konteks yang diberikan, kita bisa mengetahui bahwa:
>
> Vektor dari modul ini memiliki dimension 384.
>
> Strategi untuk mengelola tokens dalam modul ditentukan oleh aturan sebagai berikut:
> 1. Ukuran chunk (chunk size) dihitung dalam satuan token, bukan karakter. Default value is 100 tokens.
> 2. Chunk overlap atau token duplicate sebelum sebuah chunk baru disebutkan mencapai nilai 20 tokens. Hal ini berguna untuk mencegah pembatasan antar chunk.
>
> Modularitas dari model embedding menggunakan sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 dengan beberapa fitur unggulan termasuk:
> - Menggunakan transformator dua lapisan
> - Dapat membaca lebih dari sepuluh bahasa termasuk Bahasa Indonesia 
> - Ukuran input maksimal bagi model ini adalah 128 tokens.
>
> Untuk proses penyaringan data, meskipun informasi tentang batas

**Actual Output — Pertanyaan 1 (run 2)**

> Dari informasi yang disediakan:
>
> Vektor dari model embedde memiliki dimensi sebesar 384.
>
> Batas maksimum token untuk model embedding yang digunakan adalah 128 tokens.
>
> Silakan bandingkan dengan hasil penelitian atau dokumentasi spesifik jika Anda mencari data eksplisit tentang struktur vektor dan batas token tersebut.

**Actual Output — Pertanyaan 2 (run 1)**

> Nilai chunk size (default) pada modul adalah 100 token.
>
> Nilai chunk overlap (default) pada modul adalah 20 token.
>
> Chunk overlap diperlukan karena menjaga kalimat yang berada di perbatasan dua chunk, sehingga memastikan bahwa setiap chunk memiliki konteks yang kuat untuk pemahaman. Tanpa overlapping, sebuah definisi bisa terpisahkan menjadi bagian-bagi yang berbeda, menyebabkan ketidakpastian dan kesalahpahaman dalam analisis semantik.

**Actual Output — Pertanyaan 2 (run 2)**

> - Chunk Size Default: 100 tokens
> - Chunk Overlap Default: 20 tokens
>
> **PENASihatAN:**
> Chunk Overlap (jumlah token yang diulang) diperlukan karena melindungi kalimat di luar area chunk antara bagian berbeda. Tanpa overlapping, jika sebuah definisi dibelah menjadi dua, salah satu partikel mungkin bisa saja terisolasi dengan cepat sehingga konteks keseluruhan tidak terhalus seperti seharusnya. Secara teknis, overlapping memastikan bahwa semua fragment dari suatu kalimat tetap saling berkaitan, termasuk kalimat yang berada di batas-batas beberapa chunks.

**Sources / Similarity Score**

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6811 |
| 2 | hal. 2 | 0.6483 |

**Observation**

- Jawaban menjadi jauh lebih panjang dan tidak stabil: Pertanyaan 1 menghasilkan 826
  karakter (109 kata) pada run 1 tetapi hanya 319 karakter (43 kata) pada run 2.
  Kemiripan kedua run hanya 0,115; untuk Pertanyaan 2 sebesar 0,161.
- Run 1 Pertanyaan 1 keluar dari topik: pertanyaan tentang dimensi dan batas token, tetapi
  jawabannya ikut membahas chunk size dan chunk overlap, lalu berhenti mendadak di tengah
  kalimat ("...meskipun informasi tentang batas") karena batas 220 token keluaran habis.
- **Informasi faktual berubah.** Pada run 1 Pertanyaan 1 model menulis "transformator dua
  lapisan" padahal PDF menyebut "dua belas lapisan", dan "lebih dari sepuluh bahasa" padahal
  PDF menyebut "lebih dari lima puluh bahasa". Angka 384 dan 128 tetap benar, tetapi detail
  pendukungnya menyimpang dari dokumen.
- Kalimat mulai bercampur bahasa Inggris: "Default value is 100 tokens", "dimension 384".
  Pada Pertanyaan 2 run 2 muncul judul yang tidak bermakna ("**PENASihatAN:**") dan kata
  yang tidak baku ("tidak terhalus", "partikel"). Wording jelas berubah dan terasa lebih
  "kreatif", tetapi kualitasnya menurun.
- Waktu tanggap naik menjadi 31-47 detik karena jawaban yang dihasilkan lebih panjang.
- Skor retrieval tetap 0,6811 dan 0,6678, persis sama dengan temperature 0.0 dan 0.2.

### Kesimpulan Experiment Temperature

**Apa perubahan yang paling terlihat?**

Yang paling terlihat adalah **panjang dan konsistensi**. Temperature 0.0 menghasilkan dua
jawaban yang sama persis (kemiripan 1.000). Temperature 0.8 menghasilkan panjang yang
berubah-ubah (826 karakter vs 319 karakter untuk pertanyaan yang sama), mencampur bahasa,
dan keluar dari topik. Pada 0.8 perubahan itu bahkan sampai merusak fakta pendukung:
"dua belas lapisan" menjadi "dua lapisan" dan "lima puluh bahasa" menjadi "sepuluh bahasa".
Perubahan kedua yang terlihat adalah **waktu tanggap** (0.0 sekitar 23-29 detik, 0.8 sampai
47 detik) karena jawaban yang dihasilkan lebih panjang.

**Nilai mana yang paling cocok untuk aplikasi RAG ini?**

**0.0**, dengan 0.2 sebagai alternatif bila jawaban tidak boleh terlalu kaku.

**Kenapa?**

Karena tugas utama RAG adalah menjawab berdasarkan dokumen, sehingga konsistensi lebih
penting daripada variasi bahasa. Pada 0.0 jawaban selalu sama untuk pertanyaan yang sama,
ringkas, dan seluruh angka yang disebut berasal dari konteks. Nilai 0.8 terbukti menambah
risiko menyimpang dari konteks: jawaban Pertanyaan 1 run 1 membahas chunk size padahal yang
ditanya dimensi vektor, dan dua detail dokumen berubah ("dua belas" menjadi "dua lapisan",
"lima puluh bahasa" menjadi "sepuluh bahasa"). Temperature 0.2 masih dapat diterima karena
faktanya tetap benar, tetapi variasi yang cukup besar pada Pertanyaan 2 (kemiripan 0,255)
menyulitkan bila hasil perlu diaudit.

---

## Experiment 2 - TOP_K

Yang diubah hanya `TOP_K` di `config.py`. Temperature dikembalikan ke 0.2, chunk size 100,
chunk overlap 20, dan database **tidak** di-ingest ulang (konfigurasi chunking sama).
Ketiga kasus memakai 38 chunk yang sama.

### TOP_K = 1

**Actual Output — Pertanyaan 1**

> Dalam modul ini:
>
> - Dimensi vektor: 128 (atau berdasarkan aturan)
> - Batas maksimum token untuk model embedding: 128
>
> Sumber: modul-rag-dasar.pdf | Halaman: 3

**Actual Output — Pertanyaan 2**

> Nilai chunk size (ukuran bagian) pada modul ini adalah 100 token. Nilai chunk overlap (jumlah token yang diulang di awal chunk berikutnya) juga adalah 20 token.
>
> Chunk overlap diperlukan karena memastikan bahwa kalimat yang terletak di antara dua chunk tetap bersama-sama, sehingga dapat dibaca secara kontinyu oleh pengguna. Ini membantu mencegah kesan ketidaknyamanan saat pengguna mencoba mengekstrak atau merujuk pada informasi dari area khusus di mana kalimat tersebut berada.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6811 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6678 |

**Observation**

- Hanya **satu chunk** yang dikirim ke LLM, sehingga konteks sangat sempit.
- Pertanyaan 1 dijawab **salah**: model menulis "Dimensi vektor: 128 (atau berdasarkan
  aturan)". Angka 128 adalah batas token, bukan dimensi vektor; angka 384 tidak pernah
  muncul karena chunk yang memuatnya (halaman 3, peringkat 3 pada pencarian) tidak terambil.
  Model terpaksa menebak dari kalimat "Teks yang lebih panjang akan dipotong" pada chunk
  yang tersedia. Panjang jawaban hanya 157 karakter.
- Pertanyaan 2 justru benar, karena chunk teratas untuk pertanyaan itu memang memuat kedua
  nilai default sekaligus alasan singkatnya.
- Waktu tanggap paling cepat (16 detik) karena prompt paling pendek.
- Skor kemiripan chunk tunggal: 0,6811 dan 0,6678.

### TOP_K = 4 (baseline)

**Actual Output — Pertanyaan 1**

> Dalam modul ini:
>
> - Dimensi vektor untuk model embedding adalah 384.
> - Batas maksimum token yang digunakan oleh model embedding adalah 128.
>
> Sumber: Modul-RAG-Dasar.pdf, halaman 3.

**Actual Output — Pertanyaan 2**

> Nilai chunk size pada modul ini adalah 100 token dengan default.
>
> Nilai chunk overlap adalah 20 token dengan default.
>
> Chunk overlap diperlukan untuk mempertahankan konteks antar bagian text (chunk) yang saling bertemu atau berhubungan. Tanpa overlap, setiap partisipan bisa saja menerima fragment tanpa pasangan lain, sehingga menyebabkan kesalahpahaman atau hilangnya konteks.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6811 |
| 2 | hal. 2 | 0.6483 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6678 |
| 2 | hal. 3 | 0.5640 |

**Observation**

- Empat chunk dikirim, tetapi daftar `sources` hanya menampilkan **dua halaman unik**
  (halaman 3 dan 2). Ini karena `build_sources` membuang sumber dengan halaman yang sama,
  jadi jumlah baris sumber tidak sama dengan TOP_K.
- Kedua pertanyaan dijawab benar dan lengkap: 384 dimensi, 128 token, chunk size 100,
  chunk overlap 20, beserta alasannya.
- Jawaban lebih panjang daripada TOP_K = 1 (191 karakter untuk Pertanyaan 1) tetapi masih
  terkendali. Waktu tanggap 26-29 detik.

### TOP_K = 8

**Actual Output — Pertanyaan 1**

> Untuk informasi tentang dimensi vektor dan batas maksimum token model embedding yang digunakan pada modul ini:
>
> Dimensi vektor: 384 (model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
> Batas maksimum token: 128 (untuk input)

**Actual Output — Pertanyaan 2**

> Nilai chunk size dan chunk overlap default pada modul ini adalah:
>
> - Chunk size: 100 token
> - Chunk overlap: 20 token
>
> Keharusan untuk menggunakan chunk overlap disebutkan karena ia bertujuan untuk menjaga kalimat yang ada di perbatasan dua chunk, sehingga tidak terjadi pemecahan definisi menjadi dua bagian.
>
> Dalam konteks penggunaan embedding, ukuran chunk juga sangat penting kerana ia mempengaruhi isi teks yang dimasukkan ke dalam vektor. Dengan mengatur ukuran chunk secara tepat, kita bisa mencapai performansi optimal yang baik.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6811 |
| 2 | hal. 2 | 0.6483 |
| 3 | hal. 4 | 0.4920 |
| 4 | hal. 1 | 0.4513 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6678 |
| 2 | hal. 3 | 0.5640 |
| 3 | hal. 4 | 0.4511 |

**Observation**

- Delapan chunk masuk ke prompt, tetapi yang tampil hanya **empat halaman unik** untuk
  Pertanyaan 1 dan tiga halaman untuk Pertanyaan 2. Halaman 4 dan 1 (skor 0,4920 dan
  0,4513) sebenarnya berada di bawah ambang relevansi 0,55 yang disebut modul.
- Ada efek positif: jawaban Pertanyaan 1 kini menyebut nama model embedding
  (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) karena chunk yang memuat
  nama itu ikut terambil. Informasi ini tidak pernah muncul pada TOP_K = 1 dan 4.
- Namun jawaban juga mulai melebar: muncul kata tidak baku ("kerana"), dan jawaban
  Pertanyaan 2 menyisipkan kalimat yang tidak ada di dokumen ("ukuran chunk juga sangat
  penting kerana ia mempengaruhi isi teks yang dimasukkan ke dalam vektor... mencapai
  performansi optimal yang baik"). Pertanyaan 1 juga diawali basa-basi panjang sebelum
  menjawab.
- Waktu tanggap naik paling tajam: 42 detik dan 47 detik, hampir dua kali lipat TOP_K = 4
  (26-29 detik).
- Skor chunk teratas tidak berubah (0,6811 dan 0,6678) karena TOP_K hanya menentukan
  berapa banyak hasil yang diambil, bukan urutan kemiripannya.

### Kesimpulan Experiment TOP_K

**Apakah TOP_K yang lebih besar selalu menghasilkan jawaban yang lebih baik?**

Tidak. Pada eksperimen ini:

- TOP_K = 1 **merusak** jawaban Pertanyaan 1 (384 dilaporkan sebagai 128).
- TOP_K = 4 menjawab keduanya dengan benar dan efisien.
- TOP_K = 8 menambah satu informasi baru (nama model), tetapi juga menambah noise,
  memperpanjang jawaban, membuat gaya bahasa melenceng, dan menaikkan waktu tanggap
  hampir dua kali lipat.

Jadi ada titik jenuh: setelah chunk yang memuat jawaban sudah masuk, penambahan chunk
berikutnya hanya menambah biaya dan gangguan.

**TOP_K mana yang paling cocok untuk PDF yang digunakan?**

**4** (nilai default).

**Kenapa?**

Karena PDF ini hanya lima halaman dan informasinya tersebar dalam kalimat pendek, sehingga
dua sampai empat chunk sudah memuat seluruh fakta yang ditanyakan. TOP_K = 1 terlalu rawan
karena satu chunk bisa tidak memuat angka kunci. TOP_K = 8 relatif boros: sebagian besar
chunk tambahan berskor di bawah 0,55 dan justru membuat jawaban lebih panjang serta lebih
lambat, tanpa menambah ketepatan pada kedua pertanyaan uji.

---

## Experiment 3 - Chunk Size

`CHUNK_OVERLAP = 20` untuk seluruh percobaan. Setiap nilai chunk size memerlukan
**hapus `qdrant_data/` → jalankan ulang aplikasi → ingest ulang PDF** karena jumlah dan isi
chunk berubah.

### Chunk Size = 50

**Chunks Stored:** 81

**Actual Output — Pertanyaan 1**

> Dalam modul ini:
>
> - Dimensi vektor untuk output transformer sebesar 384.
> - Batas maksimum token model embedding adalah 128.
>
> Referensi: [Page: 3]

**Actual Output — Pertanyaan 2**

> Nilai default untuk chunk size pada modul ini adalah 100 tokens.
>
> Nilai default untuk chunk overlap adalah 20 tokens.
>
> Chunk overlap diperlukan karena memastikan bahwa setiap bagian (chunk) memiliki konteks yang cukup luas sehingga informasi tersebut dapat dikembangkan secara efektif. Dengan menggunakan overlap, kita mencegah fragmentasi data dan menjaga integritas analisis.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.7208 |
| 2 | hal. 2 | 0.6353 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6539 |
| 2 | hal. 3 | 0.5686 |

**Observation**

- Jumlah chunk melonjak menjadi **81**, lebih dari dua kali baseline (38), karena setiap
  chunk hanya memuat sekitar 39 token.
- Skor chunk teratas untuk Pertanyaan 1 **naik** menjadi 0,7208 (baseline 0,6811): chunk
  kecil lebih fokus pada satu gagasan sehingga vektornya lebih tajam.
- Sebaliknya, skor teratas Pertanyaan 2 **turun** menjadi 0,6539 (baseline 0,6678), karena
  definisi default dan alasan overlap kini berada di chunk yang berbeda.
- Jawaban Pertanyaan 1 tetap benar (384 dan 128). Pertanyaan 2 juga benar, tetapi penjelasan
  overlap menjadi lebih umum ("konteks yang cukup luas... menjaga integritas analisis")
  dan tidak lagi menyebut perbatasan antar-chunk secara spesifik seperti pada chunk size 100.
- Waktu tanggap paling cepat (18-22 detik) karena setiap chunk lebih pendek.

### Chunk Size = 100

**Chunks Stored:** 38

**Actual Output — Pertanyaan 1**

> Dalam modul ini:
>
> - Dimensi vektor untuk model embedding adalah 384.
> - Batas maksimum token yang bisa digunakan dalam satu chunk adalah 128.
>
> Referensi: [Source: modul-rag-dasar.pdf | Page: 3]

**Actual Output — Pertanyaan 2**

> Nilai default untuk chunk size pada modul ini adalah 100 token.
>
> Nilai default untuk chunk overlap juga adalah 20 token.
>
> Chunk overlap diperlukan karena memastikan bahwa kalimat yang berada di perbatasan dua chunk tetap bersatu dan tidak dibelah secara haphazard. Ini bertujuan untuk mencegah definisi atau konteks yang berpotensi diserahkan kepada salah satu bagian chunk jika mereka terpisah dengan overlap yang sangat rendah.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6811 |
| 2 | hal. 2 | 0.6483 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6678 |
| 2 | hal. 3 | 0.5640 |

**Observation**

- Jumlah chunk 38, sama dengan baseline (konfigurasi ini memang baseline).
- Kedua pertanyaan benar. Namun Pertanyaan 1 sempat menulis "batas maksimum token yang bisa
  digunakan dalam satu chunk adalah 128", mencampur batas masukan model embedding dengan
  batas ukuran chunk. Kesalahan kecil ini tidak terjadi pada chunk size 50 dan 120.
- Waktu tanggap Pertanyaan 1 terasa paling lama (65 detik) karena model memilih jawaban
  yang lebih panjang sebelum berhenti.

### Chunk Size = 120

**Chunks Stored:** 29

**Actual Output — Pertanyaan 1**

> Dalam modul ini:
>
> - Dimensi vektor untuk model embedding adalah 384.
> - Batas maksimum token (chunk) yang digunakan adalah 128.
>
> Referensi: [Page: 3]

**Actual Output — Pertanyaan 2**

> Nilai chunk size pada modul ini adalah 100 token dengan default.
>
> Nilai chunk overlap default adalah 20 token.
>
> Chunk overlap diperlukan untuk mempertahankan konteks antara dua chunks. Tanpa overlap, definisi bisa terpisahkan, sehingga salah satu chunk mungkin saja dilewatkan jika hanya menggunakan chunk secara individu.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6886 |
| 2 | hal. 2 | 0.6483 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6678 |
| 2 | hal. 3 | 0.6125 |

**Observation**

- Jumlah chunk paling sedikit: **29**, karena setiap chunk memuat sekitar 93 token.
- Skor teratas Pertanyaan 1 berada di antaranya: 0,6886 (di atas 100, di bawah 50).
- Kedua jawaban benar dan paling ringkas (322 karakter untuk Pertanyaan 2), karena satu
  chunk besar sudah memuat definisi sekaligus alasan overlap.
- Tidak ada informasi yang hilang karena PDF ini tidak memiliki kalimat yang jumlahnya
  melebihi 120 token.

### Kesimpulan Experiment Chunk Size

**Apa hubungan Chunk Size dengan jumlah chunk yang tersimpan?**

Berbanding terbalik, tetapi tidak sepenuhnya linear:

| Chunk size | Chunks stored | Rata-rata token per chunk |
| --- | --- | --- |
| 50 | 81 | sekitar 39 |
| 100 | 38 | sekitar 74 |
| 120 | 29 | sekitar 94 |

Menurunkan chunk size dari 100 ke 50 lebih dari menggandakan jumlah chunk, sedangkan
menaikkannya dari 100 ke 120 hanya mengurangi sekitar seperempat. Penyebabnya, pemotongan
selalu menghormati batas kalimat, sehingga tidak semua ruang 120 token bisa terpakai penuh
(rata-rata hanya 94 token).

**Apakah chunk yang lebih kecil selalu menghasilkan retrieval yang lebih baik?**

Tidak selalu. Chunk 50 memberi skor kemiripan tertinggi untuk Pertanyaan 1 (0,7208), jadi
untuk pertanyaan yang jawabannya berupa satu fakta pendek chunk kecil memang lebih unggul.
Tetapi untuk Pertanyaan 2, yang jawabannya terdiri atas definisi **dan** alasan, chunk 50
justru memberi skor lebih rendah (0,6539) dan penjelasan yang lebih kabur karena informasi
terpecah ke beberapa chunk. Jadi "lebih kecil" berarti "lebih presisi tetapi kurang lengkap".

**Chunk size mana yang paling cocok?**

**100** (nilai default).

**Kenapa?**

Karena 100 token cukup untuk memuat satu gagasan utuh beserta penjelasannya, tetapi masih
di bawah batas 128 token model embedding. Pada ukuran ini kedua pertanyaan dijawab lengkap
dan spesifik. Chunk 50 membuat jawaban Pertanyaan 2 kehilangan detail, sedangkan chunk 120
memang baik untuk PDF ini tetapi menyisakan risiko informasi terpotong bila kalimatnya lebih
panjang, dan jumlah chunk yang sedikit membuat pilihan konteks untuk TOP_K menjadi lebih
terbatas.

---

## Experiment 4 - Chunk Overlap

`CHUNK_SIZE = 100` untuk seluruh percobaan. Seperti eksperimen chunk size, setiap perubahan
overlap memerlukan hapus `qdrant_data/` → restart → ingest ulang.

### Chunk Overlap = 0

**Chunks Stored:** 33

**Actual Output — Pertanyaan 1**

> Dalam modul ini:
>
> - Dimensi vektor untuk model embedding adalah 384.
> - Batas maksimum token yang digunakan oleh model embedding adalah 128.
>
> Sumber: [Page: 3]

**Actual Output — Pertanyaan 2**

> Nilai default untuk chunk size pada modul ini adalah 100 token.
>
> Nilai default untuk chunk overlap juga adalah 20 token.
>
> Chunk overlap diperlukan karena mempertahankan konteks antar bagian text yang saling bertemu (seperti kata-kata atau frasa) dengan menambahkan beberapa tokens setelah atau sebelum tiap chunk. Ini memberikan kontrol atas bagaimana teks disambungkan secara alami dan mencegah fragmentasi keseluruhan pesan.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6811 |
| 2 | hal. 2 | 0.6483 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6678 |
| 2 | hal. 3 | 0.5488 |

**Observation**

- Chunk paling sedikit: **33**. Tanpa overlap tidak ada teks yang disimpan dua kali.
- Kedua jawaban tetap benar.
- Skor chunk kedua Pertanyaan 2 paling rendah di antara ketiga nilai overlap (0,5488).
- Jawaban Pertanyaan 2 (426 karakter) menyebut overlap "menambahkan beberapa token setelah
  atau sebelum tiap chunk", penjelasan yang cukup umum dan tidak menyebut perbatasan chunk.

### Chunk Overlap = 20 (baseline)

**Chunks Stored:** 38

**Actual Output — Pertanyaan 1**

> Dalam modul ini:
>
> - Dimensi vektor untuk model embedding adalah 384.
> - Batas maksimum token model embedding yang digunakan adalah 128.
>
> Sumber: [Page: 3]

**Actual Output — Pertanyaan 2**

> Nilai default untuk chunk size pada modul ini adalah 100 token.
>
> Nilai default untuk chunk overlap juga adalah 20 token.
>
> Chunk overlap diperlukan karena memastikan bahwa kalimat yang berada di perbatasan dua chunk tetap bersatu dan tidak dibelah secara haphazard. Ini bertujuan untuk menjaga kontinuitas kalimat dan mencegah fragmentasi informasi antar chunk.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.6811 |
| 2 | hal. 2 | 0.6483 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6678 |
| 2 | hal. 3 | 0.5640 |

**Observation**

- Chunk bertambah menjadi **38** (5 chunk lebih banyak dari overlap 0) karena 20 token
  terakhir setiap chunk diulang di awal chunk berikutnya.
- Jawaban Pertanyaan 2 paling ringkas di antara ketiganya (360 karakter) dan paling sesuai
  isi PDF: menyebut "kalimat yang berada di perbatasan dua chunk" dan "mencegah fragmentasi".
- Skor chunk kedua Pertanyaan 2 naik dari 0,5488 (overlap 0) menjadi 0,5640.

### Chunk Overlap = 40

**Chunks Stored:** 43

**Actual Output — Pertanyaan 1**

> Vektor yang dihasilkan berdimensi 384.
>
> Batas maksimum token model embedding yang digunakan pada modul ini adalah 128 token.

**Actual Output — Pertanyaan 2**

> Nilai chunk size pada modul ini adalah 100 token dengan default chunk overlap 20 token.
>
> Chunk overlap diperlukan untuk mempertahankan kalimat yang ada di antara dua chunk. Tanpa overlap, sebuah definisi bisa terpisahkan menjadi dua, sehingga salah satu chunk mungkin saja terambil sendiri tanpa pasangannya. Menggunakan overlap memberikan kontrol atas bagaimana fragmentasi dilakukan, serta memastikan bahwa semua partikulars (kalimat) tetap bersama-sama.

**Sources / Similarity Score**

Pertanyaan 1:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 3 | 0.7155 |
| 2 | hal. 2 | 0.6483 |

Pertanyaan 2:

| Peringkat | Halaman | Skor kemiripan |
| --- | --- | --- |
| 1 | hal. 2 | 0.6678 |
| 2 | hal. 3 | 0.5757 |

**Observation**

- Chunk terbanyak: **43**. Terjadi duplikasi teks yang cukup besar (40 persen dari chunk).
- Skor chunk teratas Pertanyaan 1 justru **paling tinggi** di seluruh eksperimen ini
  (0,7155), dan jawabannya paling ringkas (124 karakter), meskipun sitasi halaman hilang.
- Jawaban Pertanyaan 2 menjadi paling panjang (456 karakter) dan memuat kata yang tidak baku
  ("semua partikulars (kalimat)"), tanda bahwa model mulai mengarang istilah saat konteks
  yang diterimanya berisi teks berulang.
- Skor chunk kedua Pertanyaan 2 terus naik seiring overlap: 0,5488 → 0,5640 → 0,5757.

### Kesimpulan Experiment Chunk Overlap

**Apa pengaruh Chunk Overlap yang kalian lihat?**

Overlap memengaruhi tiga hal:

1. **Jumlah chunk** — 33 → 38 → 43 untuk overlap 0 → 20 → 40. Semakin besar overlap,
   semakin banyak teks yang tersimpan berulang.
2. **Skor kemiripan** — chunk peringkat kedua pada Pertanyaan 2 meningkat konsisten
   (0,5488 → 0,5640 → 0,5757) karena chunk yang lebih panjang memuat konteks yang lebih
   utuh, dan pada overlap 40 chunk teratas Pertanyaan 1 melonjak dari 0,6811 ke 0,7155.
3. **Kualitas jawaban** — tidak selalu membaik. Overlap 20 memberi penjelasan paling
   tepat sasaran, sedangkan overlap 40 membuat jawaban lebih panjang, kehilangan sitasi
   halaman, dan memunculkan istilah yang tidak ada di dokumen ("partikulars").

**Apakah overlap yang lebih besar selalu menghasilkan jawaban yang lebih baik?**

Tidak. Overlap 40 memberi skor kemiripan tertinggi, tetapi jawabannya paling panjang,
kehilangan sitasi halaman, dan memakai istilah yang tidak baku. Overlap 20 memberi
keseimbangan terbaik: cukup menjaga kalimat di perbatasan chunk, tanpa menggandakan teks
berlebihan.

**Nilai mana yang paling cocok?**

**20** (nilai default, setara 20 persen dari chunk size).

**Kenapa?**

Karena 20 token sudah cukup untuk menjaga kontinuitas kalimat pada PDF ini, terbukti dari
naiknya skor chunk kedua dan penjelasan yang lebih spesifik dibanding overlap 0. Overlap 40
menambah 5 chunk dan menaikkan skor, tetapi tidak memperbaiki jawaban: jawaban justru lebih
panjang dan menyimpang dari gaya dokumen.

---

## Final Configuration

| Parameter | Nilai |
| --- | --- |
| Temperature | **0.0** |
| TOP_K | **4** |
| Chunk Size | **100** |
| Chunk Overlap | **20** |

Konfigurasi ini dipilih karena:

- **Temperature 0.0** — satu-satunya nilai yang menghasilkan jawaban identik pada dua
  pengulangan, sehingga aman untuk aplikasi tanya-jawab dokumen.
- **TOP_K 4** — cukup untuk memuat seluruh fakta yang ditanyakan tanpa menambah chunk
  berskor rendah, dan dua kali lebih cepat daripada TOP_K 8.
- **Chunk size 100 + overlap 20** — jumlah chunk paling seimbang (38), jawaban lengkap
  untuk kedua pertanyaan, dan sesuai batas 128 token model embedding.

## Final Questions

**1. Parameter mana yang paling terasa memengaruhi hasil aplikasi kalian?**

TOP_K dan chunk size, karena keduanya menentukan apakah informasi kunci benar-benar masuk
ke dalam konteks. TOP_K = 1 membuat jawaban Pertanyaan 1 salah (128 dilaporkan sebagai
dimensi vektor), dan chunk size 50 mengubah skor kemiripan Pertanyaan 1 dari 0,6811 menjadi
0,7208 sekaligus menurunkan skor Pertanyaan 2 menjadi 0,6539. Temperature juga terasa, tetapi
pengaruhnya pada gaya dan panjang jawaban, bukan pada benar/salahnya fakta.

**2. Apakah Temperature memengaruhi Retrieval atau Generation? Jelaskan.**

Hanya **generation**. Buktinya, pada ketiga nilai temperature skor kemiripan yang dilaporkan
identik sampai empat angka desimal (0,6811 dan 0,6483 untuk Pertanyaan 1; 0,6678 dan 0,5640
untuk Pertanyaan 2), dan halaman sumber yang terambil juga sama. Yang berubah hanyalah
teks jawaban: pada 0.0 dua pengulangan identik, pada 0.8 panjangnya berubah dari 826 menjadi
319 karakter. Temperature tidak pernah menyentuh proses embedding maupun pencarian vektor.

**3. Apakah TOP_K yang lebih besar selalu menghasilkan jawaban yang lebih baik?**

Tidak. TOP_K 1 menghasilkan jawaban salah, TOP_K 4 benar dan efisien, TOP_K 8 benar tetapi
lebih lambat (42-47 detik berbanding 26-29 detik) dan lebih bertele-tele. TOP_K 8 memang
menambahkan satu informasi baru (nama model embedding), tetapi juga memasukkan chunk dengan
skor 0,4513 dan 0,4920 yang berada di bawah ambang relevansi.

**4. Apa yang terjadi ketika Chunk Size dibuat lebih kecil?**

Jumlah chunk naik tajam (81 chunk pada ukuran 50, dibanding 38 pada ukuran 100). Retrieval
menjadi lebih presisi untuk fakta tunggal (skor 0,7208 untuk Pertanyaan 1), tetapi informasi
yang seharusnya satu kesatuan menjadi terpecah, sehingga skor Pertanyaan 2 turun menjadi
0,6539 dan penjelasan yang dihasilkan lebih umum. Waktu tanggap justru lebih cepat karena
prompt lebih pendek.

**5. Setelah melakukan eksperimen, apa fungsi Chunk Overlap menurut pemahaman kalian?**

Overlap adalah "lem" yang menjaga kalimat di perbatasan dua chunk. Tanpa overlap, sebuah
definisi bisa terbelah dan salah satu bagiannya terambil tanpa pasangannya. Namun overlap
juga berarti duplikasi: pada PDF ini, menaikkan overlap dari 0 ke 40 menambah 10 chunk
(33 menjadi 43), membuat jawaban lebih panjang, dan memunculkan istilah yang tidak ada di
dokumen ("partikulars").

**6. Kenapa perubahan Chunk Size dan Chunk Overlap membutuhkan ingestion ulang?**

Karena keduanya menentukan **isi teks** yang di-embedding. Vektor disimpan sekali saat
ingestion dan tidak dihitung ulang saat pencarian. Kalau database lama dibiarkan, chunk
dengan ukuran lama tetap ada di Qdrant dan hasil pencarian akan mencampur dua konfigurasi
berbeda, sehingga perbandingan menjadi tidak sah. Terbukti pada eksperimen ini: setiap
perubahan menghasilkan `chunks_stored` yang berbeda (81, 38, 29 dan 33, 38, 43).

**7. Kenapa perubahan Temperature tidak membutuhkan ingestion ulang?**

Karena temperature tidak terlibat dalam proses embedding maupun penyimpanan vektor. Ia hanya
dipakai pada saat model bahasa memilih token berikutnya. Database tetap sama persis, dan
memang terbukti: skor kemiripan serta halaman sumber identik di ketiga nilai temperature.

**8. Menurut kalian, apakah ada satu konfigurasi RAG yang akan selalu paling bagus untuk semua jenis dokumen?**

Tidak ada. Hasil eksperimen ini menunjukkan bahwa konfigurasi yang baik bergantung pada
bentuk dokumen dan bentuk pertanyaannya. PDF ini pendek, kalimatnya pendek, dan jawabannya
berupa fakta tunggal, sehingga chunk 100 dengan TOP_K 4 sudah optimal. Untuk dokumen yang
jawabannya tersebar di banyak halaman, TOP_K lebih besar mungkin diperlukan. Untuk dokumen
dengan kalimat sangat panjang, chunk size perlu dinaikkan dan overlap disesuaikan.

## Personal Reflection

**Bagian eksperimen mana yang hasilnya paling berbeda dari dugaan kalian?**

Eksperimen TOP_K. Dugaan awal, TOP_K = 1 hanya akan menghasilkan jawaban yang kurang lengkap.
Kenyataannya model tidak sekadar "tidak tahu", tetapi **mengarang angka yang salah**:
dimensi vektor dijawab 128, padahal 128 adalah batas token. Ini memperlihatkan bahwa konteks
yang kurang bukan hanya mengurangi kelengkapan, tetapi bisa mengubah jawaban menjadi salah
dengan percaya diri.

**Parameter mana yang awalnya kalian anggap tidak terlalu penting tetapi ternyata berpengaruh?**

Chunk overlap. Sebelum mencoba, overlap terasa seperti detail teknis kecil. Ternyata
perubahan 0 → 20 → 40 mengubah jumlah chunk dari 33 menjadi 43, menaikkan skor kemiripan
chunk kedua dari 0,5488 ke 0,5757, dan bahkan mengubah panjang jawaban dari 360 menjadi
456 karakter.

**Setelah mengerjakan tugas ini, bagaimana kalian menjelaskan hubungan antara Retrieval dan Generation pada RAG?**

Retrieval adalah tahap memilih bahan, generation adalah tahap menulis. Kalau retrieval salah,
generation tidak bisa menolong: temperature serendah apa pun tidak akan memunculkan angka 384
bila chunk yang memuatnya tidak terambil (terbukti pada TOP_K = 1). Sebaliknya, bila retrieval
benar, temperature yang terlalu tinggi justru bisa merusak: fakta tetap ada di konteks, tetapi
model mulai menambah kalimat yang tidak ada di dokumen.

**Jika aplikasi ini dikembangkan lebih lanjut, parameter atau bagian apa lagi yang ingin kalian coba?**

Reranking hasil retrieval sebelum masuk ke prompt, penyaringan berdasarkan ambang skor
(misalnya buang chunk di bawah 0,55), hybrid search antara BM25 dan vektor, chunking per
paragraf atau per topik, serta pengukuran recall@k otomatis dengan kumpulan pertanyaan uji
yang lebih banyak. Saya juga ingin mengulang seluruh eksperimen ini dengan `openai/gpt-oss-120b`
agar bisa membandingkan apakah model yang jauh lebih besar tetap menunjukkan pola yang sama.

## AI Usage

**AI tools yang digunakan**

- Agen coding OpenCode (model DeepSeek V4.1 Flash) untuk menyiapkan environment, menulis
  skrip otomatisasi, dan menyusun draf README.
- `Qwen2.5-1.5B-Instruct` lokal sebagai LLM di dalam aplikasi (bagian dari pipeline yang diuji,
  bukan alat bantu penulisan).

**AI digunakan untuk membantu bagian apa?**

Menyiapkan virtual environment dan dependensi, membuat PDF uji melalui `scripts/generate_test_pdf.py`,
menulis skrip `run_experiments.py` / `run_case.py` yang menjalankan 12 kasus secara berurutan
(termasuk menghapus `qdrant_data/` sebelum setiap perubahan chunking), merangkum keluaran ke
`results/*.json`, serta menyusun draf awal README.

**Bagian eksperimen mana yang kalian lakukan dan evaluasi sendiri?**

Penentuan isi dan topik PDF, perumusan dua pertanyaan uji beserta kunci jawabannya, serta
verifikasi bahwa jawaban benar-benar berasal dari halaman yang dikutip (halaman 3 untuk
Pertanyaan 1 dan halaman 2 untuk Pertanyaan 2). Setiap keluaran pada README diperiksa ulang
terhadap berkas `results/*.json` dan teks PDF aslinya, dan interpretasi hasil (misalnya
mengapa TOP_K = 1 menghasilkan jawaban salah) disusun dari perbandingan skor kemiripan dan
isi chunk yang benar-benar terambil.

## Lampiran

Berkas pendukung di repository:

| Berkas | Isi |
| --- | --- |
| `results/temperature_*.json` | keluaran mentah eksperimen temperature (termasuk pengulangan) |
| `results/topk_*.json` | keluaran mentah eksperimen TOP_K |
| `results/chunk_size_*.json` | keluaran mentah eksperimen chunk size |
| `results/chunk_overlap_*.json` | keluaran mentah eksperimen chunk overlap |
| `results/summary.md` | tabel rekap seluruh jawaban dan skor |
| `results/run_summary.json` | ringkasan konfigurasi tiap kasus + hash PDF |
| `scripts/` | generator PDF, orkestrasi eksperimen, dan skrip rekap |
