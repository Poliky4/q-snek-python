import rx
from rx.scheduler import EventLoopScheduler

scheduler = EventLoopScheduler()
scheduler.schedule_periodic(
    1,
    lambda state: print("woop?")
)

input("?")

