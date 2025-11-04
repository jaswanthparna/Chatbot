import streamlit as st
from backend_with_tools import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# =========================== Utilities ===========================
def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []
    # Clear the title for new chat
    if "chat_titles" in st.session_state and thread_id in st.session_state["chat_titles"]:
        del st.session_state["chat_titles"][thread_id]

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def get_chat_title(thread_id):
    """Get a meaningful title for the chat based on first message"""
    if thread_id in st.session_state.get("chat_titles", {}):
        return st.session_state["chat_titles"][thread_id]
    
    # Load conversation and extract first user message
    messages = load_conversation(thread_id)
    for msg in messages:
        if isinstance(msg, HumanMessage) and msg.content:
            # Truncate to first 40 characters
            title = msg.content[:40] + ("..." if len(msg.content) > 40 else "")
            # Store it for future use
            if "chat_titles" not in st.session_state:
                st.session_state["chat_titles"] = {}
            st.session_state["chat_titles"][thread_id] = title
            return title
    
    # Fallback to thread ID if no messages found
    return f"Chat {thread_id[:8]}..."

def load_conversation(thread_id):
    try:
        state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
        # Check if messages key exists in state values, return empty list if not
        return state.values.get("messages", [])
    except Exception as e:
        st.error(f"Error loading conversation: {e}")
        return []

# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "chat_titles" not in st.session_state:
    st.session_state["chat_titles"] = {}

add_thread(st.session_state["thread_id"])

# ============================ Sidebar ============================
st.sidebar.title("🤖 LangGraph Chatbot")

if st.sidebar.button("➕ New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

st.sidebar.divider()
st.sidebar.header("💬 My Conversations")

if st.session_state["chat_threads"]:
    for thread_id in st.session_state["chat_threads"][::-1]:
        # Get meaningful chat title
        chat_title = get_chat_title(thread_id)
        
        if st.sidebar.button(
            chat_title,
            key=thread_id,
            type="primary" if thread_id == st.session_state["thread_id"] else "secondary",
            use_container_width=True
        ):
            st.session_state["thread_id"] = thread_id
            messages = load_conversation(thread_id)

            temp_messages = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    temp_messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage) and msg.content:
                    temp_messages.append({"role": "assistant", "content": msg.content})
            
            st.session_state["message_history"] = temp_messages
            st.rerun()
else:
    st.sidebar.info("No conversations yet. Start chatting!")

# ============================ Main UI ============================

# Render history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user's message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    # Assistant streaming block
    with st.chat_message("assistant"):
        status_holder = {"box": None}

        def ai_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Handle tool execution status
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "unknown_tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Running tool: `{tool_name}`", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Running tool: `{tool_name}`",
                            state="running",
                            expanded=True,
                        )
                    
                    # Show tool output in status box
                    with status_holder["box"]:
                        st.caption(f"Tool: {tool_name}")
                        try:
                            # Try to display as JSON if possible
                            import json
                            if isinstance(message_chunk.content, str):
                                json_content = json.loads(message_chunk.content)
                                st.json(json_content)
                            else:
                                st.json(message_chunk.content)
                        except (json.JSONDecodeError, TypeError):
                            # If not JSON, display as text
                            st.text(message_chunk.content if message_chunk.content else "Processing...")

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage) and message_chunk.content:
                    yield message_chunk.content

        # Stream and display - st.write_stream returns the full concatenated string
        ai_message = st.write_stream(ai_stream())

        # Finalize tool status if used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tools completed", state="complete", expanded=False
            )

    # Save assistant message to history
    if ai_message:
        st.session_state["message_history"].append(
            {"role": "assistant", "content": ai_message}
        )
    else:
        # Fallback if no content streamed
        st.session_state["message_history"].append(
            {"role": "assistant", "content": "I apologize, but I couldn't generate a response."}
        )
    
    # Update chat title with first user message
    thread_id = st.session_state["thread_id"]
    if thread_id not in st.session_state["chat_titles"]:
        title = user_input[:40] + ("..." if len(user_input) > 40 else "")
        st.session_state["chat_titles"][thread_id] = title