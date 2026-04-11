"""
Create a demo GIF for BenchMarked by rendering mockup HTML screens with Playwright
and assembling them into an animated GIF with Pillow.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from PIL import Image

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "demo-screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

VIEWPORT = {"width": 1280, "height": 720}

COMMON_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #0a0f1a 0%, #0d1525 50%, #0a1020 100%);
    color: #e2e8f0;
    min-height: 100vh;
    overflow: hidden;
}
.glass {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
}
header {
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding: 0 2rem;
}
.header-inner {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 64px;
}
.logo-wrap { display: flex; align-items: center; gap: 12px; }
.logo-icon {
    background: linear-gradient(135deg, #06b6d4, #2563eb);
    padding: 8px;
    border-radius: 12px;
    width: 40px; height: 40px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2);
}
.logo-icon svg { width: 24px; height: 24px; fill: white; }
.brand-name {
    font-size: 1.4rem; font-weight: 700;
    background: linear-gradient(90deg, #fff, #a5f3fc, #93c5fd);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-sub { font-size: 0.65rem; color: #94a3b8; letter-spacing: 2px; }
main { max-width: 1200px; margin: 0 auto; padding: 2rem; }
.cyan { color: #06b6d4; }
.card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-cyan { background: rgba(6,182,212,0.15); color: #06b6d4; border: 1px solid rgba(6,182,212,0.3); }
.badge-green { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 28px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.95rem;
    border: none;
    cursor: pointer;
}
.btn-primary {
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
    color: white;
    box-shadow: 0 4px 16px rgba(6, 182, 212, 0.3);
}
.grade {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px; height: 52px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 1.1rem;
}
.grade-a { background: rgba(6,182,212,0.15); color: #06b6d4; }
.grade-b { background: rgba(168,85,247,0.15); color: #a855f7; }
.progress-dot {
    width: 10px; height: 10px; border-radius: 50%;
    display: inline-block;
}
.dot-done { background: #06b6d4; }
.dot-active { background: #06b6d4; animation: pulse 1.5s infinite; }
.dot-pending { background: #334155; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
"""

HEADER_HTML = """
<header class="glass">
  <div class="header-inner">
    <div class="logo-wrap">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/></svg>
      </div>
      <div>
        <div class="brand-name">BenchMarked</div>
        <div class="brand-sub">INTELLIGENT CAREER ANALYSIS</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;">
      <span style="font-size:0.85rem;color:#94a3b8;">demo@benchmarked.app</span>
    </div>
  </div>
</header>
"""

SCREEN_1_OFFERS = f"""
<!DOCTYPE html><html><head><style>{COMMON_CSS}
.offers-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem; }}
.offer-card {{ position: relative; }}
.offer-card.selected {{ border-color: rgba(6,182,212,0.4); }}
.comp-row {{ display: flex; justify-content: space-between; padding: 6px 0; font-size: 0.9rem; }}
.comp-label {{ color: #94a3b8; }}
.comp-val {{ font-weight: 600; }}
.total {{ color: #06b6d4; font-size: 1.15rem; font-weight: 700; }}
.grades {{ display: flex; gap: 8px; margin-top: 1rem; }}
.grade-pill {{ text-align: center; }}
.grade-pill .label {{ font-size: 0.65rem; color: #94a3b8; margin-top: 4px; }}
.check {{ position: absolute; top: 1rem; right: 1rem; width: 24px; height: 24px; border-radius: 50%; background: #06b6d4; display: flex; align-items: center; justify-content: center; }}
.check svg {{ width: 14px; height: 14px; fill: white; }}
.bottom-bar {{ position: fixed; bottom: 0; left: 0; right: 0; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.05); }}
</style></head><body>
{HEADER_HTML}
<main>
  <section>
    <h2 style="font-size:1.5rem;font-weight:700;">Your Offers</h2>
    <p style="color:#94a3b8;margin-top:4px;">Compare your opportunities side-by-side</p>
    <div class="offers-grid">
      <div class="card offer-card selected">
        <div class="check"><svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg></div>
        <h3 style="font-size:1.2rem;font-weight:700;">Google</h3>
        <div style="color:#94a3b8;font-size:0.85rem;">Backend Engineer &nbsp;<span class="badge badge-cyan">L4 (SWE III)</span></div>
        <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">📍 Hyderabad, India &nbsp;&nbsp;<span class="badge badge-green">HYBRID</span></div>
        <div style="margin-top:1rem;padding:1rem;border-radius:12px;background:rgba(0,0,0,0.2);">
          <div class="comp-row"><span class="comp-label">Base Salary</span><span class="comp-val">₹55,00,000 (≈ $65,450)</span></div>
          <div class="comp-row"><span class="comp-label">Equity</span><span class="comp-val">₹20,00,000 (≈ $23,800)</span></div>
          <div class="comp-row"><span class="comp-label">Bonuses</span><span class="comp-val">₹15,50,000 (≈ $18,450)</span></div>
          <div class="comp-row" style="border-top:1px solid rgba(255,255,255,0.08);padding-top:8px;margin-top:4px;">
            <span class="comp-label">Total Comp</span><span class="total">₹80,50,000 (≈ $95,795)</span>
          </div>
        </div>
        <div class="grades">
          <div class="grade-pill"><div class="grade grade-a">A+</div><div class="label">BENEFITS</div></div>
          <div class="grade-pill"><div class="grade grade-b">B+</div><div class="label">WLB</div></div>
          <div class="grade-pill"><div class="grade grade-a">A+</div><div class="label">GROWTH</div></div>
        </div>
      </div>
      <div class="card offer-card selected">
        <div class="check"><svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg></div>
        <h3 style="font-size:1.2rem;font-weight:700;">Microsoft</h3>
        <div style="color:#94a3b8;font-size:0.85rem;">Backend Engineer &nbsp;<span class="badge badge-cyan">63 (SENIOR SDE)</span></div>
        <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">📍 Redmond, WA &nbsp;&nbsp;<span class="badge badge-green">HYBRID</span></div>
        <div style="margin-top:1rem;padding:1rem;border-radius:12px;background:rgba(0,0,0,0.2);">
          <div class="comp-row"><span class="comp-label">Base Salary</span><span class="comp-val">$160,000</span></div>
          <div class="comp-row"><span class="comp-label">Equity</span><span class="comp-val">$30,000</span></div>
          <div class="comp-row"><span class="comp-label">Bonuses</span><span class="comp-val">$40,000</span></div>
          <div class="comp-row" style="border-top:1px solid rgba(255,255,255,0.08);padding-top:8px;margin-top:4px;">
            <span class="comp-label">Total Comp</span><span class="total">$215,000</span>
          </div>
        </div>
        <div class="grades">
          <div class="grade-pill"><div class="grade grade-a">A</div><div class="label">BENEFITS</div></div>
          <div class="grade-pill"><div class="grade grade-a">A</div><div class="label">WLB</div></div>
          <div class="grade-pill"><div class="grade grade-a">A</div><div class="label">GROWTH</div></div>
        </div>
      </div>
    </div>
  </section>
</main>
<div class="bottom-bar glass">
  <div><strong>2</strong> <span style="color:#94a3b8;">Offers Selected for Comparison</span></div>
  <button class="btn btn-primary">✨ Run Quick Comparison</button>
</div>
</body></html>
"""

SCREEN_2_PROGRESS = f"""
<!DOCTYPE html><html><head><style>{COMMON_CSS}
.progress-container {{ max-width: 600px; margin: 3rem auto; }}
.progress-step {{ display: flex; align-items: center; gap: 16px; padding: 16px 0; }}
.step-icon {{ width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; }}
.step-done {{ background: rgba(6,182,212,0.15); color: #06b6d4; }}
.step-active {{ background: rgba(6,182,212,0.2); color: #06b6d4; border: 2px solid #06b6d4; animation: pulse 1.5s infinite; }}
.step-pending {{ background: rgba(51,65,85,0.3); color: #475569; }}
.step-text h4 {{ font-size: 0.95rem; font-weight: 600; }}
.step-text p {{ font-size: 0.8rem; color: #64748b; margin-top: 2px; }}
.progress-bar {{ width: 100%; height: 6px; background: #1e293b; border-radius: 3px; margin-top: 2rem; overflow: hidden; }}
.progress-fill {{ height: 100%; background: linear-gradient(90deg, #06b6d4, #3b82f6); border-radius: 3px; width: 60%; transition: width 0.3s; }}
</style></head><body>
{HEADER_HTML}
<main>
  <div class="progress-container">
    <h2 style="font-size:1.3rem;font-weight:700;text-align:center;margin-bottom:0.5rem;">Analyzing Your Offers</h2>
    <p style="text-align:center;color:#94a3b8;margin-bottom:2rem;">Deep analysis with real-time market data</p>
    <div class="card" style="padding:2rem;">
      <div class="progress-step">
        <div class="step-icon step-done">✓</div>
        <div class="step-text"><h4>Financial Analysis</h4><p>Tax calculations, cost of living adjustments</p></div>
      </div>
      <div class="progress-step">
        <div class="step-icon step-done">✓</div>
        <div class="step-text"><h4>Equity Risk Projection</h4><p>Stock scenarios, vesting analysis, risk assessment</p></div>
      </div>
      <div class="progress-step">
        <div class="step-icon step-active">📊</div>
        <div class="step-text"><h4>Market Benchmarking</h4><p>Comparing against industry standards...</p></div>
      </div>
      <div class="progress-step">
        <div class="step-icon step-pending">🤖</div>
        <div class="step-text"><h4>AI Recommendations</h4><p>Generating personalized insights</p></div>
      </div>
      <div class="progress-step">
        <div class="step-icon step-pending">📈</div>
        <div class="step-text"><h4>Visualization</h4><p>Building interactive charts</p></div>
      </div>
      <div class="progress-bar"><div class="progress-fill"></div></div>
    </div>
  </div>
</main>
</body></html>
"""

SCREEN_3_RESULTS = f"""
<!DOCTYPE html><html><head><style>{COMMON_CSS}
.tabs {{ display: flex; gap: 4px; margin-bottom: 1.5rem; background: rgba(15,23,42,0.5); border-radius: 12px; padding: 4px; }}
.tab {{ padding: 10px 20px; border-radius: 10px; font-size: 0.85rem; font-weight: 500; color: #94a3b8; cursor: pointer; }}
.tab.active {{ background: rgba(6,182,212,0.15); color: #06b6d4; }}
.rec-card {{ padding: 1.25rem; border-left: 3px solid; border-radius: 12px; margin-bottom: 1rem; background: rgba(15,23,42,0.4); }}
.score-ring {{ width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 800; }}
.radar-mock {{ width: 100%; height: 280px; background: rgba(6,182,212,0.05); border-radius: 12px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }}
.radar-mock::before {{ content: ''; position: absolute; width: 200px; height: 200px; border: 1px solid rgba(6,182,212,0.2); border-radius: 50%; }}
.radar-mock::after {{ content: ''; position: absolute; width: 140px; height: 140px; border: 1px solid rgba(6,182,212,0.15); border-radius: 50%; }}
.radar-shape {{ position: absolute; width: 160px; height: 160px; }}
.winner-badge {{ display: inline-flex; align-items: center; gap: 6px; padding: 6px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }}
.results-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
</style></head><body>
{HEADER_HTML}
<main>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">
    <div>
      <h2 style="font-size:1.4rem;font-weight:700;">AI Analysis Results</h2>
      <p style="color:#94a3b8;font-size:0.9rem;">Comprehensive Offer Analysis</p>
    </div>
    <button class="btn" style="background:rgba(6,182,212,0.15);color:#06b6d4;font-size:0.85rem;">📄 Export Results</button>
  </div>

  <div class="tabs">
    <div class="tab active">AI Recommendations</div>
    <div class="tab">Multi-Dimensional Analysis</div>
    <div class="tab">Decision Timeline</div>
    <div class="tab">Smart Choice</div>
  </div>

  <div class="results-grid">
    <div>
      <div class="rec-card" style="border-color:#06b6d4;">
        <div style="display:flex;justify-content:space-between;align-items:start;">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
              <span class="winner-badge" style="background:rgba(6,182,212,0.15);color:#06b6d4;">🏆 Top Pick</span>
            </div>
            <h3 style="font-size:1.15rem;font-weight:700;">Microsoft · Redmond</h3>
            <p style="color:#94a3b8;font-size:0.85rem;margin-top:4px;">Higher total compensation with strong growth trajectory. Excellent work-life balance and industry-leading benefits.</p>
          </div>
          <div class="score-ring" style="background:rgba(6,182,212,0.12);color:#06b6d4;">87</div>
        </div>
      </div>
      <div class="rec-card" style="border-color:#8b5cf6;">
        <div style="display:flex;justify-content:space-between;align-items:start;">
          <div>
            <h3 style="font-size:1.15rem;font-weight:700;">Google · Hyderabad</h3>
            <p style="color:#94a3b8;font-size:0.85rem;margin-top:4px;">Strong brand recognition with excellent learning opportunities. Cost of living advantage provides significant purchasing power.</p>
          </div>
          <div class="score-ring" style="background:rgba(139,92,246,0.12);color:#8b5cf6;">82</div>
        </div>
      </div>

      <div class="card" style="margin-top:1rem;">
        <h4 style="font-size:0.95rem;font-weight:600;margin-bottom:0.75rem;">Key Insights</h4>
        <div style="display:flex;flex-direction:column;gap:8px;">
          <div style="display:flex;align-items:start;gap:8px;font-size:0.85rem;">
            <span style="color:#22c55e;">💰</span>
            <span style="color:#cbd5e1;">Microsoft offers <strong>2.2x higher</strong> total compensation in absolute terms</span>
          </div>
          <div style="display:flex;align-items:start;gap:8px;font-size:0.85rem;">
            <span style="color:#f59e0b;">🏠</span>
            <span style="color:#cbd5e1;">Google Hyderabad has <strong>68% lower</strong> cost of living, improving purchasing power</span>
          </div>
          <div style="display:flex;align-items:start;gap:8px;font-size:0.85rem;">
            <span style="color:#8b5cf6;">📈</span>
            <span style="color:#cbd5e1;">Both roles offer <strong>strong equity growth</strong> potential over 4-year vesting</span>
          </div>
        </div>
      </div>
    </div>

    <div>
      <div class="card">
        <h4 style="font-size:0.95rem;font-weight:600;margin-bottom:1rem;">Multi-Dimensional Comparison</h4>
        <div class="radar-mock">
          <svg width="240" height="240" viewBox="0 0 240 240" style="position:absolute;">
            <polygon points="120,20 220,90 190,200 50,200 20,90" fill="none" stroke="rgba(6,182,212,0.2)" stroke-width="1"/>
            <polygon points="120,50 190,100 170,180 70,180 50,100" fill="none" stroke="rgba(6,182,212,0.15)" stroke-width="1"/>
            <polygon points="120,80 160,110 150,160 90,160 80,110" fill="none" stroke="rgba(6,182,212,0.1)" stroke-width="1"/>
            <!-- Microsoft (cyan) -->
            <polygon points="120,35 200,95 175,185 65,170 35,100" fill="rgba(6,182,212,0.12)" stroke="#06b6d4" stroke-width="2"/>
            <!-- Google (purple) -->
            <polygon points="120,45 180,100 160,175 80,185 40,95" fill="rgba(139,92,246,0.08)" stroke="#8b5cf6" stroke-width="2" stroke-dasharray="6,4"/>
            <!-- Labels -->
            <text x="120" y="14" fill="#94a3b8" text-anchor="middle" font-size="11">Compensation</text>
            <text x="230" y="92" fill="#94a3b8" text-anchor="start" font-size="11">Growth</text>
            <text x="200" y="210" fill="#94a3b8" text-anchor="middle" font-size="11">Benefits</text>
            <text x="40" y="210" fill="#94a3b8" text-anchor="middle" font-size="11">WLB</text>
            <text x="10" y="92" fill="#94a3b8" text-anchor="end" font-size="11">Location</text>
          </svg>
        </div>
        <div style="display:flex;justify-content:center;gap:24px;margin-top:12px;font-size:0.8rem;">
          <div style="display:flex;align-items:center;gap:6px;"><div style="width:12px;height:3px;background:#06b6d4;border-radius:2px;"></div><span style="color:#94a3b8;">Microsoft</span></div>
          <div style="display:flex;align-items:center;gap:6px;"><div style="width:12px;height:3px;background:#8b5cf6;border-radius:2px;border:1px dashed #8b5cf6;"></div><span style="color:#94a3b8;">Google</span></div>
        </div>
      </div>
    </div>
  </div>
</main>
</body></html>
"""

SCREEN_4_TIMELINE = f"""
<!DOCTYPE html><html><head><style>{COMMON_CSS}
.tabs {{ display: flex; gap: 4px; margin-bottom: 1.5rem; background: rgba(15,23,42,0.5); border-radius: 12px; padding: 4px; }}
.tab {{ padding: 10px 20px; border-radius: 10px; font-size: 0.85rem; font-weight: 500; color: #94a3b8; cursor: pointer; }}
.tab.active {{ background: rgba(6,182,212,0.15); color: #06b6d4; }}
.chart-area {{ width: 100%; height: 300px; position: relative; background: rgba(0,0,0,0.15); border-radius: 12px; padding: 1.5rem; }}
.equity-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem; }}
</style></head><body>
{HEADER_HTML}
<main>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">
    <div>
      <h2 style="font-size:1.4rem;font-weight:700;">AI Analysis Results</h2>
      <p style="color:#94a3b8;font-size:0.9rem;">Comprehensive Offer Analysis</p>
    </div>
  </div>

  <div class="tabs">
    <div class="tab">AI Recommendations</div>
    <div class="tab">Multi-Dimensional Analysis</div>
    <div class="tab active">Decision Timeline</div>
    <div class="tab">Smart Choice</div>
  </div>

  <div class="card" style="margin-bottom:1.5rem;">
    <h4 style="font-size:1rem;font-weight:600;margin-bottom:1rem;">📈 Equity Growth Projection (4-Year Vesting)</h4>
    <div class="chart-area">
      <svg width="100%" height="260" viewBox="0 0 700 260">
        <!-- Grid lines -->
        <line x1="60" y1="20" x2="60" y2="230" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
        <line x1="60" y1="230" x2="680" y2="230" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
        <line x1="60" y1="170" x2="680" y2="170" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
        <line x1="60" y1="110" x2="680" y2="110" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
        <line x1="60" y1="50" x2="680" y2="50" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
        <!-- Y-axis labels -->
        <text x="50" y="235" fill="#64748b" text-anchor="end" font-size="10">$0</text>
        <text x="50" y="175" fill="#64748b" text-anchor="end" font-size="10">$50K</text>
        <text x="50" y="115" fill="#64748b" text-anchor="end" font-size="10">$100K</text>
        <text x="50" y="55" fill="#64748b" text-anchor="end" font-size="10">$150K</text>
        <!-- X-axis labels -->
        <text x="120" y="250" fill="#64748b" text-anchor="middle" font-size="10">Year 1</text>
        <text x="280" y="250" fill="#64748b" text-anchor="middle" font-size="10">Year 2</text>
        <text x="440" y="250" fill="#64748b" text-anchor="middle" font-size="10">Year 3</text>
        <text x="600" y="250" fill="#64748b" text-anchor="middle" font-size="10">Year 4</text>
        <!-- Microsoft line (cyan) - bull scenario -->
        <polyline points="120,200 280,160 440,110 600,50" fill="none" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round"/>
        <!-- Microsoft flat scenario -->
        <polyline points="120,200 280,175 440,155 600,130" fill="none" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.5"/>
        <!-- Google line (purple) - bull scenario -->
        <polyline points="120,210 280,185 440,155 600,120" fill="none" stroke="#8b5cf6" stroke-width="2.5" stroke-linecap="round"/>
        <!-- Google flat scenario -->
        <polyline points="120,210 280,195 440,182 600,170" fill="none" stroke="#8b5cf6" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.5"/>
        <!-- Dots -->
        <circle cx="600" cy="50" r="5" fill="#06b6d4"/>
        <circle cx="600" cy="120" r="5" fill="#8b5cf6"/>
      </svg>
    </div>
    <div style="display:flex;justify-content:center;gap:24px;margin-top:8px;font-size:0.8rem;">
      <div style="display:flex;align-items:center;gap:6px;"><div style="width:16px;height:3px;background:#06b6d4;border-radius:2px;"></div><span style="color:#94a3b8;">Microsoft (Bull)</span></div>
      <div style="display:flex;align-items:center;gap:6px;"><div style="width:16px;height:3px;background:#06b6d4;border-radius:2px;opacity:0.5;"></div><span style="color:#64748b;">Microsoft (Flat)</span></div>
      <div style="display:flex;align-items:center;gap:6px;"><div style="width:16px;height:3px;background:#8b5cf6;border-radius:2px;"></div><span style="color:#94a3b8;">Google (Bull)</span></div>
      <div style="display:flex;align-items:center;gap:6px;"><div style="width:16px;height:3px;background:#8b5cf6;border-radius:2px;opacity:0.5;"></div><span style="color:#64748b;">Google (Flat)</span></div>
    </div>
  </div>

  <div class="equity-grid">
    <div class="card">
      <h4 style="font-size:0.95rem;font-weight:600;margin-bottom:0.75rem;">💼 Microsoft Cash-vs-Risk</h4>
      <div style="display:flex;align-items:center;gap:1.5rem;">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#1e293b" stroke-width="12"/>
          <circle cx="50" cy="50" r="40" fill="none" stroke="#06b6d4" stroke-width="12" stroke-dasharray="188 63" stroke-dashoffset="0" transform="rotate(-90 50 50)"/>
          <circle cx="50" cy="50" r="40" fill="none" stroke="#f59e0b" stroke-width="12" stroke-dasharray="63 188" stroke-dashoffset="-188" transform="rotate(-90 50 50)"/>
          <text x="50" y="47" fill="white" text-anchor="middle" font-size="14" font-weight="700">75%</text>
          <text x="50" y="60" fill="#94a3b8" text-anchor="middle" font-size="8">Cash</text>
        </svg>
        <div style="font-size:0.8rem;color:#94a3b8;">
          <div style="margin-bottom:4px;"><span style="color:#06b6d4;">●</span> Cash: $160K</div>
          <div><span style="color:#f59e0b;">●</span> Equity (risk-adj): $22K</div>
        </div>
      </div>
    </div>
    <div class="card">
      <h4 style="font-size:0.95rem;font-weight:600;margin-bottom:0.75rem;">💼 Google Cash-vs-Risk</h4>
      <div style="display:flex;align-items:center;gap:1.5rem;">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#1e293b" stroke-width="12"/>
          <circle cx="50" cy="50" r="40" fill="none" stroke="#8b5cf6" stroke-width="12" stroke-dasharray="176 75" stroke-dashoffset="0" transform="rotate(-90 50 50)"/>
          <circle cx="50" cy="50" r="40" fill="none" stroke="#f59e0b" stroke-width="12" stroke-dasharray="75 176" stroke-dashoffset="-176" transform="rotate(-90 50 50)"/>
          <text x="50" y="47" fill="white" text-anchor="middle" font-size="14" font-weight="700">70%</text>
          <text x="50" y="60" fill="#94a3b8" text-anchor="middle" font-size="8">Cash</text>
        </svg>
        <div style="font-size:0.8rem;color:#94a3b8;">
          <div style="margin-bottom:4px;"><span style="color:#8b5cf6;">●</span> Cash: ₹55L ($65K)</div>
          <div><span style="color:#f59e0b;">●</span> Equity (risk-adj): ₹15L ($18K)</div>
        </div>
      </div>
    </div>
  </div>
</main>
</body></html>
"""


async def capture_screens():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=2,
            color_scheme="dark",
        )
        page = await ctx.new_page()

        screens = [
            ("01-offers.png", SCREEN_1_OFFERS),
            ("02-progress.png", SCREEN_2_PROGRESS),
            ("03-results.png", SCREEN_3_RESULTS),
            ("04-timeline.png", SCREEN_4_TIMELINE),
        ]

        for filename, html in screens:
            await page.set_content(html, wait_until="networkidle")
            await page.wait_for_timeout(300)
            path = os.path.join(OUT_DIR, filename)
            await page.screenshot(path=path)
            print(f"Captured {filename}")

        await browser.close()
    return [os.path.join(OUT_DIR, s[0]) for s in screens]


def create_gif(image_paths: list[str], output_path: str, duration_ms: int = 2500):
    """Assemble screenshots into an animated GIF."""
    frames = []
    target_size = None

    for path in image_paths:
        img = Image.open(path).convert("RGBA")
        if target_size is None:
            target_size = img.size
        else:
            img = img.resize(target_size, Image.LANCZOS)

        bg = Image.new("RGBA", target_size, (10, 15, 26, 255))
        bg.paste(img, (0, 0), img)
        frames.append(bg.convert("RGB"))

    if not frames:
        print("No frames to assemble!")
        return

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )
    size_kb = os.path.getsize(output_path) / 1024
    print(f"GIF saved to {output_path} ({size_kb:.0f} KB, {len(frames)} frames, {duration_ms}ms/frame)")


async def main():
    print("=== Capturing mockup screens ===")
    image_paths = await capture_screens()

    print("\n=== Creating animated GIF ===")
    gif_path = os.path.join(OUT_DIR, "demo.gif")
    create_gif(image_paths, gif_path, duration_ms=2500)

    webp_path = os.path.join(OUT_DIR, "demo.webp")
    try:
        frames = [Image.open(p).convert("RGB") for p in image_paths]
        target_size = frames[0].size
        frames = [f.resize(target_size, Image.LANCZOS) if f.size != target_size else f for f in frames]
        frames[0].save(
            webp_path,
            save_all=True,
            append_images=frames[1:],
            duration=2500,
            loop=0,
            quality=85,
        )
        size_kb = os.path.getsize(webp_path) / 1024
        print(f"WebP saved to {webp_path} ({size_kb:.0f} KB)")
    except Exception as e:
        print(f"WebP creation failed (optional): {e}")


if __name__ == "__main__":
    asyncio.run(main())
