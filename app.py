import streamlit as st
import pandas as pd
import math
from io import BytesIO

# Excel verisini oku
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun.columns = df_urun.columns.str.strip()
df_urun["Ürün Adı"] = df_urun["Ürün Adı"].str.strip()

fiyatlar = dict(zip(df_urun["Ürün Adı"], df_urun["Fiyat (TL)"].fillna(0)))
kodlar = dict(zip(df_urun["Ürün Adı"], df_urun["Kod"].fillna("")))

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

en = st.number_input("Tarla En (m)", min_value=0, step=1)
boy = st.number_input("Tarla Boy (m)", min_value=0, step=1)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "Küçükbaş", "Büyükbaş", "At"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["MISINALI", "GALVANIZ", "ŞERIT"])

tel_model_options = {
    "MISINALI": ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"],
    "GALVANIZ": ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"],
    "ŞERIT": ["SERIT TEL"]
}
tel_model = st.selectbox("Tel Modeli", tel_model_options.get(tel_tipi, []))

direk_tipi = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])
plastik_model = ""
if direk_tipi == "Plastik":
    plastik_model = st.selectbox("Plastik Direk Modeli", [
        "PLASTIK DIREK 100cm SIYAH", "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH", "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH", "PLASTIK DIREK 125cm BEYAZ"
    ])

# Güneş Paneli
st.subheader("🌞 Güneş Paneli")
gunes_paneli = st.radio("Güneş paneli kullanılsın mı?", ["Hayır", "Evet"], horizontal=True)
gunes_panel_secimi = ""
if gunes_paneli == "Evet":
    gunes_panel_secimi = st.selectbox("Güneş Paneli Seç", ["GUNES PANELI 12W", "GUNES PANELI 25W"])

# Hesaplama yapılabiliyorsa devam et
if st.button("HESAPLA") and en > 0 and boy > 0:
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "Küçükbaş": 4, "Büyükbaş": 2, "At": 4}[hayvan]
    toplam_tel = cevre * tel_sira
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    direk_sayisi = round(cevre / direk_aralik)
    aparat = direk_sayisi * tel_sira

    # Tel makara uzunluğu
    makara_uzunluk = 200 if "SERIT" in tel_model else 500
    makara_adedi = math.ceil(toplam_tel / makara_uzunluk)

    # Enerji Ünitesi Seçimi
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

    direk_model = plastik_model if direk_tipi == "Plastik" else f"{direk_tipi.upper()} DIREK"

    # Listeyi oluştur
    liste = [
        {"Malzeme": tel_model, "Adet": makara_adedi, "Birim Fiyat": fiyatlar.get(tel_model, 0), "Kod": kodlar.get(tel_model, "")},
        {"Malzeme": direk_model, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_model, 0), "Kod": kodlar.get(direk_model, "")},
        {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun, 0), "Kod": kodlar.get(urun, "")}
    ]

    if gunes_paneli == "Evet":
        liste.append({
            "Malzeme": gunes_panel_secimi,
            "Adet": 1,
            "Birim Fiyat": fiyatlar.get(gunes_panel_secimi, 0),
            "Kod": kodlar.get(gunes_panel_secimi, "")
        })

    # İzolatörler
    izo_dict = {
        "Ahşap": ["HALKA IZALATOR VIDALI SIYAH", "HALKA IZALATOR VIDALI RENKLI",
                  "HALKA IZALATOR SOMUNLU RENKLI", "HALKA IZALATOR SOMUNLU UZUN"],
        "İnşaat Demiri": ["MIL IZALATORU R=10-18", "MIL IZALATORU R=8-14"],
        "Köşebent": ["HALKA IZALATOR SOMUNLU RENKLI", "HALKA IZALATOR SOMUNLU UZUN", "KOSE IZALATOR"],
        "Örgü Tel": ["AĞ IZALATORU"]
    }
    st.subheader("🛠️ İzolatörler")
    izo_adet = math.ceil(toplam_tel / 5)
    for izo in izo_dict.get(direk_tipi, []):
        col1, col2 = st.columns([3, 1])
        with col1:
            sec = st.radio(izo, ["Hayır", "Evet"], horizontal=True, key=izo)
        if sec == "Evet":
            with col2:
                adet = st.number_input(f"{izo} Adet", value=izo_adet, min_value=1, step=1, key=izo+"_adet")
            liste.append({
                "Malzeme": izo, "Adet": adet,
                "Birim Fiyat": fiyatlar.get(izo, 0),
                "Kod": kodlar.get(izo, "")
            })

    # Yardımcı ekipmanlar
    st.subheader("🧰 Yardımcı Ekipmanlar")
    ekipmanlar = ["TOPRAKLAMA ÇUBUĞU", "TEL GERDIRICI", "YILDIRIM SAVAR", "UYARI TABELASI",
                  "ENERJI AKTARMA KABLOSU", "AKU MAŞASI", "12V 2A ADAPTOR", "AKU ŞARJ ALETI"]
    for ekipman in ekipmanlar:
        col1, col2 = st.columns([3, 1])
        with col1:
            secim = st.radio(ekipman, ["Hayır", "Evet"], horizontal=True, key=ekipman)
        if secim == "Evet":
            with col2:
                adet = st.number_input(f"{ekipman} Adet", min_value=1, step=1, key=ekipman+"_adet")
            liste.append({
                "Malzeme": ekipman, "Adet": adet,
                "Birim Fiyat": fiyatlar.get(ekipman, 0),
                "Kod": kodlar.get(ekipman, "")
            })

    # Kapı Seti
    st.subheader("🚪 Kapı Seti")
    kapi = st.radio("Kapı Seti Eklensin mi?", ["Hayır", "Evet"], horizontal=True)
    if kapi == "Evet":
        kapi_adet = st.number_input("Kapı Seti Adedi", min_value=1, step=1)
        liste.append({
            "Malzeme": f"KAPI SETİ (C6-A x{kapi_adet}, C6-B x{2*kapi_adet}, C6-C x{kapi_adet})",
            "Adet": kapi_adet,
            "Birim Fiyat": 128.3,
            "Kod": "SET"
        })

    # Final tablo
    df = pd.DataFrame(liste)
    df.index = range(1, len(df)+1)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader("📦 Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### 💰 Toplam Maliyet: **{toplam:.2f} TL**")

    excel_data = BytesIO()
    df.to_excel(excel_data, index=False)
    st.download_button(
        label="📥 Excel Çıktısını İndir",
        data=excel_data.getvalue(),
        file_name="cit_malzeme_listesi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
