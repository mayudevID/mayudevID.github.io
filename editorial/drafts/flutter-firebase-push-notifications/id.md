# Merancang Push Notification yang Andal pada Flutter dengan Firebase Cloud Messaging

Notifikasi yang “andal” berawal dari desain yang berguna, bukan janji bahwa pesan pasti terkirim. Push message bergantung pada konfigurasi layanan, kondisi jaringan, izin pengguna, status aplikasi, dan kebijakan sistem operasi. Perlakukan push sebagai pemicu untuk memuat ulang atau membuka data terkait; server dan aplikasi tetap perlu pulih ketika pesan terlambat atau tidak tertangani.

## Pisahkan pengiriman, tampilan, dan navigasi

Payload notification dan data FCM memiliki tujuan berbeda, sementara perilaku payload campuran bergantung pada apakah aplikasi sedang aktif. Di Flutter, tangani event foreground melalui `FirebaseMessaging.onMessage`. Notifikasi yang diterima saat foreground tidak otomatis ditampilkan secara visual pada Android atau iOS; atur presentasi platform hanya jika sesuai dengan produk. Pekerjaan background menggunakan handler `onBackgroundMessage` tingkat atas. Buat handler ini singkat dan tidak bergantung pada state widget.

Tangani tap notifikasi secara terpisah dari penerimaan pesan. `getInitialMessage()` mencakup aplikasi yang dibuka dari kondisi terminated; `onMessageOpenedApp` mencakup tap yang melanjutkan aplikasi dari background. Validasi payload dan otorisasi sebelum navigasi. Deep link dapat menunjukkan tujuan, tetapi halaman tujuan tetap harus memuat data terbaru dari sumber yang tepercaya.

## Perhitungkan perbedaan platform dan izin

Minta izin notifikasi saat pengguna memahami manfaatnya. Android 13 dan lebih baru serta platform Apple memerlukan izin untuk menampilkan notifikasi. Di iOS, atur kapabilitas Push Notifications dan mode background yang diperlukan, lalu hubungkan kredensial APNs ke Firebase. Di Android, periksa notification channel serta perilaku target SDK aplikasi. Penolakan izin sebaiknya tidak menutup fungsi inti aplikasi.

## Jaga registrasi tetap mutakhir dan uji transisi status

Hubungkan registrasi perangkat dengan akun yang masuk di server, perbarui ketika registrasi berubah, dan hapus atau nonaktifkan hubungan tersebut saat sign-out sesuai kebijakan produk. Jangan perlakukan identifier registrasi sebagai kredensial autentikasi. Uji kondisi foreground, background, terminated, izin ditolak, perubahan token, sign-out, dan tap notifikasi pada konfigurasi platform nyata. Force-stop dan swipe-away dapat berbeda dari kondisi background biasa.

FCM tidak menjamin setiap pesan akan sampai atau tampil di perangkat. Rancang alur data penting agar melakukan rekonsiliasi dengan server saat aplikasi dibuka atau dilanjutkan, dan periksa laporan pengiriman ketika mendiagnosis masalah.

### Bacaan lanjutan

- [Menerima pesan di aplikasi Flutter](https://firebase.google.com/docs/cloud-messaging/flutter/receive-messages)
- [Memulai FCM di Flutter](https://firebase.google.com/docs/cloud-messaging/flutter/get-started)
- [Jenis pesan FCM](https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type)

Draft ini berisi panduan umum. Matriks sistem operasi, SDK, dan konfigurasi aplikasi harus diperiksa ulang sebelum publikasi; tidak ada klaim implementasi notifikasi proyek tertentu.
