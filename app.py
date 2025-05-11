import streamlit as st
import pandas as pd
from PIL import Image
import math
from io import BytesIO

# GitHub'dan Excel dosyasını oku
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun["Ürün Adı"] = df_urun["Ürün Adı"].str.strip().replace("UYARI TABELESA", "UYARI TABELASI")

fiyatlar = dict(zip(df_urun["Ürün Adı"], df_urun["Fiyat (TL)"].fillna(0)))
kodlar = dict(zip(df_urun["Ürün Adı"], df_urun["Kod"].fillna("")))

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

en = st.number_input("Tarla En (m)", min_value=0, step=1)
boy = st.number_input("Tarla Boy (m)", min_value=0, step=1)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "At", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["MISINALI", "GALVANIZ", "ŞERIT"])

tel_model_options = {
    "MISINALI": ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"],
    "GALVANIZ": ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"],
    "ŞERIT": ["ŞERIT TEL"]
}

tel_model = st.selectbox("Tel Modeli", tel_model_options.get(tel_tipi, []))

direk_tipi = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])

plastik_model = ""
if direk_tipi == "Plastik":
    plastik_model = st.selectbox("Plastik Direk Modeli", [
        "PLASTIK DIREK 100cm SIYAH",
        "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH",
        "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH",
        "PLASTIK DIREK 125cm BEYAZ"
    ])

tel_makara_uzunlugu = {
    "ŞERIT TEL": 200
}
tel_makara_uzunlugu_default = 500

# İzalatör aparat seçimi
aparatlar_dict = {
    "Ahşap": [
        "HALKA IZALATOR VIDALI SIYAH", "HALKA IZALATOR VIDALI RENKLI",
        "HALKA IZALATOR SOMUNLU RENKLI", "HALKA IZALATOR SOMUNLU UZUN"
    ],
    "İnşaat Demiri": ["MIL IZALATORU R=10-18", "MIL IZALATORU R=8-14"],
    "Köşebent": ["HALKA IZALATOR SOMUNLU RENKLI", "HALKA IZALATOR SOMUNLU UZUN", "KOSE IZALATOR"],
    "Örgü Tel": ["AĞ IZALATORU"]
}

st.subheader("🔩 İzolatörler")
secilen_aparatlar = []
toplam_tel = 2 * (en + boy) * {"Ayı": 4, "Domuz": 3, "Tilki": 4, "At": 4, "Küçükbaş": 4, "Büyükbaş": 2}.get(hayvan, 0)
izolator_sayisi_otomatik = math.ceil(toplam_tel / 5)

for aparat in aparatlar_dict.get(direk_tipi, []):
    col1, col2 = st.columns([3, 1])
    with col1:
        secim = st.radio(aparat, ["Hayır", "Evet"], horizontal=True, key=aparat)
    with col2:
        adet = st.number_input(f"{aparat} Adet", min_value=0, value=izolator_sayisi_otomatik if secim == "Evet" else 0, step=1, key=aparat+"_adet")
    if secim == "Evet" and adet > 0:
        secilen_aparatlar.append({
            "Malzeme": aparat,
            "Adet": adet,
            "Birim Fiyat": fiyatlar.get(aparat.strip(), 0),
            "Kod": kodlar.get(aparat.strip(), "")
        })

# Yardımcı ekipmanlar
st.subheader("🧰 Yardımcı Ekipmanlar")
ekipmanlar = [
    "KAPI", "TOPRAKLAMA ÇUBUĞU", "UYARI TABELASI", "ENERJI AKTARMA KABLOSU",
    "AKÜ ŞARJ ALETI", "YILDIRIM SAVAR", "TEL GERDIRICI"
]
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
 if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira

    # diğer hesaplamalar...

    df = pd.DataFrame(liste)
    df.index = range(1, len(df) + 1)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader("📦 Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam:.2f} TL**")

    # Excel çıktısı
    excel_data = BytesIO()
    df.to_excel(excel_data, index=False)
    st.download_button(
        label="📥 Excel Çıktısını İndir",
        data=excel_data.getvalue(),
        file_name="cit_malzeme_listesi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
       
