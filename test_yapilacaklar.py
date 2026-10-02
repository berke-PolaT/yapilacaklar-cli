import tempfile
import unittest
from datetime import date
from pathlib import Path

from yapilacaklar import GorevYoneticisi, gecikmis_mi


class GorevYoneticisiTesti(unittest.TestCase):
    def setUp(self):
        self.klasor = tempfile.TemporaryDirectory()
        self.dosya = Path(self.klasor.name) / "gorevler.json"
        self.yonetici = GorevYoneticisi(self.dosya)

    def tearDown(self):
        self.klasor.cleanup()

    def test_ekle_ve_dosyaya_kaydet(self):
        self.yonetici.ekle("Ödev yap", "yuksek", "2026-10-15")
        yeniden = GorevYoneticisi(self.dosya)
        self.assertEqual(len(yeniden.gorevler), 1)
        self.assertEqual(yeniden.gorevler[0]["baslik"], "Ödev yap")

    def test_idler_artarak_verilir(self):
        a = self.yonetici.ekle("A")
        b = self.yonetici.ekle("B")
        self.assertEqual((a["id"], b["id"]), (1, 2))

    def test_bos_baslik_eklenemez(self):
        with self.assertRaises(ValueError):
            self.yonetici.ekle("   ")

    def test_gecersiz_tarih_eklenemez(self):
        with self.assertRaises(ValueError):
            self.yonetici.ekle("Görev", son_tarih="15.10.2026")

    def test_tamamla_ve_geri_al(self):
        self.yonetici.ekle("Görev")
        self.assertTrue(self.yonetici.tamamla(1)["tamamlandi"])
        self.assertFalse(self.yonetici.geri_al(1)["tamamlandi"])

    def test_olmayan_gorev_hata_verir(self):
        with self.assertRaises(KeyError):
            self.yonetici.sil(42)

    def test_listeleme_oncelige_gore_siralar(self):
        self.yonetici.ekle("Düşük", "dusuk")
        self.yonetici.ekle("Yüksek", "yuksek")
        self.yonetici.ekle("Orta", "orta")
        basliklar = [g["baslik"] for g in self.yonetici.listele()]
        self.assertEqual(basliklar, ["Yüksek", "Orta", "Düşük"])

    def test_listeleme_filtreleri(self):
        self.yonetici.ekle("A")
        self.yonetici.ekle("B")
        self.yonetici.tamamla(1)
        self.assertEqual(len(self.yonetici.listele("bekleyen")), 1)
        self.assertEqual(len(self.yonetici.listele("tamamlanan")), 1)
        self.assertEqual(len(self.yonetici.listele("hepsi")), 2)

    def test_temizle_sadece_tamamlananlari_siler(self):
        self.yonetici.ekle("A")
        self.yonetici.ekle("B")
        self.yonetici.tamamla(2)
        self.assertEqual(self.yonetici.temizle(), 1)
        self.assertEqual([g["baslik"] for g in self.yonetici.gorevler], ["A"])


class GecikmeTesti(unittest.TestCase):
    def test_gecmis_tarihli_gorev_gecikmistir(self):
        gorev = {"tamamlandi": False, "son_tarih": "2026-01-01"}
        self.assertTrue(gecikmis_mi(gorev, bugun=date(2026, 1, 2)))
        self.assertFalse(gecikmis_mi(gorev, bugun=date(2026, 1, 1)))

    def test_tamamlanan_veya_tarihsiz_gorev_gecikmez(self):
        self.assertFalse(gecikmis_mi({"tamamlandi": True, "son_tarih": "2000-01-01"}))
        self.assertFalse(gecikmis_mi({"tamamlandi": False, "son_tarih": None}))


if __name__ == "__main__":
    unittest.main()
