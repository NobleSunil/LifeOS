import os
import re

base_dir = r"d:\Users\Documents\Mini Project\LifeOS"
templates_dir = os.path.join(base_dir, "templates")
css_dir = os.path.join(base_dir, "static", "css")

replacements = [
    # General Backgrounds
    (r'(?i)#F7F3ED', 'var(--color-bg)'),
    (r'(?i)#FDFBF7', 'var(--color-bg)'),
    
    # Surface Backgrounds
    (r'(?i)#FFFFFF', 'var(--color-surface)'),
    (r'(?i)#fff\b', 'var(--color-surface)'),
    (r'(?i)#f8fafc', 'var(--color-surface)'),
    (r'(?i)#fdfdfd', 'var(--color-surface)'),
    (r'(?i)#f1f5f9', 'var(--color-surface-2)'),
    (r'(?i)#F0EBE3', 'var(--color-surface-2)'),
    
    # Borders
    (r'(?i)#E5DDD3', 'var(--color-border)'),
    (r'(?i)#EAE6DF', 'var(--color-border)'),
    (r'(?i)#e2e8f0', 'var(--color-border)'),
    (r'(?i)#dee2e6', 'var(--color-border)'),
    
    # Text Muted
    (r'(?i)#6B7280', 'var(--color-text-muted)'),
    (r'(?i)#9CA3AF', 'var(--color-text-muted)'),
    (r'(?i)#71717A', 'var(--color-text-muted)'),
    (r'(?i)#cbd5e1', 'var(--color-text-muted)'),
    
    # Primary/Text Primary
    (r'(?i)#1C2340', 'var(--color-primary)'),
    (r'(?i)#1E3A5F', 'var(--color-primary)'),
    (r'(?i)#2D3A6B', 'var(--color-primary)'),
    (r'(?i)#2C3539', 'var(--color-text-primary)'),
    
    # Accent / Secondary
    (r'(?i)#4F46E5', 'var(--color-accent)'),
    (r'(?i)#152A47', 'var(--color-secondary)'),
    (r'(?i)#1e2a52', 'var(--color-secondary)'),
    (r'(?i)#2563EB', 'var(--color-secondary)'),
    
    # Success
    (r'(?i)#16A34A', 'var(--color-success)'),
    (r'(?i)#15803d', 'var(--color-success)'),
    (r'(?i)#BBF7D0', 'var(--color-success)'),
    (r'(?i)#4A6741', 'var(--color-success)'),
    (r'(?i)#dcfce7', 'rgba(74, 124, 89, 0.15)'),
    (r'(?i)#166534', 'var(--color-success)'),
    (r'(?i)#f0fdf4', 'rgba(74, 124, 89, 0.05)'),
    
    # Danger
    (r'(?i)#DC2626', 'var(--color-danger)'),
    (r'(?i)#C24A4A', 'var(--color-danger)'),
    (r'(?i)#ef4444', 'var(--color-danger)'),
    (r'(?i)#fca5a5', 'var(--color-danger)'),
    (r'(?i)#fef2f2', 'rgba(139, 38, 53, 0.05)'),
    
    # Warning
    (r'(?i)#D97706', 'var(--color-warning)'),
    (r'(?i)#D4A373', 'var(--color-warning)'),
    (r'(?i)#f59e0b', 'var(--color-warning)'),
    (r'(?i)#b45309', 'var(--color-warning)'),
    (r'(?i)#fff8f0', 'rgba(198, 124, 42, 0.1)'),

    # Brand Soft Maps
    (r'(?i)#f0f4ff', 'rgba(44, 24, 16, 0.05)'),
    (r'(?i)#e0f0ff', 'rgba(44, 24, 16, 0.08)'),

    # Unmapped tailwind-style badges & highlights
    (r'(?i)#64748b', 'var(--color-text-muted)'),
    (r'(?i)#fff1f2', 'rgba(139, 38, 53, 0.08)'),
    (r'(?i)#fee2e2', 'rgba(139, 38, 53, 0.12)'),
    (r'(?i)#fef3c7', 'rgba(198, 124, 42, 0.12)'),
    (r'(?i)#EEF2FF', 'rgba(44, 24, 16, 0.08)'),
    (r'(?i)#4338CA', 'var(--color-primary)'),
    (r'(?i)#C7D2FE', 'var(--color-border)'),
    (r'(?i)#FFF7ED', 'rgba(198, 124, 42, 0.08)'),
    (r'(?i)#C2410C', 'var(--color-warning)'),
    (r'(?i)#FED7AA', 'var(--color-border)'),
    (r'(?i)#F0F9FF', 'rgba(44, 24, 16, 0.05)'),
    (r'(?i)#0369A1', 'var(--color-primary)'),
    (r'(?i)#BAE6FD', 'var(--color-border)'),
    (r'(?i)#F3F4F6', 'var(--color-surface-2)'),
    (r'(?i)#E5E7EB', 'var(--color-border)'),
    (r'(?i)#C4B9AC', 'var(--color-border)'),
    (r'(?i)#FECACA', 'var(--color-danger)'),
]

old_vars = [
    (r'var\(--bg-primary\)', 'var(--color-bg)'),
    (r'var\(--bg-card\)', 'var(--color-surface)'),
    (r'var\(--bg-hover\)', 'var(--color-surface-2)'),
    (r'var\(--primary-color\)', 'var(--color-primary)'),
    (r'var\(--brand-primary\)', 'var(--color-primary)'),
    (r'var\(--success-color\)', 'var(--color-success)'),
    (r'var\(--danger-color\)', 'var(--color-danger)'),
    (r'var\(--warning-color\)', 'var(--color-warning)'),
]

directories = [templates_dir, css_dir]

for directory in directories:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html') or file.endswith('.css'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                for pattern, replace in replacements:
                    new_content = re.sub(pattern, replace, new_content)
                for pattern, replace in old_vars:
                    new_content = re.sub(pattern, replace, new_content)

                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {file}")

print("Done Refactoring colors!")
