import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
out_dir = os.path.join(repo_root, "docs", "figures")
os.makedirs(out_dir, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.0

# =============================================================
# DATA DEFINITIONS FOR SIMULATED SIRED-2026 PILOT BENCHMARK
# =============================================================
appliances = ['kettle', 'freezer', 'washing machine', 'computer', 'microwave', 'television']
freqs = [1, 5, 15]

# Brand-new simulated benchmark results (Table 2 data)
table2_data = {
    'kettle': {
        'MAE': {
            'Seq2Point Intra': [14.8, 24.8, 28.2], 'Seq2Point Cross': [28.5, 25.2, 31.8],
            'SGN Intra': [9.2, 15.6, 31.4],        'SGN Cross': [24.8, 23.4, 26.5],
            'DAE Intra': [21.4, 33.2, 36.5],       'DAE Cross': [28.0, 35.8, 27.4],
            'BiLSTM Intra': [25.6, 34.0, 35.8],    'BiLSTM Cross': [33.5, 31.2, 27.6]
        },
        'F1-score': {
            'Seq2Point Intra': [0.74, 0.00, 0.00], 'Seq2Point Cross': [0.00, 0.00, 0.00],
            'SGN Intra': [0.81, 0.00, 0.00],       'SGN Cross': [0.00, 0.00, 0.00],
            'DAE Intra': [0.61, 0.00, 0.00],       'DAE Cross': [0.00, 0.00, 0.00],
            'BiLSTM Intra': [0.69, 0.00, 0.00],    'BiLSTM Cross': [0.00, 0.00, 0.00]
        },
        'NEP': {
            'Seq2Point Intra': [0.62, 1.03, 1.18], 'Seq2Point Cross': [6.85, 5.75, 7.60],
            'SGN Intra': [0.38, 0.65, 1.31],       'SGN Cross': [5.95, 5.35, 6.30],
            'DAE Intra': [0.89, 1.38, 1.52],       'DAE Cross': [6.72, 8.50, 6.50],
            'BiLSTM Intra': [1.07, 1.42, 1.49],    'BiLSTM Cross': [8.05, 7.42, 6.55]
        }
    },
    'freezer': {
        'MAE': {
            'Seq2Point Intra': [27.4, 28.6, 26.5], 'Seq2Point Cross': [12.8, 13.1, 10.2],
            'SGN Intra': [24.2, 31.8, 25.1],       'SGN Cross': [17.6, 14.2, 10.0],
            'DAE Intra': [31.5, 29.0, 25.8],       'DAE Cross': [14.9, 13.0, 10.4],
            'BiLSTM Intra': [38.0, 29.8, 24.6],    'BiLSTM Cross': [14.2, 12.9, 10.3]
        },
        'F1-score': {
            'Seq2Point Intra': [0.46, 0.50, 0.59], 'Seq2Point Cross': [0.87, 0.82, 0.88],
            'SGN Intra': [0.53, 0.49, 0.59],       'SGN Cross': [0.86, 0.80, 0.88],
            'DAE Intra': [0.44, 0.49, 0.59],       'DAE Cross': [0.79, 0.80, 0.88],
            'BiLSTM Intra': [0.41, 0.49, 0.59],    'BiLSTM Cross': [0.81, 0.80, 0.88]
        },
        'NEP': {
            'Seq2Point Intra': [1.16, 1.21, 1.12], 'Seq2Point Cross': [0.58, 0.60, 0.45],
            'SGN Intra': [1.02, 1.34, 1.06],       'SGN Cross': [0.80, 0.65, 0.44],
            'DAE Intra': [1.33, 1.23, 1.09],       'DAE Cross': [0.67, 0.60, 0.46],
            'BiLSTM Intra': [1.61, 1.26, 1.04],    'BiLSTM Cross': [0.64, 0.59, 0.45]
        }
    },
    'washing machine': {
        'MAE': {
            'Seq2Point Intra': [19.8, 32.4, 42.8], 'Seq2Point Cross': [27.2, 48.0, 40.8],
            'SGN Intra': [13.8, 23.8, 39.2],       'SGN Cross': [32.8, 40.5, 43.2],
            'DAE Intra': [35.2, 46.5, 44.8],       'DAE Cross': [60.5, 43.6, 39.8],
            'BiLSTM Intra': [46.5, 54.2, 51.5],    'BiLSTM Cross': [50.4, 44.8, 49.2]
        },
        'F1-score': {
            'Seq2Point Intra': [0.68, 0.40, 0.31], 'Seq2Point Cross': [0.27, 0.26, 0.21],
            'SGN Intra': [0.80, 0.68, 0.39],       'SGN Cross': [0.24, 0.23, 0.25],
            'DAE Intra': [0.34, 0.22, 0.33],       'DAE Cross': [0.23, 0.24, 0.26],
            'BiLSTM Intra': [0.14, 0.13, 0.25],    'BiLSTM Cross': [0.25, 0.25, 0.29]
        },
        'NEP': {
            'Seq2Point Intra': [0.49, 0.81, 1.07], 'Seq2Point Cross': [1.04, 1.81, 1.51],
            'SGN Intra': [0.35, 0.59, 0.98],       'SGN Cross': [1.22, 1.52, 1.61],
            'DAE Intra': [0.88, 1.16, 1.12],       'DAE Cross': [2.27, 1.63, 1.48],
            'BiLSTM Intra': [1.16, 1.35, 1.29],    'BiLSTM Cross': [1.89, 1.68, 1.84]
        }
    },
    'computer': {
        'MAE': {
            'Seq2Point Intra': [3.9, 5.4, 5.5],   'Seq2Point Cross': [17.2, 16.7, 15.6],
            'SGN Intra': [4.8, 4.5, 6.1],         'SGN Cross': [18.8, 17.1, 15.7],
            'DAE Intra': [4.9, 5.0, 5.4],         'DAE Cross': [18.7, 15.9, 15.8],
            'BiLSTM Intra': [8.9, 5.2, 5.5],      'BiLSTM Cross': [16.6, 15.7, 15.7]
        },
        'F1-score': {
            'Seq2Point Intra': [1.00, 1.00, 1.00], 'Seq2Point Cross': [0.49, 0.48, 0.49],
            'SGN Intra': [1.00, 1.00, 1.00],       'SGN Cross': [0.49, 0.48, 0.49],
            'DAE Intra': [1.00, 1.00, 1.00],       'DAE Cross': [0.49, 0.48, 0.49],
            'BiLSTM Intra': [0.74, 1.00, 1.00],    'BiLSTM Cross': [0.49, 0.48, 0.49]
        },
        'NEP': {
            'Seq2Point Intra': [0.22, 0.31, 0.32], 'Seq2Point Cross': [0.81, 0.78, 0.73],
            'SGN Intra': [0.27, 0.26, 0.35],       'SGN Cross': [0.88, 0.80, 0.74],
            'DAE Intra': [0.28, 0.29, 0.32],       'DAE Cross': [0.88, 0.74, 0.74],
            'BiLSTM Intra': [0.51, 0.31, 0.32],    'BiLSTM Cross': [0.78, 0.73, 0.73]
        }
    },
    'microwave': {
        'MAE': {
            'Seq2Point Intra': [10.6, 13.0, 12.0], 'Seq2Point Cross': [13.4, 11.8, 8.1],
            'SGN Intra': [7.1, 9.2, 11.2],         'SGN Cross': [11.2, 9.2, 7.1],
            'DAE Intra': [12.1, 12.9, 14.7],       'DAE Cross': [9.3, 9.3, 10.4],
            'BiLSTM Intra': [12.4, 14.6, 14.1],    'BiLSTM Cross': [15.4, 13.1, 10.7]
        },
        'F1-score': {
            'Seq2Point Intra': [0.25, 0.16, 0.33], 'Seq2Point Cross': [0.05, 0.09, 0.07],
            'SGN Intra': [0.41, 0.36, 0.32],       'SGN Cross': [0.19, 0.13, 0.00],
            'DAE Intra': [0.22, 0.17, 0.19],       'DAE Cross': [0.08, 0.06, 0.06],
            'BiLSTM Intra': [0.15, 0.13, 0.19],    'BiLSTM Cross': [0.06, 0.04, 0.04]
        },
        'NEP': {
            'Seq2Point Intra': [0.98, 1.24, 1.12], 'Seq2Point Cross': [1.32, 1.15, 0.78],
            'SGN Intra': [0.67, 0.86, 1.05],       'SGN Cross': [1.08, 0.88, 0.68],
            'DAE Intra': [1.13, 1.22, 1.38],       'DAE Cross': [0.90, 0.89, 1.01],
            'BiLSTM Intra': [1.15, 1.38, 1.32],    'BiLSTM Cross': [1.49, 1.26, 1.03]
        }
    },
    'television': {
        'MAE': {
            'Seq2Point Intra': [11.4, 10.2, 12.2], 'Seq2Point Cross': [39.5, 33.7, 39.9],
            'SGN Intra': [9.9, 8.8, 13.2],         'SGN Cross': [42.8, 33.6, 41.7],
            'DAE Intra': [11.9, 14.3, 14.8],       'DAE Cross': [34.9, 39.0, 45.4],
            'BiLSTM Intra': [12.3, 14.4, 17.8],    'BiLSTM Cross': [40.5, 46.8, 48.9]
        },
        'F1-score': {
            'Seq2Point Intra': [0.67, 0.60, 0.57], 'Seq2Point Cross': [0.42, 0.58, 0.39],
            'SGN Intra': [0.72, 0.73, 0.46],       'SGN Cross': [0.46, 0.56, 0.30],
            'DAE Intra': [0.62, 0.57, 0.51],       'DAE Cross': [0.48, 0.39, 0.36],
            'BiLSTM Intra': [0.69, 0.60, 0.57],    'BiLSTM Cross': [0.42, 0.39, 0.38]
        },
        'NEP': {
            'Seq2Point Intra': [0.41, 0.37, 0.44], 'Seq2Point Cross': [1.07, 0.91, 1.08],
            'SGN Intra': [0.35, 0.31, 0.47],       'SGN Cross': [1.16, 0.91, 1.13],
            'DAE Intra': [0.43, 0.52, 0.53],       'DAE Cross': [0.94, 1.05, 1.23],
            'BiLSTM Intra': [0.45, 0.52, 0.64],    'BiLSTM Cross': [1.10, 1.26, 1.32]
        }
    }
}

# -------------------------------------------------------------
# FIGURE 1: Modern Sectoral Electricity Consumption Trend (2015-2026)
# -------------------------------------------------------------
print("Generating Fig 1 (Modern Sectoral Trend 2015-2026)...")
years = np.arange(2015, 2027)
res = np.array([86.4, 90.1, 94.8, 99.5, 104.2, 108.6, 114.0, 119.5, 125.2, 131.0, 137.2, 143.5])
ind = np.array([112.0, 113.2, 114.5, 115.8, 116.4, 114.2, 117.5, 118.9, 120.1, 121.2, 122.0, 122.5])
com = np.array([68.5, 70.8, 73.4, 76.2, 79.0, 76.5, 80.8, 83.9, 87.2, 90.5, 93.8, 96.8])
agr = np.array([36.8, 37.2, 37.6, 38.0, 38.4, 38.8, 39.1, 39.4, 39.7, 40.0, 40.2, 40.4])
trn = np.array([14.2, 15.0, 16.1, 17.5, 19.2, 19.8, 22.0, 24.8, 28.2, 31.9, 35.8, 39.5])

fig1, ax1 = plt.subplots(figsize=(10.5, 5.2), dpi=300)
ax1.plot(years, res, label='Residential (Electrification & HVAC)', color='#D97706', linewidth=2.6, marker='o', markersize=5.5)
ax1.plot(years, ind, label='Industrial (Automated Efficiency)', color='#DC2626', linewidth=2.4, marker='s', markersize=5)
ax1.plot(years, com, label='Commercial & Cloud IT Services', color='#0D9488', linewidth=2.4, marker='^', markersize=5)
ax1.plot(years, agr, label='Agricultural & Rural Pumping', color='#15803D', linewidth=2.2, marker='v', markersize=4.5)
ax1.plot(years, trn, label='Electrified Transport & Rail', color='#2563EB', linewidth=2.4, marker='d', markersize=5)

ax1.set_xlim(2015, 2026)
ax1.set_ylim(0, 160)
ax1.set_yticks([0, 30, 60, 90, 120, 150])
ax1.set_yticklabels(['0', '30 TWh', '60 TWh', '90 TWh', '120 TWh', '150 TWh'])
ax1.set_xlabel('Year', fontsize=12, labelpad=8, fontweight='bold')
ax1.set_ylabel('Annual Final Electricity Demand (TWh)', fontsize=12, labelpad=8, fontweight='bold')
ax1.set_xticks(years)
ax1.set_xticklabels([str(y) for y in years], rotation=0)
ax1.grid(axis='y', linestyle='--', alpha=0.35, color='#aaaaaa')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, framealpha=0.92, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9.8)
plt.title("Evolution of Final Electricity Demand by Economic Sector (2015–2026)\nHighlighting Accelerating Residential Electrification and Transport Decarbonization", 
          fontsize=12, fontweight='bold', pad=14, loc='left')
plt.tight_layout()
fig1.savefig(os.path.join(out_dir, "fig1_sector_evolution.png"), dpi=300, bbox_inches='tight')
plt.close(fig1)

# -------------------------------------------------------------
# FIGURE 2: 2025/2026 Sectoral Consumption Share Bar Chart
# -------------------------------------------------------------
print("Generating Fig 2 (2025/2026 Sectoral Share Breakdown)...")
labels_fig2 = [
    'Residential\n32.4% (143.5 TWh)', 
    'Industrial\n27.7% (122.5 TWh)', 
    'Commercial & IT\n21.9% (96.8 TWh)', 
    'Agriculture\n9.1% (40.4 TWh)', 
    'Transport (EV)\n8.9% (39.5 TWh)'
]
shares_fig2 = [32.4, 27.7, 21.9, 9.1, 8.9]
colors_fig2 = ['#D97706', '#DC2626', '#0D9488', '#15803D', '#2563EB']

fig2, ax2 = plt.subplots(figsize=(11.5, 2.9), dpi=300)
left = 0
for i, (share, color, label) in enumerate(zip(shares_fig2, colors_fig2, labels_fig2)):
    ax2.barh([0], [share], left=left, color=color, height=0.62, edgecolor='#ffffff', linewidth=1.5)
    if share > 15:
        ax2.text(left + share/2, 0, label, ha='center', va='center', fontsize=9.8, fontweight='bold', color='white')
    elif share == 9.1:
        ax2.text(left + share/2, 0, "Agri\n9.1%", ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    else: # Transport 8.9%
        ax2.text(left + share/2 + 2.8, 0.46, "Transport (EV)\n8.9% (39.5 TWh)", ha='center', va='center', fontsize=9, fontweight='bold', color='#2563EB')
        ax2.annotate('', xy=(left + share/2, 0.32), xytext=(left + share/2 + 2.2, 0.41),
                     arrowprops=dict(arrowstyle="->", color='#2563EB', lw=1.2))
    left += share

ax2.set_xlim(0, 108)
ax2.set_ylim(-0.55, 0.75)
ax2.axis('off')
plt.title("2025/2026 Macro Sectoral Electricity Demand Breakdown (Total Final Energy: 442.7 TWh)", 
          fontsize=12, fontweight='bold', pad=12, loc='left')
plt.tight_layout()
fig2.savefig(os.path.join(out_dir, "fig2_sector_share.png"), dpi=300, bbox_inches='tight')
plt.close(fig2)

# -------------------------------------------------------------
# FIGURE 3: Modern Residential Electricity End-Use Breakdown (Donut Chart)
# -------------------------------------------------------------
print("Generating Fig 3 (Modern Residential End-Use Breakdown)...")
fig3, ax3 = plt.subplots(figsize=(8.0, 8.0), dpi=300)

labels_fig3 = [
    'Space Cooling & HVAC\n25%',
    'Water Heating (Geysers)\n18%',
    'Cooking & Induction\n15%',
    'Refrigeration & Cooling\n11%',
    'Computing & Home IT\n10%',
    'Laundry & Washing\n8%',
    'Lighting (LED)\n7%',
    'EV & Miscellaneous\n6%'
]
sizes_fig3 = [25, 18, 15, 11, 10, 8, 7, 6]
colors_fig3 = [
    '#9A3412',  # Deep Rust (Cooling / HVAC)
    '#EA580C',  # Vibrant Orange (Hot Water)
    '#D97706',  # Amber (Cooking)
    '#0D9488',  # Teal (Refrigeration)
    '#2563EB',  # Royal Blue (IT / Computing)
    '#4F46E5',  # Indigo (Laundry)
    '#059669',  # Emerald (Lighting)
    '#475569'   # Slate Gray (EV & Misc)
]

wedges, _ = ax3.pie(
    sizes_fig3,
    colors=colors_fig3,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(width=0.6, edgecolor='white', linewidth=1.8, antialiased=True)
)

# Radial text placement
current_angle = 90.0
for size, label in zip(sizes_fig3, labels_fig3):
    mid_angle = current_angle - (size * 3.6) / 2.0
    rad = np.radians(mid_angle)
    r = 0.70
    x = r * np.cos(rad)
    y = r * np.sin(rad)
    fs = 9.0 if size < 8 else 9.8
    ax3.text(x, y, label, ha='center', va='center', color='white', 
             fontweight='bold', fontsize=fs)
    current_angle -= size * 3.6

# Central annotation
ax3.text(0, 0, "Modern\nResidential\nEnd-Use\n2025–2026", ha='center', va='center', 
         fontsize=12, fontweight='bold', color='#1E293B')

ax3.axis('equal')
plt.title("Residential Electricity Consumption Breakdown by End-Use Category\n(Synthesized Modern Household Electrification Profile)", 
          fontsize=12, fontweight='bold', pad=16)
plt.tight_layout()
fig3.savefig(os.path.join(out_dir, "fig3_residential_end_use.png"), dpi=300, bbox_inches='tight')
plt.close(fig3)

# -------------------------------------------------------------
# FIGURE 4: Original NILM Framework & Simulation Workflow Flowchart
# -------------------------------------------------------------
print("Generating Fig 4 (Simulation & Edge NILM Framework Flowchart)...")
fig4, ax4 = plt.subplots(figsize=(9.2, 12.5), dpi=300)
ax4.set_xlim(0, 10)
ax4.set_ylim(-0.5, 13.5)
ax4.axis('off')

def draw_box(x, y, w, h, text, bg_color='#E0F2FE', edge_color='#0284C7', text_color='#0F172A', fontsize=10, bold=False):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                         facecolor=bg_color, edgecolor=edge_color, linewidth=1.4)
    ax4.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax4.text(x, y, text, ha='center', va='center', fontsize=fontsize, fontweight=weight, color=text_color)
    return box

def draw_arrow(x1, y1, x2, y2, color='#334155'):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='->,head_width=3.8,head_length=5.5',
                            color=color, linewidth=1.4)
    ax4.add_patch(arrow)

# Flowchart elements
draw_box(5.0, 12.6, 6.2, 0.75, "Raw Residential Grid Telemetry & Synthesis\n(SIRED-2026 Pilot: 20 Homes, 2025–2026)", 
         bg_color='#DBEAFE', edge_color='#1D4ED8', bold=True, fontsize=10.5)
draw_arrow(5.0, 12.2, 5.0, 11.4)

draw_box(5.0, 11.0, 5.0, 0.75, "Temporal Downsampling Engine\n(Emulating Utility Smart Metering Constraints)", 
         bg_color='#E0E7FF', edge_color='#4338CA', bold=True, fontsize=10.5)
draw_arrow(5.0, 10.6, 2.5, 9.85)
draw_arrow(5.0, 10.6, 5.0, 9.85)
draw_arrow(5.0, 10.6, 7.5, 9.85)

draw_box(2.5, 9.5, 2.2, 0.7, "1 Minute\n(Near-Real-Time)", bg_color='#F1F5F9', edge_color='#64748B', fontsize=9.5, bold=True)
draw_box(5.0, 9.5, 2.2, 0.7, "5 Minutes\n(Sub-Interval)", bg_color='#F1F5F9', edge_color='#64748B', fontsize=9.5, bold=True)
draw_box(7.5, 9.5, 2.2, 0.7, "15 Minutes\n(Utility Standard)", bg_color='#F1F5F9', edge_color='#64748B', fontsize=9.5, bold=True)

draw_arrow(2.5, 9.15, 4.5, 8.4)
draw_arrow(5.0, 9.15, 5.0, 8.4)
draw_arrow(7.5, 9.15, 5.5, 8.4)

draw_box(5.0, 8.0, 4.8, 0.75, "Dataset Segmentation & Validation Protocols", 
         bg_color='#FEF3C7', edge_color='#D97706', bold=True, fontsize=10.5)
draw_arrow(4.2, 7.6, 3.4, 6.9)
draw_arrow(5.8, 7.6, 6.6, 6.9)

draw_box(3.4, 6.5, 2.6, 0.75, "Pilot Zone A\n(Intra-Domain)", bg_color='#FFEDD5', edge_color='#EA580C', bold=True, fontsize=10)
draw_box(6.6, 6.5, 2.6, 0.75, "Pilot Zone B\n(Cross-Domain Transfer)", bg_color='#FFEDD5', edge_color='#EA580C', bold=True, fontsize=10)

draw_arrow(3.4, 6.1, 3.4, 5.35)
draw_arrow(3.6, 6.1, 6.4, 5.35)
draw_arrow(6.6, 6.1, 6.6, 5.35)

draw_box(3.4, 5.0, 2.8, 0.7, "Intra-Domain Test\n(1-Year Training / 1-Mo Test)", bold=True, fontsize=9.5)
draw_box(6.6, 5.0, 2.8, 0.7, "Cross-Domain Test\n(Zero-Shot Adaptation)", bold=True, fontsize=9.5)

draw_arrow(3.4, 4.65, 4.8, 3.9)
draw_arrow(6.6, 4.65, 5.2, 3.9)

draw_box(5.0, 3.5, 5.2, 0.75, "Multi-Paradigm NILM Algorithm Engine", 
         bg_color='#FEE2E2', edge_color='#DC2626', bold=True, fontsize=11)

# nilmtk container box
nilmtk_box = FancyBboxPatch((0.4, 1.8), 3.2, 1.25, boxstyle="round,pad=0.08,rounding_size=0.1",
                            facecolor='#F3E8FF', edgecolor='#9333EA', linewidth=1.2)
ax4.add_patch(nilmtk_box)
ax4.text(2.0, 2.78, "Classical Benchmarks (nilmtk)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#6B21A8')
draw_box(1.2, 2.2, 1.3, 0.55, "FHMM", bg_color='#E9D5FF', edge_color='#7E22CE', bold=True)
draw_box(2.8, 2.2, 1.3, 0.55, "CO", bg_color='#E9D5FF', edge_color='#7E22CE', bold=True)

# Neural_NILM container box
neural_box = FancyBboxPatch((3.8, 1.8), 5.8, 1.25, boxstyle="round,pad=0.08,rounding_size=0.1",
                            facecolor='#CCFBF1', edgecolor='#0D9488', linewidth=1.2)
ax4.add_patch(neural_box)
ax4.text(6.7, 2.78, "Deep Neural Architectures (PyTorch)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#115E59')
draw_box(4.5, 2.2, 1.25, 0.55, "Seq2Point", bg_color='#99F6E4', edge_color='#0F766E', bold=True, fontsize=8.5)
draw_box(5.9, 2.2, 1.25, 0.55, "DAE", bg_color='#99F6E4', edge_color='#0F766E', bold=True, fontsize=8.5)
draw_box(7.3, 2.2, 1.25, 0.55, "SGN", bg_color='#99F6E4', edge_color='#0F766E', bold=True, fontsize=8.5)
draw_box(8.7, 2.2, 1.25, 0.55, "BiLSTM", bg_color='#99F6E4', edge_color='#0F766E', bold=True, fontsize=8.5)

draw_arrow(4.2, 3.1, 2.0, 3.05)
draw_arrow(5.8, 3.1, 6.7, 3.05)

# Performance Assessment
draw_box(5.0, 1.0, 5.0, 0.7, "Multi-Objective Performance Assessment\n& Pareto Composite Optimization", 
         bg_color='#DCFCE7', edge_color='#16A34A', bold=True, fontsize=10.5)
draw_arrow(2.0, 1.8, 4.2, 1.35)
draw_arrow(6.7, 1.8, 5.8, 1.35)

# Metrics at bottom
draw_box(2.2, 0.25, 1.8, 0.5, "MAE (W)", bg_color='#BBF7D0', edge_color='#15803D', bold=True, fontsize=9.5)
draw_box(5.0, 0.25, 1.8, 0.5, "F1-Score (-)", bg_color='#BBF7D0', edge_color='#15803D', bold=True, fontsize=9.5)
draw_box(7.8, 0.25, 1.8, 0.5, "NEP (-)", bg_color='#BBF7D0', edge_color='#15803D', bold=True, fontsize=9.5)

draw_arrow(4.1, 0.65, 2.5, 0.5)
draw_arrow(5.0, 0.65, 5.0, 0.5)
draw_arrow(5.9, 0.65, 7.5, 0.5)

plt.tight_layout()
fig4.savefig(os.path.join(out_dir, "fig4_nilm_framework_flowchart.png"), dpi=300, bbox_inches='tight')
plt.close(fig4)

# -------------------------------------------------------------
# FIGURE 5: 18-Panel Multi-Grid Performance Across Sampling Frequencies
# -------------------------------------------------------------
print("Generating Fig 5 (18-Panel Multi-Grid Benchmark Plot)...")

series_styles = [
    ('Seq2Point Intra', '#2563EB', '-', 'o'),
    ('Seq2Point Cross', '#2563EB', '--', 'o'),
    ('SGN Intra',       '#0D9488', '-', 's'),
    ('SGN Cross',       '#0D9488', '--', 's'),
    ('DAE Intra',       '#DC2626', '-', '^'),
    ('DAE Cross',       '#DC2626', '--', '^'),
    ('BiLSTM Intra',    '#7C3AED', '-', 'd'),
    ('BiLSTM Cross',    '#7C3AED', '--', 'd')
]

metrics = ['MAE', 'F1-score', 'NEP']
metric_labels = ['MAE (W)', 'F1-Score (-)', 'NEP (-)']

fig5, axes = plt.subplots(3, 6, figsize=(15.5, 10.5), dpi=300, sharex=True)

for col_idx, app in enumerate(appliances):
    title_str = app.replace('washing machine', 'Washing Machine').capitalize() if app != 'washing machine' else 'Washing Machine'
    axes[0, col_idx].set_title(title_str, fontsize=12, pad=12, fontweight='bold')
    
    for row_idx, met in enumerate(metrics):
        ax = axes[row_idx, col_idx]
        
        for s_name, s_color, s_ls, s_marker in series_styles:
            vals = table2_data[app][met][s_name]
            ax.plot(freqs, vals, label=s_name, color=s_color, linestyle=s_ls, 
                    marker=s_marker, markersize=5, linewidth=1.6, alpha=0.92)
            
        ax.set_xticks(freqs)
        ax.set_xticklabels(['1 min', '5 min', '15 min'], fontsize=9.5)
        ax.grid(True, linestyle=':', alpha=0.45, color='#94a3b8')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Consistent Y-axis limits per row
        if row_idx == 0: # MAE
            ax.set_ylim(-2, 70)
            ax.set_yticks([0, 20, 40, 60])
        elif row_idx == 1: # F1-score
            ax.set_ylim(-0.05, 1.05)
            ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        elif row_idx == 2: # NEP
            ax.set_ylim(-0.5, 10.5)
            ax.set_yticks([0, 2, 4, 6, 8, 10])
                
        if col_idx == 0:
            ax.set_ylabel(metric_labels[row_idx], fontsize=12, labelpad=8, fontweight='bold')
        else:
            ax.set_yticklabels([])

fig5.text(0.52, 0.02, 'Smart Meter Downsampling Interval', ha='center', va='center', fontsize=12.5, fontweight='bold')

handles, labels = axes[0, 0].get_legend_handles_labels()
fig5.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.99), 
            ncol=8, frameon=True, framealpha=0.95, edgecolor='#cbd5e1', fontsize=10, handletextpad=0.4, columnspacing=1.2)

plt.subplots_adjust(top=0.92, bottom=0.07, left=0.06, right=0.98, hspace=0.18, wspace=0.12)
fig5.savefig(os.path.join(out_dir, "fig5_multi_panel_performance_grid.png"), dpi=300, bbox_inches='tight')
plt.close(fig5)

print("All publication figures generated and saved successfully!")
