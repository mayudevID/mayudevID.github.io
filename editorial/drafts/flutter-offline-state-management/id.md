# Mengelola Data Offline dan Application State pada Flutter

Indikator offline hanya menunjukkan bahwa perangkat tampak terhubung atau tidak ke jaringan. Indikator itu tidak dapat memastikan API tertentu dapat diakses atau pengguna masih berhak membuka sumber daya yang dilindungi. Desain offline yang baik menentukan data yang bisa dibaca lokal, perubahan yang dapat diantrekan, dan kapan aplikasi perlu meminta data lagi ke server.

## Beri nama pada sumber setiap state

Pisahkan state UI sementara—seperti tab yang dipilih—dari data akun remote dan data lokal yang bertahan. Untuk setiap layar, tentukan apakah tampilan awal memakai cache, menunggu jaringan, atau menggabungkan keduanya. Tampilkan kapan informasi cache terakhir diperbarui bila kesegarannya penting. Bedakan state loading, kosong, usang, berhasil, dan gagal agar permintaan yang tidak tersedia tidak dianggap sebagai hasil kosong.

## Tentukan penyimpanan dan sinkronisasi dengan sengaja

Gunakan penyimpanan key-value sederhana untuk preferensi dan database terstruktur ketika data memiliki relasi atau perlu dicari. Panduan offline-first Flutter menjelaskan strategi repository untuk menggabungkan sumber lokal dan remote; kebijakan yang tepat bergantung pada data. Tentukan operasi yang aman untuk diulang, cara mencegah pengiriman duplikat, dan respons saat server menolak perubahan offline. Untuk perubahan yang bertentangan, buat aturan merge atau penyelesaian oleh pengguna alih-alih diam-diam menimpa salah satu versi.

## Hormati autentikasi dan kepemilikan data

Hubungkan data lokal dengan akun yang masuk dan hapus atau pisahkan data saat akun berubah. Hindari menampilkan cache pengguna pertama setelah pengguna lain masuk. Kredensial kedaluwarsa, akses yang dicabut, dan penghapusan dari server dapat membatalkan asumsi lokal; tentukan kapan aplikasi perlu memvalidasi ulang sebelum tindakan sensitif.

## Uji tanpa mengandalkan callback konektivitas

Uji airplane mode, captive portal, kegagalan DNS, permintaan lambat atau terputus, proses yang dimulai ulang, dan perubahan server bersamaan. Sinyal konektivitas hanya petunjuk; permintaan nyata tetap dapat gagal. Pastikan retry memiliki batas dan idempoten, pekerjaan antrean terlihat, serta pengguna dapat pulih dari konflik. Periksa migrasi dan backup data lokal ketika skemanya berkembang.

### Bacaan lanjutan

- [Dukungan offline-first Flutter](https://docs.flutter.dev/app-architecture/design-patterns/offline-first)
- [Studi kasus data layer Flutter](https://docs.flutter.dev/app-architecture/case-study/data-layer)
- [Arsitektur penyimpanan SQL persisten](https://docs.flutter.dev/app-architecture/design-patterns/sql)

Ini adalah panduan desain umum, bukan penjelasan tentang cara proyek portofolio tertentu menangani sinkronisasi offline.
