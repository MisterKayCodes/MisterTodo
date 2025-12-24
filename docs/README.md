# Mister_Todo — Your Personal Telegram To-Do Bot

## Overview

Mister_Todo is a lightweight, resilient Telegram bot designed to manage your tasks with minimal effort.  
It provides a simple, “lazy-person” UI with permanent reply keyboards and inline buttons, allowing you to create, track, and complete tasks without typing complex commands.  

Built with scalability and maintainability in mind, Mister_Todo follows strict architectural rules inspired by the [Level-Up Dev Rulebook (2025 Edition)](./docs/LEVEL_UP_RULEBOOK.md). This ensures reliability, clear state management, and seamless updates.

---

## Features

- **Permanent Reply Keyboard:** Quick access to [➕ New Task], [📋 My List], [📊 Habit Stats], and [⏱️ Active Timer].
- **Inline Task Controls:** Mark tasks done, add time, or delete with a single tap.
- **Robust State Management:** Using Aiogram’s FSM to track input states.
- **Durable Storage:** SQLite backend ensures all tasks and logs are safely persisted.
- **Habit Tracking:** Simple consistency scores to encourage daily productivity.
- **Safe Deployments:** Automated backups and rollback protocols to protect your data.
- **Lazy-User Friendly:** Minimal typing, emoji-rich feedback, and forgiving logic.

---

## Project Structure

```

Mister_Todo/
│
├── bot/                        # Telegram bot application layer
│   ├── main.py                 # Bot startup and event loop
│   ├── handlers/               # Command and callback handlers
│   ├── middlewares/            # Safety filters and error handling
│   ├── keyboards/              # Reply and inline keyboards
│   └── utils.py                # Helper functions
│
├── services/                   # Core business logic separate from bot API
│   ├── task_manager.py         # Task CRUD and idempotency
│   ├── stats.py                # Habit tracking logic
│   ├── scheduler.py            # Timer and scheduling logic
│   ├── persistence.py          # SQLite database abstraction
│   └── validation.py           # Input sanitization and security
│
├── storage/                    # Data persistence and logs
│   ├── db/                    # SQLite file and migrations
│   ├── logs/                   # Rotating log files
│   └── backups/                # Automated database backups
│
├── config/                     # Environment and constant configurations
│
├── tests/                      # Automated tests for core logic
│
├── docs/                       # Documentation, including this README
│
├── requirements.txt            # Pinned dependencies
├── .env.example                # Environment variable template
├── .gitignore                  # Files and folders ignored by Git
└── LICENSE                    # Project license (optional)

````

---

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Mister_Todo.git
   cd Mister_Todo
````

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   * Copy `.env.example` to `.env`
   * Add your Telegram Bot Token and other secrets

5. **Run the bot:**

   ```bash
   python -m bot.main
   ```

---

## Development Guidelines

* Follow the [Level-Up Dev Rulebook (2025 Edition)](./docs/LEVEL_UP_RULEBOOK.md) strictly.
* Write **explicit, idempotent, and readable code**.
* Use **SQLite for all persistent state**.
* Always **write tests** for new features.
* Log all significant events and errors for observability.
* Keep the **UI simple and lazy-user friendly**.
* No “smart guessing” — every user action must be explicit.

---

## Deployment & Updates

Please refer to [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed deployment steps including:

* Automated backups before updates
* Graceful shutdowns and restarts
* Monitoring logs and metrics
* Rollback procedures in case of failure

---

## Contributing

For now, Mister_Todo is a personal project. Contributions are welcome by pull request with clear, atomic commits respecting the architecture and coding standards.

---

## License

[   ]

---

## Contact

For questions or support, reach out to the maintainer.

---

```

---


