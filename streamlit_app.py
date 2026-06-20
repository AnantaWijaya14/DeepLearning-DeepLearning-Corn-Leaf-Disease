import requests
import streamlit as st
from PIL import Image
import pandas as pd


API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Corn Leaf Disease Classification",
    page_icon="🌽",
    layout="wide"
)

st.title("Corn Leaf Disease Classification")
st.write(
    "Aplikasi ini digunakan untuk mengklasifikasikan penyakit daun jagung "
    "menggunakan model MobileNetV2."
)

recommendations = {
    "Blight": (
        "Daun terindikasi penyakit Blight. Lakukan pemantauan area tanaman, "
        "pisahkan bagian tanaman yang terinfeksi jika memungkinkan, dan konsultasikan "
        "penanganan lebih lanjut dengan ahli pertanian."
    ),
    "Common_Rust": (
        "Daun terindikasi Common Rust. Perhatikan kelembapan lingkungan dan lakukan "
        "pengendalian penyakit sesuai rekomendasi pertanian setempat."
    ),
    "Gray_Leaf_Spot": (
        "Daun terindikasi Gray Leaf Spot. Lakukan pemantauan penyebaran bercak pada daun "
        "dan pertimbangkan tindakan pengendalian untuk mencegah penyebaran lebih lanjut."
    ),
    "Healthy": (
        "Daun terdeteksi dalam kondisi sehat. Tetap lakukan pemantauan rutin untuk menjaga "
        "kondisi tanaman tetap optimal."
    )
}

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload Gambar Daun Jagung")

    uploaded_file = st.file_uploader(
        "Pilih gambar daun jagung",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Preview Gambar", use_container_width=True)

with col2:
    st.subheader("Hasil Prediksi")

    if uploaded_file is not None:
        if st.button("Prediksi"):
            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                response = requests.post(
                    f"{API_URL}/predict",
                    files=files,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()

                    prediction = result["prediction"]
                    confidence = result["confidence"]

                    st.success(f"Prediksi: {prediction}")
                    st.metric("Confidence", f"{confidence * 100:.2f}%")

                    st.subheader("Rekomendasi")
                    st.write(
                        recommendations.get(
                            prediction,
                            "Belum tersedia rekomendasi untuk kelas ini."
                        )
                    )

                else:
                    st.error("Prediksi gagal. Periksa kembali API.")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Tidak dapat terhubung ke API. "
                    "Pastikan FastAPI sudah dijalankan."
                )
            except Exception as error:
                st.error(f"Terjadi error: {error}")

    else:
        st.info("Silakan upload gambar terlebih dahulu.")


st.divider()

st.subheader("Riwayat Prediksi")

if st.button("Muat Riwayat Prediksi"):
    try:
        history_response = requests.get(
            f"{API_URL}/history?limit=10",
            timeout=30
        )

        if history_response.status_code == 200:
            history_data = history_response.json()["history"]

            if len(history_data) > 0:
                df_history = pd.DataFrame(history_data)
                st.dataframe(df_history, use_container_width=True)
            else:
                st.info("Belum ada riwayat prediksi.")

        else:
            st.error("Gagal mengambil riwayat prediksi.")

    except requests.exceptions.ConnectionError:
        st.error(
            "Tidak dapat terhubung ke API. "
            "Pastikan FastAPI sudah dijalankan."
        )
    except Exception as error:
        st.error(f"Terjadi error: {error}")