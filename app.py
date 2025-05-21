import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import math

# Excel dosyasını GitHub'dan oku
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun["Ürün Adı"] = df_urun["\u00dcrün Adı"].str.strip()

fiyatlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Fiyat (TL)"].fillna(0)))
kodlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Kod"].fillna("")))

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Kullanıcı Girişleri
en = st.number_input("Tarla En (m)", min_value=0, step=1)
boy = st.number_input("Tarla Boy (m)", min_value=0, step=1)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "Küçükbaş", "Büyükbaş", "At"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["MISINALI", "GALVANIZ", "ŞERIT"])

# Tel model seçimi
tel_model_options = {
    "MISINALI": ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"],
    "GALVANIZ": ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"],
    "ŞERIT": ["ŞERIT TEL"]
}
tel_model = st.selectbox("Tel Modeli", tel_model_options.get(tel_tipi, []))

# Direk tipi ve plastik modelleri
direk_tipi = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])
plastik_model = ""
if direk_tipi == "Plastik":
    plastik_model = st.selectbox("Plastik Direk Modeli", [
        "PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"
    ])

# Güneş Paneli
st.subheader("🔋 Güneş Paneli Seçimi")
gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Hayır", "Evet"], horizontal=True)
gunes_model = ""
if gunes_paneli == "Evet":
    gunes_model = st.selectbox("Panel Modeli", ["GUNES PANELI 12W", "GUNES PANELI 25W"])

# Yardımcı ekipmanlar
st.subheader("🧰 Yardımcı Ekipmanlar")
ekipmanlar = ["TOPRAKLAMA ÇUBUĞU", "TEL GERDIRICI", "YILDIRIM SAVAR", "UYARI TABELASI", "ENERJI AKTARMA KABLOSU", "AKU ŞARJ ALETI"]
secilen_ekipmanlar = []
for ekipman in ekipmanlar:
    col1, col2 = st.columns([3, 1])
    with col1:
        secim = st.radio(ekipman, ["Hayır", "Evet"], horizontal=True, key=ekipman)
    with col2:
        adet = st.number_input(f"{ekipman} Adet", min_value=0, step=1, key=ekipman+"_adet")
    if secim == "Evet" and adet > 0:
        secilen_ekipmanlar.append({
            "Malzeme": ekipman,
            "Adet": adet,
            "Birim Fiyat": fiyatlar.get(ekipman.strip(), 0),
            "Kod": kodlar.get(ekipman.strip(), "")
        })

# Kapı seti
st.subheader("🔒 Kapı Seti")
kapiset_secim = st.radio("Kapı Seti Kullanılsın mı?", ["Hayır", "Evet"], horizontal=True)
kapiset_adet = 0
if kapiset_secim == "Evet":
    kapiset_adet = st.number_input("Kapı Seti Adedi", min_value=1, step=1, key="kapiset")

if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2, "At": 4}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)

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

    tel_makara_uzunlugu = {"ŞERIT TEL": 200}.get(tel_model.strip(), 500)
    makara_adedi = -(-toplam_tel // tel_makara_uzunlugu)
    direk_model = plastik_model if direk_tipi == "Plastik" else f"{direk_tipi.upper()} DIREK"

    liste = [
        {"Malzeme": tel_model, "Adet": makara_adedi, "Birim Fiyat": fiyatlar.get(tel_model.strip(), 0), "Kod": kodlar.get(tel_model.strip(), "")},
        {"Malzeme": direk_model, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_model.strip(), 0), "Kod": kodlar.get(direk_model.strip(), "")},
        {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun.strip(), 0), "Kod": kodlar.get(urun.strip(), "")}
    ]

    # Güneş paneli ekle
    if gunes_paneli == "Evet" and gunes_model:
        liste.append({"Malzeme": gunes_model, "Adet": 1, "Birim Fiyat": fiyatlar.get(gunes_model.strip(), 0), "Kod": kodlar.get(gunes_model.strip(), "")})

    # Yardımcı ekipmanlar
    for e in secilen_ekipmanlar:
        liste.append(e)

    # Kapı seti hesapla
    if kapiset_secim == "Evet" and kapiset_adet > 0:
        liste.append({"Malzeme": "C6-A", "Adet": kapiset_adet, "Birim Fiyat": 0, "Kod": "C6-A"})
        liste.append({"Malzeme": "C6-B", "Adet": kapiset_adet * 2, "Birim Fiyat": 0, "Kod": "C6-B"})
        liste.append({"Malzeme": "C6-C", "Adet": kapiset_adet, "Birim Fiyat": 0, "Kod": "C6-C"})
        liste.append({"Malzeme": "KAPI SETİ", "Adet": kapiset_adet, "Birim Fiyat": 128.3, "Kod": "SET"})

    df = pd.DataFrame(liste)
    df.index = range(1, len(df) + 1)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader("📆 Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam:.2f} TL**")

    excel_data = BytesIO()
    df.to_excel(excel_data, index=False)
    st.download_button(
        label="📅 Excel Çıktısını İndir",
        data=excel_data.getvalue(),
        file_name="cit_malzeme_listesi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
