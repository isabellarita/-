import streamlit as st
from datetime import datetime

# 1. 页面配置
st.set_page_config(page_title="团队协作工作流", layout="wide")
st.title("🎬 视频生产流 (含反馈透传)")

# 2. 初始化数据
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {
            "id": 1, 
            "title": "示例：AI工具测评", 
            "status": "待选题审核", 
            "owner": "小王", 
            "content": "暂无文案",
            "boss_comment": "",      # 老板的具体意见
            "feedback_type": "none"  # 状态类型: pass(通过)/reject(驳回)/hold(待定)
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
                    "boss_comment": "",
                    "feedback_type": "none"
                })
                st.success("选题已提交！")
                st.rerun()

# 4. 状态更新辅助函数 (核心修改：增加 type 记录是好消息还是坏消息)
def update_task(task_id, new_status, comment, fb_type):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            task['boss_comment'] = comment
            task['feedback_type'] = fb_type
            break

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]

# 5. 主界面布局
col1, col2, col3, col4, col5 = st.columns(5)

# ==========================================
# 第一列：选题审核池
# ==========================================
with col1:
    st.subheader("1. 选题审核池")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] in ["待选题审核", "选题待定"]:
            border_color = True
            with st.container(border=border_color):
                # 标题展示
                if task['status'] == "选题待定":
                    st.warning(f"🤔 待定：**{task['title']}**")
                else:
                    st.write(f"🆕 **{task['title']}**")
                st.caption(f"申请人: {task['owner']}")

                # --- 老板操作区 ---
                if user_role == "老板":
                    # 获取之前的意见，方便修改
                    comment_input = st.text_input("老板意见：", value=task['boss_comment'], key=f"c1_{task['id']}")
                    
                    c1, c2, c3 = st.columns([1,1,1])
                    with c1:
                        if st.button("✅", key=f"pass1_{task['id']}", help="通过"):
                            # 状态变更为：文案撰写中，类型为：pass
                            update_task(task['id'], "文案撰写中", comment_input, "pass")
                            st.rerun()
                    with c2:
                        if st.button("🤔", key=f"hold1_{task['id']}", help="待定"):
                            # 状态变更为：选题待定，类型为：hold
                            update_task(task['id'], "选题待定", comment_input, "hold")
                            st.rerun()
                    with c3:
                        if st.button("❌", key=f"del1_{task['id']}", help="删除"):
                            delete_task(task['id'])
                            st.rerun()
                
                # --- 员工查看区 ---
                else:
                    if task['status'] == "选题待定":
                        st.warning(f"老板说：{task['boss_comment']}")
                    else:
                        st.caption("等待审核中...")
                    
                    if st.button("撤回", key=f"back1_{task['id']}"):
                        delete_task(task['id'])
                        st.rerun()

# ==========================================
# 第二列：文案撰写 (员工看到反馈的核心区域)
# ==========================================
with col2:
    st.subheader("2. 文案撰写中")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "文案撰写中":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                
                # --- 🌟 核心修改：显示上一轮的反馈 ---
                if task['feedback_type'] == "pass":
                    st.success(f"✅ 选题已通过！\n\n老板嘱咐：{task['boss_comment'] if task['boss_comment'] else '无'}")
                elif task['feedback_type'] == "reject":
                    st.error(f"❌ 文案被退回！\n\n修改意见：{task['boss_comment']}")
                # ------------------------------------

                new_content = st.text_area("编写文案", value=task['content'], height=150, key=f"txt_{task['id']}")
                task['content'] = new_content
                
                if user_role == "员工":
                    if st.button("提交文案审核 ➡️", key=f"sub2_{task['id']}"):
                        # 提交后，清空反馈类型，以免干扰下一阶段
                        update_task(task['id'], "待文案审核", task['boss_comment'], "none")
                        st.rerun()

# ==========================================
# 第三列：文案审核
# ==========================================
with col3:
    st.subheader("3. 待文案审核")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "待文案审核":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                with st.expander("📄 查看详细文案", expanded=True):
                    st.text(task['content'])
                
                if user_role == "老板":
                    comment_input = st.text_input("修改/制作意见：", key=f"c3_{task['id']}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ 拍板制作", key=f"pass3_{task['id']}"):
                            update_task(task['id'], "制作中", comment_input, "pass")
                            st.rerun()
                    with c2:
                        if st.button("↩️ 打回修改", key=f"rej3_{task['id']}"):
                            # 这里的 reject 会导致回到第二列时显示红色报错
                            update_task(task['id'], "文案撰写中", comment_input, "reject")
                            st.rerun()
                else:
                    st.info("⏳ 老板正在审稿...")

# ==========================================
# 第四列：制作中 (带制作要求)
# ==========================================
with col4:
    st.subheader("4. 制作中")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "制作中":
            with st.container(border=True):
                st.write(f"**{task['title']}**")
                
                # 显示通过文案时的嘱咐
                st.success(f"🎬 文案已定稿！\n\n制作要求：{task['boss_comment'] if task['boss_comment'] else '无'}")
                
                with st.expander("查看定稿文案"):
                    st.text(task['content'])

                if st.button("✅ 制作完成", key=f"fin4_{task['id']}"):
                    update_task(task['id'], "已发布", "", "none")
                    st.rerun()

# ==========================================
# 第五列：已发布
# ==========================================
with col5:
    st.subheader("5. 已发布")
    st.divider()
    for task in st.session_state.tasks:
        if task['status'] == "已发布":
            st.write(f"✔ {task['title']}")
