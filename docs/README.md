
Mister_Todo — Your Personal Telegram To-Do Bot

Overview

Mister_Todo is a lightweight, resilient Telegram bot designed to manage your tasks with minimal effort. It provides a simple, “lazy-person” UI with permanent reply keyboards and inline buttons, allowing you to create, track, and complete tasks without typing complex commands.

Built with scalability and maintainability in mind, Mister_Todo follows strict architectural rules inspired by the Level-Up Dev Rulebook (2025 Edition). This ensures reliability, clear state management, and seamless updates.

⸻

Features
	•	Permanent Reply Keyboard: Quick access to [➕ New Task], [📋 My List], [📊 Habit Stats], and [⏱️ Active Timer (to be replaced)].
	•	Inline Task Controls: Mark tasks done, add time manually, delete with a single tap.
	•	Robust State Management: Using Aiogram’s FSM to track input states.
	•	Durable Storage: SQLite backend ensures all tasks and logs are safely persisted.
	•	Habit Tracking & Productivity:
	•	Daily/weekly completion summaries with progress bars and streak highlights.
	•	Scrollable timeline view of completed tasks with timestamps.
	•	Filtering and searching completed tasks by date, tags, priority, or project.
	•	Export completed tasks as CSV files.
	•	Reward milestones with badges and emoji feedback.
	•	Manual time logging and Pomodoro-style focus sessions planned to replace the current active timer.
	•	Idle reminders and task priority/urgency meters to enhance productivity without overwhelming users.
	•	Safe Deployments: Automated backups and rollback protocols to protect your data.
	•	Lazy-User Friendly: Minimal typing, emoji-rich feedback, forgiving logic, and explicit commands only.

⸻

Project Structure

Mister_Todo/
│
├── bot/                        # Telegram bot application layer
│   ├── main.py                 # Bot startup and event loop
│   ├── handlers/               # Command and callback handlers
│   │   ├── commands.py         # Handlers for tasks, stats, filters, export, reset
│   │   ├── callbacks.py        # Inline buttons: mark done, delete, filter navigation, export triggers
│   │   └── states.py           # FSM states including filtering and export flows
│   ├── middlewares/            # Safety filters and error handling
│   ├── keyboards/              # Reply and inline keyboards (habit stats menu, timeline navigation)
│   └── utils.py                # Helper functions (e.g., CSV generation)
│
├── services/                   # Core business logic separate from bot API
│   ├── task_manager.py         # Task CRUD and idempotency
│   ├── stats.py                # Habit tracking, streak calculation, filtering, milestones, export logic
│   ├── scheduler.py            # Timer and Pomodoro session management (planned replacement for active timer)
│   ├── persistence.py          # SQLite database abstraction with completed task history
│   └── validation.py           # Input sanitization and security
│
├── storage/                    # Data persistence and logs
│   ├── db/                     # SQLite file and migrations (tags, priority, projects)
│   ├── logs/                   # Rotating log files
│   └── backups/                # Automated database backups
│
├── config/                     # Environment and constant configurations
│
├── tests/                      # Automated tests for task, stats, scheduler, and export features
│
├── docs/                       # Documentation, including this README and Level-Up Rulebook
│
├── requirements.txt            # Pinned dependencies
├── .env.example                # Environment variable template
├── .gitignore                  # Files and folders ignored by Git
└── LICENSE                    # Project license (optional)


⸻

Setup Instructions
	1.	Clone the repository:

git clone https://github.com/yourusername/Mister_Todo.git
cd Mister_Todo


	2.	Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate


	3.	Install dependencies:

pip install -r requirements.txt


	4.	Configure environment variables:
	•	Copy .env.example to .env
	•	Add your Telegram Bot Token and other secrets
	5.	Run the bot:

python -m bot.main



⸻

Development Guidelines
	•	Follow the Level-Up Dev Rulebook (2025 Edition) strictly.
	•	Write explicit, idempotent, and readable code.
	•	Use SQLite for all persistent state.
	•	Always write tests for new features.
	•	Log all significant events and errors for observability.
	•	Keep the UI simple and lazy-user friendly.
	•	No “smart guessing” — every user action must be explicit.

⸻

Deployment & Updates

Refer to DEPLOYMENT.md for detailed deployment steps including:
	•	Automated backups before updates
	•	Graceful shutdowns and restarts
	•	Monitoring logs and metrics
	•	Rollback procedures in case of failure

⸻

Planned Work (Upcoming Features)
	•	Replace the Active Timer with a Pomodoro Timer and Manual Time Logging for tasks (services/scheduler.py and related handlers).
	•	Implement comprehensive Habit Stats functionality:
	•	Daily/weekly completion summaries with progress bars and streak highlights (services/stats.py, bot/handlers/commands.py, bot/keyboards/).
	•	Scrollable, paginated timeline views and filtering FSM (bot/handlers/states.py).
	•	Task filtering and searching by date, tags, priority, project (services/stats.py, bot/handlers/callbacks.py).
	•	CSV export of completed tasks (bot/utils.py).
	•	Reward milestones with badge/emoji notifications (services/stats.py).
	•	Idle reminders and task priority/urgency meter enhancements (bot/middlewares/, services/task_manager.py).

⸻

Contributing

For now, Mister_Todo is a personal project. Contributions are welcome by pull request with clear, atomic commits respecting the architecture and coding standards.

⸻

License



⸻

Contact

For questions or support, reach out to the maintainer.

⸻

⸻
