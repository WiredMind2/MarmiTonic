import os
import re

for root, dirs, files in os.walk('tests'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace patch('backend. with patch('
            new_content = re.sub(r"patch\(['\"]backend\.", "patch('", content)
            
            if new_content != content:
                print(f'Updating patches in {path}')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
