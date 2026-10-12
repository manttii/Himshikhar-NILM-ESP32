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
            'Seq2Point Intra': [16.2, 23.4, 26.5], 'Seq2Point Cross': [26.8, 23.1, 29.8],
            'SGN Intra': [10.3, 13.9, 29.8],       'SGN Cross': [23.2, 21.6, 24.9],
            'DAE Intra': [18.9, 31.8, 34.2],       'DAE Cross': [26.5, 33.7, 25.6],
            'BiLSTM Intra': [23.1, 32.5, 33.6],    'BiLSTM Cross': [31.2, 29.4, 25.8]
        },
        'F1-score': {
            'Seq2Point Intra': [0.71, 0.00, 0.00], 'Seq2Point Cross': [0.00, 0.00, 0.00],
            'SGN Intra': [0.79, 0.00, 0.00],       'SGN Cross': [0.00, 0.00, 0.00],
            'DAE Intra': [0.64, 0.00, 0.00],       'DAE Cross': [0.00, 0.00, 0.00],
            'BiLSTM Intra': [0.73, 0.00, 0.00],    'BiLSTM Cross': [0.00, 0.00, 0.00]
        },
        'NEP': {
            'Seq2Point Intra': [0.76, 1.14, 1.32], 'Seq2Point Cross': [7.25, 6.08, 8.04],
            'SGN Intra': [0.48, 0.68, 1.54],       'SGN Cross': [6.28, 5.65, 6.68],
            'DAE Intra': [0.91, 1.58, 1.74],       'DAE Cross': [7.18, 8.95, 6.88],
            'BiLSTM Intra': [1.15, 1.62, 1.71],    'BiLSTM Cross': [8.45, 7.82, 6.92]
        }
    },
    'freezer': {
        'MAE': {
            'Seq2Point Intra': [29.8, 31.0, 28.2], 'Seq2Point Cross': [14.2, 14.5, 11.2],
            'SGN Intra': [26.4, 34.1, 26.9],       'SGN Cross': [19.4, 15.6, 11.0],
            'DAE Intra': [33.9, 31.2, 27.5],       'DAE Cross': [16.5, 14.4, 11.4],
            'BiLSTM Intra': [41.2, 32.1, 26.2],    'BiLSTM Cross': [15.8, 14.3, 11.3]
        },
        'F1-score': {
            'Seq2Point Intra': [0.44, 0.48, 0.57], 'Seq2Point Cross': [0.85, 0.80, 0.86],
            'SGN Intra': [0.51, 0.47, 0.57],       'SGN Cross': [0.84, 0.78, 0.86],
            'DAE Intra': [0.42, 0.47, 0.57],       'DAE Cross': [0.77, 0.78, 0.86],
            'BiLSTM Intra': [0.39, 0.47, 0.57],    'BiLSTM Cross': [0.79, 0.78, 0.86]
        },
        'NEP': {
            'Seq2Point Intra': [1.39, 1.46, 1.31], 'Seq2Point Cross': [0.65, 0.67, 0.50],
            'SGN Intra': [1.23, 1.59, 1.25],       'SGN Cross': [0.90, 0.73, 0.50],
            'DAE Intra': [1.58, 1.45, 1.29],       'DAE Cross': [0.76, 0.67, 0.52],
            'BiLSTM Intra': [1.94, 1.49, 1.23],    'BiLSTM Cross': [0.73, 0.67, 0.51]
        }
    },
    'washing machine': {
        'MAE': {
            'Seq2Point Intra': [21.8, 35.4, 46.1], 'Seq2Point Cross': [29.5, 51.2, 43.5],
            'SGN Intra': [15.4, 26.2, 42.4],       'SGN Cross': [35.4, 43.5, 46.2],
            'DAE Intra': [38.6, 50.4, 48.2],       'DAE Cross': [64.8, 46.8, 42.8],
            'BiLSTM Intra': [50.2, 58.2, 55.4],    'BiLSTM Cross': [54.2, 47.9, 52.8]
        },
        'F1-score': {
            'Seq2Point Intra': [0.66, 0.38, 0.29], 'Seq2Point Cross': [0.25, 0.24, 0.19],
            'SGN Intra': [0.78, 0.65, 0.37],       'SGN Cross': [0.22, 0.21, 0.23],
            'DAE Intra': [0.32, 0.20, 0.31],       'DAE Cross': [0.21, 0.22, 0.24],
            'BiLSTM Intra': [0.12, 0.11, 0.23],    'BiLSTM Cross': [0.23, 0.23, 0.27]
        },
        'NEP': {
            'Seq2Point Intra': [0.58, 0.95, 1.24], 'Seq2Point Cross': [1.18, 2.05, 1.72],
            'SGN Intra': [0.40, 0.70, 1.15],       'SGN Cross': [1.39, 1.72, 1.84],
            'DAE Intra': [1.05, 1.38, 1.31],       'DAE Cross': [2.58, 1.86, 1.70],
            'BiLSTM Intra': [1.36, 1.58, 1.51],    'BiLSTM Cross': [2.15, 1.91, 2.10]
        }
    },
    'computer': {
        'MAE': {
            'Seq2Point Intra': [4.3, 6.0, 6.1],   'Seq2Point Cross': [18.5, 18.0, 16.8],
            'SGN Intra': [5.3, 5.0, 6.7],         'SGN Cross': [20.2, 18.4, 16.9],
            'DAE Intra': [5.4, 5.5, 6.0],         'DAE Cross': [20.1, 17.1, 17.0],
            'BiLSTM Intra': [9.8, 5.8, 6.1],      'BiLSTM Cross': [17.9, 16.9, 16.9]
        },
        'F1-score': {
            'Seq2Point Intra': [1.00, 1.00, 1.00], 'Seq2Point Cross': [0.47, 0.46, 0.47],
            'SGN Intra': [1.00, 1.00, 1.00],       'SGN Cross': [0.47, 0.46, 0.47],
            'DAE Intra': [1.00, 1.00, 1.00],       'DAE Cross': [0.47, 0.46, 0.47],
            'BiLSTM Intra': [0.72, 1.00, 1.00],    'BiLSTM Cross': [0.47, 0.46, 0.47]
        },
        'NEP': {
            'Seq2Point Intra': [0.25, 0.35, 0.36], 'Seq2Point Cross': [0.89, 0.86, 1.72],
            'SGN Intra': [0.31, 0.29, 0.40],       'SGN Cross': [0.97, 0.88, 1.84],
            'DAE Intra': [0.32, 0.33, 0.36],       'DAE Cross': [0.97, 0.82, 1.70],
            'BiLSTM Intra': [0.58, 0.35, 0.36],    'BiLSTM Cross': [0.86, 0.81, 2.10]
        }
    },
    'microwave': {
        'MAE': {
            'Seq2Point Intra': [11.5, 14.2, 13.1], 'Seq2Point Cross': [14.5, 12.8, 8.9],
            'SGN Intra': [7.9, 10.1, 12.2],        'SGN Cross': [12.2, 10.0, 7.8],
            'DAE Intra': [13.2, 14.1, 16.0],       'DAE Cross': [10.1, 10.1, 11.4],
            'BiLSTM Intra': [13.5, 15.9, 15.4],    'BiLSTM Cross': [16.7, 14.2, 11.7]
        },
        'F1-score': {
            'Seq2Point Intra': [0.23, 0.14, 0.30], 'Seq2Point Cross': [0.04, 0.08, 0.06],
            'SGN Intra': [0.38, 0.33, 0.29],       'SGN Cross': [0.17, 0.11, 0.00],
            'DAE Intra': [0.20, 0.15, 0.17],       'DAE Cross': [0.07, 0.05, 0.05],
            'BiLSTM Intra': [0.13, 0.11, 0.17],    'BiLSTM Cross': [0.05, 0.03, 0.03]
        },
        'NEP': {
            'Seq2Point Intra': [1.12, 1.41, 1.28], 'Seq2Point Cross': [1.48, 1.31, 0.90],
            'SGN Intra': [0.77, 0.98, 1.20],       'SGN Cross': [1.24, 1.01, 0.78],
            'DAE Intra': [1.29, 1.39, 1.58],       'DAE Cross': [1.03, 1.02, 1.16],
            'BiLSTM Intra': [1.32, 1.57, 1.51],    'BiLSTM Cross': [1.70, 1.44, 1.19]
        }
    },
    'television': {
        'MAE': {
            'Seq2Point Intra': [12.4, 11.1, 13.3], 'Seq2Point Cross': [42.8, 36.5, 43.2],
            'SGN Intra': [10.8, 9.6, 14.4],        'SGN Cross': [46.4, 36.4, 45.2],
            'DAE Intra': [12.9, 15.5, 16.1],       'DAE Cross': [37.8, 42.2, 49.2],
            'BiLSTM Intra': [13.4, 15.6, 19.4],    'BiLSTM Cross': [43.8, 50.6, 53.0]
        },
        'F1-score': {
            'Seq2Point Intra': [0.65, 0.58, 0.55], 'Seq2Point Cross': [0.40, 0.56, 0.37],
            'SGN Intra': [0.70, 0.71, 0.44],       'SGN Cross': [0.44, 0.54, 0.28],
            'DAE Intra': [0.60, 0.55, 0.49],       'DAE Cross': [0.46, 0.37, 0.34],
            'BiLSTM Intra': [0.67, 0.58, 0.55],    'BiLSTM Cross': [0.40, 0.37, 0.36]
        },
        'NEP': {
            'Seq2Point Intra': [0.46, 0.41, 0.50], 'Seq2Point Cross': [1.20, 1.02, 1.21],
            'SGN Intra': [0.40, 0.35, 0.53],       'SGN Cross': [1.30, 1.02, 1.27],
            'DAE Intra': [0.48, 0.58, 0.60],       'DAE Cross': [1.06, 1.18, 1.38],
            'BiLSTM Intra': [0.50, 0.58, 0.72],    'BiLSTM Cross': [1.23, 1.42, 1.48]
        }
    }
}

# -------------------------------------------------------------
# FIGURE 1: Modern Sectoral Electricity Consumption Trend (2015-2026)
# -------------------------------------------------------------
print("Generating Fig 1 (Modern Sectoral Trend 2015-2026)...")
years = np.arange(2015, 2027)
res = np.array([62.5, 63.8, 65.2, 66.9, 68.4, 70.1, 71.8, 73.5, 75.2, 76.8, 78.1, 79.4])
ind = np.array([68.2, 67.9, 67.4, 67.0, 66.5, 65.8, 65.2, 65.0, 64.8, 64.6, 64.5, 64.5])
com = np.array([54.2, 55.1, 56.0, 57.2, 58.0, 58.9, 59.8, 60.7, 61.5, 62.1, 62.8, 63.2])
trn = np.array([12.8, 13.1, 13.5, 14.0, 14.6, 15.2, 16.0, 16.8, 17.6, 18.2, 18.9, 19.5])
agr = np.array([4.1, 4.1, 4.2, 4.3, 4.3, 4.4, 4.5, 4.5, 4.6, 4.7, 4.7, 4.8])

fig1, ax1 = plt.subplots(figsize=(10.5, 5.0), dpi=300)
ax1.plot(years, res, label='Residential (Electrification)', color='#D97706', linewidth=2.6, marker='o', markersize=5)
ax1.plot(years, ind, label='Industrial (Efficiency Offset)', color='#DC2626', linewidth=2.4, marker='s', markersize=5)
ax1.plot(years, com, label='Commercial & IT Services', color='#0D9488', linewidth=2.4, marker='^', markersize=5)
ax1.plot(years, trn, label='Transport (EV & Rail)', color='#2563EB', linewidth=2.4, marker='d', markersize=5)
ax1.plot(years, agr, label='Agriculture & Prosumers', color='#15803D', linewidth=2.0, marker='v', markersize=4)

ax1.set_xlim(2015, 2026)
ax1.set_ylim(0, 90)
ax1.set_yticks([0, 20, 40, 60, 80])
ax1.set_yticklabels(['0', '20 TWh', '40 TWh', '60 TWh', '80 TWh'])
ax1.set_xlabel('Year', fontsize=12, labelpad=8, fontweight='bold')
ax1.set_ylabel('Annual Final Electricity Demand', fontsize=12, labelpad=8, fontweight='bold')
ax1.set_xticks(years)
ax1.set_xticklabels([str(y) for y in years], rotation=0)
ax1.grid(axis='y', linestyle='--', alpha=0.35, color='#aaaaaa')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, framealpha=0.9, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=10)
plt.title("Evolution of Macro Electricity Final Demand by Sector (2015–2026)\nHighlighting Rising Residential Electrification and EV Decarbonization", 
          fontsize=12, fontweight='bold', pad=14, loc='left')
plt.tight_layout()
fig1.savefig(os.path.join(out_dir, "fig1_swiss_sector_evolution.png"), dpi=300, bbox_inches='tight')
fig1.savefig(os.path.join(out_dir, "fig1_sector_evolution.png"), dpi=300, bbox_inches='tight')
plt.close(fig1)

# -------------------------------------------------------------
# FIGURE 2: 2025/2026 Sectoral Consumption Share Bar Chart
# -------------------------------------------------------------
print("Generating Fig 2 (2025/2026 Sectoral Share Breakdown)...")
labels_fig2 = [
    'Residential\n34.3% (79.4 TWh)', 
    'Industrial\n27.9% (64.5 TWh)', 
    'Commercial\n27.3% (63.2 TWh)', 
    'Transport\n8.4% (19.5 TWh)', 
    'Agri & Other\n2.1% (4.8 TWh)'
]
shares_fig2 = [34.3, 27.9, 27.3, 8.4, 2.1]
colors_fig2 = ['#D97706', '#DC2626', '#0D9488', '#2563EB', '#15803D']

fig2, ax2 = plt.subplots(figsize=(11.5, 2.8), dpi=300)
left = 0
for i, (share, color, label) in enumerate(zip(shares_fig2, colors_fig2, labels_fig2)):
    ax2.barh([0], [share], left=left, color=color, height=0.62, edgecolor='#ffffff', linewidth=1.5)
    if share > 15:
        ax2.text(left + share/2, 0, label, ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    elif share == 8.4:
        ax2.text(left + share/2, 0, "Transport\n8.4%", ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    else: # Agri 2.1%
        ax2.text(left + share/2 + 2.8, 0.46, "Agri & Other\n2.1% (4.8 TWh)", ha='center', va='center', fontsize=9, fontweight='bold', color='#15803D')
        ax2.annotate('', xy=(left + share/2, 0.32), xytext=(left + share/2 + 2.2, 0.41),
                     arrowprops=dict(arrowstyle="->", color='#15803D', lw=1.2))
    left += share

ax2.set_xlim(0, 107)
ax2.set_ylim(-0.55, 0.75)
ax2.axis('off')
plt.title("2025/2026 Sectoral Electricity Demand Breakdown (Total Final Energy: 231.4 TWh)", 
          fontsize=12, fontweight='bold', pad=12, loc='left')
plt.tight_layout()
fig2.savefig(os.path.join(out_dir, "fig2_swiss_2022_sector_share.png"), dpi=300, bbox_inches='tight')
fig2.savefig(os.path.join(out_dir, "fig2_sector_share.png"), dpi=300, bbox_inches='tight')
plt.close(fig2)

# -------------------------------------------------------------
# FIGURE 3: Modern Residential Electricity End-Use Breakdown (Donut Chart)
# -------------------------------------------------------------
print("Generating Fig 3 (Modern Residential End-Use Breakdown)...")
fig3, ax3 = plt.subplots(figsize=(8.0, 8.0), dpi=300)

labels_fig3 = [
    'Space Heating & HVAC\n26%',
    'Water Heating (Geysers)\n15%',
    'Cooking & Induction\n14%',
    'Refrigeration & Cooling\n9%',
    'Computing & Home IT\n9%',
    'Laundry & Dishwashing\n8%',
    'Inverter AC & Ventilation\n7%',
    'Lighting (LED)\n6%',
    'EV & Miscellaneous\n6%'
]
sizes_fig3 = [26, 15, 14, 9, 9, 8, 7, 6, 6]
colors_fig3 = [
    '#9A3412',  # Deep Rust (Heating)
    '#EA580C',  # Vibrant Orange (Hot Water)
    '#D97706',  # Amber (Cooking)
    '#0D9488',  # Teal (Refrigeration)
    '#2563EB',  # Royal Blue (IT / Computing)
    '#4F46E5',  # Indigo (Laundry)
    '#059669',  # Emerald (AC & Ventilation)
    '#65A30D',  # Olive Green (Lighting)
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
plt.title("Residential Electricity Consumption Breakdown by End-Use Category\n(Modern Decarbonized Household Architecture)", 
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
    # Capitalize title nicely
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
