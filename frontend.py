# frontend.py
import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="图书管理系统", page_icon="🔒")

# --- 状态管理 ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- 登录与注册页面 ---
def login_page():
    st.title("🔒 请先登录")
    
    tab1, tab2 = st.tabs(["登录", "注册新账号"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("登录")
            
            if submitted:
                try:
                    # FastAPI OAuth2 标准是用 form data 发送
                    res = requests.post(f"{API_BASE_URL}/auth/login", data={"username": username, "password": password})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.username = username
                        st.success("登录成功！")
                        st.rerun() # 刷新页面进入系统
                    else:
                        st.error(f"登录失败: {res.text}")
                except Exception as e:
                    st.error(f"连接错误: {e}")

    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("设置用户名")
            new_pass = st.text_input("设置密码", type="password")
            reg_submit = st.form_submit_button("注册")
            
            if reg_submit:
                if new_user and new_pass:
                    payload = {"username": new_user, "password": new_pass}
                    res = requests.post(f"{API_BASE_URL}/auth/register", json=payload)
                    if res.status_code == 200:
                        st.success("注册成功！请切换到登录标签进行登录。")
                    else:
                        st.error(f"注册失败: {res.text}")
                else:
                    st.warning("请填写完整")

# --- 主界面 (登录后可见) ---
def main_app():
    # 侧边栏
    st.sidebar.write(f"👤 当前用户: **{st.session_state.username}**")
    if st.sidebar.button("退出登录"):
        st.session_state.token = None
        st.session_state.username = None
        st.rerun()
        
    menu = st.sidebar.radio("功能导航", ["📖 图书编目", "📦 馆藏管理", "🔄 借还(需权限)"])
    
    # 定义请求头 (带着 Token 去访问)
    auth_headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # 1. 编目
    if menu == "📖 图书编目":
        st.header("1. 录入新书")
        # ... (和之前一样的录入逻辑，简化展示)
        with st.form("cat_form"):
            isbn = st.text_input("ISBN")
            title = st.text_input("书名")
            author = st.text_input("作者")
            publisher = st.text_input("出版社")
            price = st.number_input("价格", step=0.1)
            if st.form_submit_button("录入"):
                payload = {"isbn": isbn, "title": title, "author": author, "publisher": publisher, "price": price}
                # 这里我们假设编目也需要登录权限 (可选)
                res = requests.post(f"{API_BASE_URL}/catalog", json=payload, headers=auth_headers)
                if res.status_code == 200:
                    st.success("录入成功")
                else:
                    st.error(res.text)
        
        # 显示列表
        res = requests.get(f"{API_BASE_URL}/catalog") # GET 不需要权限
        if res.status_code == 200:
            st.dataframe(pd.DataFrame(res.json()))

    # 2. 馆藏
    elif menu == "📦 馆藏管理":
        st.header("2. 库存管理")
        with st.form("inv_form"):
            info_id = st.number_input("书目ID", min_value=1)
            barcode = st.text_input("条码")
            if st.form_submit_button("上架"):
                payload = {"barcode": barcode, "info_id": info_id}
                res = requests.post(f"{API_BASE_URL}/inventory", json=payload, headers=auth_headers)
                if res.status_code == 200:
                    st.success("上架成功")
                else:
                    st.error(res.text)
        
        if st.button("刷新库存"):
            res = requests.get(f"{API_BASE_URL}/inventory")
            if res.status_code == 200:
                data = res.json()
                if data:
                    flat_data = [{"条码": i['barcode'], "状态": i['status'], "书名": i['info']['title']} for i in data]
                    st.dataframe(pd.DataFrame(flat_data))

    # 3. 借还 (重点测试权限)
    elif menu == "🔄 借还(需权限)":
        st.header("3. 借还操作")
        st.info("此页面所有操作都受到后端保护，不带 Token 无法通过。")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("借书")
            b_code = st.text_input("借书条码")
            if st.button("借阅"):
                res = requests.post(
                    f"{API_BASE_URL}/circulation/borrow", 
                    json={"barcode": b_code},
                    headers=auth_headers # 🔥 必须带 Header
                )
                if res.status_code == 200:
                    st.success("借阅成功！")
                else:
                    st.error(f"失败: {res.json().get('detail')}")

        with col2:
            st.subheader("还书")
            r_code = st.text_input("还书条码")
            if st.button("归还"):
                res = requests.post(
                    f"{API_BASE_URL}/circulation/return", 
                    json={"barcode": r_code},
                    headers=auth_headers # 🔥 必须带 Header
                )
                if res.status_code == 200:
                    st.success("归还成功！")
                else:
                    st.error(f"失败: {res.json().get('detail')}")

# --- 程序入口 ---
if st.session_state.token:
    main_app()
else:
    login_page()