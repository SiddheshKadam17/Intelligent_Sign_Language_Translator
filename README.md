# 🤟 SignTalk Pro — Voice to Sign Language Translator

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/CustomTkinter-5.2-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/MediaPipe-0.10-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" />
</p>

<p align="center">
  A professional desktop application that converts <b>Voice / Text → Indian Sign Language (ISL) & American Sign Language (ASL)</b> animations in real time.
</p>

---

## 📸 Features

| Feature | Description |
|---|---|
| 🎙️ **Voice Input** | Speak and instantly see sign language |
| ✍️ **Text Input** | Type any text and translate to signs |
| 🇮🇳 **ISL Support** | Indian Sign Language animations |
| 🇺🇸 **ASL Support** | American Sign Language animations |
| 📜 **History** | View all past translations |
| ⭐ **Favorites** | Save frequently used phrases |
| 🏆 **Achievements** | Earn badges as you learn |
| 🎯 **Quiz Mode** | Practice and test your sign knowledge |
| 📥 **GIF Export** | Export translations as animated GIFs |
| 🌙 **Dark/Light Mode** | Multiple themes and color schemes |
| 👤 **User Profiles** | Personal login with stats tracking |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10
- Windows 10/11
- Webcam (optional)
- Microphone (for voice input)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/SignTalkPro.git
cd SignTalkPro
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the app**
```bash
cd speechtosign/enhanced_app
python professional_app_COMPLETE.py
```

---

## 📦 Requirements

```
customtkinter==5.2.2
Pillow
SpeechRecognition
pyaudio
opencv-python
mediapipe
scikit-learn
numpy==1.26.4
matplotlib
```

---

## 📁 Project Structure

```
SignTalkPro/
├── speechtosign/
│   └── enhanced_app/
│       ├── professional_app_COMPLETE.py   ← Main application
│       ├── assets/
│       │   ├── sign_images/               ← ISL sign images
│       │   ├── isl_sign_images/
│       │   └── asl_sign_images/           ← ASL sign images
│       ├── models/                        ← ML models
│       ├── database/                      ← SQLite database
│       └── src/
│           ├── core/
│           │   ├── sign_animator.py
│           │   ├── speech_handler.py
│           │   ├── database_manager.py
│           │   └── settings_manager.py
│           ├── ui/
│           └── utils/
└── requirements.txt
```

---

## 👨‍💻 Team

| Name | Role |
|---|---|
| **Siddhesh Kadam** | Lead Developer |
| **Swapnil Shinde** | UI/UX & Frontend |
| **Vaibhav Patil** | Backend & Database |
| **Tejas Pawale** | ML & Sign Recognition |

**Guide:** Prof. Pradnya Kothawade

**College:** Genba Sopanrao Moze College of Engineering, Balewadi, Pune

---

## 🛠️ Tech Stack

- **UI Framework** — CustomTkinter
- **Speech Recognition** — Google Speech API via SpeechRecognition
- **Hand Tracking** — MediaPipe
- **Machine Learning** — Scikit-learn (SVM)
- **Image Processing** — OpenCV, Pillow
- **Database** — SQLite
- **Animation** — PIL + Tkinter Canvas

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">Made with ❤️ by Team SignTalk Pro | GSMCOE Pune 2024-25</p>
