"""Generate the text-based test PDF used in every experiment.

Output: data/uploads/modul-rag-dasar.pdf (text based, no images).
Run:    python scripts/generate_test_pdf.py
"""

from pathlib import Path

import pymupdf

PAGE_W, PAGE_H = 595, 842
MARGIN = 56
BODY_SIZE = 10.5
LINE_GAP = 4.5
FONT = "helv"
FONT_BOLD = "hebo"
FONT_ITALIC = "heit"

OUT = Path(__file__).resolve().parent.parent / "data" / "uploads" / "modul-rag-dasar.pdf"


CONTENT = [
    ("title", "Modul Praktikum Sistem Temu Kembali Informasi"),
    ("title2", "Berbasis Retrieval-Augmented Generation (RAG)"),
    ("meta", "Program Studi Ilmu Komputer - Edisi Revisi 2026"),
    ("meta", "Penulis: Tim Laboratorium Sistem Cerdas"),

    ("h1", "Bab 1 Pendahuluan"),
    ("p", "Retrieval-Augmented Generation atau RAG diperkenalkan oleh Patrick Lewis pada tahun 2020. "
          "Makalah tersebut berjudul Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. "
          "Pendekatan ini menggabungkan dua komponen utama. Komponen pertama adalah retriever. Tugasnya "
          "mengambil potongan dokumen yang relevan. Komponen kedua adalah generator. Tugasnya menyusun "
          "jawaban dalam bahasa alami."),
    ("p", "Tujuan utama RAG adalah mengurangi halusinasi model bahasa besar. Model bahasa yang berdiri "
          "sendiri menjawab berdasarkan parameter hasil pelatihan. Informasi tersebut dapat kedaluwarsa. "
          "Dengan RAG, jawaban selalu ditopang oleh konteks. Konteks diambil langsung dari dokumen "
          "pengguna saat pertanyaan diajukan."),
    ("p", "Modul ini terdiri atas tujuh bab. Bab satu membahas pendahuluan. Bab dua membahas arsitektur "
          "sistem. Bab tiga membahas strategi chunking. Bab empat membahas model embedding. Bab lima "
          "membahas basis data vektor dan proses retrieval. Bab enam membahas tahap generation. Bab "
          "tujuh membahas evaluasi dan studi kasus."),
    ("p", "Penilaian praktikum dibagi menjadi dua komponen. Laporan eksperimen memiliki bobot 40 persen. "
          "Demonstrasi aplikasi memiliki bobot 60 persen. Setiap mahasiswa wajib menjalankan aplikasi di "
          "laptop masing-masing. Keluaran yang dilampirkan harus berasal dari aplikasi tersebut. Keluaran "
          "tidak boleh ditulis ulang secara manual."),
    ("h2", "1.1 Capaian Pembelajaran"),
    ("bullet", "Mahasiswa mampu membedakan tahap retrieval dan tahap generation."),
    ("bullet", "Mahasiswa mampu mengubah parameter pipeline dan mengukur dampaknya."),
    ("bullet", "Mahasiswa mampu memilih konfigurasi sesuai karakteristik dokumen."),

    ("h1", "Bab 2 Arsitektur Sistem"),
    ("p", "Alur pemrosesan dokumen pada aplikasi ini terdiri atas lima langkah. Langkah pertama adalah "
          "pengunggahan berkas PDF. Langkah kedua adalah ekstraksi teks per halaman. Langkah ketiga "
          "adalah pemotongan teks menjadi chunk. Langkah keempat adalah perubahan chunk menjadi vektor. "
          "Langkah kelima adalah penyimpanan vektor ke basis data."),
    ("p", "Saat pengguna mengajukan pertanyaan, sistem menjalankan tiga langkah tambahan. Pertanyaan "
          "diubah menjadi vektor dengan model yang sama. Sistem mencari chunk dengan kemiripan "
          "tertinggi. Konteks dan pertanyaan kemudian dikirim ke model bahasa."),
    ("p", "Ekstraksi teks dilakukan dengan pustaka PyMuPDF. Hanya halaman yang memiliki lapisan teks "
          "yang diproses. Halaman hasil pindai tanpa lapisan teks akan dilewati. Pemisahan teks "
          "menggunakan RecursiveCharacterTextSplitter dari pustaka LangChain."),
    ("p", "Penyimpanan vektor menggunakan Qdrant dalam mode lokal. Seluruh data tersimpan di dalam folder "
          "qdrant_data pada direktori proyek. Kemiripan antar vektor diukur dengan cosine similarity. "
          "Nilainya berkisar antara minus satu sampai satu. Semakin mendekati satu, semakin mirip kedua "
          "vektor tersebut."),
    ("p", "Target kinerja pada modul ini adalah waktu tanggap di bawah tiga detik. Target tersebut "
          "berlaku untuk dokumen berukuran kurang dari sepuluh halaman."),
    ("h2", "2.1 Struktur Berkas Proyek"),
    ("bullet", "main.py berisi endpoint HTTP untuk unggah dokumen, bertanya, dan membuat ringkasan."),
    ("bullet", "config.py menyimpan parameter pipeline seperti TOP_K, chunk size, dan chunk overlap."),
    ("bullet", "llm.py membungkus pemanggilan model bahasa dan menyimpan nilai temperature."),
    ("bullet", "vector_store.py mengelola koleksi Qdrant bernama rag_documents."),

    ("h1", "Bab 3 Strategi Chunking"),
    ("p", "Chunking adalah proses memotong teks halaman menjadi bagian kecil. Bagian kecil tersebut "
          "kemudian diubah menjadi vektor. Ukuran chunk dihitung dalam satuan token, bukan karakter. "
          "Nilai default pada modul ini adalah 100 token. Nilai default chunk overlap adalah 20 token."),
    ("p", "Chunk overlap adalah jumlah token yang diulang di awal chunk berikutnya. Fungsinya menjaga "
          "kalimat yang berada di perbatasan dua chunk. Tanpa overlap, sebuah definisi dapat terbelah "
          "menjadi dua. Salah satu chunk dapat terambil sendirian tanpa pasangannya."),
    ("p", "Rekomendasi umum adalah overlap sepuluh sampai dua puluh persen dari ukuran chunk. Overlap "
          "yang terlalu besar membuat basis data membengkak. Teks yang sama tersimpan berulang kali. "
          "Overlap yang terlalu kecil meningkatkan risiko kehilangan konteks."),
    ("p", "Chunk yang terlalu kecil menghasilkan informasi yang tidak lengkap. Jawaban menjadi "
          "terfragmentasi. Chunk yang terlalu besar membuat satu vektor mewakili banyak topik. Arah "
          "vektornya menjadi kabur dan skor kemiripan menurun."),
    ("p", "Ukuran chunk memengaruhi isi teks yang di-embedding. Setiap perubahan chunk size mewajibkan "
          "proses ingestion ulang. Hal yang sama berlaku untuk perubahan chunk overlap."),
    ("h2", "3.1 Prosedur Pengujian Chunking"),
    ("bullet", "Hentikan server, hapus folder qdrant_data, lalu jalankan server kembali."),
    ("bullet", "Unggah ulang berkas PDF yang sama melalui halaman utama aplikasi."),
    ("bullet", "Catat nilai chunks_stored yang dikembalikan oleh endpoint ingestion."),
    ("bullet", "Ajukan pertanyaan yang sama dan simpan jawaban beserta skor kemiripannya."),
    ("h2", "3.2 Strategi Chunking Alternatif"),
    ("p", "Selain pemotongan berbasis jumlah token, terdapat beberapa strategi lain. Semantic chunking "
          "memotong teks berdasarkan perubahan topik. Caranya membandingkan kemiripan antar kalimat "
          "berurutan. Sentence window retrieval menyimpan kalimat sebagai unit pencarian. Konteks yang "
          "dikirim adalah beberapa kalimat di sekitarnya."),
    ("p", "Parent document retrieval mengambil chunk kecil untuk pencarian. Bagian induk yang lebih "
          "besar dikirim kepada model bahasa. Ketiga strategi tersebut menyelesaikan masalah yang sama. "
          "Masalahnya adalah ketegangan antara presisi pencarian dan kelengkapan konteks."),
    ("p", "Chunk kecil unggul untuk menemukan lokasi informasi. Chunk besar unggul untuk memberi konteks "
          "yang utuh. Parent document retrieval mencoba mengambil keuntungan keduanya. Harganya adalah "
          "kompleksitas implementasi dan kebutuhan penyimpanan tambahan."),
    ("p", "Pada praktikum ini hanya pemotongan berbasis token yang diuji. Tujuannya agar variabel yang "
          "berubah tetap terkendali. Strategi lain dapat dicoba pada tugas lanjutan."),

    ("h1", "Bab 4 Model Embedding"),
    ("p", "Model embedding yang digunakan adalah "
          "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2. Model ini memiliki dua belas "
          "lapisan transformer. Vektor yang dihasilkan berdimensi 384. Model ini mendukung lebih dari "
          "lima puluh bahasa, termasuk bahasa Indonesia."),
    ("p", "Panjang masukan maksimum model tersebut adalah 128 token. Teks yang lebih panjang akan "
          "dipotong secara otomatis. Sisa teks tidak lagi diperhitungkan dalam perhitungan vektor. "
          "Karena itu ukuran chunk pada modul dijaga di bawah 128 token."),
    ("p", "Aturan penting dalam penggunaan embedding adalah konsistensi model. Vektor pertanyaan dan "
          "vektor dokumen harus berasal dari model yang sama. Jika model diganti, seluruh dokumen wajib "
          "di-ingest ulang. Ruang vektor dari model berbeda tidak dapat dibandingkan."),
    ("p", "Kualitas embedding dipengaruhi oleh kualitas teks masukan. Teks hasil ekstraksi yang "
          "berantakan menghasilkan vektor yang kurang representatif. Karena itu PDF berbasis teks yang "
          "rapi sangat dianjurkan pada seluruh eksperimen."),

    ("h1", "Bab 5 Basis Data Vektor dan Retrieval"),
    ("p", "Qdrant menyimpan setiap chunk sebagai sebuah point. Setiap point memiliki identifier unik, "
          "vektor, dan payload. Payload berisi teks chunk, nama berkas sumber, nomor halaman, dan indeks "
          "chunk. Koleksi yang digunakan bernama rag_documents. Metrik jarak yang dipakai adalah COSINE."),
    ("p", "Jumlah chunk yang diambil ditentukan oleh parameter TOP_K. Nilai default TOP_K pada modul "
          "adalah 4. Untuk pembuatan ringkasan digunakan BRIEF_TOP_K sebesar 6. Seluruh chunk yang "
          "terambil digabung menjadi satu blok konteks dan dikirim ke model bahasa."),
    ("p", "Pemilihan nilai TOP_K selalu merupakan kompromi. Nilai yang terlalu kecil berisiko tidak "
          "menyertakan chunk jawaban. Nilai yang terlalu besar menambahkan chunk yang kurang relevan. "
          "Model bahasa dapat teralihkan oleh informasi yang tidak diperlukan."),
    ("p", "Sebagai panduan praktis, skor di atas 0,75 menandakan chunk yang relevan. Skor di bawah 0,55 "
          "sering menandakan chunk yang tidak berhubungan. Ambang batas ini bersifat empiris. Nilainya "
          "bergantung pada model embedding dan jenis dokumen."),
    ("h2", "5.1 Mereset Basis Data"),
    ("bullet", "Hentikan proses server agar berkas basis data tidak terkunci."),
    ("bullet", "Hapus seluruh isi folder qdrant_data pada direktori proyek."),
    ("bullet", "Jalankan server kembali, koleksi dibuat ulang secara otomatis."),

    ("h1", "Bab 6 Tahap Generation dan Temperature"),
    ("p", "Tahap generation adalah tahap penyusunan jawaban. Model bahasa menyusun jawaban berdasarkan "
          "konteks yang diberikan. Model yang digunakan adalah openai/gpt-oss-120b melalui layanan "
          "Groq. Panjang jawaban dibatasi maksimum 512 token keluaran."),
    ("p", "Temperature mengatur tingkat keacakan pemilihan token. Nilai 0,0 membuat model memilih token "
          "dengan probabilitas tertinggi. Jawaban menjadi deterministik dan cenderung sama pada setiap "
          "pengulangan. Nilai 0,2 memberi sedikit variasi tanpa keluar dari fakta konteks. Nilai 0,8 "
          "memberi kebebasan lebih besar. Kalimat menjadi lebih bervariasi dan lebih panjang. Risiko "
          "menyimpang dari konteks juga meningkat."),
    ("p", "Temperature hanya memengaruhi tahap generation. Nilai tersebut tidak mengubah proses "
          "embedding. Isi basis data vektor juga tidak berubah. Chunk yang terambil tetap sama. Karena "
          "itu perubahan temperature tidak memerlukan ingestion ulang. Skor kemiripan tetap sama untuk "
          "pertanyaan yang sama."),
    ("p", "System prompt memerintahkan model menjawab hanya dari konteks. Model juga diminta menyebutkan "
          "sumber dan halaman bila diperlukan. Jika informasi tidak ditemukan, model harus menyatakannya "
          "dengan jujur."),
    ("h2", "6.1 Pengaruh Jumlah Konteks"),
    ("p", "Semakin banyak chunk yang dikirim, semakin panjang prompt yang diterima model bahasa. Prompt "
          "panjang meningkatkan biaya dan waktu tanggap secara linear. Model bahasa juga memiliki "
          "keterbatasan memusatkan perhatian. Fenomena ini disebut lost in the middle. Model cenderung "
          "mengabaikan informasi di tengah konteks yang panjang."),
    ("p", "Menaikkan TOP_K tanpa memeriksa kualitas chunk dapat menurunkan mutu jawaban. Strategi yang "
          "lebih baik adalah memastikan chunk teratas benar-benar relevan. Salah satu caranya adalah "
          "penyaringan berdasarkan ambang skor kemiripan."),
    ("h2", "6.2 Halusinasi dan Kesetiaan pada Konteks"),
    ("p", "Halusinasi adalah pernyataan yang tidak didukung oleh konteks. Pada sistem RAG, halusinasi "
          "muncul dalam tiga bentuk. Bentuk pertama adalah menambahkan angka yang tidak ada. Bentuk "
          "kedua adalah menggabungkan dua fakta dari halaman berbeda. Bentuk ketiga adalah menjawab "
          "dengan pengetahuan umum saat konteks tidak memuat jawaban."),
    ("p", "Cara paling sederhana menekan halusinasi adalah memperketat system prompt. Model diminta "
          "menyebutkan halaman sumber untuk setiap klaim. Cara lain adalah menurunkan temperature. "
          "Mengurangi chunk yang tidak relevan juga membantu."),

    ("h1", "Bab 7 Evaluasi dan Studi Kasus"),
    ("p", "Evaluasi RAG tidak cukup hanya dengan membaca jawaban. Diperlukan metrik retrieval seperti "
          "recall at k. Metrik ini mengukur proporsi pertanyaan yang chunk jawabannya muncul di antara k "
          "chunk teratas. Metrik lain adalah mean reciprocal rank. Pada sisi generation dikenal metrik "
          "faithfulness."),
    ("p", "Studi kasus pada modul ini menggunakan koleksi Perpustakaan Digital Universitas Cakrawala. "
          "Koleksi tersebut berisi 1.240 dokumen. Rata-rata setiap dokumen memiliki enam halaman. "
          "Pengujian dilakukan terhadap 120 pertanyaan uji. Jawaban pertanyaan telah diverifikasi manual "
          "oleh pustakawan."),
    ("p", "Konfigurasi chunk 100 token dengan overlap 20 token memberi recall at 4 sebesar 0,82. "
          "Chunk size 50 token menurunkan recall at 4 menjadi 0,74. Banyak chunk kehilangan konteks "
          "kalimat. Chunk size 150 token memberi recall at 4 sebesar 0,79. Vektor mulai mewakili terlalu "
          "banyak gagasan."),
    ("p", "TOP_K sama dengan 8 menaikkan recall at 8 menjadi 0,91. Namun skor faithfulness turun "
          "sebesar 0,06 dibandingkan TOP_K sama dengan 4. Menambah jumlah konteks tidak selalu "
          "memperbaiki kualitas jawaban."),
    ("h2", "7.1 Kesimpulan Modul"),
    ("bullet", "Tidak ada satu konfigurasi yang optimal untuk semua jenis dokumen."),
    ("bullet", "Parameter chunking memengaruhi isi basis data, temperature hanya gaya jawaban."),
    ("bullet", "Setiap perubahan parameter diuji dengan pertanyaan yang sama."),
]


class Layout:
    def __init__(self):
        self.doc = pymupdf.open()
        self.page = None
        self.y = 0.0
        self.page_no = 0

    def new_page(self):
        self.page = self.doc.new_page(width=PAGE_W, height=PAGE_H)
        self.page_no += 1
        self.y = MARGIN

    def space(self, amount):
        self.y += amount

    def need(self, height):
        if self.y + height > PAGE_H - MARGIN:
            self.new_page()

    def wrap(self, text, size, font, width):
        words = text.split(" ")
        lines, current = [], ""
        for word in words:
            candidate = word if not current else current + " " + word
            if pymupdf.get_text_length(candidate, fontname=font, fontsize=size) <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def write(self, text, size, font, leading, align_center=False, after=0.0):
        width = PAGE_W - 2 * MARGIN
        for line in self.wrap(text, size, font, width):
            self.need(leading)
            if align_center:
                w = pymupdf.get_text_length(line, fontname=font, fontsize=size)
                x = (PAGE_W - w) / 2
            else:
                x = MARGIN
            self.page.insert_text((x, self.y + size), line, fontname=font, fontsize=size)
            self.y += leading
        self.y += after

    def bullet(self, text):
        width = PAGE_W - 2 * MARGIN - 14
        lines = self.wrap(text, BODY_SIZE, FONT, width)
        for i, line in enumerate(lines):
            leading = BODY_SIZE + LINE_GAP
            self.need(leading)
            if i == 0:
                self.page.insert_text((MARGIN + 2, self.y + BODY_SIZE), "-", fontname=FONT, fontsize=BODY_SIZE)
            self.page.insert_text((MARGIN + 14, self.y + BODY_SIZE), line, fontname=FONT, fontsize=BODY_SIZE)
            self.y += leading
        self.y += 3

    def footer(self):
        for page in self.doc:
            page.insert_text(
                (PAGE_W / 2 - 40, PAGE_H - 30),
                f"Halaman {page.number + 1} dari {self.doc.page_count}",
                fontname=FONT_ITALIC,
                fontsize=8,
                color=(0.4, 0.4, 0.4),
            )


def build():
    layout = Layout()
    layout.new_page()
    for kind, text in CONTENT:
        if kind == "title":
            layout.space(24)
            layout.write(text, 19, FONT_BOLD, 24, align_center=True)
        elif kind == "title2":
            layout.write(text, 15, FONT_BOLD, 20, align_center=True, after=6)
        elif kind == "meta":
            layout.space(4)
            layout.write(text, 10, FONT_ITALIC, 14, align_center=True)
        elif kind == "h1":
            layout.space(10)
            layout.need(26)
            layout.write(text, 13.5, FONT_BOLD, 18, after=4)
        elif kind == "h2":
            layout.space(6)
            layout.need(22)
            layout.write(text, 11.5, FONT_BOLD, 16, after=2)
        elif kind == "p":
            layout.write(text, BODY_SIZE, FONT, BODY_SIZE + LINE_GAP, after=6)
        elif kind == "bullet":
            layout.bullet(text)
    layout.footer()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    layout.doc.save(str(OUT))
    layout.doc.close()
    print(f"written: {OUT} ({layout.page_no} pages)")


if __name__ == "__main__":
    build()
