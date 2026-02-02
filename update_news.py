#!/usr/bin/env python3
"""
AI News Site Auto-Updater
Fetches latest AI news and updates the website automatically
"""

import json
import os
import re
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.parse import quote_plus, unquote
import ssl

# Disable SSL verification for simplicity
ssl._create_default_https_context = ssl._create_unverified_context

def extract_real_url(duckduckgo_url):
    """Extract real URL from DuckDuckGo redirect URL"""
    # DuckDuckGo URLs look like: //duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com&rut=...
    if 'uddg=' in duckduckgo_url:
        match = re.search(r'uddg=([^&]+)', duckduckgo_url)
        if match:
            return unquote(match.group(1))
    return duckduckgo_url

def search_news(query, num_results=10):
    """Search for news using DuckDuckGo HTML"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    # Use DuckDuckGo HTML search with time filter (df=w for past week)
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}&df=w"

    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')

        # Extract results using regex
        results = []
        # Find result links and titles
        pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        matches = re.findall(pattern, html)

        for raw_url, title in matches[:num_results]:
            if title.strip():
                # Extract real URL from DuckDuckGo redirect
                real_url = extract_real_url(raw_url)
                results.append({
                    'title': title.strip(),
                    'url': real_url
                })

        return results
    except Exception as e:
        print(f"Search error for '{query}': {e}")
        return []

def get_current_date():
    """Get current date info"""
    now = datetime.now()
    week_start = now - timedelta(days=6)
    return {
        'year': now.year,
        'month': now.month,
        'day': now.day,
        'week_start_month': week_start.month,
        'week_start_day': week_start.day,
        'formatted': f"{now.year}年{now.month}月{now.day}日",
        'time': now.strftime("%H:%M")
    }

def generate_html(news_data, date_info):
    """Generate the full HTML page with updated news"""

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI资讯中心 | 全球人工智能与金融科技动态</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #7c3aed;
            --accent: #06b6d4;
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --border: #334155;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --gold: #fbbf24;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        header {{
            background: linear-gradient(135deg, var(--bg-dark) 0%, #1a1a2e 100%);
            border-bottom: 1px solid var(--border);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .logo-icon {{
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }}

        .logo h1 {{
            font-size: 1.5rem;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .header-right {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .update-info {{
            text-align: right;
        }}

        .update-time {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        .live-dot {{
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}

        .auto-update-badge {{
            background: linear-gradient(90deg, var(--success), var(--accent));
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-top: 4px;
            display: inline-block;
        }}

        .week-range {{
            color: var(--accent);
            font-size: 0.8rem;
            margin-top: 2px;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.5; transform: scale(1.2); }}
        }}

        .next-update {{
            background: var(--bg-card);
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid var(--border);
            text-align: center;
        }}

        .next-update-label {{
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}

        .countdown {{
            font-size: 1.1rem;
            font-weight: bold;
            color: var(--accent);
            font-family: monospace;
        }}

        nav {{
            background: var(--bg-card);
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }}

        .nav-links {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .nav-link {{
            padding: 8px 16px;
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 20px;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.3s;
            cursor: pointer;
        }}

        .nav-link:hover, .nav-link.active {{
            background: var(--primary);
            border-color: var(--primary);
            color: white;
        }}

        .nav-link.hot {{
            border-color: var(--danger);
            color: var(--danger);
        }}

        .nav-link.hot:hover {{
            background: var(--danger);
            color: white;
        }}

        main {{
            padding: 30px 0;
        }}

        .section-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--primary);
        }}

        .section-title h2 {{
            font-size: 1.5rem;
        }}

        .section-title .badge {{
            background: var(--primary);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
        }}

        .section-title .badge.hot {{
            background: var(--danger);
        }}

        .section-title .badge.new {{
            background: var(--success);
        }}

        .key-points {{
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%);
            border: 1px solid var(--primary);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 40px;
        }}

        .key-points h3 {{
            color: var(--accent);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .key-points ul {{
            list-style: none;
        }}

        .key-points li {{
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }}

        .key-points li:last-child {{
            border-bottom: none;
        }}

        .key-points .bullet {{
            width: 24px;
            height: 24px;
            background: var(--primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        .key-points .point-text {{
            flex: 1;
        }}

        .key-points .point-tag {{
            background: var(--secondary);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-left: 8px;
        }}

        .key-points .point-tag.urgent {{
            background: var(--danger);
        }}

        .key-points .point-tag.new {{
            background: var(--success);
        }}

        .key-points .point-link {{
            color: var(--primary);
            text-decoration: none;
            font-size: 0.85rem;
            margin-left: 12px;
            white-space: nowrap;
        }}

        .key-points .point-link:hover {{
            color: var(--accent);
            text-decoration: underline;
        }}

        .key-points .point-text strong:hover {{
            color: var(--primary);
        }}

        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }}

        .news-card {{
            background: var(--bg-card);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border);
            transition: all 0.3s;
        }}

        .news-card:hover {{
            transform: translateY(-4px);
            border-color: var(--primary);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }}

        .news-card-header {{
            padding: 20px 20px 0;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}

        .news-category {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .category-finance {{ background: rgba(245, 158, 11, 0.2); color: var(--warning); }}
        .category-product {{ background: rgba(6, 182, 212, 0.2); color: var(--accent); }}
        .category-regulation {{ background: rgba(239, 68, 68, 0.2); color: var(--danger); }}
        .category-investment {{ background: rgba(16, 185, 129, 0.2); color: var(--success); }}
        .category-tech {{ background: rgba(124, 58, 237, 0.2); color: var(--secondary); }}
        .category-vip {{ background: rgba(251, 191, 36, 0.2); color: var(--gold); }}

        .news-date {{
            color: var(--text-secondary);
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .new-badge {{
            background: var(--success);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.65rem;
            font-weight: bold;
        }}

        .news-card-body {{
            padding: 16px 20px;
        }}

        .news-card h3 {{
            font-size: 1.1rem;
            margin-bottom: 12px;
            line-height: 1.4;
        }}

        .news-card h3 a {{
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.3s;
        }}

        .news-card h3 a:hover {{
            color: var(--primary);
        }}

        .news-card-footer {{
            padding: 16px 20px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .news-source {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}

        .source-icon {{
            width: 20px;
            height: 20px;
            background: var(--bg-card-hover);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
        }}

        .read-more {{
            color: var(--primary);
            text-decoration: none;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: gap 0.3s;
        }}

        .read-more:hover {{
            gap: 8px;
        }}

        .vip-section {{
            background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
            border: 1px solid var(--gold);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 40px;
        }}

        .vip-section .section-title {{
            border-bottom-color: var(--gold);
        }}

        .quotes-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}

        .quote-card {{
            background: var(--bg-card);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border);
            position: relative;
            transition: all 0.3s;
        }}

        .quote-card:hover {{
            transform: translateY(-4px);
            border-color: var(--gold);
            box-shadow: 0 10px 30px rgba(251, 191, 36, 0.1);
        }}

        .quote-card::before {{
            content: '"';
            position: absolute;
            top: 10px;
            left: 20px;
            font-size: 4rem;
            color: var(--gold);
            opacity: 0.3;
            font-family: Georgia, serif;
            line-height: 1;
        }}

        .quote-author {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }}

        .author-avatar {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            font-weight: bold;
            color: white;
        }}

        .author-info h4 {{
            font-size: 1rem;
            color: var(--text-primary);
        }}

        .author-info span {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        .quote-text {{
            font-style: italic;
            color: var(--text-primary);
            line-height: 1.6;
            margin-bottom: 16px;
            padding-left: 20px;
            position: relative;
            z-index: 1;
        }}

        .quote-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        .quote-source {{
            color: var(--primary);
            text-decoration: none;
        }}

        .finance-section {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(239, 68, 68, 0.05) 100%);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 40px;
        }}

        .finance-section .section-title {{
            border-bottom-color: var(--warning);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid var(--border);
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 4px;
        }}

        .stat-change {{
            font-size: 0.8rem;
            margin-top: 8px;
        }}

        .stat-change.up {{ color: var(--success); }}

        footer {{
            background: var(--bg-card);
            border-top: 1px solid var(--border);
            padding: 40px 0;
            margin-top: 40px;
        }}

        .footer-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 40px;
        }}

        .footer-section h4 {{
            color: var(--text-primary);
            margin-bottom: 16px;
        }}

        .footer-section p, .footer-section a {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            text-decoration: none;
            display: block;
            margin-bottom: 8px;
        }}

        .footer-section a:hover {{
            color: var(--primary);
        }}

        .footer-bottom {{
            text-align: center;
            padding-top: 30px;
            margin-top: 30px;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}

        @media (max-width: 768px) {{
            .news-grid {{
                grid-template-columns: 1fr;
            }}
            .quotes-grid {{
                grid-template-columns: 1fr;
            }}
            .header-content {{
                flex-direction: column;
                gap: 16px;
            }}
            .nav-links {{
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <div class="logo-icon">AI</div>
                    <div>
                        <h1>AI资讯中心</h1>
                        <span style="color: var(--text-secondary); font-size: 0.8rem;">全球人工智能与金融科技动态</span>
                    </div>
                </div>
                <div class="header-right">
                    <div class="next-update">
                        <div class="next-update-label">下次自动更新</div>
                        <div class="countdown" id="countdown">--:--:--</div>
                    </div>
                    <div class="update-info">
                        <div class="update-time">
                            <span class="live-dot"></span>
                            <span>最后更新: {date_info['formatted']} {date_info['time']}</span>
                        </div>
                        <div class="week-range">本周关注: {date_info['week_start_month']}月{date_info['week_start_day']}日 - {date_info['month']}月{date_info['day']}日</div>
                        <div class="auto-update-badge">每日自动更新</div>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <nav>
        <div class="container">
            <div class="nav-links">
                <a class="nav-link active" href="#all">全部资讯</a>
                <a class="nav-link hot" href="#vip">大咖言论</a>
                <a class="nav-link" href="#finance">金融应用</a>
                <a class="nav-link" href="#products">产品发布</a>
                <a class="nav-link" href="#global">全球动态</a>
            </div>
        </div>
    </nav>

    <main class="container">
        <!-- Key Points -->
        <section class="key-points">
            <h3>&#128161; 本周核心要点 ({date_info['week_start_month']}月{date_info['week_start_day']}日-{date_info['month']}月{date_info['day']}日)</h3>
            <ul>
'''

    # Add key points from news
    for i, item in enumerate(news_data.get('highlights', [])[:6], 1):
        tag_class = 'urgent' if i <= 2 else ('new' if i <= 4 else '')
        tag_text = '重磅' if i <= 2 else ('新闻' if i <= 4 else '关注')
        html += f'''                <li>
                    <span class="bullet">{i}</span>
                    <span class="point-text">
                        <a href="{item['url']}" target="_blank" style="color: inherit; text-decoration: none;"><strong>{item['title']}</strong></a>
                        <span class="point-tag {tag_class}">{tag_text}</span>
                        <a href="{item['url']}" target="_blank" class="point-link">阅读原文 &#8594;</a>
                    </span>
                </li>
'''

    html += '''            </ul>
        </section>

        <!-- VIP Quotes -->
        <section class="vip-section" id="vip">
            <div class="section-title">
                <h2>&#127775; AI大咖言论</h2>
                <span class="badge hot">本周热点</span>
            </div>
            <div class="quotes-grid">
'''

    # Add VIP quotes
    vip_leaders = [
        {"name": "Sam Altman", "title": "OpenAI CEO", "avatar": "SA"},
        {"name": "Jensen Huang", "title": "NVIDIA CEO", "avatar": "JH"},
        {"name": "Sundar Pichai", "title": "Google CEO", "avatar": "SP"},
        {"name": "Satya Nadella", "title": "Microsoft CEO", "avatar": "SN"},
    ]

    for i, leader in enumerate(vip_leaders):
        if i < len(news_data.get('vip_news', [])):
            news_item = news_data['vip_news'][i]
            html += f'''                <div class="quote-card">
                    <div class="quote-author">
                        <div class="author-avatar">{leader['avatar']}</div>
                        <div class="author-info">
                            <h4>{leader['name']}</h4>
                            <span>{leader['title']}</span>
                        </div>
                    </div>
                    <p class="quote-text">{news_item['title']}</p>
                    <div class="quote-meta">
                        <span>{date_info['month']}月</span>
                        <a href="{news_item['url']}" target="_blank" class="quote-source">查看来源</a>
                    </div>
                </div>
'''

    html += '''            </div>
        </section>

        <!-- Stats -->
        <section>
            <div class="section-title">
                <h2>&#128202; 市场数据概览</h2>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">$2.5T+</div>
                    <div class="stat-label">2026年AI支出预测</div>
                    <div class="stat-change up">持续增长</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">85%+</div>
                    <div class="stat-label">企业采用AI</div>
                    <div class="stat-change">全球趋势</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">40%</div>
                    <div class="stat-label">工作岗位受影响</div>
                    <div class="stat-change">IMF预测</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">24/7</div>
                    <div class="stat-label">实时更新</div>
                    <div class="stat-change">自动抓取</div>
                </div>
            </div>
        </section>

        <!-- Finance Section -->
        <section class="finance-section" id="finance">
            <div class="section-title">
                <h2>&#128176; AI金融行业应用</h2>
                <span class="badge">重点关注</span>
            </div>
            <div class="news-grid">
'''

    # Add finance news
    for item in news_data.get('finance_news', [])[:6]:
        html += f'''                <article class="news-card">
                    <div class="news-card-header">
                        <span class="news-category category-finance">金融</span>
                        <span class="news-date"><span class="new-badge">NEW</span> {date_info['month']}月</span>
                    </div>
                    <div class="news-card-body">
                        <h3><a href="{item['url']}" target="_blank">{item['title']}</a></h3>
                    </div>
                    <div class="news-card-footer">
                        <span class="news-source">
                            <span class="source-icon">AI</span>
                            AI News
                        </span>
                        <a href="{item['url']}" target="_blank" class="read-more">阅读原文 &#8594;</a>
                    </div>
                </article>
'''

    html += '''            </div>
        </section>

        <!-- Global AI News -->
        <section id="products">
            <div class="section-title">
                <h2>&#127758; 全球AI产品与技术动态</h2>
            </div>
            <div class="news-grid">
'''

    # Add global news
    for item in news_data.get('global_news', [])[:6]:
        html += f'''                <article class="news-card">
                    <div class="news-card-header">
                        <span class="news-category category-tech">科技</span>
                        <span class="news-date">{date_info['month']}月</span>
                    </div>
                    <div class="news-card-body">
                        <h3><a href="{item['url']}" target="_blank">{item['title']}</a></h3>
                    </div>
                    <div class="news-card-footer">
                        <span class="news-source">
                            <span class="source-icon">AI</span>
                            Tech News
                        </span>
                        <a href="{item['url']}" target="_blank" class="read-more">阅读原文 &#8594;</a>
                    </div>
                </article>
'''

    html += f'''            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>关于本站</h4>
                    <p>AI资讯中心汇集全球最新人工智能资讯，重点关注金融行业应用和大咖言论。</p>
                    <p style="margin-top: 12px; color: var(--accent);">每日自动更新 | 关注周期: 最近7天</p>
                </div>
                <div class="footer-section">
                    <h4>资讯来源</h4>
                    <a href="https://www.cnbc.com" target="_blank">CNBC</a>
                    <a href="https://techcrunch.com" target="_blank">TechCrunch</a>
                    <a href="https://www.reuters.com" target="_blank">Reuters</a>
                    <a href="https://www.bloomberg.com" target="_blank">Bloomberg</a>
                </div>
                <div class="footer-section">
                    <h4>免责声明</h4>
                    <p>内容由自动化程序整理生成</p>
                    <p>仅供参考，不构成投资建议</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; {date_info['year']} AI资讯中心 | 最后更新: {date_info['formatted']} | GitHub Actions 自动更新</p>
            </div>
        </div>
    </footer>

    <script>
        function updateCountdown() {{
            const now = new Date();
            const tomorrow = new Date(now);
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setHours(8, 0, 0, 0);
            if (now >= tomorrow) {{
                tomorrow.setDate(tomorrow.getDate() + 1);
            }}
            const diff = tomorrow - now;
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
            document.getElementById('countdown').textContent =
                hours.toString().padStart(2, '0') + ':' + minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
        }}
        updateCountdown();
        setInterval(updateCountdown, 1000);
    </script>
</body>
</html>
'''

    return html

def main():
    print("=" * 50)
    print("AI News Site Auto-Updater")
    print("=" * 50)

    date_info = get_current_date()
    print(f"Update time: {date_info['formatted']} {date_info['time']}")

    news_data = {
        'highlights': [],
        'vip_news': [],
        'finance_news': [],
        'global_news': []
    }

    # Get current date for search queries
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Search queries - using Chinese keywords with current date for latest news
    queries = {
        'highlights': [
            f"AI人工智能 重大突破 {current_year}年{current_month}月",
            f"OpenAI ChatGPT GPT-5 最新发布 {current_year}",
            f"AI大模型 发布 新闻 {current_year}年{current_month}月",
            "DeepSeek Claude Gemini 最新动态"
        ],
        'vip_news': [
            f"Sam Altman OpenAI 最新发言 {current_year}",
            f"黄仁勋 Jensen Huang NVIDIA 演讲 {current_year}",
            f"马斯克 Elon Musk AI xAI {current_year}",
            f"李彦宏 百度 文心一言 {current_year}"
        ],
        'finance_news': [
            f"AI金融 银行 大模型应用 {current_year}年{current_month}月",
            f"人工智能 量化交易 投资 {current_year}",
            f"AI风控 智能投顾 金融科技 {current_year}"
        ],
        'global_news': [
            f"AI芯片 GPU 算力 最新 {current_year}年{current_month}月",
            f"人工智能 融资 独角兽 {current_year}",
            f"AI产品 发布会 科技公司 {current_year}年{current_month}月"
        ]
    }

    # Fetch news for each category
    for category, query_list in queries.items():
        print(f"\nFetching {category}...")
        for query in query_list:
            results = search_news(query, num_results=3)
            news_data[category].extend(results)
            print(f"  - Found {len(results)} results for '{query}'")

    # Generate HTML
    print("\nGenerating HTML...")
    html_content = generate_html(news_data, date_info)

    # Write to file
    output_path = os.path.join(os.path.dirname(__file__), 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Updated: {output_path}")
    print("=" * 50)
    print("Update complete!")

if __name__ == "__main__":
    main()
