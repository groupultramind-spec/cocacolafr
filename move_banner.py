import sys

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '<!-- CUSTOM BANNER START -->'
end_marker = '<!-- CUSTOM BANNER END -->\n'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker) + len(end_marker)

if start_idx != -1 and end_idx != -1:
    banner_code = content[start_idx:end_idx]
    
    # Remove banner from original position
    content = content[:start_idx] + content[end_idx:]
    
    # Find slider_wrapper
    target_marker = '<div\n                id="slider_wrapper"\n                class="bees-col is-4-col-phone is-8-col-tablet is-12-col-desktop"\n              ></div>'
    
    if target_marker in content:
        # replace target_marker with target_marker + banner_code inside
        new_target = '<div\n                id="slider_wrapper"\n                class="bees-col is-4-col-phone is-8-col-tablet is-12-col-desktop"\n              >\n' + banner_code + '\n              </div>'
        content = content.replace(target_marker, new_target)
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Banner moved successfully.")
    else:
        # Try to find just id="slider_wrapper"
        print("Target marker not found exactly as expected.")
else:
    print("Banner markers not found.")
