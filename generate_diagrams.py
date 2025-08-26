#!/usr/bin/env python3
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, FancyBboxPatch


def _new_fig(ax_w=14, ax_h=8):
    fig, ax = plt.subplots(figsize=(ax_w, ax_h))
    ax.axis('off')
    return fig, ax


def context_diagram_png(path="context_diagram.png"):
    fig, ax = _new_fig(16, 9)

    # Grid helpers
    left_x, mid_x, right_x = 1.0, 8.0, 15.0
    top_y, mid_y, bot_y = 7.5, 5.0, 2.5

    # Sources cluster
    ax.add_patch(Rectangle((0.5, 1.8), 5.0, 6.0, fill=False, linestyle='--', edgecolor='gray', linewidth=1.2))
    ax.text(3.0, 7.7, 'Data Sources', ha='center', va='center', fontsize=12)
    src1 = FancyBboxPatch((1.0, 6.5), 4.0, 1.0, boxstyle="round,pad=0.2", fc='#e8eef9')
    src2 = FancyBboxPatch((1.0, 5.2), 4.0, 1.0, boxstyle="round,pad=0.2", fc='#e8eef9')
    ax.add_patch(src1); ax.add_patch(src2)
    ax.text(3.0, 7.0, 'CSV/JSON Uploads', ha='center', va='center', fontsize=11)
    ax.text(3.0, 5.7, 'PCAP -> Features (optional)', ha='center', va='center', fontsize=11)

    # System cluster
    ax.add_patch(Rectangle((6.0, 1.5), 4.0, 6.5, fill=False, linestyle='-', edgecolor='black', linewidth=1.5))
    ax.text(8.0, 8.3, 'Anomaly Detection System', ha='center', va='center', fontsize=13)
    backend = FancyBboxPatch((6.4, 6.2), 3.2, 1.2, boxstyle="round,pad=0.2", fc='#fff2cc')
    results = FancyBboxPatch((6.6, 4.6), 2.8, 1.2, boxstyle="round,pad=0.2", fc='white')
    ax.add_patch(backend); ax.add_patch(results)
    ax.text(8.0, 6.8, 'Flask API\n(models: IF, AE, Ensemble)', ha='center', va='center', fontsize=11)
    ax.text(8.0, 5.2, 'Results Storage\n(JSON + Plots)', ha='center', va='center', fontsize=11)

    # Consumers cluster
    ax.add_patch(Rectangle((11.0, 1.8), 5.0, 6.0, fill=False, linestyle='--', edgecolor='gray', linewidth=1.2))
    ax.text(13.5, 7.7, 'Consumers', ha='center', va='center', fontsize=12)
    ui = FancyBboxPatch((11.5, 6.5), 4.0, 1.0, boxstyle="round,pad=0.2", fc='#e8eef9')
    analyst = FancyBboxPatch((11.5, 5.2), 4.0, 1.0, boxstyle="round,pad=0.2", fc='#e8eef9')
    ax.add_patch(ui); ax.add_patch(analyst)
    ax.text(13.5, 7.0, 'React Dashboard\n(Upload & Visualize)', ha='center', va='center', fontsize=11)
    ax.text(13.5, 5.7, 'Analyst / Stakeholder', ha='center', va='center', fontsize=11)

    # Arrows using annotate for smoother heads and optional curved paths
    def arrow(x1, y1, x2, y2, text=None, curve=0.0):
        ax.annotate(
            "",
            xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#333333",
                            shrinkA=5, shrinkB=5,
                            connectionstyle=f"arc3,rad={curve}"),
        )
        if text:
            ax.text((x1+x2)/2, (y1+y2)/2 + 0.3, text, ha='center', fontsize=10, color="#333333")

    arrow(5.0, 7.0, 6.4, 6.8, '/api/upload', curve=0.05)
    arrow(5.0, 5.7, 6.4, 6.8, None, curve=-0.05)
    arrow(8.0, 6.2, 8.0, 5.8, 'report + images')
    arrow(9.6, 6.8, 11.5, 7.0, '/api/report, /api/images', curve=0.05)
    arrow(13.5, 6.5, 13.5, 6.2, 'insight')

    ax.set_xlim(0, 17)
    ax.set_ylim(1.2, 9.0)
    ax.set_title('Context Diagram (Level-0)', fontsize=16)
    fig.tight_layout(pad=1.0)
    # Save PNG
    fig.savefig(path, dpi=300)
    # Also export a crisp SVG version
    svg_path = path.rsplit('.', 1)[0] + '.svg'
    fig.savefig(svg_path, format='svg')
    plt.close(fig)


def flow_chart_png(path="flow_chart.png"):
    fig, ax = _new_fig(18, 5)

    steps = [
        'START', 'Load Data', 'Preprocess', 'Train (IF, AE)', 'Predict',
        'Ensemble', 'Visualize', 'Save Models', 'Report', 'END'
    ]
    x0, y0 = 1.0, 2.0
    w, h, gap = 1.8, 0.9, 0.8

    coords = {}
    for i, label in enumerate(steps):
        x = x0 + i * (w + gap)
        fc = 'white' if label in ('START', 'END') else '#e8eef9'
        ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0.2", fc=fc))
        ax.text(x + w/2, y0 + h/2, label, ha='center', va='center', fontsize=10)
        coords[label] = (x, y0)

    # Arrows
    def connect(l1, l2):
        x1, y1 = coords[l1]
        x2, y2 = coords[l2]
        ax.add_patch(FancyArrow(x1 + w, y1 + h/2, (x2 - x1) - w, 0, width=0.02,
                                head_width=0.2, head_length=0.25, length_includes_head=True, color='#333333'))

    for i in range(len(steps) - 1):
        connect(steps[i], steps[i+1])

    ax.set_xlim(0.5, x0 + len(steps) * (w + gap) + 0.5)
    ax.set_ylim(1.2, 3.5)
    ax.set_title('Flow Chart (Control Flow)', fontsize=16)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def deployment_view_png(path="deployment_view.png"):
    fig, ax = _new_fig(16, 9)

    # Host box
    ax.add_patch(Rectangle((0.7, 0.8), 14.6, 7.8, fill=False, linestyle='-', edgecolor='black', linewidth=1.8))
    ax.text(8.0, 8.4, 'Host: Linux Machine (CPU, optional GPU)', ha='center', va='center', fontsize=13)

    # Runtime components
    ax.add_patch(Rectangle((1.1, 6.2), 13.8, 1.6, fill=False, linestyle='-', edgecolor='black'))
    ax.text(8.0, 7.95, 'Runtime Components', ha='center', fontsize=12)

    venv = FancyBboxPatch((1.4, 6.4), 4.0, 1.2, boxstyle="round,pad=0.2", fc='#fff2cc')
    flask = FancyBboxPatch((6.0, 6.4), 4.0, 1.2, boxstyle="round,pad=0.2", fc='#fff2cc')
    react = FancyBboxPatch((10.6, 6.4), 4.0, 1.2, boxstyle="round,pad=0.2", fc='#fff2cc')
    ax.add_patch(venv); ax.add_patch(flask); ax.add_patch(react)
    ax.text(3.4, 7.0, 'Python venv\n(requirements.txt)', ha='center')
    ax.text(8.0, 7.0, 'Flask API (5000)\nsrc/server.py', ha='center')
    ax.text(12.6, 7.0, 'Vite/React (5173)\nfrontend/', ha='center')

    # Storage
    ax.add_patch(Rectangle((1.1, 1.2), 13.8, 4.6, fill=False, linestyle='-', edgecolor='black'))
    ax.text(8.0, 5.7, 'Storage', ha='center', fontsize=12)

    models = FancyBboxPatch((1.5, 1.6), 4.0, 3.2, boxstyle="round,pad=0.2", fc='white')
    results = FancyBboxPatch((6.1, 1.6), 4.0, 3.2, boxstyle="round,pad=0.2", fc='white')
    config = FancyBboxPatch((10.7, 1.6), 4.0, 3.2, boxstyle="round,pad=0.2", fc='white')
    ax.add_patch(models); ax.add_patch(results); ax.add_patch(config)
    ax.text(3.5, 3.2, 'models/saved_models\nIF .joblib, AE .h5, preprocessor .joblib', ha='center')
    ax.text(8.1, 3.2, 'results/\nreport.json, plots.png', ha='center')
    ax.text(12.7, 3.2, 'config/config.yaml', ha='center')

    # Arrows
    def arrow(x1, y1, x2, y2, text=None):
        ax.add_patch(FancyArrow(x1, y1, x2-x1, y2-y1, width=0.03, head_width=0.25, head_length=0.35, length_includes_head=True, color='#333333'))
        if text:
            ax.text((x1+x2)/2, (y1+y2)/2 + 0.25, text, ha='center', fontsize=10)

    arrow(5.4, 7.0, 6.0, 7.0, None)  # venv -> flask
    arrow(10.0, 7.0, 10.6, 7.0, '/api/*')  # flask -> react
    arrow(8.0, 6.4, 8.1, 4.8, 'writes')  # flask -> results
    arrow(8.0, 6.4, 3.5, 4.8, 'reads/writes')  # flask <-> models
    arrow(12.7, 3.2, 8.0, 6.4, 'reads')  # config -> flask

    ax.set_xlim(0.5, 15.5)
    ax.set_ylim(0.8, 8.7)
    ax.set_title('Deployment View (Single-Machine)', fontsize=16)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


if __name__ == '__main__':
    context_diagram_png('context_diagram.png')
    flow_chart_png('flow_chart.png')
    deployment_view_png('deployment_view.png')
    print('Diagrams generated: context_diagram.png, flow_chart.png, deployment_view.png')
