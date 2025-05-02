
import streamlit as st

st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)

hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel = st.selectbox("Tel Tipi", ["Misinalı", "Galvaniz", "Şerit"])
direk = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])

if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)
    aparat = direk_sayisi * tel_sira

    if toplam_tel <= 15000:
        urun = "Safe 2000"
    elif toplam_tel <= 30000:
        urun = "Safe 4000"
    elif toplam_tel <= 45000:
        urun = "Safe 6000"
    else:
        urun = "Safe 8000"

    st.subheader("Malzeme Listesi")
    st.write(f"Toplam Tel: {toplam_tel:.2f} m")
    st.write(f"Direk Sayısı: {direk_sayisi}")
    st.write(f"Bağlantı Aparatı: {aparat}")
    st.write(f"Ürün: {urun}")
