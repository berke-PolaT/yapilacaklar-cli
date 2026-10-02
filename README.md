# ✅ Yapılacaklar Listesi (To-Do CLI)

Görevlerini terminalden yönetebileceğin, verileri JSON dosyasında saklayan bir komut satırı uygulaması. Python ile yazıldı.

## ✨ Özellikler

- Görev **ekleme, tamamlama, geri alma ve silme**
- **Öncelik seviyeleri**: yüksek, orta, düşük
- **Son tarih** desteği ve süresi geçen görevler için **"GECİKTİ!"** uyarısı
- Önceliğe ve tarihe göre **otomatik sıralama**
- Bekleyen, tamamlanan veya tüm görevleri **filtreleme**
- Tamamlanan görevleri tek komutla **temizleme**
- **İstatistik** özeti
- Veriler `gorevler.json` dosyasında kalıcı olarak saklanır

## 🚀 Kullanım

Python 3.8 veya üstü gerekir. Ek kütüphane gerekmez.

```bash
python yapilacaklar.py ekle "Algoritma ödevini teslim et" -o yuksek -t 2026-10-15
python yapilacaklar.py ekle "Git öğren" -o dusuk
python yapilacaklar.py listele
python yapilacaklar.py tamamla 1
python yapilacaklar.py listele --hepsi
python yapilacaklar.py istatistik
```

### Komutlar

| Komut | Açıklama |
|---|---|
| `ekle "metin" [-o öncelik] [-t YYYY-AA-GG]` | Yeni görev ekler |
| `listele [--hepsi \| --tamamlanan]` | Görevleri listeler (varsayılan: bekleyenler) |
| `tamamla <no>` | Görevi tamamlandı olarak işaretler |
| `geri-al <no>` | Tamamlanan görevi bekleyene geri alır |
| `sil <no>` | Görevi siler |
| `temizle` | Tamamlanan tüm görevleri siler |
| `istatistik` | Toplam, tamamlanan, bekleyen ve geciken görev sayıları |

## 🖥️ Örnek Çıktı

```
 No  Dur  Öncelik Son Tarih              Görev
----------------------------------------------------------------------
  1  [ ]  Yüksek  2026-10-15             Algoritma ödevini teslim et
  2  [ ]  Orta    2026-09-30 (GECİKTİ!)  Fizik lab raporu
  3  [ ]  Düşük   -                      Git öğren
  4  [x]  Orta    -                      Market alışverişi
```

## 🗂️ Veri Formatı

```json
[
  {
    "id": 1,
    "baslik": "Algoritma ödevini teslim et",
    "oncelik": "yuksek",
    "son_tarih": "2026-10-15",
    "tamamlandi": false,
    "olusturulma": "2026-10-02T16:54:07"
  }
]
```

## 🧪 Testler

```bash
python -m unittest -v
```

## 📚 Bu Projede Öğrendiklerim

- Sınıf (class) yapısı ile kodu düzenleme
- `json` modülü ile kalıcı veri saklama
- `argparse` ile alt komutlu (subcommand) CLI tasarımı
- `datetime` ile tarih işlemleri
- `sorted()` ve `lambda` ile çok kriterli sıralama
- Hata yönetimi ve anlamlı hata mesajları
- `unittest` ve geçici dosyalarla test yazma

## 📄 Lisans

[MIT](LICENSE)
