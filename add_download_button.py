import re

with open('bbox_annotation_streamlit.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the progress section and add download button after it
pattern = r'(st\.sidebar\.metric\("Remaining", remaining\))'
replacement = r'''\1
    
    # Download button
    if len(st.session_state.annotations) > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💾 Save Annotations")
        annotations_json = json.dumps(st.session_state.annotations, indent=2)
        st.sidebar.download_button(
            label=f"⬇️ Download {len(st.session_state.annotations)} Annotations",
            data=annotations_json,
            file_name=f"annotations_{st.session_state.annotator_id}.json",
            mime="application/json",
            use_container_width=True
        )
        st.sidebar.info("💡 Click to save your work! Download frequently.")'''

content = re.sub(pattern, replacement, content, count=1)

with open('bbox_annotation_streamlit.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Download button added successfully')
