# ⚡ Selenium Automation Bot – High-Throughput Account Workflow

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium)
![Status](https://img.shields.io/badge/Status-Production--Ready-success?style=for-the-badge)

A **professional-grade Selenium automation framework** engineered for high-volume account management. 
This bot implements a **multi-threaded bi-directional processing engine** to handle logins, data extraction, and security challenges (popups, rate limits) with human-like resilience.

---

## 🎥 Project Demo

<!-- 
    TODO: Upload your demo video or GIF here. 
    Example: ![Demo](demo.gif) or [Watch Video](link_to_youtube)
-->
![Project Demo Placeholder](https://via.placeholder.com/800x400?text=Automation+Bot+Demo+Video+Coming+Soon)

---

## 🚀 Key Features

### ⚡ High-Performance Architecture
- **Bi-Directional Concurrency**: Unique threading strategy processes the account list from both **Top-to-Bottom** and **Bottom-to-Top** simultaneously to maximize throughput (~1,900 accounts/hour).
- **Scalable Design**: Capable of running hundreds of threads (dependent on hardware) with synchronized index locking.

### 🛡️ Smart Resilience
- **Rate-Limit Detection**: Automatically detects "operating too fast" warnings and switches to a slow-retry mode to bypass temporary blocks.
- **Popup Handling**: aggressive `fast_popup_handler` clears unexpected modals instantly using JavaScript injection.
- **DOM Validation**: Uses `WebDriverWait` and `ExpectedConditions` to ensure stability even on slow connections.

### 🔒 Security & Logging
- **Masked Logging**: All sensitive data (phone numbers, credentials) is automatically masked in logs (`+91XXXX...`) for safe sharing.
- **Incognito Mode**: Launches strictly in Incognito/Headless-ready modes to ensure clean sessions.

---

## 🧩 Project Structure

```text
selenium-automation-bot/
├── main.py              # 🧠 Core Multi-threaded Engine
├── config.py            # ⚙️ Centralized Configuration (Selectors, URLs)
├── utils/
│   ├── interaction.py   # 🎭 Human-like delays & input sanitization
│   ├── masking.py       # 🔒 Data masking for logs
│   └── logger.py        # 📝 Structured logging setup
├── input.sample.json    # 📄 Input format template
├── output.sample.json   # 📄 Output format template
└── requirements.txt     # 📦 Dependencies
```

---

## 🛠️ Usage

1.  **Configure Input**
    Create an `input.json` file with your account credentials:
    ```json
    [
        {
            "account_id": "ACC_001",
            "login_identifier": "user1",
            "credential": "password123"
        }
    ]
    ```

2.  **Run the Bot**
    ```bash
    python main.py
    ```

3.  **Monitor Output**
    *   Real-time logs will show progress in the terminal.
    *   Results are saved incrementally to `output1.json` (Top Bot) and `output2.json` (Bottom Bot).

---

## ⚙️ How It Works

1.  **Initialization**: Loads `input.json` and splits the workload.
2.  **Dual-Threading**: 
    *   `Top-Bot` starts from index 0 `->`
    *   `Bottom-Bot` starts from end `<-`
3.  **Processing Loop**:
    *   **Login**: Enters credentials with human-like typing delays.
    *   **Balance Check**: Extracts financial data if login succeeds.
    *   **Logout**: Cleanly ends session to prevent crossover.
4.  **Completion**: Stops when threads meet in the middle.

---

## ⚠️ Ethical Disclaimer
This software is designed for **educational purposes** and **authorized automation testing**. 
Users must ensure they have permission to automate interactions with the target platform.

---

## 👨‍💻 Author
**Aryan Prajapati**
*Automation Engineer • Python Developer • Selenium Expert*

[![GitHub](https://img.shields.io/badge/GitHub-AryanPrajapati9456-181717?style=flat&logo=github)](https://github.com/AryanPrajapati9456)