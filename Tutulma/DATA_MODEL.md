# Tutulma — Veri Modeli

## Amaç
Unity'ye geçildiğinde görev, diyalog, envanter ve kayıt sistemlerinin aynı veri mantığını kullanmasını sağlamak.

## Kimlikler
Her oyun nesnesi benzersiz bir ID kullanır: görev, eşya, diyalog, karakter, bölge ve kayıt noktası.

## Görev verisi
- ID
- Başlık
- Hedefler
- Ön koşullar
- Ödül/sonuç
- Dünya etkileri
- İlgili bölge

## Diyalog verisi
- ID
- Konuşmacı
- Metin
- Seçenekler
- Ön koşullar
- Sonuçlar

## Eşya verisi
- ID
- İsim
- Kategori
- Açıklama
- Ağırlık
- Kullanım türü
- Biriktirilebilirlik

## Kayıt verisi
- Hikâye ilerlemesi
- Görev durumları
- Diyalog kararları
- Envanter
- Oyuncu konumu
- Dünya durumu
- Ayarlar

## Kural
Oyun mantığı ile veri birbirine gereksiz şekilde gömülmeyecek. Böylece içerik genişletilebilir ve kayıt sistemi güvenilir tutulabilir.
