import os

filepath = r'c:\Users\ds012\OneDrive\Desktop\jarvis_ai - Copy\frontend\src\index.css'

with open(filepath, 'rb') as f:
    content = f.read()

# We know the corrupt part was added at the very end after the last clean '}'.
# Find the last closing brace and cut everything after it.
# The `\x00` bytes are from UTF16. So let's decode to utf-8 with errors='ignore',
# find the last '}', and then construct a clean file.

decoded = content.decode('utf-8', errors='ignore')
last_brace_idx = decoded.rfind('}')

clean_content = decoded[:last_brace_idx+1]
clean_content += '\n\n.waveform-bar-glow { box-shadow: 0 0 8px rgba(0, 194, 255, 0.6); }\n'

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(clean_content)

print("Fixed index.css")
