#!/usr/bin/env python3
"""
Build script to generate index.html for GitHub Pages.
Embeds the platform README, all 13 docs, and budget projection scenarios
into a single, self-contained, responsive, high-performance web application.
"""

import os
import glob
import json
import csv
import re

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Load README.md
    with open(os.path.join(root_dir, 'README.md'), 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # 2. Load all docs/*.md
    doc_files = sorted(glob.glob(os.path.join(root_dir, 'docs', '*.md')))
    docs = []
    for filepath in doc_files:
        filename = os.path.basename(filepath)
        doc_id = filename.replace('.md', '')
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else doc_id
        
        # Parse sections: Summary, Policy items, Implementation & Administration
        summary = ""
        policy_items = []
        implementation = ""
        
        sum_match = re.search(r'Summary\s*\n\n(.*?)(?=\n\n(?:Policy items|Contract|Key assumptions)|$)', content, re.DOTALL)
        if sum_match:
            summary = sum_match.group(1).strip()
            
        pol_match = re.search(r'Policy items\s*\n\n(.*?)(?=\n\nImplementation & Administration|$)', content, re.DOTALL)
        if pol_match:
            raw_items = pol_match.group(1).strip().split('\n')
            for item in raw_items:
                item = item.strip()
                if item.startswith('- '):
                    policy_items.append(item[2:].strip())
                    
        imp_match = re.search(r'Implementation & Administration\s*\n\n(.*?)(?=\n\n|$)', content, re.DOTALL)
        if imp_match:
            implementation = imp_match.group(1).strip()

        docs.append({
            'id': doc_id,
            'filename': filename,
            'title': title,
            'summary': summary,
            'policy_items': policy_items,
            'implementation': implementation,
            'content': content
        })

    # 3. Load Scenarios from outputs/
    scenarios = {}
    scenario_keys = {
        'central_balanced': 'Central Case (Balanced)',
        'optimistic': 'Optimistic Scenario',
        'conservative': 'Conservative Scenario'
    }
    for key, display_name in scenario_keys.items():
        filepath = os.path.join(root_dir, 'outputs', f'10yr_projection_{key}.csv')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = []
                for r in reader:
                    rows.append({
                        'Year': int(r.get('Year', 0)),
                        'GDP': float(r.get('GDP', 0)),
                        'BaselineReceipts': float(r.get('BaselineReceipts', 0)),
                        'BaselineOutlays': float(r.get('BaselineOutlays', 0)),
                        'PolicyRevenue': float(r.get('PolicyRevenue', 0)),
                        'PolicySpending': float(r.get('PolicySpending', 0)),
                        'TotalReceipts': float(r.get('TotalReceipts', 0)),
                        'TotalOutlays': float(r.get('TotalOutlays', 0)),
                        'Deficit': float(r.get('Deficit', 0))
                    })
                scenarios[key] = {
                    'name': display_name,
                    'rows': rows
                }

    site_data = {
        'readme': readme_content,
        'docs': docs,
        'scenarios': scenarios
    }

    # Generate HTML
    html_content = generate_html(site_data)
    
    output_html_path = os.path.join(root_dir, 'index.html')
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Successfully generated {output_html_path} ({len(html_content):,} bytes)")

def generate_html(data):
    json_data = json.dumps(data)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Platform for a Democratic Socialist Government</title>
  <meta name="description" content="Policy Framework, Legislative Priorities, and 10-Year Reproducible Budget Model.">
  <meta property="og:title" content="Platform for a Democratic Socialist Government">
  <meta property="og:description" content="A comprehensive platform of economic reform, democratic reconstruction, and reproducible 10-year budget projections.">
  <meta property="og:type" content="website">
  <meta name="theme-color" content="#dc2626">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🌹</text></svg>">
  
  <style>
    :root {{
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --font-serif: "Charter", "Georgia", "Cambria", serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;

      --bg-body: #f8fafc;
      --bg-surface: #ffffff;
      --bg-surface-elevated: #ffffff;
      --bg-sidebar: #f1f5f9;
      --bg-muted: #e2e8f0;
      --bg-accent-subtle: #fef2f2;
      --bg-accent-border: #fecaca;
      --bg-highlight: #fef3c7;
      
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-light: #64748b;
      --text-accent: #dc2626;

      --border-color: #e2e8f0;
      --border-strong: #cbd5e1;

      --primary: #dc2626;
      --primary-hover: #b91c1c;
      --primary-focus: rgba(220, 38, 38, 0.25);
      
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
      --card-shadow-hover: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      
      --sidebar-width: 320px;
      --header-height: 64px;
      --content-max-width: 860px;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --transition-fast: 0.15s ease;
    }}

    [data-theme="dark"] {{
      --bg-body: #090d16;
      --bg-surface: #111827;
      --bg-surface-elevated: #1f2937;
      --bg-sidebar: #0e1422;
      --bg-muted: #1e293b;
      --bg-accent-subtle: rgba(239, 68, 68, 0.12);
      --bg-accent-border: rgba(239, 68, 68, 0.28);
      --bg-highlight: rgba(245, 158, 11, 0.2);

      --text-main: #f8fafc;
      --text-muted: #cbd5e1;
      --text-light: #94a3b8;
      --text-accent: #f87171;

      --border-color: #1f2937;
      --border-strong: #374151;

      --primary: #ef4444;
      --primary-hover: #f87171;
      --primary-focus: rgba(239, 68, 68, 0.35);

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --card-shadow-hover: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html, body {{
      height: 100%;
      font-family: var(--font-sans);
      color: var(--text-main);
      background-color: var(--bg-body);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}

    a {{
      color: var(--primary);
      text-decoration: none;
      transition: color var(--transition-fast);
    }}

    a:hover {{
      text-decoration: underline;
    }}

    /* Layout */
    .app-container {{
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }}

    /* Header */
    .site-header {{
      height: var(--header-height);
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 50;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1.5rem;
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .menu-toggle-btn {{
      display: none;
      background: none;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      color: var(--text-main);
      padding: 0.4rem;
      cursor: pointer;
    }}

    .logo-container {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      font-weight: 700;
      font-size: 1.05rem;
      color: var(--text-main);
      text-decoration: none;
      white-space: nowrap;
    }}

    .logo-icon {{
      width: 28px;
      height: 28px;
      fill: var(--primary);
    }}

    .header-center {{
      flex: 1;
      max-width: 440px;
      margin: 0 1.5rem;
      position: relative;
    }}

    .search-input-wrapper {{
      position: relative;
      display: flex;
      align-items: center;
      width: 100%;
    }}

    .search-input-wrapper svg {{
      position: absolute;
      left: 0.75rem;
      width: 16px;
      height: 16px;
      fill: var(--text-light);
      pointer-events: none;
    }}

    .search-input {{
      width: 100%;
      height: 36px;
      padding: 0 2.2rem 0 2.2rem;
      border-radius: 9999px;
      border: 1px solid var(--border-color);
      background: var(--bg-sidebar);
      color: var(--text-main);
      font-size: 0.875rem;
      outline: none;
      transition: all var(--transition-fast);
    }}

    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-focus);
      background: var(--bg-surface);
    }}

    .search-shortcut {{
      position: absolute;
      right: 0.6rem;
      font-size: 0.7rem;
      padding: 0.15rem 0.35rem;
      background: var(--border-color);
      color: var(--text-muted);
      border-radius: 4px;
      pointer-events: none;
    }}

    .search-results-dropdown {{
      position: absolute;
      top: 42px;
      left: 0;
      right: 0;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15);
      max-height: 420px;
      overflow-y: auto;
      display: none;
      z-index: 100;
    }}

    .search-results-dropdown.active {{
      display: block;
    }}

    .search-result-item {{
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--border-color);
      cursor: pointer;
      display: block;
      color: var(--text-main);
    }}

    .search-result-item:hover, .search-result-item.selected {{
      background: var(--bg-muted);
      text-decoration: none;
    }}

    .search-result-title {{
      font-weight: 600;
      font-size: 0.9rem;
      color: var(--primary);
    }}

    .search-result-snippet {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 0.2rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .header-right {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .btn-icon {{
      background: none;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      color: var(--text-main);
      padding: 0.45rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
    }}

    .btn-icon:hover {{
      background: var(--bg-muted);
      border-color: var(--border-strong);
    }}

    .btn-icon svg {{
      width: 18px;
      height: 18px;
      fill: currentColor;
    }}

    /* Main body layout */
    .app-main {{
      display: flex;
      flex: 1;
    }}

    /* Sidebar */
    .sidebar {{
      width: var(--sidebar-width);
      min-width: var(--sidebar-width);
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border-color);
      height: calc(100vh - var(--header-height));
      position: sticky;
      top: var(--header-height);
      overflow-y: auto;
      padding: 1.25rem 0.75rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .sidebar-section-title {{
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-light);
      padding: 0 0.75rem;
      margin-bottom: 0.35rem;
    }}

    .nav-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }}

    .nav-item a {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.45rem 0.75rem;
      border-radius: var(--radius-sm);
      color: var(--text-muted);
      font-size: 0.875rem;
      font-weight: 500;
      transition: all var(--transition-fast);
      text-decoration: none;
    }}

    .nav-item a:hover {{
      background: var(--bg-muted);
      color: var(--text-main);
    }}

    .nav-item.active a {{
      background: var(--bg-accent-subtle);
      color: var(--primary);
      font-weight: 600;
      border-left: 3px solid var(--primary);
    }}

    .nav-num {{
      font-size: 0.75rem;
      font-family: var(--font-mono);
      opacity: 0.85;
      min-width: 1.8rem;
    }}

    /* Content Area */
    .content-area {{
      flex: 1;
      padding: 2.5rem 2rem 4rem 2rem;
      max-width: calc(var(--content-max-width) + 4rem);
      margin: 0 auto;
      width: 100%;
    }}

    /* Hero / Header of doc */
    .doc-hero {{
      margin-bottom: 2rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 1.5rem;
    }}

    .badge-category {{
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--primary);
      background: var(--bg-accent-subtle);
      border: 1px solid var(--bg-accent-border);
      padding: 0.25rem 0.6rem;
      border-radius: 9999px;
      margin-bottom: 0.75rem;
    }}

    .doc-title {{
      font-size: 2.15rem;
      font-weight: 800;
      line-height: 1.2;
      color: var(--text-main);
      margin-bottom: 0.75rem;
      font-family: var(--font-sans);
    }}

    .doc-meta-actions {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-top: 1rem;
      font-size: 0.825rem;
      color: var(--text-light);
    }}

    .btn-action {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.35rem 0.65rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      color: var(--text-muted);
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      transition: all var(--transition-fast);
      text-decoration: none;
    }}

    .btn-action:hover {{
      background: var(--bg-muted);
      color: var(--text-main);
      text-decoration: none;
    }}

    .btn-action svg {{
      width: 14px;
      height: 14px;
      fill: currentColor;
    }}

    /* Callout & Summary boxes */
    .summary-card {{
      background: var(--bg-accent-subtle);
      border: 1px solid var(--bg-accent-border);
      border-left: 4px solid var(--primary);
      border-radius: var(--radius-md);
      padding: 1.25rem 1.5rem;
      margin-bottom: 2rem;
    }}

    .summary-title {{
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--primary);
      margin-bottom: 0.4rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .summary-text {{
      font-size: 1rem;
      color: var(--text-main);
      line-height: 1.6;
    }}

    /* Section Headings */
    .section-title {{
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--text-main);
      margin: 2rem 0 1rem 0;
      padding-bottom: 0.4rem;
      border-bottom: 2px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    /* Policy items grid/cards */
    .policy-items-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 1rem;
      margin-bottom: 2rem;
    }}

    .policy-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 1.25rem 1.5rem;
      box-shadow: var(--card-shadow);
      transition: transform var(--transition-fast), box-shadow var(--transition-fast);
      position: relative;
    }}

    .policy-card:hover {{
      box-shadow: var(--card-shadow-hover);
      border-color: var(--border-strong);
    }}

    .policy-card-title {{
      font-weight: 700;
      font-size: 1.05rem;
      color: var(--text-main);
      margin-bottom: 0.35rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .policy-card-bullet {{
      width: 8px;
      height: 8px;
      background: var(--primary);
      border-radius: 50%;
      flex-shrink: 0;
    }}

    .policy-card-desc {{
      color: var(--text-muted);
      font-size: 0.95rem;
      line-height: 1.55;
    }}

    /* Implementation card */
    .impl-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 1.25rem 1.5rem;
      margin-bottom: 2.5rem;
    }}

    .impl-title {{
      font-size: 0.9rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-light);
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .impl-desc {{
      color: var(--text-muted);
      font-size: 0.95rem;
      line-height: 1.6;
    }}

    /* Markdown rendered typography */
    .markdown-body {{
      font-size: 1rem;
      color: var(--text-main);
      line-height: 1.7;
    }}

    .markdown-body h1, .markdown-body h2, .markdown-body h3 {{
      color: var(--text-main);
      margin-top: 1.8rem;
      margin-bottom: 0.8rem;
      font-weight: 700;
    }}

    .markdown-body h1 {{ font-size: 1.85rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; }}
    .markdown-body h2 {{ font-size: 1.4rem; }}
    .markdown-body h3 {{ font-size: 1.15rem; }}

    .markdown-body p {{
      margin-bottom: 1rem;
    }}

    .markdown-body ul, .markdown-body ol {{
      margin-bottom: 1.25rem;
      padding-left: 1.75rem;
    }}

    .markdown-body li {{
      margin-bottom: 0.4rem;
    }}

    .markdown-body table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1.5rem 0;
      font-size: 0.875rem;
      overflow-x: auto;
      display: block;
    }}

    .markdown-body th, .markdown-body td {{
      padding: 0.65rem 0.9rem;
      border: 1px solid var(--border-color);
      text-align: left;
    }}

    .markdown-body th {{
      background: var(--bg-muted);
      font-weight: 700;
      color: var(--text-main);
    }}

    .markdown-body td.num, .markdown-body th.num {{
      text-align: right;
      font-variant-numeric: tabular-nums;
    }}

    .markdown-body tr:nth-child(even) {{
      background: var(--bg-sidebar);
    }}

    .markdown-body blockquote {{
      border-left: 4px solid var(--primary);
      padding: 0.5rem 1rem;
      background: var(--bg-accent-subtle);
      color: var(--text-muted);
      margin: 1rem 0;
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    }}

    .markdown-body hr {{
      border: 0;
      height: 1px;
      background: var(--border-color);
      margin: 2.5rem 0;
    }}

    /* Table styles for Budget Model */
    .scenario-tabs {{
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.25rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.5rem;
    }}

    .scenario-tab-btn {{
      padding: 0.5rem 1rem;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      background: var(--bg-surface);
      color: var(--text-muted);
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      transition: all var(--transition-fast);
    }}

    .scenario-tab-btn:hover {{
      background: var(--bg-muted);
      color: var(--text-main);
    }}

    .scenario-tab-btn.active {{
      background: var(--primary);
      border-color: var(--primary);
      color: #ffffff;
    }}

    .metrics-summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}

    .metric-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 1rem;
      box-shadow: var(--card-shadow);
    }}

    .metric-label {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-light);
      margin-bottom: 0.35rem;
    }}

    .metric-value {{
      font-size: 1.45rem;
      font-weight: 800;
      font-variant-numeric: tabular-nums;
      color: var(--text-main);
    }}

    .metric-subtext {{
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 0.2rem;
    }}

    .table-responsive-wrapper {{
      width: 100%;
      overflow-x: auto;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      margin-bottom: 2rem;
      background: var(--bg-surface);
      box-shadow: var(--card-shadow);
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.875rem;
    }}

    .data-table th, .data-table td {{
      padding: 0.65rem 0.85rem;
      border-bottom: 1px solid var(--border-color);
      white-space: nowrap;
    }}

    .data-table th {{
      background: var(--bg-sidebar);
      font-weight: 700;
      color: var(--text-main);
      text-align: right;
    }}

    .data-table th:first-child, .data-table td:first-child {{
      text-align: left;
      font-weight: 600;
    }}

    .data-table td {{
      text-align: right;
      font-variant-numeric: tabular-nums;
      color: var(--text-muted);
    }}

    .data-table tbody tr:hover {{
      background: var(--bg-muted);
    }}

    .data-table tfoot tr {{
      font-weight: 700;
      background: var(--bg-sidebar);
      border-top: 2px solid var(--border-strong);
    }}

    .data-table tfoot td {{
      color: var(--text-main);
    }}

    /* Pagination / Next doc footer */
    .doc-nav-footer {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      margin-top: 3.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border-color);
    }}

    .doc-nav-btn {{
      display: flex;
      flex-direction: column;
      padding: 0.75rem 1rem;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      background: var(--bg-surface);
      color: var(--text-main);
      text-decoration: none;
      transition: all var(--transition-fast);
      max-width: 48%;
    }}

    .doc-nav-btn:hover {{
      border-color: var(--primary);
      background: var(--bg-accent-subtle);
      text-decoration: none;
    }}

    .doc-nav-label {{
      font-size: 0.725rem;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.05em;
      color: var(--text-light);
    }}

    .doc-nav-title {{
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--primary);
      margin-top: 0.2rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .doc-nav-btn.next {{
      text-align: right;
      margin-left: auto;
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: var(--text-main);
      color: var(--bg-body);
      padding: 0.6rem 1.2rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.25s ease;
      z-index: 999;
    }}

    .toast.show {{
      transform: translateY(0);
      opacity: 1;
    }}

    /* View Mode Toggler */
    .view-mode-toggle {{
      display: inline-flex;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      overflow: hidden;
      background: var(--bg-surface);
    }}

    .view-mode-btn {{
      padding: 0.3rem 0.65rem;
      background: none;
      border: none;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
    }}

    .view-mode-btn.active {{
      background: var(--primary);
      color: #ffffff;
    }}

    /* Mobile Responsive */
    @media (max-width: 900px) {{
      .sidebar {{
        position: fixed;
        left: -100%;
        top: var(--header-height);
        height: calc(100vh - var(--header-height));
        z-index: 45;
        transition: left 0.25s ease;
        box-shadow: 10px 0 25px rgba(0,0,0,0.1);
      }}

      .sidebar.open {{
        left: 0;
      }}

      .menu-toggle-btn {{
        display: flex;
      }}

      .content-area {{
        padding: 1.5rem 1rem 3rem 1rem;
      }}

      .header-center {{
        display: none;
      }}

      .header-center.mobile-open {{
        display: block;
        position: absolute;
        top: var(--header-height);
        left: 0;
        right: 0;
        max-width: none;
        margin: 0;
        padding: 0.75rem 1rem;
        background: var(--bg-surface);
        border-bottom: 1px solid var(--border-color);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
      }}

      .doc-title {{
        font-size: 1.65rem;
      }}
    }}

    /* Print Styles */
    @media print {{
      .site-header, .sidebar, .doc-nav-footer, .doc-meta-actions, .view-mode-toggle, .scenario-tabs {{
        display: none !important;
      }}
      .app-main {{
        display: block;
      }}
      .content-area {{
        max-width: 100%;
        padding: 0;
      }}
      body {{
        background: #fff;
        color: #000;
      }}
      .policy-card {{
        border: 1px solid #ccc;
        box-shadow: none;
        page-break-inside: avoid;
      }}
    }}
  </style>
</head>
<body>
  <div class="app-container">
    <!-- Header -->
    <header class="site-header">
      <div class="header-left">
        <button class="menu-toggle-btn" id="menuToggleBtn" aria-label="Toggle navigation menu">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
          </svg>
        </button>
        <a href="#overview" class="logo-container">
          <svg class="logo-icon" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
          <span>Democratic Socialist Agenda</span>
        </a>
      </div>

      <div class="header-center" id="searchHeaderCenter">
        <div class="search-input-wrapper">
          <svg viewBox="0 0 24 24">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
          <input type="text" id="searchInput" class="search-input" placeholder="Search policies, revenue, sections..." autocomplete="off">
          <span class="search-shortcut">/</span>
        </div>
        <div class="search-results-dropdown" id="searchResultsDropdown"></div>
      </div>

      <div class="header-right">
        <button class="btn-icon" id="themeToggleBtn" title="Toggle Light/Dark Theme" aria-label="Toggle Theme">
          <svg id="themeIconSun" viewBox="0 0 24 24" style="display:none;">
            <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41s-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41s-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/>
          </svg>
          <svg id="themeIconMoon" viewBox="0 0 24 24">
            <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/>
          </svg>
        </button>
        <a href="https://github.com/glenpierce/newDemocraticSocialistAgendaProposal" target="_blank" rel="noopener noreferrer" class="btn-icon" title="View repository on GitHub">
          <svg viewBox="0 0 24 24">
            <path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/>
          </svg>
        </a>
      </div>
    </header>

    <!-- Main Body -->
    <div class="app-main">
      <!-- Sidebar -->
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-group">
          <div class="sidebar-section-title">Core Document</div>
          <ul class="nav-list">
            <li class="nav-item" id="nav-overview">
              <a href="#overview">
                <span>📜</span>
                <span>Platform Overview</span>
              </a>
            </li>
          </ul>
        </div>

        <div class="sidebar-group">
          <div class="sidebar-section-title">Detailed Policy Drafts</div>
          <ul class="nav-list" id="policyNavList">
            <!-- Injected dynamically -->
          </ul>
        </div>

        <div class="sidebar-group">
          <div class="sidebar-section-title">Fiscal Projections</div>
          <ul class="nav-list">
            <li class="nav-item" id="nav-budget-model">
              <a href="#budget-model">
                <span>📊</span>
                <span>10-Year Budget Model</span>
              </a>
            </li>
          </ul>
        </div>
      </aside>

      <!-- Content Area -->
      <main class="content-area" id="contentArea">
        <!-- Rendered dynamically -->
      </main>
    </div>
  </div>

  <div class="toast" id="toast">Link copied to clipboard</div>

  <!-- CDN Marked with fallback -->
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>

  <!-- Embedded Platform Data -->
  <script>
    const SITE_DATA = {json_data};
  </script>

  <!-- Main Application Script -->
  <script>
    (function() {{
      const state = {{
        currentRoute: 'overview',
        currentScenario: 'central_balanced',
        viewMode: 'structured', // 'structured' or 'markdown'
        theme: localStorage.getItem('dsa_theme') || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      }};

      // Initialize Theme
      applyTheme(state.theme);

      function applyTheme(theme) {{
        document.documentElement.setAttribute('data-theme', theme);
        state.theme = theme;
        localStorage.setItem('dsa_theme', theme);
        const sun = document.getElementById('themeIconSun');
        const moon = document.getElementById('themeIconMoon');
        if (theme === 'dark') {{
          sun.style.display = 'block';
          moon.style.display = 'none';
        }} else {{
          sun.style.display = 'none';
          moon.style.display = 'block';
        }}
      }}

      document.getElementById('themeToggleBtn').addEventListener('click', () => {{
        applyTheme(state.theme === 'dark' ? 'light' : 'dark');
      }});

      // Sidebar Navigation Builder
      const policyNavList = document.getElementById('policyNavList');
      SITE_DATA.docs.forEach((doc, idx) => {{
        const li = document.createElement('li');
        li.className = 'nav-item';
        li.id = 'nav-' + doc.id;
        
        // Extract roman numeral or clean title
        const romanMatch = doc.title.match(/^([IVXLCDM]+)\.\s*(.*)/);
        const num = romanMatch ? romanMatch[1] : (idx + 1).toString().padStart(2, '0');
        const label = romanMatch ? romanMatch[2] : doc.title;

        li.innerHTML = `
          <a href="#${{doc.id}}">
            <span class="nav-num">${{num}}.</span>
            <span>${{escapeHtml(label)}}</span>
          </a>
        `;
        policyNavList.appendChild(li);
      }});

      // Mobile Menu Toggle
      const sidebar = document.getElementById('sidebar');
      const menuToggleBtn = document.getElementById('menuToggleBtn');
      menuToggleBtn.addEventListener('click', () => {{
        sidebar.classList.toggle('open');
      }});

      // Close mobile menu on link click
      sidebar.addEventListener('click', (e) => {{
        if (e.target.closest('a')) {{
          sidebar.classList.remove('open');
        }}
      }});

      // Simple Markdown Fallback if Marked fails
      function renderMarkdown(md) {{
        if (typeof marked !== 'undefined' && marked.parse) {{
          return marked.parse(md);
        }}
        // Basic fallback
        return md
          .replace(/^### (.*$)/gim, '<h3>$1</h3>')
          .replace(/^## (.*$)/gim, '<h2>$1</h2>')
          .replace(/^# (.*$)/gim, '<h1>$1</h1>')
          .replace(/\\*\\*(.*)\\*\\*/gim, '<strong>$1</strong>')
          .replace(/\\*(.*)\\*/gim, '<em>$1</em>')
          .replace(/\\n\\n/gim, '<br><br>');
      }}

      // Helper for Toast
      function showToast(msg) {{
        const toast = document.getElementById('toast');
        toast.textContent = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2000);
      }}

      // Routing
      function handleRoute() {{
        const hash = window.location.hash.replace('#', '') || 'overview';
        state.currentRoute = hash;

        // Update nav active classes
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        const activeNav = document.getElementById('nav-' + hash);
        if (activeNav) activeNav.classList.add('active');

        // Render appropriate content
        if (hash === 'overview') {{
          renderOverview();
        }} else if (hash === 'budget-model') {{
          renderBudgetModel();
        }} else {{
          const doc = SITE_DATA.docs.find(d => d.id === hash);
          if (doc) {{
            renderDoc(doc);
          }} else {{
            renderOverview();
          }}
        }}

        window.scrollTo(0, 0);
      }}

      window.addEventListener('hashchange', handleRoute);
      window.addEventListener('DOMContentLoaded', handleRoute);

      // Render Platform Overview (README)
      function renderOverview() {{
        const container = document.getElementById('contentArea');
        const html = `
          <div class="doc-hero">
            <span class="badge-category">Core Platform Platform</span>
            <h1 class="doc-title">Platform for a Democratic Socialist Government</h1>
            <p style="font-size: 1.15rem; color: var(--text-muted); line-height: 1.6;">
              A comprehensive program of economic reform, democratic reconstruction, and public investment intended to restore institutional capacity and align governance with the public interest.
            </p>
            <div class="doc-meta-actions">
              <a href="https://github.com/glenpierce/newDemocraticSocialistAgendaProposal/blob/main/README.md" target="_blank" rel="noopener" class="btn-action">
                <svg viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>
                View on GitHub
              </a>
              <button class="btn-action" onclick="copyCurrentUrl()">
                <svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                Share Platform
              </button>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-title">
              <span>🌟</span>
              <span>Platform Foundation</span>
            </div>
            <div class="summary-text">
              The United States has the productive capacity, technical expertise, and financial resources to provide economic security, political stability, and broad prosperity. Persistent inequality, institutional dysfunction, and declining public trust are the result of policy design choices, not structural inevitabilities.
            </div>
          </div>

          <div class="section-title">
            <span>Platform Pillars & Policy Drafts</span>
            <span style="font-size: 0.85rem; font-weight: normal; color: var(--text-light);">13 Detailed Proposals</span>
          </div>

          <div class="policy-items-grid" style="grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));">
            ${{SITE_DATA.docs.map(doc => `
              <a href="#${{doc.id}}" class="policy-card" style="text-decoration:none; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                  <div class="policy-card-title" style="color:var(--primary); font-size: 1rem;">
                    <span class="policy-card-bullet"></span>
                    <span>${{escapeHtml(doc.title)}}</span>
                  </div>
                  <div class="policy-card-desc" style="display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-top:0.4rem;">
                    ${{escapeHtml(doc.summary || 'Click to view the detailed legislative and administrative draft.')}}
                  </div>
                </div>
                <div style="margin-top: 1rem; font-size: 0.8rem; font-weight: 600; color: var(--primary);">
                  Read proposal →
                </div>
              </a>
            `).join('')}}
          </div>

          <div class="section-title">
            <span>Full Manifesto Text</span>
          </div>

          <article class="markdown-body">
            ${{renderMarkdown(SITE_DATA.readme)}}
          </article>

          <div class="doc-nav-footer">
            <div></div>
            <a href="#01-fiscal-policy-and-wealth-concentration" class="doc-nav-btn next">
              <span class="doc-nav-label">Next Section</span>
              <span class="doc-nav-title">I. Fiscal Policy & Wealth Concentration →</span>
            </a>
          </div>
        `;
        container.innerHTML = html;
      }}

      // Render Individual Policy Document
      function renderDoc(doc) {{
        const container = document.getElementById('contentArea');
        const currentIndex = SITE_DATA.docs.findIndex(d => d.id === doc.id);
        const prevDoc = currentIndex > 0 ? SITE_DATA.docs[currentIndex - 1] : null;
        const nextDoc = currentIndex < SITE_DATA.docs.length - 1 ? SITE_DATA.docs[currentIndex + 1] : null;

        let contentHtml = '';
        if (state.viewMode === 'structured' && doc.policy_items && doc.policy_items.length > 0) {{
          contentHtml = `
            ${{doc.summary ? `
              <div class="summary-card">
                <div class="summary-title">
                  <span>📌</span>
                  <span>Executive Summary</span>
                </div>
                <div class="summary-text">${{escapeHtml(doc.summary)}}</div>
              </div>
            ` : ''}}

            <div class="section-title">
              <span>Policy Items & Measures</span>
              <span style="font-size: 0.85rem; font-weight: normal; color: var(--text-light);">${{doc.policy_items.length}} Specific Proposals</span>
            </div>

            <div class="policy-items-grid">
              ${{doc.policy_items.map(item => {{
                const parts = item.split('—');
                const title = parts.length > 1 ? parts[0].trim() : '';
                const desc = parts.length > 1 ? parts.slice(1).join('—').trim() : item;
                return `
                  <div class="policy-card">
                    <div class="policy-card-title">
                      <span class="policy-card-bullet"></span>
                      <span>${{title ? escapeHtml(title) : 'Proposal'}}</span>
                    </div>
                    <div class="policy-card-desc">${{escapeHtml(desc)}}</div>
                  </div>
                `;
              }}).join('')}}
            </div>

            ${{doc.implementation ? `
              <div class="impl-card">
                <div class="impl-title">
                  <span>🏛️</span>
                  <span>Implementation & Administration</span>
                </div>
                <div class="impl-desc">${{escapeHtml(doc.implementation)}}</div>
              </div>
            ` : ''}}
          `;
        }} else {{
          // Markdown view
          contentHtml = `
            <article class="markdown-body">
              ${{renderMarkdown(doc.content)}}
            </article>
          `;
        }}

        const html = `
          <div class="doc-hero">
            <span class="badge-category">Policy Framework</span>
            <h1 class="doc-title">${{escapeHtml(doc.title)}}</h1>
            
            <div class="doc-meta-actions">
              <div class="view-mode-toggle">
                <button class="view-mode-btn ${{state.viewMode === 'structured' ? 'active' : ''}}" onclick="toggleViewMode('structured')">Structured View</button>
                <button class="view-mode-btn ${{state.viewMode === 'markdown' ? 'active' : ''}}" onclick="toggleViewMode('markdown')">Full Source</button>
              </div>

              <a href="https://github.com/glenpierce/newDemocraticSocialistAgendaProposal/blob/main/docs/${{doc.filename}}" target="_blank" rel="noopener" class="btn-action">
                <svg viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>
                GitHub File
              </a>

              <button class="btn-action" onclick="copyCurrentUrl()">
                <svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                Copy Link
              </button>
            </div>
          </div>

          ${{contentHtml}}

          <div class="doc-nav-footer">
            ${{prevDoc ? `
              <a href="#${{prevDoc.id}}" class="doc-nav-btn prev">
                <span class="doc-nav-label">← Previous</span>
                <span class="doc-nav-title">${{escapeHtml(prevDoc.title)}}</span>
              </a>
            ` : `
              <a href="#overview" class="doc-nav-btn prev">
                <span class="doc-nav-label">← Platform</span>
                <span class="doc-nav-title">Overview</span>
              </a>
            `}}
            ${{nextDoc ? `
              <a href="#${{nextDoc.id}}" class="doc-nav-btn next">
                <span class="doc-nav-label">Next →</span>
                <span class="doc-nav-title">${{escapeHtml(nextDoc.title)}}</span>
              </a>
            ` : `
              <a href="#budget-model" class="doc-nav-btn next">
                <span class="doc-nav-label">Next →</span>
                <span class="doc-nav-title">10-Year Budget Model</span>
              </a>
            `}}
          </div>
        `;

        container.innerHTML = html;
      }}

      window.toggleViewMode = function(mode) {{
        state.viewMode = mode;
        handleRoute();
      }};

      // Render 10-Year Budget Model
      function renderBudgetModel() {{
        const container = document.getElementById('contentArea');
        const scenario = SITE_DATA.scenarios[state.currentScenario] || SITE_DATA.scenarios['central_balanced'];
        const rows = scenario.rows || [];

        // Compute metrics
        let totalReceipts10 = 0;
        let totalOutlays10 = 0;
        let totalPolicyRev10 = 0;
        let totalPolicySpend10 = 0;
        let cumulativeNetDeficitChange = 0;

        rows.forEach(r => {{
          totalReceipts10 += r.TotalReceipts;
          totalOutlays10 += r.TotalOutlays;
          totalPolicyRev10 += r.PolicyRevenue;
          totalPolicySpend10 += r.PolicySpending;
          const baselineDef = r.BaselineOutlays - r.BaselineReceipts;
          cumulativeNetDeficitChange += (r.Deficit - baselineDef);
        }});

        const year10GDP = rows.length ? rows[rows.length - 1].GDP : 0;

        const html = `
          <div class="doc-hero">
            <span class="badge-category">Fiscal Architecture</span>
            <h1 class="doc-title">XIII. Economic Analysis & 10-Year Budget Projections</h1>
            <p style="font-size: 1.05rem; color: var(--text-muted);">
              Parameterized, reproducible 10-year fiscal model comparing baseline federal receipts and outlays to the platform's policy package.
            </p>
            <div class="doc-meta-actions">
              <a href="https://github.com/glenpierce/newDemocraticSocialistAgendaProposal/blob/main/docs/13-economic-analysis-and-10-year-projections.md" target="_blank" rel="noopener" class="btn-action">
                <svg viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>
                View Document 13
              </a>
              <a href="https://github.com/glenpierce/newDemocraticSocialistAgendaProposal/blob/main/tools/10yr_budget_model.py" target="_blank" rel="noopener" class="btn-action">
                <svg viewBox="0 0 24 24"><path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/></svg>
                Python Budget Script
              </a>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-title">
              <span>🎯</span>
              <span>Model Objective & Baseline Contract</span>
            </div>
            <div class="summary-text">
              The platform pairs robust progressive revenue generation (wealth tax, corporate minimums, capital gains parity, enhanced enforcement) with investments in healthcare, education, climate, and social infrastructure. Starting from current nominal U.S. GDP of <strong>$31.0 trillion</strong> and baseline receipts/outlays of $5.0T/$7.0T.
            </div>
          </div>

          <div class="section-title">
            <span>Projection Scenarios</span>
          </div>

          <div class="scenario-tabs">
            <button class="scenario-tab-btn ${{state.currentScenario === 'central_balanced' ? 'active' : ''}}" onclick="switchScenario('central_balanced')">Central Balanced Case</button>
            <button class="scenario-tab-btn ${{state.currentScenario === 'optimistic' ? 'active' : ''}}" onclick="switchScenario('optimistic')">Optimistic Scenario</button>
            <button class="scenario-tab-btn ${{state.currentScenario === 'conservative' ? 'active' : ''}}" onclick="switchScenario('conservative')">Conservative Scenario</button>
          </div>

          <div class="metrics-summary-grid">
            <div class="metric-card">
              <div class="metric-label">10-Yr Policy Revenue</div>
              <div class="metric-value" style="color: #16a34a;">+$${{(totalPolicyRev10 / 1000).toFixed(2)}}T</div>
              <div class="metric-subtext">$${{totalPolicyRev10.toLocaleString('en-US', {{maximumFractionDigits:1}})}}B cumulative</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">10-Yr Policy Spending</div>
              <div class="metric-value" style="color: var(--primary);">+$${{(totalPolicySpend10 / 1000).toFixed(2)}}T</div>
              <div class="metric-subtext">$${{totalPolicySpend10.toLocaleString('en-US', {{maximumFractionDigits:1}})}}B cumulative</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">Cumulative Deficit Delta</div>
              <div class="metric-value" style="color: ${{cumulativeNetDeficitChange <= 0 ? '#16a34a' : 'var(--primary)'}};">
                ${{cumulativeNetDeficitChange > 0 ? '+' : ''}}${{cumulativeNetDeficitChange.toLocaleString('en-US', {{maximumFractionDigits:1}})}}B
              </div>
              <div class="metric-subtext">${{cumulativeNetDeficitChange <= 0 ? 'Surplus / Deficit Reduced' : 'Additional Deficit'}}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">Year 10 Nominal GDP</div>
              <div class="metric-value">$${{(year10GDP / 1000).toFixed(1)}}T</div>
              <div class="metric-subtext">$${{year10GDP.toLocaleString('en-US', {{maximumFractionDigits:1}})}}B</div>
            </div>
          </div>

          <div class="section-title">
            <span>Annual Fiscal Projections Table (USD Billions)</span>
          </div>

          <div class="table-responsive-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Year</th>
                  <th>Nominal GDP</th>
                  <th>Base Receipts</th>
                  <th>Base Outlays</th>
                  <th>Policy Revenue</th>
                  <th>Policy Spending</th>
                  <th>Total Receipts</th>
                  <th>Total Outlays</th>
                  <th>Annual Deficit</th>
                </tr>
              </thead>
              <tbody>
                ${{rows.map(r => `
                  <tr>
                    <td>Year ${{r.Year}}</td>
                    <td>$${{r.GDP.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                    <td>$${{r.BaselineReceipts.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                    <td>$${{r.BaselineOutlays.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                    <td style="color:#16a34a; font-weight:600;">+$${{r.PolicyRevenue.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                    <td style="color:var(--primary); font-weight:600;">+$${{r.PolicySpending.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                    <td style="font-weight:600;">$${{r.TotalReceipts.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                    <td style="font-weight:600;">$${{r.TotalOutlays.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                    <td style="font-weight:700;">$${{r.Deficit.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                  </tr>
                `).join('')}}
              </tbody>
              <tfoot>
                <tr>
                  <td>10-Yr Total</td>
                  <td>—</td>
                  <td>—</td>
                  <td>—</td>
                  <td style="color:#16a34a;">+$${{totalPolicyRev10.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                  <td style="color:var(--primary);">+$${{totalPolicySpend10.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                  <td>$${{totalReceipts10.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                  <td>$${{totalOutlays10.toLocaleString('en-US', {{minimumFractionDigits: 1, maximumFractionDigits: 1}})}}</td>
                  <td>—</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <div class="section-title">
            <span>Policy Levers & Steady-State Assumptions</span>
          </div>

          <div class="policy-items-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
            <div class="policy-card">
              <div class="policy-card-title"><span class="policy-card-bullet"></span> Wealth Tax (8% >$100M)</div>
              <div class="policy-card-desc">
                Estimated steady-state taxable wealth base = $10.0T. Compliance factor = 60%, administrative cost = 5%. Generates <strong>$456B - $700B/yr</strong> at full implementation.
              </div>
            </div>
            <div class="policy-card">
              <div class="policy-card-title"><span class="policy-card-bullet"></span> Corporate & Minimum Tax</div>
              <div class="policy-card-desc">
                Anti-avoidance provisions, global minimum tax, and transfer pricing reform generating <strong>+$150B to +$200B/yr</strong>.
              </div>
            </div>
            <div class="policy-card">
              <div class="policy-card-title"><span class="policy-card-bullet"></span> Capital Gains Parity</div>
              <div class="policy-card-desc">
                Aligning capital gains tax rates with ordinary income for high earners and mark-to-market treatment generating <strong>+$120B to +$150B/yr</strong>.
              </div>
            </div>
            <div class="policy-card">
              <div class="policy-card-title"><span class="policy-card-bullet"></span> Single-Payer Healthcare Net Cost</div>
              <div class="policy-card-desc">
                Replaces private premiums with public funding. Eliminates administrative overhead and drug price gouging, netting <strong>+$200B to +$300B/yr</strong> federal spending.
              </div>
            </div>
          </div>

          <div class="impl-card" style="margin-top: 2rem;">
            <div class="impl-title">
              <span>💻</span>
              <span>Reproduce & Verify the Model Locally</span>
            </div>
            <div class="impl-desc">
              <p style="margin-bottom: 0.5rem;">The projection model is open-source and parameterized in Python. To run all scenarios locally:</p>
              <pre style="background:var(--bg-muted); padding:0.8rem; border-radius:6px; font-family:var(--font-mono); font-size:0.85rem; overflow-x:auto;"><code>python3 tools/10yr_budget_model.py</code></pre>
              <p style="margin-top: 0.5rem; font-size: 0.85rem;">Outputs are saved to <code>outputs/10yr_projection_[scenario].csv</code> matching the published data above.</p>
            </div>
          </div>

          <div class="doc-nav-footer">
            <a href="#12-housing-mental-health-and-social-services" class="doc-nav-btn prev">
              <span class="doc-nav-label">← Previous</span>
              <span class="doc-nav-title">XII. Housing, Mental Health & Social Services</span>
            </a>
            <a href="#overview" class="doc-nav-btn next">
              <span class="doc-nav-label">Return to Start →</span>
              <span class="doc-nav-title">Platform Overview</span>
            </a>
          </div>
        `;

        container.innerHTML = html;
      }}

      window.switchScenario = function(scen) {{
        state.currentScenario = scen;
        renderBudgetModel();
      }};

      window.copyCurrentUrl = function() {{
        navigator.clipboard.writeText(window.location.href).then(() => {{
          showToast('Link copied to clipboard');
        }}).catch(() => {{
          showToast('Failed to copy link');
        }});
      }};

      // Search functionality
      const searchInput = document.getElementById('searchInput');
      const searchDropdown = document.getElementById('searchResultsDropdown');

      // Build search index
      const searchIndex = [];
      searchIndex.push({{
        id: 'overview',
        title: 'Platform for a Democratic Socialist Government (Manifesto)',
        content: SITE_DATA.readme
      }});
      searchIndex.push({{
        id: 'budget-model',
        title: 'Economic Analysis & 10-Year Budget Projections',
        content: 'budget projection model gdp receipts outlays wealth tax corporate capital gains single payer deficit surplus scenarios'
      }});
      SITE_DATA.docs.forEach(doc => {{
        searchIndex.push({{
          id: doc.id,
          title: doc.title,
          content: doc.content + ' ' + (doc.policy_items ? doc.policy_items.join(' ') : '') + ' ' + doc.implementation
        }});
      }});

      searchInput.addEventListener('input', (e) => {{
        const q = e.target.value.trim().toLowerCase();
        if (!q) {{
          searchDropdown.classList.remove('active');
          searchDropdown.innerHTML = '';
          return;
        }}

        const matches = [];
        searchIndex.forEach(item => {{
          const titleMatch = item.title.toLowerCase().indexOf(q);
          const contentMatch = item.content.toLowerCase().indexOf(q);
          if (titleMatch !== -1 || contentMatch !== -1) {{
            let snippet = '';
            if (contentMatch !== -1) {{
              const start = Math.max(0, contentMatch - 40);
              const end = Math.min(item.content.length, contentMatch + 100);
              snippet = '...' + item.content.substring(start, end).replace(/\\n/g, ' ') + '...';
            }} else {{
              snippet = item.title;
            }}
            matches.push({{
              id: item.id,
              title: item.title,
              snippet: snippet
            }});
          }}
        }});

        if (matches.length > 0) {{
          searchDropdown.innerHTML = matches.slice(0, 8).map(m => `
            <a href="#${{m.id}}" class="search-result-item" onclick="closeSearch()">
              <div class="search-result-title">${{escapeHtml(m.title)}}</div>
              <div class="search-result-snippet">${{escapeHtml(m.snippet)}}</div>
            </a>
          `).join('');
          searchDropdown.classList.add('active');
        }} else {{
          searchDropdown.innerHTML = '<div style="padding:1rem; font-size:0.85rem; color:var(--text-light); text-align:center;">No matching policies or text found</div>';
          searchDropdown.classList.add('active');
        }}
      }});

      window.closeSearch = function() {{
        searchDropdown.classList.remove('active');
        searchInput.value = '';
      }};

      document.addEventListener('click', (e) => {{
        if (!e.target.closest('#searchHeaderCenter')) {{
          searchDropdown.classList.remove('active');
        }}
      }});

      // Keyboard shortcut '/'
      document.addEventListener('keydown', (e) => {{
        if (e.key === '/' && document.activeElement !== searchInput) {{
          e.preventDefault();
          searchInput.focus();
          searchInput.select();
        }}
        if (e.key === 'Escape') {{
          closeSearch();
          searchInput.blur();
        }}
      }});

      function escapeHtml(text) {{
        if (!text) return '';
        return text
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#039;');
      }}

    }})();
  </script>
</body>
</html>
"""
    return html

if __name__ == '__main__':
    main()
