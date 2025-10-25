# Firebase Setup Guide

## 📍 Where to Add Firebase Credentials

Place your Firebase service account key as:
```
backend/firebase-key.json
```

## 🔑 How to Get Firebase Credentials

### Step 1: Go to Firebase Console
1. Visit [Firebase Console](https://console.firebase.google.com/)
2. Select your project (or create a new one)

### Step 2: Navigate to Service Accounts
1. Click the **gear icon** ⚙️ next to "Project Overview"
2. Select **"Project settings"**
3. Go to the **"Service accounts"** tab

### Step 3: Generate Private Key
1. Click **"Generate new private key"** button
2. Click **"Generate key"** in the confirmation dialog
3. A JSON file will download automatically

### Step 4: Place the File
1. Rename the downloaded file to `firebase-key.json`
2. Move it to the `backend/` directory
3. Final location: `backend/firebase-key.json`

## 📋 Example File Structure

```
backend/
├── firebase-key.json          ← Place your credentials here
├── main.py
├── .env
└── ...
```

## 🔒 Security Notes

✅ **Already Protected:**
- `firebase-key.json` is in `.gitignore` (won't be committed to git)
- Credentials are loaded securely by Firebase Admin SDK

⚠️ **Important:**
- Never commit `firebase-key.json` to version control
- Keep your service account key secret
- Only share with trusted team members via secure channels

## 🛠️ Configure Firebase Storage Bucket

After adding credentials, update `.env`:

```bash
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

To find your bucket name:
1. Go to Firebase Console → Storage
2. Look at the top for your bucket URL
3. Copy the bucket name (e.g., `my-project.appspot.com`)

## ✅ Verify Setup

Test your setup:

```bash
cd backend
python -c "from utils.firebase_utils import initialize_firebase; initialize_firebase(); print('✅ Firebase initialized successfully!')"
```

## 📊 What Firebase Stores

### Firestore (Database)
- Transcripts
- Analysis results (filler count, clarity score, suggestions)
- Timestamps
- User IDs

### Storage (Files)
- Uploaded audio files
- Organized in `audio/` folder

## 🚨 Troubleshooting

### Error: "firebase-key.json not found"
- Make sure the file is in the `backend/` directory
- Check the filename is exactly `firebase-key.json`
- Run `ls backend/firebase-key.json` to verify

### Error: "Could not load the default credentials"
- Check the JSON file is valid
- Verify you downloaded a service account key (not OAuth client)
- Ensure file has proper permissions

### Error: "Permission denied"
- Make sure the service account has Editor or Owner role
- Check Firestore and Storage are enabled in Firebase Console

## 🔗 Need Help?

- [Firebase Documentation](https://firebase.google.com/docs/admin/setup)
- [Service Account Keys](https://firebase.google.com/docs/admin/setup#initialize-sdk)

