from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tasks.file_tasks import delete_expired_files


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        delete_expired_files,
        trigger="interval",
        hours=1,
        id="clear_expired_files",
        replace_existing=True,
    )

    return scheduler
