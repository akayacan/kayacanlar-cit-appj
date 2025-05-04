import streamlit as st
import pandas as pd
import math
from io import BytesIO

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Excel verisini GitHub'dan oku
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

tel_tipleri = {
    "Misinalı": ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"],
    "Galvaniz": ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"],
    "Şerit": ["SERIT TEL"]
}
tel = st.selectbox("Tel Tipi", list(tel_tipleri.keys()))
tel_model = st.selectbox("Tel Modeli", tel_tipleri[tel])

direk_tipleri = {
    "Plastik": [
        "PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"
    ],
    "Ahşap": ["Direk"],
    "İnşaat Demiri": ["Direk"],
    "Köşebent": ["Direk"],
    "Örgü Tel": ["Direk"]
}
direk = st.selectbox("Direk Tipi", list(direk_tipleri.keys()))
direk_model = st.selectbox("Direk Modeli", direk_tipleri[direk])

gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])
gece_modu = st.radio("Gece Modu Eklensin mi?", ["Hayır", "Evet"])

# Yardımcı ekipman radio butonları
sikma = st.radio("Sıkma Aparatı eklensin mi?", ["Hayır", "Evet"])
toprak = st.radio("Topraklama Çubuğu eklensin mi?", ["Hayır", "Evet"])
yildirim = st.radio("Yıldırım Savar eklensin mi?", ["Hayır", "Evet"])
gerdirici = st.radio("Tel Gerdirici eklensin mi?", ["Hayır", "Evet"])
uyari = st.radio("Uyarı Tabelası eklensin mi?", ["Hayır", "Evet"])
kablosu = st.radio("Enerji Aktarma Kablosu eklensin mi?", ["Hayır", "Evet"])
masasi = st.radio("Akü Maşası eklensin mi?", ["Hayır", "Evet"])
adaptor = st.radio("Adaptör eklensin mi?", ["Hayır", "Evet"])
sarj = st.radio("Akü Şarj Aleti eklensin mi?", ["Hayır", "Evet"])


# HESAPLA butonu
if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel_metre = cevre * tel_sira
    direk_sayisi = math.ceil(cevre / direk_aralik)
    aparat_sayisi = direk_sayisi * tel_sira

    # Tel makara hesaplama
    makara_uzunlugu = 200 if tel_model == "SERIT TEL" else 500
    makara_adedi = math.ceil(toplam_tel_metre / makara_uzunlugu)

    # Ürün belirleme
    if toplam_tel_metre <= 250:
        urun = "ECO 500"
    elif toplam_tel_metre <= 1000:
        urun = "ECO 1000"
    elif toplam_tel_metre <= 15000:
        urun = "Safe 2000"
    elif toplam_tel_metre <= 30000:
        urun = "Safe 4000"
    elif toplam_tel_metre <= 45000:
        urun = "Safe 6000"
    elif toplam_tel_metre <= 60000:
        urun = "Safe 8000"
    else:
        urun = "Safe 10000"

    # Malzeme listesi
    liste = [
        {"Malzeme": tel_model, "Adet": makara_adedi, "Birim Fiyat": fiyatlar.get(tel_model, 0), "Kod": kodlar.get(tel_model, "")},
        {"Malzeme": direk_model, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_model, 0), "Kod": kodlar.get(direk_model, "")},
        if sikma == "Evet":
            liste.append({"Malzeme": "Sıkma Aparatı", "Adet": 1, "Birim Fiyat": fiyatlar.get("Sıkma Aparatı", 0), "Kod": kodlar.get("Sıkma Aparatı", "")})
        if toprak == "Evet":
            liste.append({"Malzeme": "Topraklama Çubuğu", "Adet": 1, "Birim Fiyat": fiyatlar.get("Topraklama Çubuğu", 0), "Kod": kodlar.get("Topraklama Çubuğu", "")})
        if yildirim == "Evet":
            liste.append({"Malzeme": "Yıldırım Savar", "Adet": 1, "Birim Fiyat": fiyatlar.get("Yıldırım Savar", 0), "Kod": kodlar.get("Yıldırım Savar", "")})
        if gerdirici == "Evet":
            liste.append({"Malzeme": "Tel Gerdirici", "Adet": 1, "Birim Fiyat": fiyatlar.get("Tel Gerdirici", 0), "Kod": kodlar.get("Tel Gerdirici", "")})
        if uyari == "Evet":
            liste.append({"Malzeme": "Uyarı Tabelası", "Adet": 1, "Birim Fiyat": fiyatlar.get("Uyarı Tabelası", 0), "Kod": kodlar.get("Uyarı Tabelası", "")})
        if kablosu == "Evet":
            liste.append({"Malzeme": "Enerji Aktarma Kablosu", "Adet": 1, "Birim Fiyat": fiyatlar.get("Enerji Aktarma Kablosu", 0), "Kod": kodlar.get("Enerji Aktarma Kablosu", "")})
        if masasi == "Evet":
            liste.append({"Malzeme": "Akü Maşası", "Adet": 1, "Birim Fiyat": fiyatlar.get("Akü Maşası", 0), "Kod": kodlar.get("Akü Maşası", "")})
        if adaptor == "Evet":
            liste.append({"Malzeme": "Adaptör", "Adet": 1, "Birim Fiyat": fiyatlar.get("Adaptör", 0), "Kod": kodlar.get("Adaptör", "")})
        if sarj == "Evet":
            liste.append({"Malzeme": "Akü Şarj Aleti", "Adet": 1, "Birim Fiyat": fiyatlar.get("Akü Şarj Aleti", 0), "Kod": kodlar.get("Akü Şarj Aleti", "")})

        {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0), "Kod": kodlar.get(urun, "")}
    ]

    if gece_modu == "Evet":
        liste.append({"Malzeme": "Gece Modülü", "Adet": 1, "Birim Fiyat": fiyatlar.get("Gece Modülü", 0), "Kod": kodlar.get("Gece Modülü", "")})

    for e in secili_ekipmanlar:
        liste.append({"Malzeme": e, "Adet": 1, "Birim Fiyat": fiyatlar.get(e, 0), "Kod": kodlar.get(e, "")})

    df = pd.DataFrame(liste)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader("📦 Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam:.2f} TL**")

    # Excel çıktısı
    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button("📥 Excel Çıktısı Al", data=output.getvalue(), file_name="cit_malzeme_listesi.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
