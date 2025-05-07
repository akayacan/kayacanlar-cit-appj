import streamlit as st
import pandas as pd
import math
import io
from PIL import Image

# GitHub'dan Excel dosyasını oku
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)

# Fiyat ve kod sözlüklerini oluştur
fiyatlar = dict(zip(df_urun["Ürün Adı"], df_urun["Fiyat (TL)"]))
kodlar = dict(zip(df_urun["Ürün Adı"], df_urun["Kod"]))

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Girişler
en = st.number_input("Tarla En (m)", min_value=0, step=1, format="%d")
boy = st.number_input("Tarla Boy (m)", min_value=0, step=1, format="%d")
hayvan = st.selectbox("Hayvan Türü", ["", "Ayı", "Domuz", "Tilki", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["", "Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["", "MISINALI", "GALVANIZ", "ŞERIT"])

tel_model = ""
if tel_tipi == "MISINALI":
    tel_model = st.selectbox("Misinalı Tel Seçimi", ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"])
elif tel_tipi == "GALVANIZ":
    tel_model = st.selectbox("Galvaniz Tel Seçimi", ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"])
elif tel_tipi == "ŞERIT":
    tel_model = "ŞERIT TEL"

direk_tipi = st.selectbox("Direk Tipi", ["", "Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])

direk_model = ""
if direk_tipi == "Plastik":
    direk_model = st.selectbox("Plastik Direk Modeli", [
        "PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"
    ])
else:
    direk_model = direk_tipi  # Ahşap, İnşaat Demiri, vb. tek modeli var gibi düşünülür

# Hesaplama
if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2}.get(hayvan, 0)
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}.get(arazi, 1)
    toplam_tel = cevre * tel_sira

    if tel_model == "ŞERIT TEL":
        makara_uzunluk = 200
    else:
        makara_uzunluk = 500

    makara_adedi = math.ceil(toplam_tel / makara_uzunluk)
    direk_sayisi = round(cevre / direk_aralik)
    aparat = direk_sayisi * tel_sira

    # Ürün seçimi (tel uzunluğuna göre)
    urun = ""
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

    liste = [
        {"Malzeme": tel_model, "Adet": makara_adedi, "Birim Fiyat": fiyatlar.get(tel_model, 0), "Kod": kodlar.get(tel_model,"")},
        {"Malzeme": direk_model, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_model, 0), "Kod": kodlar.get(direk_model,"")},
        {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0), "Kod": kodlar.get(urun, "")}
    ]

    # Malzeme listesini dataframe'e dönüştür
    df = pd.DataFrame(liste)
    df.index += 1  # 1'den başlasın
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader(":package: Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### :moneybag: Toplam Maliyet: **{toplam:.2f} TL**")

    # Excel indir
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    st.download_button(
        label="Excel Çıktısı Al",
        data=excel_buffer.getvalue(),
        file_name="malzeme_listesi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
