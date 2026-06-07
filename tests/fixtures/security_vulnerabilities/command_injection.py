import os

user_input = input()

# Real command injection vulnerability
cmd = "echo user profile: " + user_input
os.system(cmd)
