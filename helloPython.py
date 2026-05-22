import streamlit as st

st.title("Hello, 世界！")

# 先创建一个滑块，把用户选的值存到变量 number 里
number = st.slider("选一个数字", 0, 100, 50)

# 再用 number 来展示结果
st.write(f"你选了 {number}，它的平方是 {number * number}")



