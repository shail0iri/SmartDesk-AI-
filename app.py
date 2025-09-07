import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, jsonify
import io
import base64
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "analyzed_tickets.csv"

def plot_to_base64(fig):
    """Convert Matplotlib figure to base64 string for HTML embedding"""
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    encoded = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return encoded

@app.route('/')
def index():
    try:
        if not os.path.exists(DATA_FILE):
            return f"Error: {DATA_FILE} not found."

        # Load dataset
        df = pd.read_csv(DATA_FILE)

        # Plot 1: Sentiment Distribution
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        df["sentiment"].value_counts().plot(kind='barh', ax=ax1, color=sns.color_palette("Dark2"))
        ax1.spines[['top', 'right']].set_visible(False)
        ax1.set_title('Sentiment Distribution')
        plot_url1 = plot_to_base64(fig1)

        # Plot 2: Urgency Distribution
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        df["urgency"].value_counts().plot(kind='barh', ax=ax2, color=sns.color_palette("Dark2"))
        ax2.spines[['top', 'right']].set_visible(False)
        ax2.set_title('Urgency Distribution')
        plot_url2 = plot_to_base64(fig2)

        # Plot 3: Category Distribution
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        df["category"].value_counts().plot(kind='barh', ax=ax3, color=sns.color_palette("Dark2"))
        ax3.spines[['top', 'right']].set_visible(False)
        ax3.set_title('Category Distribution')
        plot_url3 = plot_to_base64(fig3)

        # Statistics
        stats = {
            'total_tickets': len(df),
            'sentiment_counts': df['sentiment'].value_counts().to_dict(),
            'urgency_counts': df['urgency'].value_counts().to_dict(),
            'category_counts': df['category'].value_counts().to_dict()
        }

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return render_template('index.html',
                               plot1=plot_url1,
                               plot2=plot_url2,
                               plot3=plot_url3,
                               stats=stats,
                               current_time=current_time)

    except Exception as e:
        return f"Error loading data: {str(e)}"

@app.route('/data')
def get_data():
    try:
        df = pd.read_csv(DATA_FILE)
        return jsonify({
            'success': True,
            'data': df.to_dict(orient='records'),
            'total_records': len(df)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Use Render's PORT or default to 8000
    app.run(host='0.0.0.0', port=port, debug=False)
