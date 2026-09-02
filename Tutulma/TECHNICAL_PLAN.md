# Tutulma — Teknik Plan

## Ana teknoloji
Unity.

## Mimari yaklaşım
Sistemler bağımsız ve genişletilebilir tutulacak. Oyuncu, dünya, görev, yapay zekâ, kayıt ve ağ sistemleri birbirine gereksiz şekilde bağlanmayacak.

## İlk teknik katman
- Player controller
- Camera
- World bootstrap
- Sun anomaly
- Temel etkileşim
- Görev veri yapısı
- Save/load planı

## Sonraki teknik katmanlar
- Environment streaming
- AI
- Dialogue
- Quest system
- Inventory/equipment
- Vehicles
- Space travel
- Save system
- Audio
- Visual effects
- Multiplayer

## Büyük dünya yaklaşımı
Dünya ve uzay tek parça dev bir sahne olarak tasarlanmak zorunda değildir. Bölgesel yükleme, sahne bölme ve gerektiğinde temsilî ölçek kullanılacaktır.

## Performans
Hedef yüksek görsel kalite + kararlı performanstır. Optimizasyon sonradan yapılacak bir iş değil, sistemler geliştikçe sürekli kontrol edilecek bir gerekliliktir.

## Multiplayer
Multiplayer, tek oyunculu mimarinin tamamını sonradan bozacak şekilde eklenmeyecek. Ağ gerektiren sistemler erken aşamada veri ve sorumluluk açısından buna uygun tasarlanacak; gerçek ağ uygulaması prototipten sonra yapılacak.

## Git
Unity'nin ürettiği geçici/büyük klasörler depoya alınmayacak. Kaynak kod, tasarım belgeleri ve gerekli proje dosyaları sürümlendirilecek.
