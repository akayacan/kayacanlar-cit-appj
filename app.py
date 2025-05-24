import streamlit as st
import pandas as pd
import math
from io import BytesIO

# Excel'den verileri al
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun.columns = df_urun.columns.str.strip()  # başlıklar temizlensin
df_urun["Ürün Adı"] = df_urun["Ürün Adı"].astype(str).str.strip()

fiyatlar = dict(zip(df_urun["Ürün Adı"], df_urun["Fiyat (TL)"]))
kodlar = dict(zip(df_urun["Ürün Adı"], df_urun["Kod"]))

st.set_page_config(layout="wide")
st.title("🐑 Kayacanlar - Çit Malzeme Hesaplama Programı")

# Tarla bilgileri
en = st.number_input("Tarla En (m)", min_value=0, step=1)
boy = st.number_input("Tarla Boy (m)", min_value=0, step=1)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "Küçükbaş", "Büyükbaş", "At"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])

# Tel seçimi
tel_tipi = st.selectbox("Tel Tipi", ["MISINALI", "GALVANIZ", "SERIT"])
tel_model_options = {
    "MISINALI": ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"],
    "GALVANIZ": ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"],
    "SERIT": ["SERIT TEL"]
}
tel_model = st.selectbox("Tel Modeli", tel_model_options.get(tel_tipi, []))

# Direk seçimi
direk_tipi = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])
plastik_model = ""
if direk_tipi == "Plastik":
    plastik_model = st.selectbox("Plastik Direk Modeli", [
        "PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"
    ])

# Güneş paneli
st.subheader("🌞 Güneş Paneli")
gunes_paneli = st.radio("Güneş paneli kullanılsın mı?", ["Hayır", "Evet"], horizontal=True)
gunes_panel_secimi = ""
if gunes_paneli == "Evet":
    gunes_panel_secimi = st.selectbox("Güneş Paneli Seç", ["GUNES PANELI 12W", "GUNES PANELI 25W"])

# İzolatör sayısı otomatik hesapla
izolator_sayisi_otomatik = 0 if en == 0 or boy == 0 else math.ceil((en + boy) * 2 * {
    "Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2, "At": 4
}[hayvan] / 5)

# İzolatör Seçimi
st.subheader("🔧 İzolatörler")
aparatlar_dict = {
    "Ahşap": [
        "HALKA IZALATOR VIDALI SIYAH", "HALKA IZALATOR VIDALI RENKLI",
        "HALKA IZALATOR SOMUNLU RENKLI", "HALKA IZALATOR SOMUNLU UZUN"
    ],
    "İnşaat Demiri": ["MIL IZALATORU R=10-18", "MIL IZALATORU R=8-14"],
    "Köşebent": ["HALKA IZALATOR SOMUNLU RENKLI", "HALKA IZALATOR SOMUNLU UZUN", "KOSE IZALATOR"],
    "Örgü Tel": ["AĞ IZALATORU"]
}
secilen_aparatlar = []
for aparat in aparatlar_dict.get(direk_tipi, []):
    col1, col2 = st.columns([3, 1])
    secim = col1.radio(aparat, ["Hayır", "Evet"], key=aparat)
    if secim == "Evet":
        adet = col2.number_input(f"{aparat} Adet", min_value=1, step=1, value=izolator_sayisi_otomatik, key=aparat + "_adet")
        secilen_aparatlar.append({
            "Malzeme": aparat,
            "Adet": adet,
            "Birim Fiyat": fiyatlar.get(aparat, 0),
            "Kod": kodlar.get(aparat, "")
        })

# Yardımcı Ekipmanlar
st.subheader("🧰 Yardımcı Ekipmanlar")
ekipmanlar = [
    "TOPRAKLAMA ÇUBUĞU", "TEL GERDIRICI", "YILDIRIM SAVAR",
    "UYARI TABELASI", "ENERJI AKTARMA KABLOSU", "AKU MAŞASI",
    "12V 2A ADAPTOR", "AKU ŞARJ ALETI"
]
secilen_ekipmanlar = []
for ekipman in ekipmanlar:
    col1, col2 = st.columns([3, 1])
    secim = col1.radio(ekipman, ["Hayır", "Evet"], key=ekipman)
    if secim == "Evet":
        adet = col2.number_input(f"{ekipman} Adet", min_value=1, step=1, key=ekipman + "_adet")
        secilen_ekipmanlar.append({
            "Malzeme": ekipman,
            "Adet": adet,
            "Birim Fiyat": fiyatlar.get(ekipman, 0),
            "Kod": kodlar.get(ekipman, "")
        })

# Kapı Seti
st.subheader("🚪 Kapı Seti")
kapiseti = st.radio("Kapı seti kullanılsın mı?", ["Hayır", "Evet"], horizontal=True)
kapiseti_adet = 0
if kapiseti == "Evet":
    kapiseti_adet = st.number_input("Kapı Seti Adedi", min_value=1, step=1)
    # Her setin içinde C6-A (1x), C6-B (2x), C6-C (1x) olacak
    for urun, carpan in [("C6-A", 1), ("C6-B", 2), ("C6-C", 1)]:
        secilen_ekipmanlar.append({
            "Malzeme": f"{urun} (Kapı Seti)", 
            "Adet": kapiseti_adet * carpan,
            "Birim Fiyat": 0,
            "Kod": urun
        })
    secilen_ekipmanlar.append({
        "Malzeme": "Kapı Seti", "Adet": kapiseti_adet,
        "Birim Fiyat": 128.3, "Kod": "SET-KAPI"
    })

# Hesapla Butonu
if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2, "At": 4}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)

    tel_makara_uzunlugu = {"SERIT TEL": 200}
    makara_adedi = math.ceil(toplam_tel / tel_makara_uzunlugu.get(tel_model, 500))
    direk_model = plastik_model if direk_tipi == "Plastik" else f"{direk_tipi.upper()} DIREK"

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

    malzeme_listesi = [
        {"Malzeme": tel_model, "Adet": makara_adedi, "Birim Fiyat": fiyatlar.get(tel_model, 0), "Kod": kodlar.get(tel_model, "")},
        {"Malzeme": direk_model, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_model, 0), "Kod": kodlar.get(direk_model, "")},
        {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0), "Kod": kodlar.get(urun, "")},
    ]

    if gunes_panel_secimi:
        malzeme_listesi.append({
            "Malzeme": gunes_panel_secimi, "Adet": 1,
            "Birim Fiyat": fiyatlar.get(gunes_panel_secimi, 0),
            "Kod": kodlar.get(gunes_panel_secimi, "")
        })

    for item in secilen_aparatlar + secilen_ekipmanlar:
        malzeme_listesi.append(item)

    df = pd.DataFrame(malzeme_listesi)
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
