# Tutulma — Pre-Unity Consistency Audit

## Amaç
Unity'ye geçmeden önce tasarım belgelerinin birbirleriyle uyumunu kontrol eden son tasarım denetimi.

## Kontrol Sonuçları

### Hikâye ↔ Oynanış
- Güneş anomalisi ana olay örgüsünün merkezinde kalıyor.
- Dünya'dan ayrılma hedefi görev yapısına bağlanabiliyor.
- Uzaylılar erken dönemde ortaya çıkıyor ve yalnızca savaş düşmanı olarak kullanılmıyor.
- İlk oyunun finali, sonraki oyunların daha büyük kozmik hikâyesine kapı bırakıyor.

### Oyuncu ↔ Sistemler
- Oyuncu keşif, etkileşim, görev, ekipman ve hayatta kalma döngüsünün merkezinde.
- Envanter ve ekipman görevlerle doğrudan ilişkilendirilebilir.
- Diyalog ve seçimler görev sonuçlarını etkileyebilecek şekilde tasarlanacak.
- Araçlar ayrı bir sistem olarak ele alınarak oyuncu kontrolünden kopuk tasarlanmayacak.

### Dünya ↔ Performans
- Dünya tek parça dev sahne olmak zorunda değil.
- Bölgesel yükleme/streaming kullanılabilir.
- Kozmik nesneler gerektiğinde temsilî ölçekle gösterilebilir.
- Görsel kalite; LOD, ışık, efekt ve görüş mesafesiyle birlikte yönetilecek.

### Multiplayer ↔ Tek Oyuncu
- Multiplayer sonradan bütün mimariyi bozacak bir eklenti olarak tasarlanmayacak.
- Ağ gerektiren veri ve sorumluluklar baştan ayrıştırılacak.
- İlk prototipin multiplayer'ı tamamlaması gerekmiyor.

### Git ↔ Unity
- Tasarım belgeleri kaynak koddan ayrı tutuluyor.
- Unity'nin geçici klasörleri depoya alınmayacak.
- Kaynak kod ve gerekli proje ayarları sürümlendirilecek.

## Bilinçli Olarak Ertelenen Kararlar

Bazı kararlar Unity Editor ve hedef donanım görülmeden kesinleştirilmemeli:
- Kesin Unity sürümü
- Render pipeline seçimi
- Nihai grafik ayarları
- Kesin multiplayer çözümü
- Nihai asset paketleri
- Hedef çözünürlük/FPS kombinasyonu

Bu kararları şimdiden rastgele sabitlemek yerine prototip aşamasında ölçüm yaparak belirlemek daha güvenlidir.

## Sonuç
Tasarım omurgasında kritik bir çelişki bulunmadı. Bir sonraki aşama Unity içinde gerçek prototip oluşturmak için gerekli temel hazırlığın tamamlanmasıdır.
