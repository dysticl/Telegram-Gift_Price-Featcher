from telethon.tl.functions import payments
import inspect

print("Available methods in telethon.tl.functions.payments:")
for name, obj in inspect.getmembers(payments):
    if inspect.isclass(obj) and name.endswith("Request"):
        print(f"- {name}")
