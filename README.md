# 📱 Android Kotlin Pose Tracking

This repository contains an **Android Kotlin** application that leverages the **phone camera** to stream video and analyze human movement using **MediaPipe**.

## 🚀 Features
- **Real-time pose detection** using **MediaPipe**.
- **Joint position extraction** and **joint angle calculation**.
- **Dynamic baseline** refresh standing pose.
- **Exercise repetition counting** and **progress tracking**.

## 🏗️ Technologies Used
- **Kotlin** for Android development.
- **MediaPipe** for human pose detection.
- **Mathematical analysis** for joint angle calculations.
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
│   ├── 📁 python                    # Joint angle calculation, progress analysis and counting
├── 📄 README.md                    # Project documentation
└── 📄 build.gradle                  # Build configuration
```

## 🛠️ Setup & Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/sophia172/magic-cv-developer-test.git
   cd magic-cv-developer-test
   ```
2. **Open in Android Studio**
   - Open Android Studio and select "Open an existing project."
3. **Change abiFilters setting in *build.gradle* Module level**
   - The Python interpreter is a native component, so you must use the abiFilters setting to specify which ABIs you want the app to support. The currently available ABIs are:
     - `armeabi-v7a` for older Android devices (Python 3.11 and older only)
     - `arm64-v8a` for current Android devices, and emulators on Apple silicon
     - `x86` for older emulators (Python 3.11 and older only)
     - `x86_64` for current emulators
```kotlin
   android {
        defaultConfig {
                       ndk {
                               // On Apple silicon, you can omit x86_64.
                               abiFilters "arm64-v8a", "x86_64"
                            }
                        }
            }
```

4**Run the app on your device/emulator**
   - Connect your Android phone or use an emulator.
   - Sync Porject with Gradle file.
   - Click on "Run" ▶️.



## 📊 How It Works
1. **Camera captures the video stream.**
2. **MediaPipe detects body joints** and extracts 3D coordinates of key landmarks.
3. **Knee and hip joint angles are calculated** from the detected coordinates.
4. **Standing position angles are updated** after each lunge to serve as the baseline reference.
5. **Lunge progress is determined** by comparing the current hip and knee angles to the baseline. A full lunge is defined when:
   - Hip angle reaches **55 degrees**
   - Knee angle reaches **90 degrees**
6. **Repetitions are counted**, and progress is tracked based on movement consistency.


## 🏋️‍♀️ Example Use Case
This project can be used to analyze and score **exercise performance**, such as:
- Lunge

## 📌 To-Do List


## 🤝 Contributing
Feel free to **fork** this repository, submit **issues**, or open **pull requests**.

## 📜 License
This project is licensed under the **MIT License**.



