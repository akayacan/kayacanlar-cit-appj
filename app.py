import streamlit as st
import pandas as pd
from PIL import Image
import io
import math

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# Excel'den ürün verilerini çek
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun["\u00dcrün Adı"] = df_urun["\u00dcrün Adı"].str.strip()

# Fiyat ve Kod sözlüklerini olustur
fiyatlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Fiyat"]))
kodlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Kod"]))

# Kullanıcı girişleri
en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "At", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["Şerit", "Misinalı", "Galvaniz"])

tel_opsiyon = ""
if tel_tipi == "Şerit":
    tel_opsiyon = st.selectbox("Şerit Tel Seçimi", ["ŞERIT TEL"])
elif tel_tipi == "Misinalı":
    tel_opsiyon = st.selectbox("Misinalı Tel Seçimi", ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"])
elif tel_tipi == "Galvaniz":
    tel_opsiyon = st.selectbox("Galvaniz Tel Seçimi", ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"])

direk = st.selectbox("Direk Tipi", ["PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ", "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ", "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"])
gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])
gece_modu = st.radio("Gece Modu Eklensin mi?", ("Hayır", "Evet"))

# Yardımcı Ekipmanlar
ekipmanlar = [
    "Sıkma Aparatı", "Topraklama Çubuğu", "Yıldırım Savar", "Tel Gerdirici",
    "Uyarı Tabelası", "Enerji Aktarma Kablosu", "Akü Maşası", "Adaptör", "Akü Şarj Aleti"
]
secili_ekipmanlar = st.multiselect("Yardımcı Ekipmanlar (isteğe bağlı)", ekipmanlar)

if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "At": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)
    aparat = direk_sayisi * tel_sira

    # Enerji cihazı seçimi
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

    # Tel makara uzunlukları
    makara_uzunluk = {"Şerit": 200, "Misinalı": 500, "Galvaniz": 500}
    secilen_makara = makara_uzunluk[tel_tipi]
    makara_sayisi = math.ceil(toplam_tel / secilen_makara)

    liste = [
        {"Malzeme": tel_opsiyon, "Kod": kodlar.get(tel_opsiyon, "-"), "Adet": makara_sayisi, "Birim Fiyat": fiyatlar.get(tel_opsiyon, 0)},
        {"Malzeme": direk, "Kod": kodlar.get(direk, "-"), "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk, 0)},
        {"Malzeme": "Aparat", "Kod": kodlar.get("Aparat", "-"), "Adet": aparat, "Birim Fiyat": fiyatlar.get("Aparat", 0)},
        {"Malzeme": urun, "Kod": kodlar.get(urun, "-"), "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0)}
    ]

    if gece_modu == "Evet":
        liste.append({"Malzeme": "Gece Modülü", "Kod": kodlar.get("Gece Modülü", "-"), "Adet": 1, "Birim Fiyat": fiyatlar.get("Gece Modülü", 0)})

    for e in secili_ekipmanlar:
        liste.append({"Malzeme": e, "Kod": kodlar.get(e, "-"), "Adet": 1, "Birim Fiyat": fiyatlar.get(e, 0)})

    df = pd.DataFrame(liste)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader("📦 Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam:.2f} TL**")

    # Excel çıktısı
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    st.download_button(
        label="📥 Excel Çıktısı Al",
        data=excel_buffer.getvalue(),
        file_name="malzeme_listesi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
