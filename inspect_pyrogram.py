from pyrogram import raw
import inspect

print("Available methods in raw.functions.payments:")
for name, obj in inspect.getmembers(raw.functions.payments):
    if inspect.isclass(obj):
        print(f"- {name}")
