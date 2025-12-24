
# Deployment & Rollback Procedures for Mister_Todo

*Ensuring safe, reliable, and zero-downtime updates for your personal Telegram To-Do Bot.*

---

## Pre-Deployment Checklist (Staging)

1. **Backup Production Data**  
   - Copy the current SQLite database to the backups folder:  
     ```bash
     cp storage/db/todo.sqlite storage/backups/todo_$(date +%F_%T).sqlite
     ```  
   - Confirm backup exists and is readable.

2. **Run All Tests Locally**  
   - Activate your virtual environment.  
   - Run the full test suite:  
     ```bash
     pytest tests/
     ```  
   - Fix any failures before proceeding.

3. **Verify Environment Variables**  
   - Ensure `.env` file has valid tokens and settings for the deployment environment.

---

## Deployment Steps

1. **Graceful Stop of Bot Service**  
   - If running as a systemd service or process manager, stop the bot gracefully:  
     ```bash
     systemctl stop mister_todo.service
     ```  
   - Or if running manually, send interrupt (Ctrl+C) ensuring clean shutdown.

2. **Pull Latest Code and Update Dependencies**  
   - Pull code from your repository:  
     ```bash
     git pull origin main
     ```  
   - Update dependencies as needed:  
     ```bash
     pip install -r requirements.txt
     ```  

3. **Apply Database Migrations (if any)**  
   - If you add migrations, run them here (adjust commands per your migration tool):  
     ```bash
     alembic upgrade head
     ```  

4. **Restart the Bot**  
   - Start your bot again:  
     ```bash
     systemctl start mister_todo.service
     ```  
   - Or run manually:  
     ```bash
     python -m bot.main
     ```  

5. **Monitor Logs and Metrics**  
   - Check logs for errors or unusual warnings:  
     ```bash
     tail -f storage/logs/bot.log
     ```  
   - Confirm bot responsiveness in Telegram.

---

## Post-Deployment Verification

- Confirm new features or fixes are working as expected.  
- Check the latest logs for any unexpected errors.  
- Verify the database is intact and no data loss occurred.

---

## Rollback Procedure

If you detect a critical failure after deployment:

1. **Stop the Bot Service**  
   ```bash
   systemctl stop mister_todo.service
````

2. **Restore Last Known Good Database Backup**

   * Identify the latest backup file:

     ```bash
     ls -ltr storage/backups/
     ```
   * Copy the backup over the live database:

     ```bash
     cp storage/backups/todo_YYYY-MM-DD_HH:MM:SS.sqlite storage/db/todo.sqlite
     ```

3. **Revert Codebase to Previous Stable Commit**

   * Use Git to checkout the previous commit or tag:

     ```bash
     git checkout <previous_commit_hash>
     ```

4. **Restart the Bot**

   ```bash
   systemctl start mister_todo.service
   ```

5. **Verify Bot Stability**

   * Check logs and test critical bot commands.

---

## Notes

* Automate backups before every deployment to eliminate human error.
* Consider adding a health-check script or bot command to verify uptime and responsiveness.
* Always communicate planned downtimes to users if you expand beyond personal use.

---

*Following this protocol ensures Mister_Todo stays reliable and your data safe through all updates.*

```

---

