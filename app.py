import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 页面配置
st.set_page_config(page_title="团队协作工作流", layout="wide")
st.title("🎬 视频生产流 (数据持久版)")

# --- 💾 核心修改：数据读写函数 ---
FILE_PATH = 'tasks.csv'

def load_data():
    # 如果文件存在，就读取它
    if os.path.exists(FILE_PATH):
        try:
            # 读取并将所有空值填充为空字符串，防止报错
            return pd.read_csv(FILE_PATH).fillna("").to_dict('records')
        except:
            return []
    else:
        # 如果文件不存在，返回初始数据
        return [
            {
                "id": 1, 
                "title": "示例：AI工具测评", 
                "status": "待选题审核", 
                "owner": "小王", 
                "content": "暂无文案",
                "boss_comment": "",
                "feedback_type": "none"
            }
        ]

def save_data(tasks):
    # 把最新的任务列表存入 CSV 文件
    df = pd.DataFrame(tasks)
    df.to_csv(FILE_PATH, index=False)
    # 同时更新当前页面的缓存
    st.session_state.tasks = tasks

# 2. 初始化数据 (每次刷新页面都会重新读取文件)
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_data()

# ----------------------------------------------------
# 以下逻辑基本不变，只是在修改数据后增加了 save_data() 调用
# ----------------------------------------------------

# 3. 侧边栏：角色切换与新建
with st.sidebar:
    st.header("👤 角色选择")
    user_role = st.radio("当前身份：", ("员工", "老板"))
    
    st.divider()
    
    if user_role == "员工":
        st.header("➕ 新建选题")
        with st.form("new_task"):
            new_title = st.text_input("选题标题")
            new_owner = st.text_input("负责人", value="我")
            submitted = st.form_submit_button("提交给老板审核")
            if submitted and new_title:
                # 获取当前最新的 ID
                current_ids = [t['id'] for t in st.session_state.tasks]
                new_id = max(current_ids) + 1 if current_ids else 1
                
                new_task = {
                    "id": new_id,
                    "title": new_title,
                    "status": "待选题审核",
                    "owner": new_owner,
                    "content": "",
                    "boss_comment": "",
                    "feedback_type": "none"
                }
                # 添加并保存到文件
                st.session_state.tasks.append(new_task)
                save_data(st.session_state.tasks) # <--- 存盘
                
                st.success("选题已提交！")
                st.rerun()

# 4. 状态更新辅助函数
def update_task(task_id, new_status, comment, fb_type):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            task['boss_comment'] = comment
            task['feedback_type'] = fb_type
            break
    save_data(st.session_state.tasks) # <--- 存盘

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]
    save_data(st.session_state.tasks) # <--- 存盘

def update_content(task_id, new_content):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['content'] = new_content
            break
    save_data(st.session_state.tasks) # <--- 存盘

# 5. 主界面布局
col1, col2, col3, col4, col5 = st.columns(5)

# 第一列：选题审核
with col1:
    st.subheader("1. 选题审核池")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] in ["待选题审核", "选题待定"]:
            border_color = True
            with st.container(border=border_color):
                if task['status'] == "选题待定":
                    st.warning(f"🤔 待定：**{task['title']}**")
                else:
                    st.write(f"🆕 **{task['title']}**")
                st.caption(f"申请人: {task['owner']}")

                if user_role == "老板":
                    comment_input = st.text_input("老板意见：", value=str(task['boss_comment']), key=f"c1_{task['id']}")
                    c1, c2, c3 = st.columns([1,1,1])
                    with c1:
                        if st.button("✅", key=f"p1_{task['id']}"):
                            update_task(task['id'], "文案撰写中", comment_input, "pass")
                            st.rerun()
                    with c2:
                        if st.button("🤔", key=f"h1_{task['id']}"):
                            update_task(task['id'], "选题待定", comment_input, "hold")
                            st.rerun()
                    with c3:
                        if st.button("❌", key=f"d1_{task['id']}"):
                            delete_task(task['id'])
                            st.rerun()
                else:
                    if task['status'] == "选题待定":
                        st.warning(f"老板说：{task['boss_comment']}")
                    if st.button("撤回", key=f"b1_{task['id']}"):
                        delete_task(task['id'])
                        st.rerun()

# 第二列：文案撰写 (需要增加实时保存文案的功能)
with col2:
    st.subheader("2. 文案撰写中")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "文案撰写中":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                if task['feedback_type'] == "pass":
                    st.success(f"✅ 嘱咐：{task['boss_comment']}")
                elif task['feedback_type'] == "reject":
                    st.error(f"❌ 退回意见：{task['boss_comment']}")

                # 注意：这里需要处理输入框的保存逻辑
                # 我们使用 on_change 回调或者每次输入后手动保存不太方便
                # 这里使用简单的逻辑：输入框改变时暂时不存，点击按钮时存，或者利用key自动绑定
                # 为了简化，我们让用户每次修改完需要点一下任意按钮（Streamlit特性），或者我们加个“保存草稿”按钮
                
                content_val = st.text_area("编写文案", value=str(task['content']), height=150, key=f"txt_{task['id']}")
                
                # 检测到内容变化自动更新内存，但为了存盘，我们可以加个小按钮，或者在提交时统一保存
                if content_val != task['content']:
                    update_content(task['id'], content_val)

                if user_role == "员工":
                    if st.button("提交审核 ➡️", key=f"sub2_{task['id']}"):
                        update_task(task['id'], "待文案审核", task['boss_comment'], "none")
                        st.rerun()

# 第三列：文案审核
with col3:
    st.subheader("3. 待文案审核")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "待文案审核":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                with st.expander("查看文案", expanded=True):
                    st.text(task['content'])
                
                if user_role == "老板":
                    comment_input = st.text_input("意见：", key=f"c3_{task['id']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ 拍板", key=f"p3_{task['id']}"):
                            update_task(task['id'], "制作中", comment_input, "pass")
                            st.rerun()
                    with c2:
                        if st.button("↩️ 打回", key=f"r3_{task['id']}"):
                            update_task(task['id'], "文案撰写中", comment_input, "reject")
                            st.rerun()

# 第四列：制作中
with col4:
    st.subheader("4. 制作中")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "制作中":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                st.success(f"制作要求：{task['boss_comment']}")
                if st.button("✅ 完成", key=f"f4_{task['id']}"):
                    update_task(task['id'], "已发布", "", "none")
                    st.rerun()

# 第五列：已发布
with col5:
    st.subheader("5. 已发布")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "已发布":
            st.write(f"✔ {task['title']}")
