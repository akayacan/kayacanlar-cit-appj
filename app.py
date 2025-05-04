import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# 🎯 Excel dosyasını GitHub'dan oku
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)

# Girişler
en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "At", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])

# Tel tipi ve kalınlığı
tel_tipi = st.selectbox("Tel Tipi", ["Misinalı", "Galvaniz", "Şerit"])
if tel_tipi == "Misinalı":
    tel_secimi = st.selectbox("Misinalı Tel Seçimi", ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"])
elif tel_tipi == "Galvaniz":
    tel_secimi = st.selectbox("Galvaniz Tel Seçimi", ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"])
elif tel_tipi == "Şerit":
    tel_secimi = st.selectbox("Şerit Tel Seçimi", ["SERIT TEL"])
else:
    tel_secimi = tel_tipi

# Direk tipi ve alt seçenekleri
direk_tipi = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])
if direk_tipi == "Plastik":
    direk_secimi = st.selectbox("Plastik Direk Seçimi", [
        "PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"
    ])
else:
    direk_secimi = direk_tipi

# Diğer seçimler
gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])
gece_modu = st.radio("Gece Modu Eklensin mi?", ("Hayır", "Evet"))

# Yardımcı ekipmanlar
ekipmanlar = [
    "Sıkma Aparatı", "Topraklama Çubuğu", "Yıldırım Savar", "Tel Gerdirici",
    "Uyarı Tabelası", "Enerji Aktarma Kablosu", "Akü Maşası", "Adaptör", "Akü Şarj Aleti"
]
secili_ekipmanlar = st.multiselect("Yardımcı Ekipmanlar (İsteğe Bağlı)", ekipmanlar)

# Hesapla butonu
if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "At": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)
    aparat = direk_sayisi * tel_sira

    # ▶ Tel uzunluğuna göre cihaz seçimi
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
    elif toplam_tel <= 75000:
        urun = "Safe 10000"
    else:
        urun = "Cihaz Belirtilmedi"

    # Ürün fiyatlarını Excel’den al
    fiyatlar = dict(zip(df_urun["Ürün Adı"], df_urun["Fiyat (TL)"]))
    kodlar = dict(zip(df_urun["Ürün Adı"], df_urun["Kod"]))

    # Liste oluştur
    liste = [
        {"Malzeme": tel_secimi, "Adet": toplam_tel, "Birim Fiyat": fiyatlar.get(tel_secimi, 0)},
        {"Malzeme": direk_secimi, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_secimi, 0)},
        {"Malzeme": "Aparat", "Adet": aparat, "Birim Fiyat": fiyatlar.get("Aparat", 0)},
        {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0)}
    ]

    if gece_modu == "Evet":
        liste.append({"Malzeme": "Gece Modülü", "Adet": 1, "Birim Fiyat": fiyatlar.get("Gece Modülü", 0)})

    for e in secili_ekipmanlar:
        liste.append({"Malzeme": e, "Adet": 1, "Birim Fiyat": fiyatlar.get(e, 0)})

    # Tabloyu oluştur
    df = pd.DataFrame(liste)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    # Çıktı göster
    st.subheader("📦 Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam:.2f} TL**")

    # Ürün kodunu göster (isteğe bağlı)
    if urun in kodlar:
        st.markdown(f"🔢 **Ürün Kodu:** `{kodlar[urun]}`")

