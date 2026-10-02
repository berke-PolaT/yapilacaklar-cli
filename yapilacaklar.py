"""Yapılacaklar Listesi (To-Do CLI)

Görevleri JSON dosyasında saklayan komut satırı uygulaması.

Kullanım:
    python yapilacaklar.py ekle "Ödev teslim et" -o yuksek -t 2026-10-15
    python yapilacaklar.py listele
    python yapilacaklar.py tamamla 1
    python yapilacaklar.py sil 2
    python yapilacaklar.py temizle
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

VARSAYILAN_DOSYA = Path(__file__).with_name("gorevler.json")

ONCELIKLER = {"yuksek": 0, "orta": 1, "dusuk": 2}
ONCELIK_ETIKETLERI = {"yuksek": "Yüksek", "orta": "Orta", "dusuk": "Düşük"}


class GorevYoneticisi:
    """Görevleri ekleyen, listeleyen ve JSON dosyasına kaydeden sınıf."""

    def __init__(self, dosya=VARSAYILAN_DOSYA):
        self.dosya = Path(dosya)
        self.gorevler = self._yukle()

    def _yukle(self):
        if not self.dosya.exists():
            return []
        try:
            with open(self.dosya, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Uyarı: {self.dosya.name} okunamadı, boş liste ile başlanıyor.",
                  file=sys.stderr)
            return []

    def _kaydet(self):
        with open(self.dosya, "w", encoding="utf-8") as f:
            json.dump(self.gorevler, f, ensure_ascii=False, indent=2)

    def _yeni_id(self):
        return max((g["id"] for g in self.gorevler), default=0) + 1

    def _bul(self, gorev_id):
        for gorev in self.gorevler:
            if gorev["id"] == gorev_id:
                return gorev
        raise KeyError(f"{gorev_id} numaralı görev bulunamadı.")

    def ekle(self, baslik, oncelik="orta", son_tarih=None):
        baslik = baslik.strip()
        if not baslik:
            raise ValueError("Görev başlığı boş olamaz.")
        if oncelik not in ONCELIKLER:
            raise ValueError(f"Geçersiz öncelik: {oncelik}")
        if son_tarih is not None:
            tarih_dogrula(son_tarih)

        gorev = {
            "id": self._yeni_id(),
            "baslik": baslik,
            "oncelik": oncelik,
            "son_tarih": son_tarih,
            "tamamlandi": False,
            "olusturulma": datetime.now().isoformat(timespec="seconds"),
        }
        self.gorevler.append(gorev)
        self._kaydet()
        return gorev

    def tamamla(self, gorev_id):
        gorev = self._bul(gorev_id)
        gorev["tamamlandi"] = True
        self._kaydet()
        return gorev

    def geri_al(self, gorev_id):
        gorev = self._bul(gorev_id)
        gorev["tamamlandi"] = False
        self._kaydet()
        return gorev

    def sil(self, gorev_id):
        gorev = self._bul(gorev_id)
        self.gorevler.remove(gorev)
        self._kaydet()
        return gorev

    def temizle(self):
        """Tamamlanmış görevleri siler ve silinen görev sayısını döndürür."""
        once = len(self.gorevler)
        self.gorevler = [g for g in self.gorevler if not g["tamamlandi"]]
        self._kaydet()
        return once - len(self.gorevler)

    def listele(self, durum="bekleyen"):
        """Görevleri önceliğe ve son tarihe göre sıralı döndürür.

        durum: "bekleyen", "tamamlanan" veya "hepsi"
        """
        if durum == "bekleyen":
            secilenler = [g for g in self.gorevler if not g["tamamlandi"]]
        elif durum == "tamamlanan":
            secilenler = [g for g in self.gorevler if g["tamamlandi"]]
        else:
            secilenler = list(self.gorevler)

        return sorted(secilenler, key=lambda g: (
            g["tamamlandi"],
            ONCELIKLER[g["oncelik"]],
            g["son_tarih"] or "9999-12-31",
            g["id"],
        ))

    def istatistik(self):
        toplam = len(self.gorevler)
        biten = sum(1 for g in self.gorevler if g["tamamlandi"])
        geciken = sum(1 for g in self.gorevler if gecikmis_mi(g))
        return {"toplam": toplam, "tamamlanan": biten,
                "bekleyen": toplam - biten, "geciken": geciken}


def tarih_dogrula(metin):
    try:
        return date.fromisoformat(metin)
    except ValueError:
        raise ValueError(f"Geçersiz tarih: '{metin}'. Biçim YYYY-AA-GG olmalı.") from None


def gecikmis_mi(gorev, bugun=None):
    if gorev["tamamlandi"] or not gorev["son_tarih"]:
        return False
    bugun = bugun or date.today()
    return date.fromisoformat(gorev["son_tarih"]) < bugun


def gorev_satiri(gorev):
    isaret = "[x]" if gorev["tamamlandi"] else "[ ]"
    oncelik = ONCELIK_ETIKETLERI[gorev["oncelik"]]
    tarih = gorev["son_tarih"] or "-"
    if gecikmis_mi(gorev):
        tarih += " (GECİKTİ!)"
    return f"{gorev['id']:>3}  {isaret}  {oncelik:<7} {tarih:<22} {gorev['baslik']}"


def tabloyu_yazdir(gorevler):
    if not gorevler:
        print("Listelenecek görev yok.")
        return
    print(f"{'No':>3}  {'Dur':<3}  {'Öncelik':<7} {'Son Tarih':<22} Görev")
    print("-" * 70)
    for gorev in gorevler:
        print(gorev_satiri(gorev))


def argumanlari_oku(argv=None):
    ayristirici = argparse.ArgumentParser(
        prog="yapilacaklar",
        description="Komut satırından yapılacaklar listesi yönetimi.")
    ayristirici.add_argument("--dosya", default=VARSAYILAN_DOSYA,
                             help="görevlerin saklandığı JSON dosyası")
    komutlar = ayristirici.add_subparsers(dest="komut", required=True)

    ekle = komutlar.add_parser("ekle", help="yeni görev ekle")
    ekle.add_argument("baslik", help="görev açıklaması")
    ekle.add_argument("-o", "--oncelik", choices=ONCELIKLER, default="orta",
                      help="öncelik (varsayılan: orta)")
    ekle.add_argument("-t", "--tarih", help="son tarih (YYYY-AA-GG)")

    listele = komutlar.add_parser("listele", help="görevleri listele")
    grup = listele.add_mutually_exclusive_group()
    grup.add_argument("--hepsi", action="store_true", help="tamamlananlar dahil hepsi")
    grup.add_argument("--tamamlanan", action="store_true", help="sadece tamamlananlar")

    for ad, aciklama in [("tamamla", "görevi tamamlandı işaretle"),
                         ("geri-al", "tamamlanan görevi geri al"),
                         ("sil", "görevi sil")]:
        alt = komutlar.add_parser(ad, help=aciklama)
        alt.add_argument("id", type=int, help="görev numarası")

    komutlar.add_parser("temizle", help="tamamlanan görevleri sil")
    komutlar.add_parser("istatistik", help="özet bilgileri göster")

    return ayristirici.parse_args(argv)


def main(argv=None):
    arg = argumanlari_oku(argv)
    yonetici = GorevYoneticisi(arg.dosya)

    try:
        if arg.komut == "ekle":
            gorev = yonetici.ekle(arg.baslik, arg.oncelik, arg.tarih)
            print(f"Eklendi: #{gorev['id']} {gorev['baslik']}")

        elif arg.komut == "listele":
            durum = "hepsi" if arg.hepsi else "tamamlanan" if arg.tamamlanan else "bekleyen"
            tabloyu_yazdir(yonetici.listele(durum))

        elif arg.komut == "tamamla":
            gorev = yonetici.tamamla(arg.id)
            print(f"Tamamlandı: #{gorev['id']} {gorev['baslik']}")

        elif arg.komut == "geri-al":
            gorev = yonetici.geri_al(arg.id)
            print(f"Geri alındı: #{gorev['id']} {gorev['baslik']}")

        elif arg.komut == "sil":
            gorev = yonetici.sil(arg.id)
            print(f"Silindi: #{gorev['id']} {gorev['baslik']}")

        elif arg.komut == "temizle":
            adet = yonetici.temizle()
            print(f"{adet} tamamlanmış görev silindi.")

        elif arg.komut == "istatistik":
            ist = yonetici.istatistik()
            print(f"Toplam    : {ist['toplam']}")
            print(f"Tamamlanan: {ist['tamamlanan']}")
            print(f"Bekleyen  : {ist['bekleyen']}")
            print(f"Geciken   : {ist['geciken']}")

    except (KeyError, ValueError) as hata:
        sys.exit(f"Hata: {hata.args[0]}")


if __name__ == "__main__":
    main()
