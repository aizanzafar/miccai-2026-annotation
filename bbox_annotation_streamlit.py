#!/usr/bin/env python3
"""
Phase 2 Bbox Annotation Interface - Streamlit Web Version
MICCAI 2026 - MedVeriGround Pilot Dataset

Web-based interface for remote annotators (especially medical professionals).
Polished UI with interactive bbox editing, progress tracking, and auto-save.

Usage:
    streamlit run bbox_annotation_streamlit.py -- --proposals bbox_proposals_qwen_v1.json --images pilot_dataset/ --annotator [YOUR_ID]
"""

import streamlit as st
import json
import requests
try:
    from github_saver import save_to_github, test_github_connection
    GITHUB_SAVE_ENABLED = True
except:
    GITHUB_SAVE_ENABLED = False
import cv2
import numpy as np
from pathlib import Path
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

# Page config
st.set_page_config(
    page_title="Phase 2 Bbox Annotation",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .decision-button {
        margin: 0.5rem;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.authenticated = False  # Simple password protection
        st.session_state.data = None
        st.session_state.annotations = []
        st.session_state.current_idx = 0
        st.session_state.current_evid_idx = 0
        st.session_state.bbox = None
        st.session_state.original_bbox = None
        st.session_state.annotation_start_time = None
        st.session_state.flagged = False
        st.session_state.adjusting = False
        st.session_state.annotator_id = None


def load_data(proposals_path, images_dir, annotator_id):
    """Load proposals and existing annotations."""
    with open(proposals_path, 'r') as f:
        data = json.load(f)
    
    images_dir = Path(images_dir)
    
    # Check for existing annotations
    output_path = f"annotations_{annotator_id}.json"
    annotations = []
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            annotations = json.load(f)
    
    return data, annotations, images_dir, output_path


def denormalize_bbox(bbox, img_shape):
    """Convert normalized [x_c, y_c, w, h] to pixel [x1, y1, x2, y2]."""
    if bbox == "NO_VISIBLE_GROUNDING" or bbox is None:
        return None
    
    h, w = img_shape[:2]
    x_c, y_c, box_w, box_h = bbox
    
    x1 = int((x_c - box_w/2) * w)
    y1 = int((y_c - box_h/2) * h)
    x2 = int((x_c + box_w/2) * w)
    y2 = int((y_c + box_h/2) * h)
    
    return [x1, y1, x2, y2]


def normalize_bbox(bbox, img_shape):
    """Convert pixel [x1, y1, x2, y2] to normalized [x_c, y_c, w, h]."""
    h, w = img_shape[:2]
    x1, y1, x2, y2 = bbox
    
    x_c = ((x1 + x2) / 2) / w
    y_c = ((y1 + y2) / 2) / h
    box_w = (x2 - x1) / w
    box_h = (y2 - y1) / h
    
    # Clamp to [0, 1]
    x_c = max(0, min(1, x_c))
    y_c = max(0, min(1, y_c))
    box_w = max(0, min(1, box_w))
    box_h = max(0, min(1, box_h))
    
    return [x_c, y_c, box_w, box_h]


def draw_bbox_on_image(image_path, bbox, adjusted=False):
    """Draw bbox on image and return PIL Image."""
    # Load image
    img = Image.open(image_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    if bbox and bbox != "NO_VISIBLE_GROUNDING":
        x1, y1, x2, y2 = bbox
        
        # Choose color
        color = (255, 165, 0) if adjusted else (0, 255, 0)  # Orange if adjusted, Green if original
        
        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        
        # Draw corner handles
        handle_size = 8
        for px, py in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
            draw.ellipse([px-handle_size, py-handle_size, px+handle_size, py+handle_size], 
                        fill=color, outline='white')
    
    return img


def save_annotation(example, evid, decision, final_bbox, rejection_reason=None):
    """Save annotation to session state."""
    # Determine adjustment type
    adjustment_type = 'none'
    if decision == 'adjust':
        adjustment_type = 'both'  # Simplified
    
    # Determine grounding tier
    if final_bbox == 'NO_VISIBLE_GROUNDING':
        tier = 'tier3_no_grounding'
    elif final_bbox is None:
        tier = 'rejected'
    else:
        area = final_bbox[2] * final_bbox[3]
        tier = 'tier1_tight' if area < 0.3 else 'tier2_anatomical'
    
    # Create annotation entry
    annotation = {
        'example_id': example['id'],
        'evid_index': st.session_state.current_evid_idx,
        'evid_phrase': evid.get('evid_phrase', 'N/A'),
        'original_evid': evid.get('original_evid', 'N/A'),
        'proposed_bbox': evid.get('bbox', 'NO_VISIBLE_GROUNDING'),
        'final_bbox': final_bbox,
        'decision': decision,
        'adjustment_type': adjustment_type,
        'rejection_reason': rejection_reason,
        'grounding_tier': tier,
        'annotator_id': st.session_state.annotator_id,
        'annotation_time': datetime.now().isoformat(),
        'time_spent': round(time.time() - st.session_state.annotation_start_time, 2),
        'confidence': None,
        'notes': 'FLAGGED' if st.session_state.flagged else None,
        'question': example.get('question', 'N/A'),
        'answer': example.get('answer', 'N/A')
    }
    
    st.session_state.annotations.append(annotation)
    
    # Auto-save
    save_progress()


def save_progress():
    """Save progress to GitHub or local file."""
    if GITHUB_SAVE_ENABLED and hasattr(st, 'secrets') and st.secrets.get('github_token'):
        # First, load existing annotations from GitHub
        try:
            from github_saver import load_from_github
            existing = load_from_github(st.session_state.annotator_id)
            if existing:
                # Merge: keep existing + add new ones not in existing
                existing_ids = {(a['example_id'], a['evid_index']) for a in existing}
                new_annotations = [a for a in st.session_state.annotations 
                                 if (a['example_id'], a['evid_index']) not in existing_ids]
                all_annotations = existing + new_annotations
            else:
                all_annotations = st.session_state.annotations
        except:
            all_annotations = st.session_state.annotations
        
        # Auto-save to GitHub with merged list
        success, message = save_to_github(all_annotations, st.session_state.annotator_id)
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



def next_evid():
    """Move to next EVID or example."""
    example = st.session_state.data[st.session_state.current_idx]
    
    # Check if more EVIDs in current example
    if st.session_state.current_evid_idx + 1 < len(example['evid_proposals']):
        st.session_state.current_evid_idx += 1
        load_current_evid()
    else:
        # Move to next example
        if st.session_state.current_idx + 1 < len(st.session_state.data):
            st.session_state.current_idx += 1
            st.session_state.current_evid_idx = 0
            st.session_state.flagged = False
            load_current_evid()
        else:
            st.success("🎉 All examples completed!")
            st.balloons()


def load_current_evid():
    """Load current EVID into session state."""
    example = st.session_state.data[st.session_state.current_idx]
    evid = example['evid_proposals'][st.session_state.current_evid_idx]
    
    # Load bbox
    proposed_bbox = evid.get('bbox', 'NO_VISIBLE_GROUNDING')
    if proposed_bbox != "NO_VISIBLE_GROUNDING":
        img_path = st.session_state.images_dir / example['image_path']
        img = Image.open(img_path)
        st.session_state.bbox = denormalize_bbox(proposed_bbox, (img.height, img.width, 3))
        st.session_state.original_bbox = st.session_state.bbox.copy() if st.session_state.bbox else None
    else:
        st.session_state.bbox = "NO_VISIBLE_GROUNDING"
        st.session_state.original_bbox = "NO_VISIBLE_GROUNDING"
    
    st.session_state.annotation_start_time = time.time()
    st.session_state.adjusting = False


def main():
    """Main Streamlit app."""
    initialize_session_state()
    
    # Simple password protection (optional - uncomment to enable)
    # PASSWORD = "miccai2026"  # Change this!
    # if not st.session_state.authenticated:
    #     st.markdown('<div class="main-header">🔒 Authentication Required</div>', unsafe_allow_html=True)
    #     password = st.text_input("Enter password", type="password")
    #     if st.button("Login"):
    #         if password == PASSWORD:
    #             st.session_state.authenticated = True
    #             st.rerun()
    #         else:
    #             st.error("Incorrect password")
    #     return
    
    # Sidebar - Configuration
    with st.sidebar:
        st.markdown('<div class="main-header">🔬 Bbox Annotation</div>', unsafe_allow_html=True)
        
        if not st.session_state.initialized:
            st.markdown("### 📋 Setup")
            
            proposals_path = st.text_input(
                "Proposals JSON Path",
                value="bbox_proposals_qwen_v1.json",
                help="Path to bbox_proposals_qwen_v1.json"
            )
            
            images_dir = st.text_input(
                "Images Directory",
                value="images/",
                help="Path to images folder"
            )
            
            annotator_id = st.text_input(
                "Annotator ID",
                placeholder="e.g., dr_smith",
                help="Your unique identifier"
            )
            
            if st.button("🚀 Start Annotation", type="primary"):
                if not annotator_id:
                    st.error("Please enter an Annotator ID")
                elif not os.path.exists(proposals_path):
                    st.error(f"Proposals file not found: {proposals_path}")
                elif not os.path.exists(images_dir):
                    st.error(f"Images directory not found: {images_dir}")
                else:
                    with st.spinner("Loading data..."):
                        data, annotations, images_dir_path, output_path = load_data(
                            proposals_path, images_dir, annotator_id
                        )
                        
                        st.session_state.data = data
                        st.session_state.annotations = annotations
                        st.session_state.images_dir = images_dir_path
                        st.session_state.output_path = output_path
                        st.session_state.annotator_id = annotator_id
                        st.session_state.current_idx = len(annotations)  # Resume
                        st.session_state.initialized = True
                        
                        # Load first unannotated example
                        if st.session_state.current_idx < len(data):
                            load_current_evid()
                        
                        st.rerun()
        
        else:
            # Progress tracking
            st.markdown("### 📊 Progress")
            total_evids = sum(len(ex['evid_proposals']) for ex in st.session_state.data)
            progress = len(st.session_state.annotations) / total_evids
            st.progress(progress)
            st.metric("Annotations", f"{len(st.session_state.annotations)}/{total_evids}")
            st.metric("Examples", f"{st.session_state.current_idx + 1}/{len(st.session_state.data)}")
            
            # Current example info
            st.markdown("---")
            st.markdown("### 📍 Current")
            example = st.session_state.data[st.session_state.current_idx]
            evid = example['evid_proposals'][st.session_state.current_evid_idx]
            
            st.markdown(f"**Example ID:** `{example['id']}`")
            st.markdown(f"**EVID:** {st.session_state.current_evid_idx + 1}/{len(example['evid_proposals'])}")
            st.markdown(f"**Dataset:** {example.get('dataset', 'N/A')}")
            st.markdown(f"**Complexity:** {example.get('proxy_complexity', 'N/A')}")
            
            # Flag toggle
            st.markdown("---")
            st.session_state.flagged = st.checkbox("🚩 Flag for Review", value=st.session_state.flagged)
            
            # Statistics
            st.markdown("---")
            st.markdown("### 📈 Session Stats")
            if st.session_state.annotations:
                decisions = [a['decision'] for a in st.session_state.annotations]
                st.metric("Accept", decisions.count('accept'))
                st.metric("Adjust", decisions.count('adjust'))
                st.metric("Reject", decisions.count('reject'))
                st.metric("No Grounding", decisions.count('no_grounding'))
            
            # Help
            st.markdown("---")
            # Download annotations button
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
        
        if st.button("❓ Show Guidelines"):
                st.session_state.show_help = True
    
    # Main area
    if not st.session_state.initialized:
        st.markdown('<div class="main-header">Phase 2 Bbox Verification</div>', unsafe_allow_html=True)
        st.markdown("""
        ### Welcome to the Bbox Annotation Interface! 👋
        
        This web-based tool allows you to verify and adjust bounding boxes for medical VQA evidence phrases.
        
        **Steps to get started:**
        1. Enter your **Annotator ID** in the sidebar
        2. Verify the **Proposals JSON** and **Images Directory** paths
        3. Click **Start Annotation** to begin
        
        **Features:**
        - ✅ Interactive bbox adjustment with sliders
        - 💾 Auto-save every annotation
        - 📊 Progress tracking
        - 🔄 Resume from where you left off
        - 🚩 Flag examples for review
        """)
        return
    
    # Check if completed
    if st.session_state.current_idx >= len(st.session_state.data):
        st.success("🎉 All examples completed!")
        st.markdown(f"**Total annotations:** {len(st.session_state.annotations)}")
        st.markdown(f"**Output file:** `{st.session_state.output_path}`")
        st.balloons()
        return
    
    # Current example
    example = st.session_state.data[st.session_state.current_idx]
    evid = example['evid_proposals'][st.session_state.current_evid_idx]
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="main-header">Example {st.session_state.current_idx + 1} / {len(st.session_state.data)}</div>', unsafe_allow_html=True)
    with col2:
        if st.session_state.flagged:
            st.warning("🚩 FLAGGED")
    
    # Question and Answer
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(f"**Question:** {example.get('question', 'N/A')}")
    st.markdown(f"**Answer:** {example.get('answer', 'N/A')}")
    st.markdown(f"**EVID Phrase:** \"{evid.get('evid_phrase', 'N/A')}\"")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Image and bbox
    img_path = st.session_state.images_dir / example['image_path']
    
    if not img_path.exists():
        st.error(f"Image not found: {img_path}")
        return
    
    # Display image with bbox
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🖼️ Image with Bbox")
        
        if st.session_state.bbox == "NO_VISIBLE_GROUNDING":
            # Just show image without bbox
            st.image(str(img_path), use_container_width=True)
            st.info("**NO_VISIBLE_GROUNDING** - No bbox proposed")
        else:
            # Draw bbox on image
            adjusted = (st.session_state.bbox != st.session_state.original_bbox)
            img_with_bbox = draw_bbox_on_image(img_path, st.session_state.bbox, adjusted)
            st.image(img_with_bbox, use_container_width=True)
            
            # Color legend
            if adjusted:
                st.markdown("🟠 **Orange**: Adjusted bbox | 🟢 **Green**: Original bbox")
            else:
                st.markdown("🟢 **Green**: Proposed bbox")
    
    with col2:
        st.markdown("### ⚙️ Bbox Adjustment")
        
        if st.session_state.bbox != "NO_VISIBLE_GROUNDING" and st.session_state.bbox is not None:
            # Load image dimensions
            img = Image.open(img_path)
            img_w, img_h = img.size
            
            # Adjustment mode
            adjust_mode = st.radio("Adjustment Mode", ["Move", "Resize"], key="adjust_mode")
            
            x1, y1, x2, y2 = st.session_state.bbox
            
            if adjust_mode == "Move":
                st.markdown("**Move Bbox**")
                # Calculate valid ranges (ensure min < max)
                bbox_w = x2 - x1
                bbox_h = y2 - y1
                max_x = img_w - bbox_w
                max_y = img_h - bbox_h
                
                # Check if bbox can be moved
                if max_x > 0 and max_y > 0:
                    new_x1 = st.slider("X Position", 0, max_x, min(x1, max_x), key="move_x")
                    new_y1 = st.slider("Y Position", 0, max_y, min(y1, max_y), key="move_y")
                    
                    if new_x1 != x1 or new_y1 != y1:
                        dx = new_x1 - x1
                        dy = new_y1 - y1
                        st.session_state.bbox = [x1 + dx, y1 + dy, x2 + dx, y2 + dy]
                        st.rerun()
                else:
                    st.info(" Bbox is full width/height - cannot move. Use Resize instead.")
                    st.rerun()
            
            else:  # Resize
                st.markdown("**Resize Bbox**")
                # Calculate valid ranges (min 10px bbox size)
                max_left_x = max(0, x2 - 10)
                max_top_y = max(0, y2 - 10)
                min_right_x = min(img_w, x1 + 10)
                min_bottom_y = min(img_h, y1 + 10)
                
                # Only show sliders if valid ranges exist
                if max_left_x >= 0:
                    new_x1 = st.slider("Left X", 0, max_left_x, min(x1, max_left_x), key="resize_x1")
                else:
                    new_x1 = x1
                    
                if max_top_y >= 0:
                    new_y1 = st.slider("Top Y", 0, max_top_y, min(y1, max_top_y), key="resize_y1")
                else:
                    new_y1 = y1
                    
                if min_right_x <= img_w:
                    new_x2 = st.slider("Right X", min_right_x, img_w, max(x2, min_right_x), key="resize_x2")
                else:
                    new_x2 = x2
                    
                if min_bottom_y <= img_h:
                    new_y2 = st.slider("Bottom Y", min_bottom_y, img_h, max(y2, min_bottom_y), key="resize_y2")
                else:
                    new_y2 = y2
                
                if [new_x1, new_y1, new_x2, new_y2] != [x1, y1, x2, y2]:
                    st.session_state.bbox = [new_x1, new_y1, new_x2, new_y2]
                    st.rerun()
            
            # Reset button
            if st.button("🔄 Reset to Original"):
                st.session_state.bbox = st.session_state.original_bbox.copy()
                st.rerun()
        
        else:
            st.info("No bbox to adjust (NO_VISIBLE_GROUNDING)")
    
    # Decision buttons
    st.markdown("---")
    st.markdown("### ✅ Decision")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Accept", type="primary", use_container_width=True):
            # Determine if adjusted
            decision = 'adjust' if st.session_state.bbox != st.session_state.original_bbox else 'accept'
            
            # Normalize bbox
            if st.session_state.bbox != "NO_VISIBLE_GROUNDING":
                img = Image.open(img_path)
                final_bbox = normalize_bbox(st.session_state.bbox, (img.height, img.width, 3))
            else:
                final_bbox = "NO_VISIBLE_GROUNDING"
            
            save_annotation(example, evid, decision, final_bbox)
            next_evid()
            st.rerun()
    
    with col2:
        if st.button("❌ Reject", use_container_width=True):
            st.session_state.show_reject_dialog = True
    
    with col3:
        if st.button("🚫 No Grounding", use_container_width=True):
            save_annotation(example, evid, 'no_grounding', 'NO_VISIBLE_GROUNDING')
            next_evid()
            st.rerun()
    
    with col4:
        if st.button("⏭️ Skip (Temp)", use_container_width=True):
            next_evid()
            st.rerun()
    
    # Reject dialog
    if st.session_state.get('show_reject_dialog', False):
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("### ❌ Rejection Reason")
        
        reason = st.selectbox(
            "Select reason",
            [
                "Wrong anatomy",
                "Wrong laterality",
                "Hallucinated finding",
                "Modality mismatch",
                "Phrase-image mismatch",
                "Other (specify below)"
            ]
        )
        
        if reason == "Other (specify below)":
            reason = st.text_input("Specify reason")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Reject", type="primary"):
                save_annotation(example, evid, 'reject', None, rejection_reason=reason)
                st.session_state.show_reject_dialog = False
                next_evid()
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.show_reject_dialog = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Guidelines modal
    if st.session_state.get('show_help', False):
        with st.expander("📖 Annotation Guidelines", expanded=True):
            st.markdown("""
            ### 3-Tier Grounding Policy
            
            **Tier 1 (Tight)**: Bbox tightly around finding (<20% padding)
            - Examples: "mass", "fracture", "nodule"
            
            **Tier 2 (Anatomical)**: Bbox on relevant region (NOT whole image)
            - Examples: "right hemithorax", "liver parenchyma"
            
            **Tier 3 (NO_VISIBLE_GROUNDING)**: No spatial grounding
            - Negations: "no fracture", "absent"
            - Abstract: "normal", "unremarkable"
            
            ### Key Rules
            
            ⚠️ **Negations → NO_VISIBLE_GROUNDING** (cannot box non-existent findings)
            
            ⚠️ **No whole-image boxes** (even for general findings)
            
            ⚠️ **Ambiguous phrases** → Use Question + Answer context
            
            ⚠️ **Adjust, don't reject** (if bbox is close, adjust it)
            
            ### Decision Actions
            
            - **Accept**: Bbox is correct (or adjusted and now correct)
            - **Reject**: Bbox is fundamentally wrong AND cannot be corrected
            - **No Grounding**: Should be NO_VISIBLE_GROUNDING (Tier 3)
            - **Skip**: Temporarily skip (NOT saved, use only for difficult cases)
            """)
            
            if st.button("Close Guidelines"):
                st.session_state.show_help = False
                st.rerun()


if __name__ == '__main__':
    main()
