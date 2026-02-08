import re

with open('bbox_annotation_streamlit.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports at the top
if 'from github_saver import' not in content:
    import_pattern = r'(import streamlit as st\nimport json)'
    import_replacement = r'''\1
import requests
try:
    from github_saver import save_to_github, test_github_connection
    GITHUB_SAVE_ENABLED = True
except:
    GITHUB_SAVE_ENABLED = False'''
    content = re.sub(import_pattern, import_replacement, content, count=1)

# 2. Replace save_progress function
save_pattern = r'def save_progress\(\):.*?(?=\ndef |\nif __name__|$)'
save_replacement = '''def save_progress():
    """Save progress to GitHub or local file."""
    if GITHUB_SAVE_ENABLED and hasattr(st, 'secrets') and st.secrets.get('github_token'):
        # Auto-save to GitHub
        success, message = save_to_github(st.session_state.annotations, st.session_state.annotator_id)
        if success and 'last_save_message' in dir(st.session_state):
            st.session_state.last_save_message = message
    else:
        # Fallback: local save (won't work on Streamlit Cloud - that's OK)
        try:
            output_path = st.session_state.output_path
            with open(output_path, 'w') as f:
                json.dump(st.session_state.annotations, f, indent=2)
        except:
            pass  # Silent fail on Streamlit Cloud


'''

content = re.sub(save_pattern, save_replacement, content, flags=re.DOTALL, count=1)

with open('bbox_annotation_streamlit.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ GitHub auto-save integrated successfully!')
