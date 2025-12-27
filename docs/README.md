🚀 Mister_Todo — Your Personal Telegram Productivity Engine


📖 Overview
Mister_Todo is a resilient, senior-architected Telegram bot designed for high-performance task management with a "lazy-user" interface. Unlike standard to-do apps, Mister_Todo is built on the Level-Up Dev Rulebook (2025 Edition), ensuring that the system is always in a known state, handles errors explicitly, and persists data with 100% reliability.

Whether you are tracking daily habits, classifying work by priority, or exporting productivity reports, Mister_Todo manages the complexity so you don't have to.


✨ Key Features (2025 Edition)

🧠 Smart Date Parsing: Powered by dateparser. Type "next Friday," "20th Dec," or "tomorrow," and the bot automatically interprets and stores the correct ISO date.

📊 Habit Stats & Streaks: Real-time analytics including daily goal progress bars (visual "Lvl" meters) and "🔥 Streak" tracking.

📜 Paginated Archive: A clean, historical view of all completed tasks. Flip through your history using [Prev] and [Next] buttons without cluttering your chat.

📂 Time-Series Classification: Instantly filter your archive to see what you finished Today, this Week, or this Month.

⚖️ Priority-First Workflow: Every task is classified by priority (🔴 High, 🟡 Medium, 🟢 Low) during creation to help you focus on what matters.

📑 One-Click CSV Export: Export your entire completion history into a professionally formatted CSV file, grouped by date.

🛡️ Resilient Architecture: Built to survive crashes. FSM states and database migrations ensure your data is safe even after a reboot.


🏗️ Project Structure
Mister_Todo follows a Service-Oriented Architecture (SOA) to keep the bot UI separate from the core business logic.
text
Mister_Todo/
├── bot/                        # 📱 Telegram UI Layer (aiogram)
│   ├── main.py                 # System entry point & router registration
│   ├── utils.py                # Messy date normalization (NLP)
│   ├── handlers/               
│   │   ├── commands.py         # Entry points (Menus & FSM starts)
│   │   ├── callbacks.py        # Interactions (Done, Delete, Pagination, Export)
│   │   └── states.py           # Finite State Machine definitions
│   └── keyboards/              
│       ├── reply.py            # Primary navigation menu
│       └── inline.py           # Task-specific & Archive buttons
├── services/                   # ⚙️ Business Logic Tier (The "Brain")
│   ├── task_manager.py         # Task lifecycle, CSV generation, & filtering
│   ├── stats.py                # Productivity math, streaks, & progress bars
│   └── persistence.py          # SQLite Abstraction & Idempotent Migrations
├── storage/                    # 💾 Durable Persistence
│   ├── db/                     # SQLite database files
│   ├── exports/                # Generated CSV reports
│   └── logs/                   # Detailed system heartbeats
└── .env                        # Secrets & Tokens (Pinned)


🛠️ Setup Instructions
1. Clone & Environment

bash
git clone github.com
cd Mister_Todo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate


2. Install Dependencies

bash
pip install aiogram python-dotenv dateparser


3. Configuration

Create a .env file in the root directory:
env
BOT_TOKEN=your_telegram_bot_token_here


4. Run the Engine

bash
python -m bot.main


📐 The Senior Rulebook (Rules We Follow)

This project strictly adheres to the Level-Up Dev Rulebook:
Rule 1 (Known State): The system never "guesses." Every action results in an explicit state change.
Rule 3 (Single Responsibility): Each file does one job. persistence.py handles the DB; callbacks.py handles buttons.
Rule 11 (Separation of Logic): You can change the Telegram Bot for a Web App, and the services/ logic would stay exactly the same.
Rule 13 (2025 Standards): Uses timezone-aware UTC timestamps and class-based Bot properties.

📈 Planned Roadmap
Paginated Archive & Navigation
Natural Language Date Parsing
Priority Selection Workflow
Weekly/Monthly Data Classification
Idle Reminders: Friendly nudges if you have been inactive (Phase 5).
Manual Time Logging: Track exactly how many hours a task took.
Multi-Project Support: Grouping tasks by specific work streams.


🤝 Contact
Maintained by Mister Kay



Junior devs focus on making it work. Senior devs focus on making it last.


Love From Mister

