# PPE-Detetction-Model

A real-time Computer Vision application that uses a custom YOLO model to ensure workplace safety by detecting Personal Protective Equipment (PPE). The system captures live video from your webcam, detects whether people have the required safety gear on, and automatically saves snapshot evidence of any violations.

## Features

- **Real-Time Detection**: Analyzes standard webcam video stream in real time.
- **YOLO Powered**: Uses a custom-trained YOLO model (`model/best.pt`) optimized for finding safety gear.
- **Tracks Missing Gear**: Alerts specifically when gear is missing, tracking:
  - Boots 🥾
  - Gloves 🧤
  - Goggles 🥽
  - Helmet ⛑️
  - Vest 🦺 
- **Automated Violation Logging**: Anytime a violation is detected, a snapshot with bounded boxes and warning text is automatically saved to the `violations/` directory with a timestamp.
- **Smart Cooldown System**: Prevents disk-spamming by employing a customizable cooldown (default 5 seconds) before logging the exact same violation scenario.

## Prerequisites

- Python 3.8+
- A working webcam

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   git clone https://github.com/MANPREETS47/PPE-Detetction-Model.git
   ```

2. **Install Required Libraries**:
   Install all necessary python packages using the `requirements.txt` file.
   ```bash
   pip install -r requirements.txt
   ```
   > **Note**: This will install `ultralytics` (which contains YOLO), `opencv-python` (for webcam rendering), and `numpy`.

3. **Ensure model exists**:
   Make sure your trained model file (`best.pt`) is located in the `model/` folder relative to `main.py`.

## Usage

Start the system by running the main Python script:

```bash
python main.py
```

- A window titled **"PPE Detection System"** will appear showing your camera feed.
- The system will overlay bounding boxes and labels when it detects a person and/or missing safety equipment.
- The total violation count will be displayed at all times in the upper left corner.
- **To exit the application**, select the video window and press the `q` key on your keyboard.

## How it Works 

Instead of generating false positives when body parts simply aren't in the frame, this system mostly relies on **negative classes** specifically trained to identify when PPE *should* be there but isn't (e.g. `no_boots`, `no_helmet`). 

Because there isn't a specific `no_vest` class, the application contains built-in logic to trigger a missing vest violation if a `Person` is detected but a `Vest` is not, keeping your environment perfectly secure.

## Directory Structure

```text
/
├── main.py              # Main inference script
├── requirements.txt     # Python dependencies
├── model/
│   └── best.pt          # Custom YOLOv8 Weights
└── violations/          # Auto-generated. Stores violation evidence images
```
