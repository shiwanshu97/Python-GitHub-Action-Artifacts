from datetime import datetime

print("Python artifact demo")

with open("result.txt", "w") as file:
  file.write("Hello from Github\n")
  file.write("This file is created in Github\n")
  file.write(f"Generated Time: {datetime.now()}\n")

print("result.txt file is created successfully")
