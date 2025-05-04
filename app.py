import streamlit as st
import pandas as pd
import math
import requests

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Excel verisini GitHub'dan al
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun["\u00dcrün Adı"] = df_urun["\u00dcrün Adı"].str.strip()

fiyatlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Fiyat (TL)"]))
kodlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Kod"]))

# Girişler
en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["Misinalı", "Galvaniz", "Şerit"])

tel_model = None
if tel_tipi == "Misinalı":
    tel_model = st.selectbox("Misinalı Tel Modeli", ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"])
elif tel_tipi == "Galvaniz":
    tel_model = st.selectbox("Galvaniz Tel Modeli", ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"])
elif tel_tipi == "Şerit":
    tel_model = "SERIT TEL"

direk_tipi = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])
direk_model = direk_tipi
if direk_tipi == "Plastik":
    direk_model = st.selectbox("Plastik Direk Modeli", [
        "PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"
    ])

gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])
gece_modu = st.radio("Gece Modu Eklensin mi?", ("Hayır", "Evet"))

# Aparatlar Bloğu
st.markdown("### 🪧 Yardımcı Aparatlar")
aparatlar = [
    "Sıkma Aparatı", "Topraklama Çubuğu", "Yıldırım Savar", "Tel Gerdirici",
    "Uyarı Tabelası", "Enerji Aktarma Kablosu", "Akü Maşası", "Adaptör", "Akü Şarj Aleti"
]

aparat_secimleri = {}
for aparat in aparatlar:
    col1, col2 = st.columns([2, 1])
    with col1:
        secim = st.radio(aparat, ["Hayır", "Evet"], key=aparat)
    with col2:
        adet = st.number_input("Adet", min_value=1, step=1, value=1, key=aparat+"_adet") if secim == "Evet" else 0
    aparat_secimleri[aparat] = adet

# Hesaplama
if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = math.ceil(cevre / direk_aralik)
    aparat_adedi = direk_sayisi * tel_sira

    # Makara hesabı
    if tel_model == "SERIT TEL":
        makara_uzunluk = 200
    else:
        makara_uzunluk = 500
    makara_adedi = math.ceil(toplam_tel / makara_uzunluk)

    # Enerji cihazı belirleme
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
        {"Malzeme": tel_model, "Adet": makara_adedi, "Birim Fiyat": fiyatlar.get(tel_model, 0), "Kod": kodlar.get(tel_model, "")},
        {"Malzeme": direk_model, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_model, 0), "Kod": kodlar.get(direk_model, "")},
        {"Malzeme": "Aparat", "Adet": aparat_adedi, "Birim Fiyat": fiyatlar.get("Aparat", 0), "Kod": kodlar.get("Aparat", "")},
        {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0), "Kod": kodlar.get(urun, "")}
    ]

    if gece_modu == "Evet":
        liste.append({"Malzeme": "Gece Modülü", "Adet": 1, "Birim Fiyat": fiyatlar.get("Gece Modülü", 0), "Kod": kodlar.get("Gece Modülü", "")})

    for aparat, adet in aparat_secimleri.items():
        if adet > 0:
            liste.append({"Malzeme": aparat, "Adet": adet, "Birim Fiyat": fiyatlar.get(aparat, 0), "Kod": kodlar.get(aparat, "")})

    df = pd.DataFrame(liste)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader(":package: Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### :money_with_wings: Toplam Maliyet: **{toplam:.2f} TL**")

    data = df.to_csv(index=False).encode("utf-8")
    st.download_button("CSV Çıktısını İndir", data, "cit_malzeme_listesi.csv", "text/csv")
