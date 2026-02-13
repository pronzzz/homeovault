# HomeoVault 🏥

![HomeoVault Banner](https://img.shields.io/badge/HomeoVault-Medical_Inventory_System-blue?style=for-the-badge&logo=appveyor)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/status-Stable-success?style=flat-square)

**HomeoVault** is a specialized, secure, and intuitive inventory management system designed specifically for Homeopathic Pharmacies and Practitioners. Built with reliability and ease of use in mind, it handles the unique requirements of medical inventory, including potency tracking, expiry management, and strict stock control.

---

## 🌟 Key Features

### 📦 Smart Inventory Management

- **Detailed Tracking**: Record Medicine Name, Potency (e.g., 30C, 200C), Form (Dilution, Globules), Bottle Size, Manufacturer, and Batch Number.
- **Unique SKU System**: Automatically prevents duplicate entries for the same batch/product combination.
- **Negative Stock Protection**: Ensures your inventory count never drops below zero.

### 🛡️ Safety & Compliance

- **Expiry Awareness**: Automatically flags expired medicines and prevents accidental sales (with manager override).
- **Startup Health Scan**: Runs a comprehensive diagnostic on every launch to identify expired batches and low-stock items.
- **Data Integrity**: Performs database integrity checks on startup to prevent data corruption.

### 📊 Modern Dashboard

- **Real-Time Analytics**: View low-stock alerts and expiry warnings instantly.
- **Transaction History**: Complete audit trail of all stock additions, sales, and adjustments.
- **One-Click Export**: Export your entire inventory to CSV for external reporting or auditing.

### 🚀 Developer Friendly

- **Auto-Backups**: Automatically backs up the database to `backups/` on every restart.
- **Cross-Platform**: Runs seamlessly on macOS, Windows, and Linux.
- **Standalone Mode**: Can be compiled into a single executable file.

---

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python) - High performance, easy to maintain.
- **Database**: SQLModel (SQLite) - Simple, file-based, reliable.
- **Frontend**: Vanilla JavaScript / HTML5 / CSS3 - Lightweight, fast, no build step required for UI.
- **Distribution**: PyInstaller - For creating standalone executables.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher

### Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/pronzzz/homeovault.git
    cd homeovault
    ```

2. **Create a Virtual Environment**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To start the server and automatically launch the dashboard:

**macOS / Linux:**

```bash
./run.sh
```

**Windows:**
Double-click `run.bat` or run:

```bat
run.bat
```

The application will be available at `http://localhost:8000`.

---

## 📖 Documentation

- [User Guide](GUIDE.md) - Detailed instructions on using the application.
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to HomeoVault.
- [Code of Conduct](CODE_OF_CONDUCT.md) - Our community standards.

---

## 📦 Building Standalone Executable

You can package HomeoVault into a single file for distribution:

```bash
python3 build.py
```

The executable will be created in the `dist/` folder.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by [Pranav Dwivedi](https://github.com/pronzzz)
