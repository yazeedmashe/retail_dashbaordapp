import streamlit as st
import pandas as pd 
import numpy as np

st.title("Simple Dashboard")

st.sidebar.header("User Input")

option = st.sidebar.selectbox("choose a number", range(1,11))

st.subheader("Random Data")

data = np.random.randn(10,option)

st.line_chart(data)

name = st.text_input("Enter Your Name")

st.write(f'Hello, {name}')
