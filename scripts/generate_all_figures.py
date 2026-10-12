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

# -------------------------------------------------------------
# FIGURE 1: Evolution of electricity final consumption by sector in Switzerland (2000-2022)
# -------------------------------------------------------------
print("Regenerating Fig 1...")
years = np.arange(2000, 2023)
industry = np.array([66.5, 67.8, 67.0, 67.2, 68.8, 70.2, 70.5, 70.4, 71.8, 67.2, 
                     71.2, 70.8, 70.1, 69.2, 66.2, 66.0, 64.9, 65.5, 63.2, 62.9, 60.8, 64.5, 63.5])
transport = np.array([13.4, 13.8, 14.1, 14.8, 14.7, 14.9, 15.3, 15.2, 15.5, 15.1, 
                      15.6, 15.2, 15.4, 15.5, 15.2, 15.5, 15.9, 15.8, 15.7, 15.6, 14.8, 15.6, 16.5])
residential = np.array([57.2, 59.5, 60.3, 62.1, 64.2, 66.8, 67.1, 66.0, 67.8, 67.6, 
                        70.5, 67.2, 68.9, 70.1, 68.0, 70.2, 71.5, 72.0, 71.2, 71.1, 71.8, 75.2, 71.5])
commercial = np.array([51.2, 55.4, 56.1, 58.5, 60.1, 62.0, 62.8, 62.4, 65.1, 64.6, 
                       66.4, 64.2, 64.8, 65.2, 63.0, 64.5, 63.8, 63.7, 63.5, 61.8, 57.8, 59.4, 58.7])
agriculture = np.array([3.5, 3.6, 3.6, 3.7, 3.7, 3.8, 3.8, 3.5, 3.5, 3.5, 
                        3.6, 3.5, 3.5, 3.5, 3.4, 3.5, 3.4, 3.4, 3.3, 3.3, 3.2, 3.4, 3.5])

fig1, ax1 = plt.subplots(figsize=(10, 4.8), dpi=300)
ax1.plot(years, industry, label='Industry', color='#E06653', linewidth=2.2)
ax1.plot(years, transport, label='Transport', color='#E89C5D', linewidth=2.2)
ax1.plot(years, residential, label='Residential', color='#E5B842', linewidth=2.2)
ax1.plot(years, commercial, label='Commercial', color='#269285', linewidth=2.2)
ax1.plot(years, agriculture, label='Agriculture', color='#2A4B54', linewidth=2.2)

ax1.set_xlim(2000, 2022)
ax1.set_ylim(0, 85)
ax1.set_yticks([0, 40, 80])
ax1.set_yticklabels(['0', '40k', '80k'])
ax1.set_xlabel('Year', fontsize=12, labelpad=8)
ax1.set_ylabel('Energy Consumption (TJ)', fontsize=12, labelpad=8)
ax1.set_xticks([2000, 2005, 2010, 2015, 2020])
ax1.grid(axis='y', linestyle='-', alpha=0.3, color='#cccccc')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.legend(loc='upper right', bbox_to_anchor=(1.16, 1.0), frameon=False, fontsize=10)
plt.tight_layout()
fig1.savefig(os.path.join(out_dir, "fig1_swiss_sector_evolution.png"), dpi=300, bbox_inches='tight')
plt.close(fig1)

# -------------------------------------------------------------
# FIGURE 2: Electricity final consumption by Sector in Switzerland, 2022
# -------------------------------------------------------------
print("Regenerating Fig 2...")
labels = ['Industry\n30.3%', 'Transport\n6.3%', 'Residential\n33.9%', 'Commercial\n27.8%', 'Agriculture\n1.7%']
shares = [30.3, 6.3, 33.9, 27.8, 1.7]
colors = ['#E06653', '#E89C5D', '#E5B842', '#269285', '#2A4B54']

fig2, ax2 = plt.subplots(figsize=(11, 2.6), dpi=300)
left = 0
for i, (share, color, label) in enumerate(zip(shares, colors, labels)):
    ax2.barh([0], [share], left=left, color=color, height=0.6, edgecolor='black', linewidth=0.8)
    # Positioning text
    if share > 10:
        ax2.text(left + share/2, 0, label, ha='center', va='center', fontsize=10, fontweight='medium', color='black')
    elif share == 6.3:
        ax2.text(left + share/2, 0, "Transport\n6.3%", ha='center', va='center', fontsize=8.5, fontweight='medium', color='black')
    else: # Agriculture 1.7%
        # Place label with callout above or slightly to the right
        ax2.text(left + share/2 + 2.5, 0.45, "Agriculture\n1.7%", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2A4B54')
        ax2.annotate('', xy=(left + share/2, 0.3), xytext=(left + share/2 + 2.0, 0.38),
                     arrowprops=dict(arrowstyle="->", color='#2A4B54', lw=1.0))
    left += share

ax2.set_xlim(0, 106)
ax2.set_ylim(-0.5, 0.7)
ax2.axis('off')
plt.tight_layout()
fig2.savefig(os.path.join(out_dir, "fig2_swiss_2022_sector_share.png"), dpi=300, bbox_inches='tight')
plt.close(fig2)

# -------------------------------------------------------------
# FIGURE 4: Workflow flowchart of NILM Framework
# -------------------------------------------------------------
print("Regenerating Fig 4...")
fig4, ax4 = plt.subplots(figsize=(9, 12), dpi=300)
ax4.set_xlim(0, 10)
ax4.set_ylim(-0.5, 13.5)
ax4.axis('off')

def draw_box(x, y, w, h, text, bg_color='#C9E7B3', edge_color='#6D9351', text_color='#111111', fontsize=10, bold=False):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                         facecolor=bg_color, edgecolor=edge_color, linewidth=1.2)
    ax4.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax4.text(x, y, text, ha='center', va='center', fontsize=fontsize, fontweight=weight, color=text_color)
    return box

def draw_arrow(x1, y1, x2, y2):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='->,head_width=3.5,head_length=5',
                            color='#333333', linewidth=1.2)
    ax4.add_patch(arrow)

# Hierarchy
draw_box(5.0, 12.5, 3.4, 0.7, "Data Preparation", bold=True, fontsize=11)
draw_arrow(5.0, 12.15, 5.0, 11.35)

draw_box(5.0, 11.0, 3.6, 0.7, "Downsampling Data", bold=True, fontsize=11)
draw_arrow(5.0, 10.65, 2.5, 9.85)
draw_arrow(5.0, 10.65, 5.0, 9.85)
draw_arrow(5.0, 10.65, 7.5, 9.85)

draw_box(2.5, 9.5, 2.2, 0.7, "1 Minute", fontsize=10.5)
draw_box(5.0, 9.5, 2.2, 0.7, "5 Minutes", fontsize=10.5)
draw_box(7.5, 9.5, 2.2, 0.7, "15 Minutes", fontsize=10.5)

draw_arrow(2.5, 9.15, 4.5, 8.35)
draw_arrow(5.0, 9.15, 5.0, 8.35)
draw_arrow(7.5, 9.15, 5.5, 8.35)

draw_box(5.0, 8.0, 3.6, 0.7, "Data Segmentation", bold=True, fontsize=11)
draw_arrow(4.2, 7.65, 3.5, 6.85)
draw_arrow(5.8, 7.65, 6.5, 6.85)

draw_box(3.5, 6.5, 2.2, 0.7, "REFIT\n(UK)", bg_color='#E8978A', edge_color='#B24D3D', text_color='#111111', bold=True, fontsize=10.5)
draw_box(6.5, 6.5, 2.2, 0.7, "ECO\n(Swiss)", bg_color='#E8978A', edge_color='#B24D3D', text_color='#111111', bold=True, fontsize=10.5)

draw_arrow(3.5, 6.15, 3.5, 5.35)
draw_arrow(3.8, 6.15, 6.2, 5.35)
draw_arrow(6.5, 6.15, 6.5, 5.35)

draw_box(3.5, 5.0, 2.6, 0.7, "Intra-dataset\nValidation", bold=True, fontsize=10.5)
draw_box(6.5, 5.0, 2.6, 0.7, "Cross-dataset\nValidation", bold=True, fontsize=10.5)

draw_arrow(3.5, 4.65, 4.8, 3.85)
draw_arrow(6.5, 4.65, 5.2, 3.85)

draw_box(5.0, 3.5, 3.4, 0.7, "NILM Algorithms", bg_color='#F2A365', edge_color='#D96B27', text_color='#111111', bold=True, fontsize=11)

# nilmtk container box
nilmtk_box = FancyBboxPatch((0.4, 1.8), 3.2, 1.2, boxstyle="round,pad=0.08,rounding_size=0.1",
                            facecolor='#FBE7A1', edgecolor='#D4A017', linewidth=1.2)
ax4.add_patch(nilmtk_box)
ax4.text(2.0, 2.75, "nilmtk", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#6B4E00')
draw_box(1.2, 2.15, 1.3, 0.55, "FHMM", bg_color='#E28456', edge_color='#B24D3D', bold=True)
draw_box(2.8, 2.15, 1.3, 0.55, "CO", bg_color='#E28456', edge_color='#B24D3D', bold=True)

# Neural_NILM container box
neural_box = FancyBboxPatch((3.8, 1.8), 5.8, 1.2, boxstyle="round,pad=0.08,rounding_size=0.1",
                            facecolor='#FBE7A1', edgecolor='#D4A017', linewidth=1.2)
ax4.add_patch(neural_box)
ax4.text(6.7, 2.75, "Neural_NILM (PyTorch)", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#6B4E00')
draw_box(4.5, 2.15, 1.25, 0.55, "Seq2Point", bg_color='#E28456', edge_color='#B24D3D', bold=True, fontsize=8.5)
draw_box(5.9, 2.15, 1.25, 0.55, "DAE", bg_color='#E28456', edge_color='#B24D3D', bold=True, fontsize=8.5)
draw_box(7.3, 2.15, 1.25, 0.55, "SGN", bg_color='#E28456', edge_color='#B24D3D', bold=True, fontsize=8.5)
draw_box(8.7, 2.15, 1.25, 0.55, "BiLSTM", bg_color='#E28456', edge_color='#B24D3D', bold=True, fontsize=8.5)

draw_arrow(4.2, 3.15, 2.0, 3.0)
draw_arrow(5.8, 3.15, 6.7, 3.0)

# Performance Assessment
draw_box(5.0, 1.0, 3.6, 0.65, "Performance Assessment", bold=True, fontsize=11)
draw_arrow(2.0, 1.8, 4.2, 1.32)
draw_arrow(6.7, 1.8, 5.8, 1.32)

# Metrics at bottom
draw_box(2.5, 0.25, 1.8, 0.5, "MAE", bold=True, fontsize=10.5)
draw_box(5.0, 0.25, 1.8, 0.5, "F1-score", bold=True, fontsize=10.5)
draw_box(7.5, 0.25, 1.8, 0.5, "NEP", bold=True, fontsize=10.5)

draw_arrow(4.3, 0.68, 2.5, 0.5)
draw_arrow(5.0, 0.68, 5.0, 0.5)
draw_arrow(5.7, 0.68, 7.5, 0.5)

plt.tight_layout()
fig4.savefig(os.path.join(out_dir, "fig4_nilm_framework_flowchart.png"), dpi=300, bbox_inches='tight')
plt.close(fig4)

# -------------------------------------------------------------
# FIGURE 5: Multi-panel performance grid (3 rows x 6 columns)
# -------------------------------------------------------------
print("Regenerating Fig 5...")
appliances = ['kettle', 'freezer', 'washing machine', 'computer', 'microwave', 'television']
freqs = [1, 5, 15]

table2_data = {
    'kettle': {
        'MAE': {
            'Seq2Point Intra': [15.0, 21.7, 24.8], 'Seq2Point Cross': [25.0, 21.5, 28.0],
            'SGN Intra': [9.1, 12.8, 28.6],       'SGN Cross': [21.8, 20.1, 23.4],
            'DAE Intra': [17.5, 30.2, 32.6],       'DAE Cross': [24.8, 32.0, 24.1],
            'BiLSTM Intra': [21.7, 30.4, 31.7],    'BiLSTM Cross': [29.6, 27.8, 24.2]
        },
        'F1-score': {
            'Seq2Point Intra': [0.68, 0.00, 0.00], 'Seq2Point Cross': [0.00, 0.00, 0.00],
            'SGN Intra': [0.77, 0.00, 0.00],       'SGN Cross': [0.00, 0.00, 0.00],
            'DAE Intra': [0.62, 0.00, 0.00],       'DAE Cross': [0.00, 0.00, 0.00],
            'BiLSTM Intra': [0.75, 0.00, 0.00],    'BiLSTM Cross': [0.00, 0.00, 0.00]
        },
        'NEP': {
            'Seq2Point Intra': [0.84, 1.21, 1.39], 'Seq2Point Cross': [7.48, 6.27, 8.27],
            'SGN Intra': [0.51, 0.72, 1.61],       'SGN Cross': [6.52, 5.88, 6.90],
            'DAE Intra': [0.98, 1.69, 1.82],       'DAE Cross': [7.42, 9.34, 7.10],
            'BiLSTM Intra': [1.22, 1.70, 1.78],    'BiLSTM Cross': [8.86, 8.12, 7.14]
        }
    },
    'freezer': {
        'MAE': {
            'Seq2Point Intra': [28.2, 29.5, 26.7], 'Seq2Point Cross': [13.1, 13.3, 10.1],
            'SGN Intra': [25.0, 32.2, 25.3],       'SGN Cross': [18.0, 14.3, 10.0],
            'DAE Intra': [32.1, 29.4, 26.0],       'DAE Cross': [15.2, 13.3, 10.3],
            'BiLSTM Intra': [39.0, 30.2, 24.8],    'BiLSTM Cross': [14.5, 13.2, 10.3]
        },
        'F1-score': {
            'Seq2Point Intra': [0.42, 0.46, 0.55], 'Seq2Point Cross': [0.83, 0.78, 0.84],
            'SGN Intra': [0.49, 0.45, 0.55],       'SGN Cross': [0.82, 0.76, 0.84],
            'DAE Intra': [0.40, 0.45, 0.55],       'DAE Cross': [0.75, 0.76, 0.84],
            'BiLSTM Intra': [0.38, 0.45, 0.55],    'BiLSTM Cross': [0.77, 0.76, 0.84]
        },
        'NEP': {
            'Seq2Point Intra': [1.45, 1.52, 1.37], 'Seq2Point Cross': [0.69, 0.70, 0.53],
            'SGN Intra': [1.29, 1.66, 1.30],       'SGN Cross': [0.94, 0.76, 0.53],
            'DAE Intra': [1.65, 1.51, 1.34],       'DAE Cross': [0.80, 0.70, 0.54],
            'BiLSTM Intra': [2.01, 1.55, 1.28],    'BiLSTM Cross': [0.76, 0.70, 0.54]
        }
    },
    'washing machine': {
        'MAE': {
            'Seq2Point Intra': [20.2, 33.2, 43.3], 'Seq2Point Cross': [27.7, 48.5, 40.9],
            'SGN Intra': [14.1, 24.4, 39.9],       'SGN Cross': [33.1, 40.8, 43.6],
            'DAE Intra': [36.3, 47.8, 45.5],       'DAE Cross': [61.5, 44.0, 40.3],
            'BiLSTM Intra': [47.1, 54.9, 52.1],    'BiLSTM Cross': [51.0, 45.1, 49.7]
        },
        'F1-score': {
            'Seq2Point Intra': [0.64, 0.36, 0.27], 'Seq2Point Cross': [0.23, 0.22, 0.17],
            'SGN Intra': [0.76, 0.63, 0.35],       'SGN Cross': [0.20, 0.19, 0.21],
            'DAE Intra': [0.30, 0.18, 0.29],       'DAE Cross': [0.19, 0.20, 0.22],
            'BiLSTM Intra': [0.10, 0.10, 0.21],    'BiLSTM Cross': [0.21, 0.21, 0.25]
        },
        'NEP': {
            'Seq2Point Intra': [0.61, 1.00, 1.31], 'Seq2Point Cross': [1.23, 2.15, 1.81],
            'SGN Intra': [0.43, 0.74, 1.21],       'SGN Cross': [1.46, 1.81, 1.93],
            'DAE Intra': [1.10, 1.45, 1.38],       'DAE Cross': [2.72, 1.95, 1.78],
            'BiLSTM Intra': [1.42, 1.66, 1.58],    'BiLSTM Cross': [2.26, 2.00, 2.20]
        }
    },
    'computer': {
        'MAE': {
            'Seq2Point Intra': [4.0, 5.7, 5.8],   'Seq2Point Cross': [17.5, 17.0, 15.9],
            'SGN Intra': [5.0, 4.7, 6.3],         'SGN Cross': [19.1, 17.3, 15.9],
            'DAE Intra': [5.1, 5.2, 5.7],         'DAE Cross': [19.1, 16.2, 16.1],
            'BiLSTM Intra': [9.3, 5.5, 5.7],      'BiLSTM Cross': [17.0, 16.0, 16.0]
        },
        'F1-score': {
            'Seq2Point Intra': [1.00, 1.00, 1.00], 'Seq2Point Cross': [0.45, 0.44, 0.45],
            'SGN Intra': [1.00, 1.00, 1.00],       'SGN Cross': [0.45, 0.44, 0.45],
            'DAE Intra': [1.00, 1.00, 1.00],       'DAE Cross': [0.45, 0.44, 0.45],
            'BiLSTM Intra': [0.70, 1.00, 1.00],    'BiLSTM Cross': [0.45, 0.44, 0.45]
        },
        'NEP': {
            'Seq2Point Intra': [0.27, 0.38, 0.39], 'Seq2Point Cross': [0.94, 0.91, 1.81],
            'SGN Intra': [0.33, 0.31, 0.42],       'SGN Cross': [1.02, 0.93, 1.93],
            'DAE Intra': [0.34, 0.35, 0.38],       'DAE Cross': [1.02, 0.87, 1.78],
            'BiLSTM Intra': [0.62, 0.37, 0.38],    'BiLSTM Cross': [0.91, 0.86, 2.20]
        }
    },
    'microwave': {
        'MAE': {
            'Seq2Point Intra': [10.8, 13.4, 12.3], 'Seq2Point Cross': [13.7, 12.1, 8.4],
            'SGN Intra': [7.4, 9.4, 11.5],         'SGN Cross': [11.5, 9.4, 7.3],
            'DAE Intra': [12.5, 13.3, 15.1],       'DAE Cross': [9.5, 9.5, 10.7],
            'BiLSTM Intra': [12.7, 15.0, 14.5],    'BiLSTM Cross': [15.8, 13.4, 11.0]
        },
        'F1-score': {
            'Seq2Point Intra': [0.21, 0.12, 0.28], 'Seq2Point Cross': [0.03, 0.07, 0.05],
            'SGN Intra': [0.35, 0.30, 0.27],       'SGN Cross': [0.15, 0.09, 0.00],
            'DAE Intra': [0.18, 0.13, 0.15],       'DAE Cross': [0.06, 0.04, 0.04],
            'BiLSTM Intra': [0.11, 0.09, 0.15],    'BiLSTM Cross': [0.04, 0.02, 0.02]
        },
        'NEP': {
            'Seq2Point Intra': [1.19, 1.49, 1.36], 'Seq2Point Cross': [1.57, 1.39, 0.96],
            'SGN Intra': [0.82, 1.04, 1.28],       'SGN Cross': [1.32, 1.07, 0.83],
            'DAE Intra': [1.38, 1.48, 1.68],       'DAE Cross': [1.09, 1.08, 1.23],
            'BiLSTM Intra': [1.40, 1.67, 1.61],    'BiLSTM Cross': [1.81, 1.53, 1.26]
        }
    },
    'television': {
        'MAE': {
            'Seq2Point Intra': [11.8, 10.5, 12.6], 'Seq2Point Cross': [40.6, 34.6, 41.1],
            'SGN Intra': [10.2, 9.0, 13.6],        'SGN Cross': [44.0, 34.5, 42.9],
            'DAE Intra': [12.2, 14.7, 15.2],       'DAE Cross': [35.9, 40.0, 46.7],
            'BiLSTM Intra': [12.7, 14.8, 18.3],    'BiLSTM Cross': [41.5, 48.0, 50.3]
        },
        'F1-score': {
            'Seq2Point Intra': [0.63, 0.56, 0.53], 'Seq2Point Cross': [0.38, 0.54, 0.35],
            'SGN Intra': [0.67, 0.68, 0.42],       'SGN Cross': [0.42, 0.52, 0.26],
            'DAE Intra': [0.58, 0.53, 0.47],       'DAE Cross': [0.44, 0.35, 0.32],
            'BiLSTM Intra': [0.65, 0.56, 0.53],    'BiLSTM Cross': [0.38, 0.35, 0.34]
        },
        'NEP': {
            'Seq2Point Intra': [0.49, 0.44, 0.53], 'Seq2Point Cross': [1.28, 1.09, 1.29],
            'SGN Intra': [0.43, 0.38, 0.57],       'SGN Cross': [1.38, 1.09, 1.35],
            'DAE Intra': [0.51, 0.62, 0.64],       'DAE Cross': [1.13, 1.26, 1.47],
            'BiLSTM Intra': [0.53, 0.62, 0.77],    'BiLSTM Cross': [1.31, 1.51, 1.58]
        }
    }
}

series_styles = [
    ('Seq2Point Intra', '#E5A038', '-', 'o'),
    ('Seq2Point Cross', '#E5A038', '--', 'o'),
    ('SGN Intra',       '#0033CC', '-', 'o'),
    ('SGN Cross',       '#0033CC', '--', 'o'),
    ('DAE Intra',       '#CC2200', '-', 'o'),
    ('DAE Cross',       '#CC2200', '--', 'o'),
    ('BiLSTM Intra',    '#1B8A38', '-', 'o'),
    ('BiLSTM Cross',    '#1B8A38', '--', 'o')
]

metrics = ['MAE', 'F1-score', 'NEP']
metric_labels = ['MAE (W)', 'F1-score (-)', 'NEP (-)']

fig5, axes = plt.subplots(3, 6, figsize=(15, 10.5), dpi=300, sharex=True)

for col_idx, app in enumerate(appliances):
    axes[0, col_idx].set_title(app, fontsize=12, pad=12)
    
    for row_idx, met in enumerate(metrics):
        ax = axes[row_idx, col_idx]
        
        for s_name, s_color, s_ls, s_marker in series_styles:
            vals = table2_data[app][met][s_name]
            ax.plot(freqs, vals, label=s_name, color=s_color, linestyle=s_ls, 
                    marker=s_marker, markersize=4, linewidth=1.5, alpha=0.9)
            
        ax.set_xticks(freqs)
        ax.set_xticklabels(['1', '5', '15'])
        ax.grid(True, linestyle=':', alpha=0.4, color='#bbbbbb')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Consistent Y-axis limits per row exactly like the paper
        if row_idx == 0: # MAE
            ax.set_ylim(-2, 65)
            ax.set_yticks([0, 20, 40, 60])
        elif row_idx == 1: # F1-score
            ax.set_ylim(-0.05, 1.05)
            ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        elif row_idx == 2: # NEP
            ax.set_ylim(-0.5, 10.5)
            ax.set_yticks([0, 2, 4, 6, 8, 10])
                
        if col_idx == 0:
            ax.set_ylabel(metric_labels[row_idx], fontsize=12, labelpad=8)
        else:
            ax.set_yticklabels([])

for col_idx in range(6):
    axes[2, col_idx].set_xlabel('Sampling Frequency (min)', fontsize=10, labelpad=6)

handles, labels = axes[0, 0].get_legend_handles_labels()
fig5.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.99), 
            ncol=8, frameon=False, fontsize=10.5, handletextpad=0.4, columnspacing=1.2)

plt.subplots_adjust(top=0.92, bottom=0.07, left=0.06, right=0.98, hspace=0.18, wspace=0.12)
fig5.savefig(os.path.join(out_dir, "fig5_multi_panel_performance_grid.png"), dpi=300, bbox_inches='tight')
plt.close(fig5)

print("Updated figures regenerated successfully!")
