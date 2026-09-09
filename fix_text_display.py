#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('NPI_dashboard_new.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add :root definitions in <style>
root_vars = """
    :root {
      --bg-page: #f5f5f7;
      --bg-card: #ffffff;
      --border-color: #e5e5ea;
      --text-main: #1d1d1f;
      --text-secondary: #6e6e73;
      --text-muted: #86868b;
      --accent-blue: #0071e3;
      --accent-blue-subtle: rgba(0, 113, 227, 0.08);
      --accent-purple: #af52de;
      --accent-gray: #8e8e93;
      --accent-green: #34c759;
      --accent-red: #ff3b30;
      --bar-bg: #eef0f4;
    }
"""

if ':root {' not in content:
    content = content.replace('<style>', '<style>' + root_vars)

# 2. Fix CSS rules for bubbles with bulletproof background & text colors
old_bubble_css = """    .ai-msg-row.user .ai-msg-bubble {
      background: var(--accent-blue);
      color: #ffffff;
      border-bottom-right-radius: 4px;
      box-shadow: 0 3px 10px rgba(0, 113, 227, 0.25);
    }

    .ai-msg-row.assistant .ai-msg-bubble {
      background: #f7f8fa;
      color: var(--text-main);
      border: 1px solid #ebedf2;
      border-bottom-left-radius: 4px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
    }"""

new_bubble_css = """    .ai-msg-row.user .ai-msg-bubble {
      background: #0071e3 !important;
      color: #ffffff !important;
      border-bottom-right-radius: 4px;
      box-shadow: 0 3px 12px rgba(0, 113, 227, 0.3);
      font-size: 13.5px;
      font-weight: 500;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .ai-msg-row.assistant .ai-msg-bubble {
      background: #f7f8fa !important;
      color: #1d1d1f !important;
      border: 1px solid #ebedf2 !important;
      border-bottom-left-radius: 4px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
      font-size: 13px;
      line-height: 1.6;
      word-break: break-word;
    }"""

if old_bubble_css in content:
    content = content.replace(old_bubble_css, new_bubble_css)

# 3. Update appendMessage to ensure user message textContent is directly set
old_append_msg = """function appendMessage(role, htmlContent) {
      const container = document.getElementById('ai-messages-container');
      const row = document.createElement('div');
      row.className = `ai-msg-row ${role}`;
      row.innerHTML = `<div class="ai-msg-bubble">${htmlContent}</div>`;
      container.appendChild(row);
      container.scrollTop = container.scrollHeight;
    }"""

new_append_msg = """function appendMessage(role, content) {
      const container = document.getElementById('ai-messages-container');
      const row = document.createElement('div');
      row.className = `ai-msg-row ${role}`;
      const bubble = document.createElement('div');
      bubble.className = 'ai-msg-bubble';
      
      if (role === 'user') {
          bubble.textContent = content; // 确保用户输入文本直接显示，不被 HTML 解析异常拦截
      } else {
          bubble.innerHTML = content;
      }
      row.appendChild(bubble);
      container.appendChild(row);
      container.scrollTop = container.scrollHeight;
    }"""

if old_append_msg in content:
    content = content.replace(old_append_msg, new_append_msg)

with open('NPI_dashboard_new.html', 'w', encoding='utf-8') as f:
    f.write(content)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Patched styles and appendMessage successfully!')
