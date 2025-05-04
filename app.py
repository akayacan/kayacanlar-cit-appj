import streamlit as st
import pandas as pd
from PIL import Image
import math

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Excel dosyasını GitHub'dan oku
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun.columns = df_urun.columns.str.strip()

# Kod ve fiyat sözlüklerini tanımla
fiyatlar = dict(zip(df_urun["Ürün Adı"], df_urun["Fiyat"]))
kodlar = dict(zip(df_urun["Ürün Adı"], df_urun["Kod"]))

# Giriş değerleri
en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "At", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["MISINALI", "GALVANIZ", "SERIT"])

# Alt seçenek: Kalınlık seçimi
tel_kalınlıklar = {
    "MISINALI": ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"],
    "GALVANIZ": ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"],
    "SERIT": ["SERIT TEL"]
}
alt_tel = st.selectbox("Tel Kalınlığı", tel_kalınlıklar[tel_tipi])

# Hesapla butonu
if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "At": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    tel_uzunluk = cevre * tel_sira

    # Makara uzunlukları
    if "ŞERIT" in alt_tel.upper():
        makara_uzunluk = 200
    else:
        makara_uzunluk = 500

    makara_sayisi = math.ceil(tel_uzunluk / makara_uzunluk)

    # Uygun enerji cihazı seçimi
    cihaz = ""
    if tel_uzunluk <= 250:
        cihaz = "ECO 500"
    elif tel_uzunluk <= 1000:
        cihaz = "ECO 1000"
    elif tel_uzunluk <= 15000:
        cihaz = "Safe 2000"
    elif tel_uzunluk <= 30000:
        cihaz = "Safe 4000"
    elif tel_uzunluk <= 45000:
        cihaz = "Safe 6000"
    elif tel_uzunluk <= 60000:
        cihaz = "Safe 8000"
    else:
        cihaz = "Safe 10000"

    liste = [
        {"Malzeme": alt_tel, "Adet": makara_sayisi},
        {"Malzeme": cihaz, "Adet": 1}
    ]

    # Kod ve fiyat ekle
    for row in liste:
        urun = row["Malzeme"]
        row["Kod"] = kodlar.get(urun, "-")
        row["Birim Fiyat"] = fiyatlar.get(urun, 0)
        row["Toplam"] = row["Adet"] * row["Birim Fiyat"]

    df_son = pd.DataFrame(liste)
    toplam = df_son["Toplam"].sum()

    st.subheader("📦 Malzeme ve Kod Listesi")
    st.dataframe(df_son, use_container_width=True)
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam:.2f} TL**")

    # Excel çıktısı indir
    with pd.ExcelWriter("malzeme_listesi.xlsx", engine="openpyxl") as writer:
        df_son.to_excel(writer, index=False)
    with open("malzeme_listesi.xlsx", "rb") as f:
        st.download_button("📄 Excel Çıktısını İndir", f.read(), file_name="malzeme_listesi.xlsx")
