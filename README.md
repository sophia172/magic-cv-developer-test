# 📱 Android Kotlin Pose Tracking

This repository contains an **Android Kotlin** application that leverages the **phone camera** to stream video and analyze human movement using **MediaPipe**.

## 🚀 Features
- **Real-time pose detection** using **MediaPipe**.
- **Joint position extraction** and **joint angle calculation**.
- **Movement comparison** against a reference exercise.
- **Similarity evaluation** using **Dynamic Time Warping (DTW)** or **Cosine Similarity**.
- **Exercise repetition counting** and **progress tracking**.

## 🏗️ Technologies Used
- **Kotlin** for Android development.
- **MediaPipe** for human pose detection.
- **Mathematical analysis** for joint angle calculations.
- **DTW and Cosine Similarity** for movement comparison.
- **Python script integration** within the Kotlin project with **chaquo**

## 📂 Project Structure
```
📦 YourProjectName
├── 📁 app/src/main
│   ├── 📁 kotlin+java/fit.magic.cv
│   │   ├── 📁 exercise_info      # UI
│   │   ├── 📁 fragment           # Camera stream handling
│   │   ├── 📁 repcounter          # Python integration
│   │   ├── 📄 MainActivity.kt       # Camera stream handling
│   ├── 📁 res/layout               # UI layouts
│   ├── 📁 res/drawable             # App icons and images
│   ├── 📁 python                    # Joint angle calculation, DTW & Cosine similarity comparison
├── 📄 README.md                    # Project documentation
└── 📄 build.gradle                  # Build configuration
```

## 🛠️ Setup & Installation
1. **Clone the repository**
   ```bash
   git clone [https://github.com/your-username/your-repo.git](https://github.com/sophia172/magic-cv-developer-test.git)
   cd magic-cv-developer-test
   ```
2. **Open in Android Studio**
   - Open Android Studio and select "Open an existing project."
3. **Run the app on your device/emulator**
   - Connect your Android phone or use an emulator.
   - Sync Porject with Gradle file.
   - Click on "Run" ▶️.

## 📊 How It Works
1. **Camera captures the video stream.**
2. **MediaPipe detects body joints** and extracts joint positions.
3. **Joint angles are calculated** based on detected positions.
4. **The movement is compared** against a predefined reference using:
   - **Dynamic Time Warping (DTW)**
   - **Cosine Similarity**
5. **Repetitions are counted**, and progress is tracked based on similarity scores.

## 🏋️‍♀️ Example Use Case
This project can be used to analyze and score **exercise performance**, such as:
- Lunge

## 📌 To-Do List


## 🤝 Contributing
Feel free to **fork** this repository, submit **issues**, or open **pull requests**.

## 📜 License
This project is licensed under the **MIT License**.



