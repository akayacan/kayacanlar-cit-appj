
import streamlit as st

st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Girişler
en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel = st.selectbox("Tel Tipi", ["Misinalı", "Galvaniz", "Şerit"])
direk = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])
gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])

# Fiyatlar
fiyatlar = {
    "tel_m": 5.0,
    "direk": 30.0,
    "aparat": 2.5,
    "Safe 2000": 1000,
    "Safe 4000": 1500,
    "Safe 6000": 2000,
    "Safe 8000": 2500,
    "KOMPACT 200": 2200,
    "KOMPACT 400": 2800,
    "KOMPACT 600": 3500
}

# Hesapla
if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)
    aparat = direk_sayisi * tel_sira

    # Ürün seçimi
    urun = ""
    if gunes_paneli == "Evet":
        if toplam_tel <= 15000:
            urun = "KOMPACT 200"
        elif toplam_tel <= 30000:
            urun = "KOMPACT 400"
        elif toplam_tel <= 45000:
            urun = "KOMPACT 600"
        else:
            urun = "Safe 8000"
    else:
        if toplam_tel <= 15000:
            urun = "Safe 2000"
        elif toplam_tel <= 30000:
            urun = "Safe 4000"
        elif toplam_tel <= 45000:
            urun = "Safe 6000"
        else:
            urun = "Safe 8000"

    # Fiyatlandır
    toplam_fiyat = (
        toplam_tel * fiyatlar["tel_m"] +
        direk_sayisi * fiyatlar["direk"] +
        aparat * fiyatlar["aparat"] +
        fiyatlar.get(urun, 0)
    )

    # Sonuçlar
    st.subheader("Malzeme Listesi ve Fiyatlandırma")
    st.write(f"Toplam Tel: {toplam_tel:.2f} m  →  {toplam_tel*fiyatlar['tel_m']:.2f} TL")
    st.write(f"Direk Sayısı: {direk_sayisi}     →  {direk_sayisi*fiyatlar['direk']:.2f} TL")
    st.write(f"Bağlantı Aparatı: {aparat}       →  {aparat*fiyatlar['aparat']:.2f} TL")
    st.write(f"Ürün: {urun}                     →  {fiyatlar.get(urun, 0):.2f} TL")
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam_fiyat:.2f} TL**")
