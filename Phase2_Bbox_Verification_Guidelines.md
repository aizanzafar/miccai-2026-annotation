# Phase 2: Bbox Verification Guidelines
**MICCAI 2026 - MedVeriGround Pilot Dataset**  
**Date**: February 9, 2026  
**Task**: Verify and adjust bounding boxes for evidence phrases in medical VQA

---

## 📋 **OVERVIEW**

### **Your Task**
Review 145-170 medical images with **vision-model-proposed bounding boxes** for evidence phrases. For each bbox:
- ✅ **Accept** if correct
- 🔧 **Adjust** if nearly correct (drag to fix)
- ❌ **Reject** if completely wrong
- 🚫 **Mark as NO_VISIBLE_GROUNDING** if no valid spatial grounding exists

### **Why This Matters**
These bboxes will be used to:
1. Train verifiable medical VQA models
2. Establish gold standard for future research
3. Measure inter-annotator agreement (IAA)

### **Time Estimate**
~4-5 hours (1.5-2 minutes per example)

---

## 🎯 **3-TIER GROUNDING POLICY**

### **Tier 1: Tight Grounding** (Localizable Findings)
**Goal**: Bbox tightly around the finding with <20% padding

**Examples**:
- ✅ "mass" → Box around mass with minimal padding
- ✅ "left lung nodule" → Box around nodule in left lung
- ✅ "fracture" → Box tightly around fracture line
- ✅ "consolidation in right lower lobe" → Box around dense area

**Bad Examples**:
- ❌ "mass" → Box covers entire lung (too loose)
- ❌ "left lung" → Box only covers upper lobe (incomplete)

**Visual Example**:
```
GOOD (Tier 1):          BAD (Too Loose):        BAD (Too Tight):
┌────────────┐          ┌────────────┐          ┌────────────┐
│            │          │            │          │            │
│   ┌──┐     │          │ ┌────────┐ │          │    ●       │
│   │●│     │          │ │   ●    │ │          │            │
│   └──┘     │          │ └────────┘ │          │            │
│            │          │            │          │            │
└────────────┘          └────────────┘          └────────────┘
Tight + padding         Covers too much         Missing context
```

---

### **Tier 2: Anatomical Region** (General Findings)
**Goal**: Bbox on anatomically relevant region (NOT whole image)

**When to use**:
- Phrase describes large anatomical region ("right hemithorax")
- Finding is diffuse/distributed ("bilateral infiltrates")
- Phrase is anatomical reference ("upper abdomen")

**Examples**:
- ✅ "right hemithorax" → Box covering right half of chest
- ✅ "bilateral infiltrates" → Box covering both lungs
- ✅ "cardiomegaly" → Box around heart shadow
- ✅ "liver parenchyma" → Box covering liver region

**Bad Examples**:
- ❌ "right hemithorax" → Box covers entire image
- ❌ "bilateral infiltrates" → Box only on left lung

**Critical Rule**: Even for general findings, **NEVER** box the entire image. Find the anatomically relevant subregion.

---

### **Tier 3: NO_VISIBLE_GROUNDING** (Non-Spatial Concepts)
**Goal**: Mark as `NO_VISIBLE_GROUNDING` if no valid bbox exists

⚠️ **IMPORTANT**:  
**NO_VISIBLE_GROUNDING is a VALID and DESIRED outcome.**  
It indicates that the evidence phrase does not correspond to a spatially localizable region.  
**Marking NO_VISIBLE_GROUNDING is NOT a failure** and should be used confidently when appropriate.

**When to use**:
- ❌ Negation: answer = "no" / "absent" / "negative" (e.g., "no fracture")
- ❌ Abstract concepts: "normal", "unremarkable", "stable"
- ❌ Counts/quantities: "two lesions" (count, not location)
- ❌ Comparisons: "larger than previous"
- ❌ Technical descriptors: "CT scan", "axial view"

**Examples**:
- 🚫 "no fracture" → NO_VISIBLE_GROUNDING (nothing to box)
- 🚫 "normal chest radiograph" → NO_VISIBLE_GROUNDING (abstract)
- 🚫 "three nodules" → NO_VISIBLE_GROUNDING (count, not grounding)
- ✅ "fracture" → Box around fracture (positive finding, Tier 1)

**Critical Rule**: If the answer says "no"/"absent"/"negative", the evidence phrase should have NO_VISIBLE_GROUNDING (you cannot box something that isn't there).

---

## 🖱️ **ANNOTATION INTERFACE**

### **Screen Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ Example 15/145                   [Progress: 10%]            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────┐                   │
│  │                                     │  Question:         │
│  │       Medical Image                 │  "Where is the     │
│  │                                     │   abnormality?"    │
│  │         ┌──────┐                    │                    │
│  │         │ bbox │ <- Green (proposed)│  Answer:           │
│  │         └──────┘                    │  "Right upper lobe"│
│  │                                     │                    │
│  └─────────────────────────────────────┘  EVID phrase:     │
│                                           "Right"           │
│                                                             │
│  [A] Accept  [Drag] Adjust  [R] Reject  [N] No Grounding   │
└─────────────────────────────────────────────────────────────┘
```

### **Keyboard Shortcuts**

| Key | Action | When to Use |
|-----|--------|-------------|
| **A** | Accept | Bbox is correct (Tier 1 or Tier 2) |
| **Click & Drag** | Adjust | Bbox is close but needs repositioning/resizing |
| **R** | Reject | Bbox is fundamentally wrong AND cannot be corrected (see below) |
| **N** | No Grounding | Should be NO_VISIBLE_GROUNDING (Tier 3) |

#### ❌ **Reject (When to Use)**

Use **Reject** only when:
- The proposed bbox is **fundamentally wrong** AND
- The correct grounding **cannot be inferred with confidence**

**Reject does NOT mean**:
- The example is invalid
- The phrase has no grounding (use **NO_VISIBLE_GROUNDING** for that)
- The bbox is slightly misplaced (use **Adjust** instead)

**When rejecting, you MUST choose a reason**:
- ❌ **Wrong anatomy** (e.g., boxes liver when phrase is "spleen")
- ❌ **Wrong laterality** (e.g., boxes left when phrase is "right")
- ❌ **Hallucinated finding** (boxes something not present)
- ❌ **Modality mismatch** (boxes wrong anatomical plane)
- ❌ **Phrase-image mismatch** (phrase doesn't correspond to anything visible)

**Guideline**: If you can adjust the bbox to make it correct → **Adjust, don't Reject**
| **←/→** | Navigate | Previous/Next example (after decision) |
| **?** | Help | Show this guide |
| **S** | Save | Save progress (auto-saves every 10 examples) |

### **Adjustment Mode**
When adjusting:
1. **Move**: Click inside bbox and drag
2. **Resize**: Click corners/edges and drag
3. **Confirm**: Press **A** when satisfied
4. **Cancel**: Press **Esc** to revert

### **Tier Adjustment Rule**

Annotators **may change the grounding tier** if required:
- **Tier 1 → Tier 2**: If tight localization is not justified (e.g., bbox must expand to anatomical region)
- **Tier 1/2 → Tier 3**: If no spatial grounding exists (e.g., discovered to be negation/abstract)
- **Tier 3 → Tier 1/2**: If you determine a valid bbox exists (override model sentinel)

**Any tier change will be logged automatically.**

Example: Vision model proposed tiny Tier-1 box for "Right hemithorax" → You expand to full right chest → Tier becomes Tier-2 (anatomical)

---

## ✅ **DECISION TREE**

```
Start
  │
  ├─→ Is answer "no"/"absent"/"negative"?
  │     └─→ YES → Press [N] (NO_VISIBLE_GROUNDING)
  │     └─→ NO → Continue
  │
  ├─→ Is phrase abstract/count/comparison?
  │     └─→ YES → Press [N] (NO_VISIBLE_GROUNDING)
  │     └─→ NO → Continue
  │
  ├─→ Is bbox tightly around finding (<20% padding)?
  │     └─→ YES → Press [A] (Accept as Tier 1)
  │     └─→ NO → Continue
  │
  ├─→ Is bbox on anatomical region (not whole image)?
  │     └─→ YES, correct → Press [A] (Accept as Tier 2)
  │     └─→ YES, but wrong region → Drag to adjust
  │     └─→ NO (covers whole image) → Press [R] (Reject)
  │
  └─→ Is bbox completely wrong location?
        └─→ YES → Press [R] (Reject, will prompt reason)
```

---

## 📊 **EXAMPLES WITH DECISIONS**

### **Example 1: Clear Accept (Tier 1)**
- **Question**: "What is the abnormality?"
- **Answer**: "Mass in left lung"
- **EVID phrase**: "Mass"
- **Proposed bbox**: Green box tightly around mass in left lung
- **Decision**: ✅ **Press [A]** (Tier 1, correct tight grounding)

---

### **Example 2: Needs Adjustment**
- **Question**: "Where is the fracture?"
- **Answer**: "Midshaft of femur"
- **EVID phrase**: "Midshaft of femur"
- **Proposed bbox**: Box on distal femur (wrong location)
- **Decision**: 🔧 **Drag bbox** to midshaft, then **Press [A]**

---

### **Example 3: Reject - Whole Image**
- **Question**: "What organ is affected?"
- **Answer**: "Liver"
- **EVID phrase**: "Liver"
- **Proposed bbox**: Covers entire CT scan (85%+ of image)
- **Decision**: ❌ **Press [R]** → Reason: "Covers whole image, should box liver region only"

---

### **Example 4: NO_VISIBLE_GROUNDING (Negation)**
- **Question**: "Is there a fracture?"
- **Answer**: "No"
- **EVID phrase**: "No fracture"
- **Proposed bbox**: Green box somewhere (incorrect - vision model over-grounded)
- **Decision**: 🚫 **Press [N]** (Negation - cannot box non-existent finding)

---

### **Example 5: NO_VISIBLE_GROUNDING (Abstract)**
- **Question**: "What is the diagnosis?"
- **Answer**: "Normal chest X-ray"
- **EVID phrase**: "Normal"
- **Proposed bbox**: Green box on lung (incorrect)
- **Decision**: 🚫 **Press [N]** (Abstract concept, no specific finding)

---

### **Example 6: Accept (Tier 2 - Anatomical)**
- **Question**: "Where is the abnormality?"
- **Answer**: "Right hemithorax"
- **EVID phrase**: "Right hemithorax"
- **Proposed bbox**: Box covering right half of chest (40% of image)
- **Decision**: ✅ **Press [A]** (Tier 2, correct anatomical region)

---

### **Example 7: Adjust - Too Tight**
- **Question**: "What is shown?"
- **Answer**: "Pneumothorax in left lung"
- **EVID phrase**: "Pneumothorax"
- **Proposed bbox**: Tiny box on one edge (missing full extent)
- **Decision**: 🔧 **Drag corners** to cover full pneumothorax area, then **Press [A]**

---

### **Example 8: Reject - Wrong Anatomy**
- **Question**: "Where is the lesion?"
- **Answer**: "Right kidney"
- **EVID phrase**: "Right kidney"
- **Proposed bbox**: Box on left kidney (laterality error)
- **Decision**: ❌ **Press [R]** → Reason: "Wrong laterality (left vs right)"

---

## ⚠️ **COMMON PITFALLS**

### **1. Don't Accept Whole-Image Boxes**
❌ **Wrong**: Box covers 80%+ of image for specific finding  
✅ **Right**: Box covers anatomically relevant subregion

### **2. Don't Box Negations**
❌ **Wrong**: "No fracture" → Box on bone  
✅ **Right**: "No fracture" → NO_VISIBLE_GROUNDING

### **3. Don't Be Too Tight**
❌ **Wrong**: "Mass" → Box exactly on mass border (0% padding)  
✅ **Right**: "Mass" → Box with 10-20% padding for context

### **4. Don't Be Too Loose**
❌ **Wrong**: "Nodule" → Box covers entire lung lobe  
✅ **Right**: "Nodule" → Box tightly around nodule

### **5. Check Laterality**
⚠️ **Critical**: "Right lung" ≠ "Left lung"  
Always verify left/right matches the phrase

---

## 📝 **QUALITY CRITERIA**

Your annotations will be evaluated on:

1. **Accuracy** (70%+ acceptance rate target)
   - Correct tier classification
   - Appropriate bbox size and location
   - Proper NO_VISIBLE_GROUNDING usage

2. **Consistency** (Inter-Annotator Agreement)
   - 30 examples will be annotated by both annotators
   - Target: Mean IoU ≥0.70, Median ≥0.75

3. **Reasoning Quality**
   - Clear rejection reasons (if applicable)
   - Documented edge cases

---

## 🔍 **EDGE CASES & FAQ**

### **Q1: Phrase is ambiguous (e.g., "Right" alone)**

**⚠️ CRITICAL RULE - Ambiguous Directional Phrases**

If the EVID phrase is **directional only** (e.g., "Right", "Left", "Posterior", "Midline"):

1. **Use Question + Answer to infer the anatomical referent**
   - Example: phrase="Right", answer="Right upper lobe" → Box the right upper lobe region
2. **If a clear referent exists → Box the anatomical region (Tier 2)**
   - Treat as anatomical grounding, not tight localization
3. **If no clear referent exists → Flag for review (do NOT guess)**
   - Press **?** → **Flag** with note "Ambiguous referent"

**Do NOT**:
- ❌ Reject ambiguous phrases (they may be valid with context)
- ❌ Guess aggressively without Question/Answer support
- ❌ Mark as NO_VISIBLE_GROUNDING if an anatomical region can be inferred

### **Q2: Multiple findings for one phrase (e.g., "bilateral infiltrates")**
**A**: Box the region that covers BOTH findings.
- Don't create multiple boxes (interface only supports 1 bbox per phrase)
- Box should encompass the anatomically relevant area

### **Q3: Bbox is 90% correct, needs tiny adjustment**
**A**: Still adjust it! Precision matters for IAA measurement.

### **Q4: Phrase is technical jargon I don't understand**
**A**: 
1. Read Question + Answer for context
2. Look for visual correlates in image
3. If still unclear, mark for **review** (press **?** → **Flag**)

### **Q5: Vision model proposed NO_VISIBLE_GROUNDING, but I think there should be a bbox**
**A**: You can override! 
- Press **Esc** to exit "no grounding" state
- Draw your own bbox
- System will log this as "human-overridden sentinel"

### **Q6: Proposed bbox is on wrong modality plane (e.g., axial vs sagittal)**
**A**: This shouldn't happen (single image per example), but if it does:
- Press **R** (Reject)
- Reason: "Wrong anatomical plane"

---

## 📊 **LOGGING & TRACKING**

Every decision is logged with **14 fields**:

1. `example_id`: Unique identifier
2. `evid_index`: Which EVID phrase (if multiple)
3. `evid_phrase`: Text of evidence phrase
4. `proposed_bbox`: Vision model's proposal
5. `final_bbox`: Your verified bbox (or NO_VISIBLE_GROUNDING)
6. `decision`: accept / adjust / reject / no_grounding
7. `adjustment_type`: none / position / size / both (if adjusted)
8. `rejection_reason`: Free text (if rejected)
9. `grounding_tier`: tier1_tight / tier2_anatomical / tier3_no_grounding
10. `annotator_id`: Your ID
11. `annotation_time`: Timestamp
12. `time_spent`: Seconds spent on this example
13. `confidence`: Your confidence (1-5 scale, optional)
14. `notes`: Free text (optional, for edge cases)

This rich logging enables:
- IAA calculation (IoU on overlap subset)
- Error analysis (common rejection reasons)
- Tier distribution validation

---

## 🎯 **SUCCESS METRICS**

### **Target Metrics** (Based on Phase 2 Generation Results):

| Metric | Target | Current (Vision Model) |
|--------|--------|------------------------|
| **Acceptance rate** | ≥70% | 99.6% valid (excellent start) |
| **NO_VISIBLE_GROUNDING** | 10-20% | 18.1% (healthy) |
| **Tier 1 ratio** | ≥60% | 70.1% (good quality) |
| **Mean IoU (IAA)** | ≥0.70 | TBD (your annotations) |
| **Median IoU (IAA)** | ≥0.75 | TBD (your annotations) |

### **Your Role**:
You're validating 99.6% valid proposals from a state-of-the-art vision model (Qwen2.5-VL-7B). Most should be **Accept** or minor **Adjust**. Focus energy on:
- Correcting laterality errors
- Fixing whole-image boxes
- Validating NO_VISIBLE_GROUNDING sentinels
- Ensuring tier consistency

---

## 📦 **MATERIALS PROVIDED**

1. **This guideline document** (Phase2_Bbox_Verification_Guidelines.md)
2. **Bbox proposals** (bbox_proposals_qwen_v1.json) - 200 examples
3. **Images** (pilot_dataset/ folder) - 200 medical images
4. **Annotation interface** (bbox_annotation_interface.py) - Python + OpenCV tool
5. **Example outputs** (for reference)

---

## 🚀 **GETTING STARTED**

### **Setup** (5 minutes):

1. **Install dependencies**:
   ```bash
   pip install opencv-python pillow numpy
   ```

2. **Run interface**:
   ```bash
   python bbox_annotation_interface.py \
     --proposals bbox_proposals_qwen_v1.json \
     --images pilot_dataset/ \
     --output annotations_[YOUR_NAME].json \
     --annotator [YOUR_ID]
   ```

3. **Start annotating**:
   - Interface will load first example
   - Press **?** anytime for help
   - Progress auto-saves every 10 examples

### **Tips for Efficiency**:

1. **Use keyboard shortcuts** (faster than mouse clicks)
2. **Trust the proposals** (99.6% valid - most need just Accept)
3. **Adjust, don't reject** (if bbox is close, drag to fix)
4. **Batch similar tasks** (e.g., do all negations first)
5. **Take breaks** (every 30-40 examples)

---

## 📞 **SUPPORT**

### **Questions during annotation**:
- **Technical issues**: Contact PI immediately
- **Medical terminology**: Use provided Answer field for context
- **Edge cases**: Flag for review (press **?** → **Flag**)

### **Expected challenges**:
- ~5-10 genuinely ambiguous cases (will discuss in review meeting)
- ~2-3 vision model hallucinations (reject with clear reason)
- ~15-20 negations (should be NO_VISIBLE_GROUNDING)

---

## ✅ **FINAL CHECKLIST**

Before starting:
- [ ] Read all 3 tier definitions
- [ ] Review all 8 examples
- [ ] Understand keyboard shortcuts
- [ ] Test interface on 2-3 examples
- [ ] Confirm output file path

During annotation:
- [ ] Check Question + Answer for context
- [ ] Verify laterality (left/right)
- [ ] Ensure no whole-image boxes
- [ ] Mark negations as NO_VISIBLE_GROUNDING
- [ ] Adjust before rejecting

After completion:
- [ ] Verify output file saved
- [ ] Check progress: 145-170 examples completed
- [ ] Note any flagged edge cases
- [ ] Submit annotations to PI

---

## 📊 **EXPECTED OUTCOMES**

After your verification:
1. **170 annotations** with verified bboxes
2. **30 overlap** with second annotator (IAA measurement)
3. **30 gold standard** (blind from-scratch annotations)
4. **High-quality dataset** for MICCAI 2026 paper

**Thank you for your rigorous work! Your annotations will advance medical AI verifiability research.**

---

**Document Version**: 1.0  
**Last Updated**: February 9, 2026  
**Contact**: [PI Email/Slack]  
**Estimated Time**: 4-5 hours (~1.5 min/example)
