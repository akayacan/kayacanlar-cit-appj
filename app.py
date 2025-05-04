import streamlit as st
import pandas as pd
import math
import io

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Excel'den fiyat ve kod bilgilerini al
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun["Ürün Adı"] = df_urun["Ürün Adı"].str.strip()

fiyatlar = dict(zip(df_urun["Ürün Adı"], df_urun["Fiyat (TL)"]))
kodlar = dict(zip(df_urun["Ürün Adı"], df_urun["Kod"]))

# Girişler
en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["Misinalı", "Galvaniz", "Şerit"])

# Tel modeli seçimleri
tel_model = ""
if tel_tipi == "Misinalı":
    tel_model = st.selectbox("Misinalı Tel Modeli", ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"])
elif tel_tipi == "Galvaniz":
    tel_model = st.selectbox("Galvaniz Tel Modeli", ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"])
else:
    tel_model = "ŞERIT TEL"

direk_model = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])
if direk_model == "Plastik":
    direk_model = st.selectbox("Plastik Direk Modeli", [
        "PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"])

gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])
gece_modu = st.radio("Gece Modu Eklensin mi?", ["Hayır", "Evet"])

# Aparat seçimi
st.subheader("🔧 Aparat Seçimi")
aparat_bilgileri = df_urun.iloc[19:32]  # A20-A32 dahil
aparatlar = []

for _, row in aparat_bilgileri.iterrows():
    ad = row["Ürün Adı"]
    kod = row["Kod"]
    fiyat = row["Fiyat (TL)"]

    col1, col2 = st.columns([2, 1])
    with col1:
        secim = st.radio(f"{ad} eklensin mi?", ["Hayır", "Evet"], key=f"secim_{ad}")
    if secim == "Evet":
        with col2:
            adet = st.number_input(f"{ad} adedi", min_value=1, step=1, key=f"adet_{ad}")
        aparatlar.append({
            "Malzeme": ad,
            "Adet": adet,
            "Birim Fiyat": fiyat,
            "Kod": kod
        })

if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)
    aparat_adet = direk_sayisi * tel_sira

    # Makara hesabı
    if "ŞERIT" in tel_model.upper():
        makara_uzunlugu = 200
    else:
        makara_uzunlugu = 500
    makara_adedi = math.ceil(toplam_tel / makara_uzunlugu)

    # Enerji ünitesi seçimi
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
        {"Malzeme": "Aparat", "Adet": aparat_adet, "Birim Fiyat": fiyatlar.get("Aparat", 0), "Kod": kodlar.get("Aparat", "")},
        {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0), "Kod": kodlar.get(urun, "")},
    ]

    if gece_modu == "Evet":
        liste.append({"Malzeme": "Gece Modülü", "Adet": 1, "Birim Fiyat": fiyatlar.get("Gece Modülü", 0), "Kod": kodlar.get("Gece Modülü", "")})

    for a in aparatlar:
        liste.append(a)

    df = pd.DataFrame(liste)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader("📦 Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam:,.2f} TL**")

    excel_io = io.BytesIO()
    df.to_excel(excel_io, index=False)
    excel_io.seek(0)
    st.download_button(
    label="📥 Excel İndir",
    data=excel_io,
    file_name="cit_malzeme_listesi.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

