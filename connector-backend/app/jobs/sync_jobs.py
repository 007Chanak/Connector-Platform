from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from app.services.xero_sync_service import (
    sync_xero_customers_service
)

scheduler = BackgroundScheduler()

#scheduler.add_job(
#    sync_xero_customers_service,
#    "interval",
#    minutes=5,
#    args=[1]
#)

#scheduler.start()

print("Scheduler started...")