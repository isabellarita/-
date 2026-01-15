import streamlit as st
from datetime import datetime

# 1. 页面配置
st.set_page_config(page_title="审批流工作台", layout="wide")
st.title("🎬 视频生产流 (含老板审批)")

# 2. 初始化数据 (模拟数据库)
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "title": "示例：AI工具测评", "status": "待选题审核", "owner": "小王", "content": "暂无文案"},
        {"id": 2, "title": "示例：公司Vlog", "status": "文案撰写中", "owner": "小李", "content": "这是初稿..."},
    ]

# 3. 侧边栏：角色切换与新建
with st.sidebar:
    st.header("👤 角色模拟")
    # 模拟登录身份
    user_role = st.radio("当前操作人身份：", ("员工", "老板"))
    
    st.divider()
    
    # 仅员工可新建选题
    if user_role == "员工":
        st.header("➕ 新建选题")
        with st.form("new_task"):
            new_title = st.text_input("选题标题")
            new_owner = st.text_input("负责人", value="我")
            submitted = st.form_submit_button("提交给老板审核")
            if submitted and new_title:
                new_id = len(st.session_state.tasks) + 1
                st.session_state.tasks.append({
                    "id": new_id,
                    "title": new_title,
                    "status": "待选题审核", # 初始状态直接进入审核
                    "owner": new_owner,
                    "content": ""
                })
                st.success("选题已提交，等待老板审核！")
                st.rerun()

# 4. 定义流转逻辑函数
def update_status(task_id, new_status):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            break

# 5. 主界面布局 (根据流程分列)
col1, col2, col3, col4, col5 = st.columns(5)

# --- 第一列：选题审核池 (老板的主场) ---
with col1:
    st.subheader("1. 待选题审核")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "待选题审核":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                st.caption(f"申请人: {task['owner']}")
                
                if user_role == "老板":
                    c1, c2 = st.columns(2)
                    if c1.button("✅ 通过", key=f"app_idea_{task['id']}"):
                        update_status(task['id'], "文案撰写中")
                        st.rerun()
                    if c2.button("❌ 驳回", key=f"rej_idea_{task['id']}"):
                         # 驳回逻辑可以是删除，或者回到草稿，这里简单处理为从列表消失
                        st.session_state.tasks.remove(task)
                        st.rerun()
                else:
                    st.warning("⏳ 等待老板拍板")

# --- 第二列：文案撰写 (员工的主场) ---
with col2:
    st.subheader("2. 文案撰写中")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "文案撰写中":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                # 模拟写文案
                new_content = st.text_area("文案内容", value=task['content'], key=f"txt_{task['id']}")
                task['content'] = new_content
                
                if user_role == "员工":
                    if st.button("提交文案审核 ➡️", key=f"sub_script_{task['id']}"):
                        update_status(task['id'], "待文案审核")
                        st.rerun()
                else:
                    st.info("员工正在撰写...")

# --- 第三列：文案审核 (老板的主场) ---
with col3:
    st.subheader("3. 待文案审核")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "待文案审核":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                with st.expander("查看详细文案"):
                    st.write(task['content'])
                
                if user_role == "老板":
                    c1, c2 = st.columns(2)
                    if c1.button("✅ 拍板", key=f"app_script_{task['id']}"):
                        update_status(task['id'], "制作中")
                        st.rerun()
                    if c2.button("↩️ 返工", key=f"rej_script_{task['id']}"):
                        update_status(task['id'], "文案撰写中") # 打回上一级
                        st.rerun()
                else:
                    st.warning("⏳ 等待老板拍板")

# --- 第四列：制作中 ---
with col4:
    st.subheader("4. 制作中")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "制作中":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                st.success("老板已确认文案")
                if st.button("完成制作", key=f"fin_{task['id']}"):
                    update_status(task['id'], "已发布")
                    st.rerun()

# --- 第五列：已发布 ---
with col5:
    st.subheader("5. 已发布")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "已发布":
            st.write(f"✔ {task['title']}")