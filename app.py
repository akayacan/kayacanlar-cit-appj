import streamlit as st
import pandas as pd
import math
import io

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# 📥 Excel dosyasını GitHub'dan oku
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun["Ürün Adı"] = df_urun["Ürün Adı"].str.strip()

# Sözlüklere dönüştür
fiyatlar = dict(zip(df_urun["Ürün Adı"], df_urun["Fiyat (TL)"]))
kodlar = dict(zip(df_urun["Ürün Adı"], df_urun["Kod"]))

# Kullanıcı girdileri
en = st.number_input("Tarla En (m)", min_value=0, step=1, format="%d")
boy = st.number_input("Tarla Boy (m)", min_value=0, step=1, format="%d")
hayvan = st.selectbox("Hayvan Türü", ["", "Ayı", "Domuz", "Tilki", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["", "Düz", "Otluk", "Eğimli"])
tel_model = st.selectbox("Tel Tipi", ["", "MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm", "GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm", "ŞERIT TEL"])
direk = st.selectbox("Direk Tipi", ["", "Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])

# Plastik direk modeli seçimi
direk_model = direk  # varsayılan
direk_label = direk
if direk == "Plastik":
    plastik_modeller = ["100 cm Siyah", "100 cm Beyaz", "105 cm Siyah", "105 cm Beyaz", "125 cm Siyah", "125 cm Beyaz"]
    secilen_plastik = st.selectbox("Plastik Direk Modeli", plastik_modeller)
    direk_model = f"PLASTIK DIREK {secilen_plastik.upper()}"
    direk_label = "Plastik"

st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])
gece_modu = st.radio("Gece Modu Eklensin mi?", ["Hayır", "Evet"])

# Aparatlar - Direk Tipine Göre
st.subheader("Aparatlar")
aparat_secimleri = []

if direk_label == "Ahşap":
    aparat_secimleri = [
        ("Vida İzolatörü", "C1-E"),
        ("Vida İzolatörü Renkli", "C1-A1"),
        ("İzolatör Civata Somun", "C1-A2"),
        ("İzolatör Uzun Vida", "C1-D")
    ]
elif direk_label == "İnşaat Demiri":
    aparat_secimleri = [
        ("Mil İzolatörü R=10-18", "C4"),
        ("Mil İzolatörü R=8-14", "C4A")
    ]
elif direk_label == "Köşebent":
    aparat_secimleri = [
        ("İzolatör Civata Somun", "C1-A2"),
        ("İzolatör Uzun Vida", "C1-D"),
        ("Köşe İzolatörü", "C16")
    ]
elif direk_label == "Örgü Tel":
    aparat_secimleri = [("Ağ İzolatörü", "C10")]

secilen_aparatlar = []
for isim, kod in aparat_secimleri:
    col1, col2 = st.columns([2, 1])
    with col1:
        secim = st.radio(f"{isim} kullanılsın mı?", ["Hayır", "Evet"], horizontal=True, key=isim)
    if secim == "Evet":
        with col2:
            adet = st.number_input(f"{isim} Adet", min_value=1, step=1, key=f"adet_{isim}")
            secilen_aparatlar.append((isim, adet))

# Ek Ekipmanlar
st.subheader("Ekipmanlar")
ekipman_listesi = [
    "KAPI", "TOPRAKLAMA", "UYARI LEVHA", "ENERJI AKTARMA KABLO",
    "AKÜ ŞARJ", "YILDIRIMSAVAR", "TEL GERDIRME"
]
ekipmanlar = []
for ekipman in ekipman_listesi:
    col1, col2 = st.columns([2, 1])
    with col1:
        sec = st.radio(f"{ekipman} eklensin mi?", ["Hayır", "Evet"], horizontal=True, key=f"sec_{ekipman}")
    if sec == "Evet":
        with col2:
            adet = st.number_input(f"{ekipman} Adet", min_value=1, step=1, key=f"adet_{ekipman}")
            ekipmanlar.append((ekipman, adet))

if st.button("HESAPLA"):
    if en > 0 and boy > 0 and hayvan and arazi and tel_model:
        cevre = 2 * (en + boy)
        tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
        direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
        toplam_tel = cevre * tel_sira
        direk_sayisi = round(cevre / direk_aralik)

        makara_uzunluk = 200 if "ŞERIT" in tel_model.upper() else 500
        makara_adedi = math.ceil(toplam_tel / makara_uzunluk)

        liste = [
            {"Malzeme": tel_model, "Adet": makara_adedi, "Birim Fiyat": fiyatlar.get(tel_model, 0), "Kod": kodlar.get(tel_model,"")},
            {"Malzeme": direk_model, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_model, 0), "Kod": kodlar.get(direk_model, "")}
        ]

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

        liste.append({"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0), "Kod": kodlar.get(urun, "")})

        for isim, adet in secilen_aparatlar + ekipmanlar:
            liste.append({"Malzeme": isim, "Adet": adet, "Birim Fiyat": fiyatlar.get(isim, 0), "Kod": kodlar.get(isim, "")})

        df = pd.DataFrame(liste)
        df.index += 1  # index 1'den başlasın
        df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
        toplam = df["Toplam"].sum()

        st.subheader("📦 Malzeme ve Fiyat Listesi")
        st.dataframe(df, use_container_width=True)
        st.markdown(f"### 💰 Toplam Maliyet: **{toplam:.2f} TL**")

        excel_data = io.BytesIO()
        df.to_excel(excel_data, index=True)
        st.download_button(
            label="📥 Excel Çıktısını İndir",
            data=excel_data.getvalue(),
            file_name="malzeme_listesi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Lütfen tüm alanları doldurun.")
