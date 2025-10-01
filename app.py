import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from flask import Flask, render_template, jsonify
import io
import base64
import os
from datetime import datetime
import time

app = Flask(__name__)

DATA_FILE = "analyzed_tickets.csv"

def plot_to_base64(fig):
    """Convert Matplotlib figure to base64 string"""
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
            return "Data file not found", 500
        
        df = pd.read_csv(DATA_FILE)
        
        if df.empty:
            return "Dataset is empty", 500
        
        # Check required columns
        required_columns = ['sentiment', 'urgency', 'category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return f"Missing columns: {', '.join(missing_columns)}", 500
        
        # Generate plots
        plt.style.use('default')
        
        # Plot 1: Sentiment
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        df["sentiment"].value_counts().plot(kind='barh', ax=ax1, color=sns.color_palette("Dark2"))
        ax1.spines[['top', 'right']].set_visible(False)
        ax1.set_title('Sentiment Distribution')
        plot_url1 = plot_to_base64(fig1)

        # Plot 2: Urgency
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        df["urgency"].value_counts().plot(kind='barh', ax=ax2, color=sns.color_palette("Dark2"))
        ax2.spines[['top', 'right']].set_visible(False)
        ax2.set_title('Urgency Distribution')
        plot_url2 = plot_to_base64(fig2)

        # Plot 3: Category
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        df["category"].value_counts().head(10).plot(kind='barh', ax=ax3, color=sns.color_palette("Dark2"))
        ax3.spines[['top', 'right']].set_visible(False)
        ax3.set_title('Top 10 Categories')
        plot_url3 = plot_to_base64(fig3)

        # Statistics
        stats = {
            'total_tickets': len(df),
            'sentiment_counts': df['sentiment'].value_counts().to_dict(),
            'urgency_counts': df['urgency'].value_counts().to_dict(),
            'category_counts': df['category'].value_counts().head(10).to_dict(),
        }

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return render_template('index.html',
                               plot1=plot_url1,
                               plot2=plot_url2,
                               plot3=plot_url3,
                               stats=stats,
                               current_time=current_time)
                               
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/health')
def health_check():
    """Health endpoint for UptimeRobot monitoring"""
    try:
        # Basic health checks
        if not os.path.exists(DATA_FILE):
            return jsonify({
                'status': 'degraded',
                'message': 'Data file missing',
                'timestamp': datetime.now().isoformat()
            }), 200
        
        df = pd.read_csv(DATA_FILE)
        
        return jsonify({
            'status': 'healthy',
            'service': 'SmartDesk AI',
            'timestamp': datetime.now().isoformat(),
            'tickets_count': len(df),
            'version': '1.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/status')
def status():
    """Detailed status page"""
    try:
        files = os.listdir('.')
        csv_exists = os.path.exists(DATA_FILE)
        csv_size = os.path.getsize(DATA_FILE) if csv_exists else 0
        
        return jsonify({
            'status': 'operational',
            'current_directory': os.getcwd(),
            'files_count': len(files),
            'csv_exists': csv_exists,
            'csv_size': csv_size,
            'uptime_check': 'UptimeRobot configured'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
