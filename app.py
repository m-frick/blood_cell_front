from IPython.core.pylabtools import figsize
from scipy.ndimage.measurements import label
import streamlit as st
import numpy as np
from PIL import Image
import requests
import matplotlib.pyplot as plt
import json


st.set_page_config(layout="wide")
st.title("Blood sample analysis")
uploaded_file = st.file_uploader("Upload a blood sample .png image", type=["png", "jpg"])


if uploaded_file is not None:
    #st.write(type(uploaded_file))

    st.markdown("""### Uploaded Image""")
    st.image(uploaded_file,width=500)

    # st.markdown("""### To read file as bytes""")
    # bytes_data = uploaded_file.getvalue()
    # reshape necessary, but could only get shape with PIL, not from bytes directly

    st.markdown("""### Segmented Image""")
    # image = Image.open(io.BytesIO(bytes_data))
    image = Image.open(uploaded_file)
    #st.image(image)
    #st.write("Image shape: ", np.asarray(image).shape)
    #st.write(np.asarray(image))


    files = { "file": uploaded_file.getvalue() }

    with st.spinner("Processing..."):
        response = requests.post("http://localhost:8000/segmenter",
                                    files=files)

        images = json.loads(response.json()["list_ROI"])
        images = [np.array(image) for image in images]

        predictions = np.array(json.loads(response.json()["predictions"]))
        predictions = np.round(predictions, 2)
        pred_list = predictions.tolist()
        pred_finish = [int(100*abs(1-item)) for pred in pred_list for item in pred]

        num_of_uninfected = 0
        num_of_infected = 0
        for pred in pred_finish:
            if pred >= 50:
                num_of_infected += 1
            else:
                num_of_uninfected += 1

        pred_finish = [f"{pred}%" for pred in pred_finish]

        st.write(f"#### Number of segmented Cells:{len(predictions)}")
        st.image(images[0],width=500)

        fig_hist, axs = plt.subplots(1,2,figsize=(10,3))
        axs[0].set_xticks([0,50,100])
        axs[0].set_xticklabels(["Uninfected", "Threshold", "Infected"])
        N, bins, patches = axs[0].hist(pred_finish, range=[0, 1],bins=100)
        for i in range(0,50,1):
            patches[i].set_facecolor('g')
        for i in np.arange(50, 100,1):
            patches[i].set_facecolor('r')
        axs[1].pie([num_of_uninfected, num_of_infected],
                   colors=["g","r"],
                   labels=["Uninfected Cell", "Infected Cell"],
                   autopct='%1.0f%%',
                   rotatelabels=True)
        st.pyplot(fig_hist)

        st.markdown("""### Red blood cells with chance of being infected""")
        st.image(images[1:],width=200, caption=pred_finish)

    st.success("Done!")
