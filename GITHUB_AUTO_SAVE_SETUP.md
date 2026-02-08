# 🔐 GitHub Auto-Save Setup Guide

## ✅ **Automatic Saving to GitHub**

Your Streamlit app is now configured to **automatically save annotations to GitHub** after every annotation decision. No manual downloads needed!

---

## 📋 **Setup Steps (5 minutes)**

### **Step 1: Create GitHub Personal Access Token**

1. Go to: **https://github.com/settings/tokens**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. **Token settings**:
   - **Note**: `Streamlit Annotation App`
   - **Expiration**: `90 days` (or custom)
   - **Select scopes**:
     - ✅ **repo** (Full control of private repositories)
       - ✅ repo:status
       - ✅ repo_deployment  
       - ✅ public_repo
       - ✅ repo:invite
       - ✅ security_events
4. Click **"Generate token"** at the bottom
5. **COPY THE TOKEN** (you won't see it again!)
   - It looks like: `ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

---

### **Step 2: Add Token to Streamlit Cloud**

1. Go to your Streamlit Cloud dashboard: **https://share.streamlit.io/**
2. Click on your app: **`miccai-2026-annotation`**
3. Click **⚙️ Settings** (three dots menu → "Settings")
4. Go to **"Secrets"** tab
5. Paste this configuration (replace `YOUR_TOKEN_HERE` with your actual token):

```toml
github_token = "ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
github_repo = "aizanzafar/miccai-2026-annotation"
github_branch = "main"
```

6. Click **"Save"**
7. **Restart the app** (Settings → Reboot app)

---

## ✨ **How It Works**

### **Automatic Saving**:
- ✅ Saves after **every annotation** (Accept, Reject, No Grounding)
- ✅ Saves to: `annotations/{annotator_id}.json`
- ✅ Commit message includes timestamp and count
- ✅ No action needed from annotator

### **File Location**:
- GitHub: `https://github.com/aizanzafar/miccai-2026-annotation/tree/main/annotations`
- Filename: `annotations/dr_lastname.json`

### **Monitoring Progress**:
```
Watch the annotations/ folder on GitHub:
https://github.com/aizanzafar/miccai-2026-annotation/tree/main/annotations
```

Every save creates a new commit - you can see real-time progress!

---

## 🔧 **Troubleshooting**

### **Problem 1: Token expired**
**Error**: `401 Unauthorized`
**Solution**: 
- Create a new token (Step 1)
- Update Streamlit secrets (Step 2)
- Reboot app

### **Problem 2: Auto-save not working**
**Check**:
1. Token is correctly pasted in Streamlit Cloud secrets (no extra spaces)
2. Token has `repo` scope permissions
3. App was rebooted after adding secrets
4. Check app logs for error messages

### **Problem 3: Want to verify it's working**
**Test**:
1. Complete 1 annotation in the app
2. Check GitHub: `annotations/{your_id}.json`
3. Should see a new commit within seconds
4. File should contain 1 annotation

---

## 🎯 **Advantages of Auto-Save**

### **For Annotators**:
- ✅ No need to remember to download
- ✅ Can close browser anytime (progress saved)
- ✅ Can annotate across multiple sessions
- ✅ Can annotate from multiple devices

### **For You**:
- ✅ Real-time progress monitoring
- ✅ Automatic backups (GitHub history)
- ✅ No need to collect files from annotators
- ✅ Version control (can see annotation timeline)

---

## 📊 **Monitoring Annotations**

### **View in GitHub**:
```
https://github.com/aizanzafar/miccai-2026-annotation/tree/main/annotations
```

### **Download all annotations**:
```powershell
cd "C:\Users\z0056hnb\Documents\My Research\miccai-2026-annotation"
git pull origin main
# All annotations are in annotations/ folder
```

### **Check progress**:
```powershell
cd annotations
python -c "import json; import glob; files = glob.glob('*.json'); print(f'Total annotators: {len(files)}'); [print(f'{f}: {len(json.load(open(f)))} annotations') for f in files]"
```

---

## 🔒 **Security Notes**

1. **Token Security**:
   - Never share your token
   - Never commit token to GitHub code
   - Token is stored securely in Streamlit Cloud secrets
   - Token is NOT visible in the app UI

2. **Repository Access**:
   - Token only has access to this specific repo
   - If compromised, revoke at: https://github.com/settings/tokens

3. **Best Practice**:
   - Use 90-day expiration
   - Create calendar reminder to renew
   - Use minimal scope permissions (just `repo`)

---

## 🚀 **You're All Set!**

After completing both steps:
1. ✅ Annotations auto-save to GitHub
2. ✅ Download button still available as backup
3. ✅ Can monitor progress in real-time
4. ✅ No manual file collection needed

**Test it**: Complete 1 annotation → Check `annotations/` folder in GitHub → Should see your file! 🎉

---

**Created**: February 9, 2026  
**For**: MICCAI 2026 Phase 2 Bbox Annotation - Automatic GitHub Sync
