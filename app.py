
import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Girişler
en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel = st.selectbox("Tel Tipi", ["Misinalı", "Galvaniz", "Şerit"])
direk = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])
gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])
gece_modu = st.radio("Gece Modu Eklensin mi?", ("Hayır", "Evet"))


ekipmanlar = [
    "Sıkma Aparatı", "Topraklama Çubuğu", "Yıldırım Savar", "Tel Gerdirici",
    "Uyarı Tabelası", "Enerji Aktarma Kablosu", "Akü Maşası", "Adaptör", "Akü Şarj Aleti"
]
secili_ekipmanlar = st.multiselect("Yardımcı Ekipmanlar (İsteğe Bağlı)", ekipmanlar)

fiyatlar = {
    "Tel (m)": 5.0, "Direk": 30.0, "Aparat": 2.5,
    "Safe 2000": 1000, "Safe 4000": 1500, "Safe 6000": 2000, "Safe 8000": 2500,
    "KOMPACT 200": 2200, "KOMPACT 400": 2800, "KOMPACT 600": 3500,
    "Sıkma Aparatı": 250, "Topraklama Çubuğu": 150, "Yıldırım Savar": 500,
    "Tel Gerdirici": 200, "Uyarı Tabelası": 50, "Enerji Aktarma Kablosu": 100,
    "Akü Maşası": 80, "Adaptör": 300, "Akü Şarj Aleti": 600,
}

gorseller = {
    "Safe": "safe2000.jpg", "KOMPACT": "kompack200.jpg",
    "Misinalı": "misina.jpg", "Galvaniz": "galvaniz.jpg", "Şerit": "şerit_tel.jpg"
}

if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)
    aparat = direk_sayisi * tel_sira

    if gunes_paneli == "Evet":
        if toplam_tel <= 15000: urun = "KOMPACT 200"
        elif toplam_tel <= 30000: urun = "KOMPACT 400"
        elif toplam_tel <= 45000: urun = "KOMPACT 600"
        else: urun = "Safe 8000"
    else:
        if toplam_tel <= 15000: urun = "Safe 2000"
        elif toplam_tel <= 30000: urun = "Safe 4000"
        elif toplam_tel <= 45000: urun = "Safe 6000"
        else: urun = "Safe 8000"

    liste = [
    {"Malzeme": "Tel (m)", "Adet": toplam_tel, "Birim Fiyat": fiyatlar["Tel (m)"]},
    {"Malzeme": "Direk", "Adet": direk_sayisi, "Birim Fiyat": fiyatlar["Direk"]},
    {"Malzeme": "Aparat", "Adet": aparat, "Birim Fiyat": fiyatlar["Aparat"]},
    {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar[urun]}
    ]

    # gece modu kontrolü artık listenin DIŞINDA
    if gece_modu == "Evet":
        liste.append({"Malzeme": "Gece Modülü", "Adet": 1, "Birim Fiyat": 1500})

    for e in secili_ekipmanlar:
        liste.append({"Malzeme": e, "Adet": 1, "Birim Fiyat": fiyatlar[e]})


    df = pd.DataFrame(liste)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader("📦 Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam:.2f} TL**")

    st.subheader("📷 Seçilen Ürün Görseli")
    if gunes_paneli == "Evet":
        dosya = "kompack200.jpg"
    else:
        dosya = "safe2000.jpg"

    try:
        image = Image.open(f"images/{dosya}")
        st.image(image, caption=urun, width=300)
    except:
        st.warning("Görsel bulunamadı.")

