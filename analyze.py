import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

body_start = html.find('<body')
main_start = html.find('<main')
next_div = html.find('<div id="__next">')

print(f"body_start: {body_start}")
print(f"main_start: {main_start}")
print(f"next_div: {next_div}")

# Find lines around __next
lines = html.split('\n')
for i, line in enumerate(lines):
    if '<div id="__next">' in line:
        print(f"__next found at line {i+1}")
        for j in range(max(0, i-5), min(len(lines), i+10)):
            print(f"{j+1}: {lines[j]}")
        break
