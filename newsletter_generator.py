import os
import glob
from jinja2 import Template

def generate_newsletter():
    # 1. Find the latest Markdown post files
    post_dir = "LinkedIn_Posts"
    files = glob.glob(os.path.join(post_dir, "*.md"))
    # Sort by time desc
    files.sort(key=os.path.getmtime, reverse=True)
    
    if not files:
        print("No post files found to generate newsletter.")
        return

    latest_files = files[:3]
    print(f"Aggregating {len(latest_files)} latest post collections for newsletter.")
    
    content_html = ""
    
    for fpath in latest_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            # Convert simple markdown to HTML (basic implementation)
            # Just wrapping paragraphs
            content_html += f"<div class='post-collection'><h2>From File: {os.path.basename(fpath)}</h2><pre>{content}</pre></div><hr>"

    # 2. Create HTML Template
    template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Helvetica, Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; color: #333; }
            h1 { color: #0044cc; }
            .header { background: #f4f4f4; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .post-collection { background: #fff; padding: 20px; border: 1px solid #ddd; margin-bottom: 20px; border-radius: 8px; }
            pre { white-space: pre-wrap; font-family: inherit; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Weekly Legal Insights & Career Opportunities</h1>
            <p>Here is a digest of our top LinkedIn updates from the past week.</p>
        </div>
        
        {{ content }}
        
        <div class="footer">
            <p>Interested in joining our team? Reply to this email.</p>
        </div>
    </body>
    </html>
    """)
    
    final_html = template.render(content=content_html)
    
    output_path = "LinkedIn_Posts/newsletter_digest.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print(f"Newsletter generated at: {output_path}")

if __name__ == "__main__":
    generate_newsletter()
