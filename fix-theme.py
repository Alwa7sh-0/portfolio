import re, glob, os

pages = glob.glob(os.path.expanduser("~/mnt/portfolio/*.html"))

for path in pages:
    with open(path, 'r') as f:
        html = f.read()
    
    # Skip 404 (no theme switcher)
    if 'theme-default' not in html:
        continue
    
    basename = os.path.basename(path)
    
    # 1. Add localStorage.setItem inside setTheme function
    # Different pages have slightly different setTheme patterns, but all set body class
    # We need to add localStorage save after the class change
    
    # Pattern: various setTheme functions - replace them all with a unified version
    # that includes localStorage
    
    # Also need to add on-load restore code
    
    # Step 1: Add a <script> right after <body> (or at start of body) to restore theme
    # before any rendering happens, to prevent flash
    restore_script = """<script>
(function(){var t=localStorage.getItem('portfolio-theme');if(t)document.body.classList.add(t);})();
</script>"""
    
    # Insert right after <body> or <body ...>
    if 'portfolio-theme' not in html:  # don't double-apply
        html = re.sub(r'(<body[^>]*>)', r'\1\n' + restore_script, html, count=1)
    
    # Step 2: Modify setTheme to save to localStorage
    # And modify click handlers to also update active state from storage on load
    
    # Replace the setTheme function - handle both minified and expanded versions
    # Add localStorage.setItem
    
    # For the "active" class on the default button - need to check localStorage on load
    # Replace the default "active" on the button with dynamic assignment
    
    # Remove hardcoded "active" from theme-default button
    html = html.replace('class="theme-btn active" id="theme-default"', 'class="theme-btn" id="theme-default"')
    
    # Now patch the setTheme function to include localStorage
    # Handle minified version (most pages)
    html = re.sub(
        r"function setTheme\(t\)\{document\.body\.classList\.remove\('theme-retro'\);if\(t\)document\.body\.classList\.add\(t\);(\w+)\.forEach\(function\(b\)\{b\.classList\.remove\('active'\);\}\);\}",
        r"function setTheme(t){document.body.classList.remove('theme-retro');if(t){document.body.classList.add(t);localStorage.setItem('portfolio-theme',t);}else{localStorage.removeItem('portfolio-theme');}\1.forEach(function(b){b.classList.remove('active');});}",
        html
    )
    
    # Handle expanded version (blog.html, gallery.html, interests.html)
    # blog pattern
    if 'function setTheme(themeClass)' in html:
        html = re.sub(
            r"function setTheme\(themeClass\) \{",
            "function setTheme(themeClass) {\n      if(themeClass){localStorage.setItem('portfolio-theme',themeClass);}else{localStorage.removeItem('portfolio-theme');}",
            html, count=1
        )
    
    if 'function setTheme(t) {' in html:
        html = re.sub(
            r"function setTheme\(t\) \{",
            "function setTheme(t) {\n      if(t){localStorage.setItem('portfolio-theme',t);}else{localStorage.removeItem('portfolio-theme');}",
            html, count=1
        )
    
    # Add code to set the correct active button on page load
    # Find the last theme-retro click handler and add init code after
    init_code = "\n    // Restore active button from saved theme\n    (function(){var saved=localStorage.getItem('portfolio-theme');if(saved){var btn=document.getElementById(saved);if(btn)btn.classList.add('active');}else{var def=document.getElementById('theme-default');if(def)def.classList.add('active');}})();"
    
    if 'Restore active button' not in html:
        # Insert after the last theme button click handler
        # Find the retro click handler line and add after it
        patterns = [
            "setTheme('theme-retro'); this.classList.add('active');",
            "setTheme('theme-retro');this.classList.add('active');",
        ]
        for pat in patterns:
            idx = html.rfind(pat)
            if idx != -1:
                # Find the end of that line (next semicolon + }) or newline
                end = html.find('\n', idx)
                if end != -1:
                    html = html[:end] + init_code + html[end:]
                break
    
    with open(path, 'w') as f:
        f.write(html)
    print(f"Patched {basename}")

