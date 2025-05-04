import streamlit as st
import pandas as pd
import math

st.set_page_config(layout="wide")
st.title("KAYACANLAR - Çit Malzeme Hesaplama Programı")

# 🚀 Excel'den fiyat ve kod verilerini al
excel_url = "https://raw.githubusercontent.com/akayacan/kayacanlar-cit-appj/main/urun_listesi.xlsx"
df_urun = pd.read_excel(excel_url)
df_urun.columns = df_urun.columns.str.strip()
df_urun["\u00dcrün Adı"] = df_urun["\u00dcrün Adı"].str.strip()

fiyatlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Fiyat (TL)"]))
kodlar = dict(zip(df_urun["\u00dcrün Adı"], df_urun["Kod"]))

# 🔹 Kullanıcı Girişleri
en = st.number_input("Tarla En (m)", min_value=1.0, step=1.0)
boy = st.number_input("Tarla Boy (m)", min_value=1.0, step=1.0)
hayvan = st.selectbox("Hayvan Türü", ["Ayı", "Domuz", "Tilki", "At", "Küçükbaş", "Büyükbaş"])
arazi = st.selectbox("Arazi Tipi", ["Düz", "Otluk", "Eğimli"])
tel_tipi = st.selectbox("Tel Tipi", ["Misinalı", "Galvaniz", "Şerit"])

# ✔️ Alt tel çeşitleri
alt_teller = {
    "Misinalı": ["MISINALI TEL 2mm", "MISINALI TEL 3mm", "MISINALI TEL 4mm"],
    "Galvaniz": ["GALVANIZ TEL 1mm", "GALVANIZ TEL 1.25mm"],
    "Şerit": ["ŞERIT TEL"]
}
tel_kalinlik = st.selectbox("Tel Çeşidi", alt_teller[tel_tipi])

direk = st.selectbox("Direk Tipi", ["Ahşap", "İnşaat Demiri", "Köşebent", "Örgü Tel", "Plastik"])
gunes_paneli = st.radio("Güneş Paneli Kullanılsın mı?", ["Evet", "Hayır"])
gece_modu = st.radio("Gece Modu Eklensin mi?", ("Hayır", "Evet"))

ekipmanlar = [
    "Sıkma Aparatı", "Topraklama Çubuğu", "Yıldırım Savar", "Tel Gerdirici",
    "Uyarı Tabelası", "Enerji Aktarma Kablosu", "Akü Maşası", "Adaptör", "Akü Şarj Aleti"
]
secili_ekipmanlar = st.multiselect("Yardımcı Ekipmanlar (isteğe bağlı)", ekipmanlar)

# ✅ Hesaplama
tel_makara_uzunluk = {  # her ürün adı için makara boyu
    "ŞERIT TEL": 200
}

def get_makara_sayisi(urun_adi, toplam_metre):
    makara_uzunluk = tel_makara_uzunluk.get(urun_adi.upper(), 500)
    return math.ceil(toplam_metre / makara_uzunluk)

if st.button("HESAPLA"):
    cevre = 2 * (en + boy)
    tel_sira = {"Ayı": 4, "Domuz": 3, "Tilki": 4, "At": 4, "Küçükbaş": 4, "Büyükbaş": 2}[hayvan]
    direk_aralik = {"Düz": 4, "Otluk": 3, "Eğimli": 2}[arazi]
    toplam_tel = cevre * tel_sira
    direk_sayisi = round(cevre / direk_aralik)
    aparat = direk_sayisi * tel_sira
    makara_sayisi = get_makara_sayisi(tel_kalinlik, toplam_tel)

    # ✨ Enerji cihazı seçimi
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

    liste = [
        {"Malzeme": tel_kalinlik, "Adet": makara_sayisi, "Birim Fiyat": fiyatlar.get(tel_kalinlik, 0), "Kod": kodlar.get(tel_kalinlik, "")},
        {"Malzeme": "Direk", "Adet": direk_sayisi, "Birim Fiyat": fiyatlar.get("Direk", 0), "Kod": kodlar.get("Direk", "")},
        {"Malzeme": "Aparat", "Adet": aparat, "Birim Fiyat": fiyatlar.get("Aparat", 0), "Kod": kodlar.get("Aparat", "")},
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
    st.download_button(
        label="📄 Excel Çıktısını İndir",
        data=df.to_excel(index=False).encode("utf-8"),
        file_name="cit_malzeme_listesi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
