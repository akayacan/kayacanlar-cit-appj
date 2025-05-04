import streamlit as st
import pandas as pd
from PIL import Image
import math

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Ürün listesini Github'dan çek
df_urun = pd.read_excel("https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx")
df_urun["\u00dcrün Adı"] = df_urun["\u00dcrün Adı"].str.strip()

fiyatlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Fiyat (TL)"]))
kodlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Kod"]))

# Girişler
en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["Misinalı", "Galvaniz", "Şerit"])

# Alt modelleri tel tipine göre ayır
tel_modelleri = {
    "Misinalı": ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"],
    "Galvaniz": ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"],
    "Şerit": ["ŞERIT TEL"]
}
tel_model = st.selectbox("Tel Modeli", tel_modelleri[tel_tipi])

# Makara uzunlukları (metre)
tel_makara_uzunluk = {
    "ŞERIT TEL": 200
}
def makara_boyu(tel_model):
    return tel_makara_uzunluk.get(tel_model.upper(), 500)  # default 500m

direk = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])

plastik_modeller = [
    "PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ",
    "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ",
    "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"
]
if direk == "Plastik":
    direk_model = st.selectbox("Plastik Direk Modeli", plastik_modeller)
else:
    direk_model = direk

gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])
gece_modu = st.radio("Gece Modu Eklensin mi?", ("Hayır", "Evet"))

st.markdown("**Yardımcı Ekipmanlar (Evet/Hayır):**")
sikma = st.radio("Sıkma Aparatı", ["Hayır", "Evet"])
toprak = st.radio("Topraklama Çubuğu", ["Hayır", "Evet"])
yildirim = st.radio("Yıldırım Savar", ["Hayır", "Evet"])
gerdirici = st.radio("Tel Gerdirici", ["Hayır", "Evet"])
uyari = st.radio("Uyarı Tabelası", ["Hayır", "Evet"])
kablosu = st.radio("Enerji Aktarma Kablosu", ["Hayır", "Evet"])
masasi = st.radio("Akü Maşası", ["Hayır", "Evet"])
adaptor = st.radio("Adaptör", ["Hayır", "Evet"])
sarj = st.radio("Akü Şarj Aleti", ["Hayır", "Evet"])

if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)
    aparat_sayisi = direk_sayisi * tel_sira

    # Makara hesabı
    makara_uzunluk = makara_boyu(tel_model)
    makara_adedi = math.ceil(toplam_tel / makara_uzunluk)

    # Ürün seçimi
    if toplam_tel <= 250:
        urun = "ECO 500"
    elif toplam_tel <= 1000:
        urun = "ECO 1000"
    elif toplam_tel <= 15000:
        urun = "Safe 2000"
    elif toplam_tel <= 30000:
        urun = "Safe 4000"
    elif toplam_tel <= 45000:
        urun = "Safe 6000"
    elif toplam_tel <= 60000:
        urun = "Safe 8000"
    else:
        urun = "Safe 10000"

    liste = []
    liste.append({"Malzeme": tel_model, "Adet": makara_adedi, "Birim Fiyat": fiyatlar.get(tel_model, 0), "Kod": kodlar.get(tel_model, "")})
    liste.append({"Malzeme": direk_model, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_model, 0), "Kod": kodlar.get(direk_model, "")})
    liste.append({"Malzeme": "Aparat", "Adet": aparat_sayisi, "Birim Fiyat": fiyatlar.get("Aparat", 0), "Kod": kodlar.get("Aparat", "")})
    liste.append({"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0), "Kod": kodlar.get(urun, "")})

    for malzeme, secim in zip(
        ["Sıkma Aparatı", "Topraklama Çubuğu", "Yıldırım Savar", "Tel Gerdirici",
         "Uyarı Tabelası", "Enerji Aktarma Kablosu", "Akü Maşası", "Adaptör", "Akü Şarj Aleti"],
        [sikma, toprak, yildirim, gerdirici, uyari, kablosu, masasi, adaptor, sarj]):
        if secim == "Evet":
            liste.append({"Malzeme": malzeme, "Adet": 1, "Birim Fiyat": fiyatlar.get(malzeme, 0), "Kod": kodlar.get(malzeme, "")})

    df = pd.DataFrame(liste)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader(":orange[Malzeme ve Fiyat Listesi]")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### :moneybag: Toplam Maliyet: **{toplam:.2f} TL**")

    # Excel çıktısı
    data = df.to_csv(index=False).encode("utf-8")
    st.download_button("Excel Çıktısı Al", data, file_name="cit_malzeme_listesi.csv", mime="text/csv")
