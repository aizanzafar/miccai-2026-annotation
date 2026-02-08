import re
import json

with open('bbox_annotation_streamlit.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add download button before the guidelines button
pattern = r'(if st\.button\("❓ Show Guidelines"\):)'
replacement = r'''# Download annotations button
        if len(st.session_state.annotations) > 0:
            st.markdown("---")
            st.markdown("### 💾 Save Progress")
            annotations_json = json.dumps(st.session_state.annotations, indent=2)
            st.download_button(
                label=f"⬇️ Download {len(st.session_state.annotations)} Annotations",
                data=annotations_json,
                file_name=f"annotations_{st.session_state.annotator_id}.json",
                mime="application/json",
                use_container_width=True
            )
            st.info("💡 Download frequently to save your progress!")
        
        \1'''

if re.search(pattern, content):
    content = re.sub(pattern, replacement, content)
    with open('bbox_annotation_streamlit.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Download button added successfully!')
else:
    print('❌ Pattern not found - checking file structure...')
    # Search for alternative patterns
    if 'Show Guidelines' in content:
        print('Found "Show Guidelines" button')
    if 'st.sidebar' in content:
        print('Found sidebar usage')
