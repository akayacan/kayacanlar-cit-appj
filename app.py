import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import math

# Excel dosyasini oku
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun.columns = df_urun.columns.str.strip()
df_urun["\u00dcr\u00fcn Ad\u0131"] = df_urun["\u00dcr\u00fcn Ad\u0131"].str.strip()

fiyatlar = dict(zip(df_urun["\u00dcr\u00fcn Ad\u0131"], df_urun["Fiyat (TL)"].fillna(0)))
kodlar = dict(zip(df_urun["\u00dcr\u00fcn Ad\u0131"], df_urun["Kod"].fillna("")))

st.set_page_config(layout="wide")
st.title("KAYACANLAR - \u00c7it Malzeme Hesaplama Program\u0131")

# Girdi Alanlar\u0131
en = st.number_input("Tarla En (m)", min_value=0, step=1)
boy = st.number_input("Tarla Boy (m)", min_value=0, step=1)
hayvan = st.selectbox("Hayvan T\u00fcr\u00fc", ["Ay\u0131", "Domuz", "Tilki", "K\u00fc\u00e7\u00fckba\u015f", "B\u00fcy\u00fckba\u015f", "At"])
arazi = st.selectbox("Arazi Tipi", ["D\u00fcz", "Otluk", "Ei\u011fimli"])
tel_tipi = st.selectbox("Tel Tipi", ["MISINALI", "GALVANIZ", "\u015eERIT"])

tel_model_options = {
    "MISINALI": ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"],
    "GALVANIZ": ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"],
    "\u015eERIT": ["\u015eERIT TEL"]
}

tel_model = st.selectbox("Tel Modeli", tel_model_options.get(tel_tipi, []))

direk_tipi = st.selectbox("Direk Tipi", ["Ah\u015fap", "\u0130n\u015faat Demiri", "K\u00f6\u015febent", "\u00d6rg\u00fc Tel", "Plastik"])

plastik_model = ""
if direk_tipi == "Plastik":
    plastik_model = st.selectbox("Plastik Direk Modeli", [
        "PLASTIK DIREK 100cm SIYAH",
        "PLASTIK DIREK 100cm BEYAZ",
        "PLASTIK DIREK 105cm SIYAH",
        "PLASTIK DIREK 105cm BEYAZ",
        "PLASTIK DIREK 125cm SIYAH",
        "PLASTIK DIREK 125cm BEYAZ"
    ])

# Otomatik izolat\u00f6r say\u0131s\u0131 hesapla
tel_sira_dict = {"Ay\u0131": 4, "Domuz": 3, "Tilki": 4, "K\u00fc\u00e7\u00fckba\u015f": 4, "B\u00fcy\u00fckba\u015f": 2, "At": 4}
izolator_sayisi_otomatik = 0 if en == 0 or boy == 0 else math.ceil((en + boy) * 2 * tel_sira_dict[hayvan] / 5)

# G\u00fcne\u015f Paneli
st.subheader("\ud83c\udf1e G\u00fcne\u015f Paneli")
gunes_paneli = st.radio("G\u00fcne\u015f paneli kullan\u0131ls\u0131n m\u0131?", ["Hay\u0131r", "Evet"])
gunes_panel_secimi = ""
if gunes_paneli == "Evet":
    gunes_panel_secimi = st.selectbox("G\u00fcne\u015f Paneli Se\u00e7", ["GUNES PANELI 12W", "GUNES PANELI 25W"])

# \u0130zolat\u00f6r Se\u00e7imi
st.subheader("\ud83d\udd27 \u0130zolat\u00f6rler")
aparatlar_dict = {
    "Ah\u015fap": ["HALKA IZALATOR VIDALI SIYAH", "HALKA IZALATOR VIDALI RENKLI", "HALKA IZALATOR SOMUNLU RENKLI", "HALKA IZALATOR SOMUNLU UZUN"],
    "\u0130n\u015faat Demiri": ["MIL IZALATORU R=10-18", "MIL IZALATORU R=8-14"],
    "K\u00f6\u015febent": ["HALKA IZALATOR SOMUNLU RENKLI", "HALKA IZALATOR SOMUNLU UZUN", "KOSE IZALATOR"],
    "\u00d6rg\u00fc Tel": ["A\u011e IZALATORU"]
}

secilen_aparatlar = []
for aparat in aparatlar_dict.get(direk_tipi, []):
    col1, col2 = st.columns([3, 1])
    with col1:
        secim = st.radio(aparat, ["Hay\u0131r", "Evet"], horizontal=True, key=aparat)
    if secim == "Evet":
        with col2:
            adet = st.number_input(f"{aparat} Adet", value=izolator_sayisi_otomatik, min_value=1, step=1, key=aparat+"_adet")
        secilen_aparatlar.append({
            "Malzeme": aparat,
            "Adet": adet,
            "Birim Fiyat": fiyatlar.get(aparat.strip(), 0),
            "Kod": kodlar.get(aparat.strip(), "")
        })

# Yard\u0131mc\u0131 ekipmanlar
st.subheader("\ud83e\uddf0 Yard\u0131mc\u0131 Ekipmanlar")
ekipmanlar = [
    "TOPRAKLAMA \u00c7UBU\u011eU", "TEL GERDIRICI", "YILDIRIM SAVAR",
    "UYARI TABELASI", "ENERJI AKTARMA KABLOSU", "AKU \u015eARJ ALETI", "KAPI SETI"
]
secilen_ekipmanlar = []

for ekipman in ekipmanlar:
    col1, col2 = st.columns([3, 1])
    with col1:
        secim = st.radio(ekipman, ["Hay\u0131r", "Evet"], horizontal=True, key=ekipman)
    if secim == "Evet":
        with col2:
            adet = st.number_input(f"{ekipman} Adet", min_value=1, step=1, key=ekipman+"_adet")
        if ekipman == "KAPI SETI":
            secilen_ekipmanlar.append({"Malzeme": "C6-A", "Adet": adet, "Birim Fiyat": 0, "Kod": "C6-A"})
            secilen_ekipmanlar.append({"Malzeme": "C6-B", "Adet": adet * 2, "Birim Fiyat": 0, "Kod": "C6-B"})
            secilen_ekipmanlar.append({"Malzeme": "C6-C", "Adet": adet, "Birim Fiyat": 0, "Kod": "C6-C"})
            secilen_ekipmanlar.append({"Malzeme": "KAPI SETI", "Adet": adet, "Birim Fiyat": 128.3, "Kod": "CA-9"})
        else:
            secilen_ekipmanlar.append({
                "Malzeme": ekipman,
                "Adet": adet,
                "Birim Fiyat": fiyatlar.get(ekipman.strip(), 0),
                "Kod": kodlar.get(ekipman.strip(), "")
            })

# Hesapla
if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = tel_sira_dict[hayvan]
    direk_aralik = {"D\u00fcz": 4, "Otluk": 3, "Ei\u011fimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)

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

    tel_makara_uzunlugu = {"\u015eERIT TEL": 200}
    makara_uzunlugu = tel_makara_uzunlugu.get(tel_model.strip(), 500)
    makara_adedi = -(-toplam_tel // makara_uzunlugu)

    direk_model = plastik_model if direk_tipi == "Plastik" else f"{direk_tipi.upper()} DIREK"

    liste = [
        {"Malzeme": tel_model, "Adet": makara_adedi, "Birim Fiyat": fiyatlar.get(tel_model.strip(), 0), "Kod": kodlar.get(tel_model.strip(), "")},
        {"Malzeme": direk_model, "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get(direk_model.strip(), 0), "Kod": kodlar.get(direk_model.strip(), "")},
        {"Malzeme": urun, "Adet": 1, "Birim Fiyat": fiyatlar.get(urun.strip(), 0), "Kod": kodlar.get(urun.strip(), "")}
    ]

    if gunes_paneli == "Evet" and gunes_panel_secimi:
        liste.append({
            "Malzeme": gunes_panel_secimi,
            "Adet": 1,
            "Birim Fiyat": fiyatlar.get(gunes_panel_secimi, 0),
            "Kod": kodlar.get(gunes_panel_secimi, "")
        })

    liste.extend(secilen_aparatlar)
    liste.extend(secilen_ekipmanlar)

    df = pd.DataFrame(liste)
    df.index = range(1, len(df)+1)
    df["Toplam"] = df["Adet"] * df["Birim Fiyat"]
    toplam = df["Toplam"].sum()

    st.subheader("\ud83d\udce6 Malzeme ve Fiyat Listesi")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"### \ud83d\udcb0 Toplam Maliyet: **{toplam:.2f} TL**")

    excel_data = BytesIO()
    df.to_excel(excel_data, index=False)
    st.download_button(
        label="\ud83d\udcc5 Excel \u00c7\u0131kt\u0131s\u0131n\u0131 \u0130ndir",
        data=excel_data.getvalue(),
        file_name="cit_malzeme_listesi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
