import streamlit as st
from datetime import datetime

# 1. 页面配置
st.set_page_config(page_title="审批流工作台", layout="wide")
st.title("🎬 视频生产流 (含批注与待定)")

# 2. 初始化数据
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {
            "id": 1, 
            "title": "示例：AI工具测评", 
            "status": "待选题审核", 
            "owner": "小王", 
            "content": "暂无文案",
            "boss_comment": ""  # 新增：老板批注字段
        },
    ]

# 3. 侧边栏：角色切换与新建
with st.sidebar:
    st.header("👤 角色模拟")
    user_role = st.radio("当前操作人身份：", ("员工", "老板"))
    
    st.divider()
    
    if user_role == "员工":
        st.header("➕ 新建选题")
        with st.form("new_task"):
            new_title = st.text_input("选题标题")
            new_owner = st.text_input("负责人", value="我")
            submitted = st.form_submit_button("提交给老板审核")
            if submitted and new_title:
                new_id = len(st.session_state.tasks) + 1 if st.session_state.tasks else 1
                st.session_state.tasks.append({
                    "id": new_id,
                    "title": new_title,
                    "status": "待选题审核",
                    "owner": new_owner,
                    "content": "",
                    "boss_comment": ""
                })
                st.success("选题已提交！")
                st.rerun()

# 4. 状态流转函数
def update_status(task_id, new_status):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            break

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]

# 5. 主界面布局
col1, col2, col3, col4, col5 = st.columns(5)

# --- 第一列：选题审核池 (重点修改区域) ---
with col1:
    st.subheader("1. 选题审核池")
    st.divider()
    for task in st.session_state.tasks:
        # 显示 "待审核" 和 "待定" 的任务
        if task['status'] in ["待选题审核", "选题待定"]:
            # 根据状态显示不同的边框颜色（视觉提示）
            border_color = True 
            
            with st.container(border=border_color):
                # 标题部分
                if task['status'] == "选题待定":
                    st.warning(f"🤔 待定：**{task['title']}**")
                else:
                    st.write(f"🆕 **{task['title']}**")
                
                st.caption(f"申请人: {task['owner']}")
                
                # --- 老板视图 ---
                if user_role == "老板":
                    # 1. 批注输入框
                    new_comment = st.text_input("老板意见/批注：", value=task['boss_comment'], key=f"cmt_{task['id']}")
                    task['boss_comment'] = new_comment # 实时保存
                    
                    # 2. 按钮操作区
                    c1, c2, c3 = st.columns([1,1,1])
                    with c1:
                        if st.button("✅", key=f"pass_{task['id']}", help="通过"):
                            update_status(task['id'], "文案撰写中")
                            st.rerun()
                    with c2:
                        if st.button("🤔", key=f"hold_{task['id']}", help="待定"):
                            update_status(task['id'], "选题待定")
                            st.rerun()
                    with c3:
                        if st.button("❌", key=f"rej_{task['id']}", help="直接删除"):
                            delete_task(task['id'])
                            st.rerun()
                            
                # --- 员工视图 ---
                else:
                    # 显示老板的批注
                    if task['boss_comment']:
                        st.info(f"老板说：{task['boss_comment']}")
                    
                    if task['status'] == "选题待定":
                        st.caption("状态：老板正在考虑中...")
                    else:
                        st.caption("状态：等待审核")
                    
                    # 员工删除/撤回按钮
                    if st.button("🗑️ 撤回/删除", key=f"del_{task['id']}"):
                        delete_task(task['id'])
                        st.rerun()

# --- 第二列：文案撰写 ---
with col2:
    st.subheader("2. 文案撰写中")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "文案撰写中":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                if task['boss_comment']:
                     st.caption(f"老板备注：{task['boss_comment']}")
                
                new_content = st.text_area("文案内容", value=task['content'], key=f"txt_{task['id']}")
                task['content'] = new_content
                
                if user_role == "员工":
                    if st.button("提交文案审核 ➡️", key=f"sub_script_{task['id']}"):
                        update_status(task['id'], "待文案审核")
                        st.rerun()

# --- 第三列：文案审核 ---
with col3:
    st.subheader("3. 待文案审核")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "待文案审核":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                with st.expander("查看文案"):
                    st.write(task['content'])
                
                if user_role == "老板":
                    c1, c2 = st.columns(2)
                    if c1.button("✅ 拍板", key=f"app_s_{task['id']}"):
                        update_status(task['id'], "制作中")
                        st.rerun()
                    if c2.button("↩️ 返工", key=f"rej_s_{task['id']}"):
                        update_status(task['id'], "文案撰写中")
                        st.rerun()

# --- 第四列：制作中 ---
with col4:
    st.subheader("4. 制作中")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "制作中":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                st.success("进入制作流程")
                if st.button("完成", key=f"fin_{task['id']}"):
                    update_status(task['id'], "已发布")
                    st.rerun()

# --- 第五列：已发布 ---
with col5:
    st.subheader("5. 已发布")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "已发布":
            st.write(f"✔ {task['title']}")
