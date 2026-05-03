import re

with open("ui_components.py", "r", encoding="utf-8") as f:
    content = f.read()

helper = """

def safe_html(html_str: str):
    # Remove all leading whitespace from every line so Streamlit doesn't render it as a markdown code block
    cleaned = "\\n".join(line.lstrip() for line in html_str.split("\\n"))
    st.markdown(cleaned, unsafe_allow_html=True)

"""

# Inject helper right after imports
content = content.replace("import streamlit as st\n", "import streamlit as st\n" + helper)

# Replace st.markdown calls
content = content.replace("st.markdown(f\"\"\"", "safe_html(f\"\"\"")
content = content.replace("st.markdown(\"\"\"", "safe_html(\"\"\"")

# Fix the trailing arguments
content = content.replace('""", unsafe_allow_html=True)', '""")')

with open("ui_components.py", "w", encoding="utf-8") as f:
    f.write(content)

print("ui_components.py patched successfully.")
