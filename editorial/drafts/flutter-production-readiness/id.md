# Persiapan Aplikasi Flutter untuk Production: Checklist Engineering

Merilis aplikasi adalah satu pencapaian; mengoperasikannya dengan aman adalah pekerjaan berikutnya. Tinjauan sebelum rilis sebaiknya menelusuri apa yang terjadi ketika data tidak tersedia, permintaan mengalami timeout, pengguna berganti akun, atau rilis perlu dibatalkan. Checklist ini merupakan panduan rekayasa umum, bukan laporan insiden pada proyek tertentu.

## Mulai dari batas yang dapat diuji

Pisahkan tanggung jawab UI dari akses data. Tempatkan panggilan API pada service dan kelola cache, aturan retry, serta pemetaan data pada repository atau batas yang setara. Panduan arsitektur Flutter merekomendasikan lapisan UI dan data; repository menangani kebutuhan seperti cache, penanganan error, dan retry. Gunakan struktur secukupnya. Nama lapisan tidak sepenting kepemilikan tanggung jawab dan input-output yang jelas serta dapat diuji.

## Buat kegagalan terlihat dan dapat dipulihkan

Modelkan kegagalan yang diperkirakan—status offline, sesi yang kedaluwarsa, input tidak valid, dan error server—agar UI dapat menjelaskan masalah dan menawarkan langkah aman. Jangan samakan setiap exception dengan status berhasil atau data kosong. Catat konteks yang cukup untuk mendiagnosis masalah tanpa menyimpan kredensial atau data sensitif pengguna. Tangani error framework dan asynchronous yang tidak tertangkap pada batas yang sesuai, tetapi jangan mengandalkan handler global sebagai pengganti pemulihan lokal.

## Perlakukan konfigurasi sebagai bagian dari rilis

Pastikan setiap flavor mengarah ke API dan proyek Firebase yang tepat. Jangan simpan rahasia di aplikasi klien: nilai yang dikirim bersama aplikasi mobile harus dianggap dapat diekstrak. Periksa signing, bundle identifier, permission, kapabilitas notifikasi, pengungkapan privasi, dan materi toko untuk Android serta iOS. Catat artefak dan revisi sumber yang digunakan pada setiap rilis.

## Uji jalur kegagalan, lalu ukur

Uji parsing dan aturan bisnis dengan unit test, uji state loading, kosong, berhasil, dan error dengan widget test, lalu gunakan integration test untuk alur pengguna berisiko tinggi. Sertakan sesi kedaluwarsa, respons lambat, tap berulang, aplikasi dilanjutkan kembali, dan layanan tidak tersedia. Ukur startup dan performa frame pada profile build serta perangkat yang mewakili pengguna; debug build bukan pengukuran performa production. Tambahkan crash reporting hanya dengan kebijakan privasi dan pemetaan rilis yang jelas.

## Rencanakan pembaruan pertama setelah rilis

Tetapkan cara mendeteksi rilis bermasalah, menangani insiden, mengirim perbaikan, dan menjaga data pengguna saat upgrade. Pantau crash-free sessions, latensi, dan penyelesaian tugas bersama laporan dukungan; satu skor tidak cukup untuk menjelaskan keandalan. Pelihara dependency dan target platform, lalu ulangi checklist ketika risiko atau dukungan platform berubah.

### Bacaan lanjutan

- [Panduan arsitektur aplikasi Flutter](https://docs.flutter.dev/app-architecture/guide)
- [Penanganan error di Flutter](https://docs.flutter.dev/testing/errors)
- [Pengujian aplikasi Flutter](https://docs.flutter.dev/testing/overview)
- [Praktik terbaik performa Flutter](https://docs.flutter.dev/perf/best-practices)

Draft ini tidak menggunakan contoh implementasi spesifik proyek. Contoh atau klaim operasional yang ditambahkan untuk publikasi perlu ditinjau sumbernya dan dikonfirmasi pemiliknya.
