import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, send_file, jsonify
import io
import base64
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Load and process data
        df = pd.read_csv("analyzed_tickets.csv")
        
        # Generate plots
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        df.groupby('sentiment').size().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
        ax1.spines[['top', 'right']].set_visible(False)
        plt.title('Sentiment Distribution')
        plt.tight_layout()
        
        # Convert plot to base64 for HTML
        img1 = io.BytesIO()
        plt.savefig(img1, format='png', bbox_inches='tight', dpi=100)
        img1.seek(0)
        plot_url1 = base64.b64encode(img1.getvalue()).decode()
        plt.close(fig1)
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        df.groupby('product').size().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
        ax2.spines[['top', 'right']].set_visible(False)
        plt.title('Product Distribution')
        plt.tight_layout()
        
        img2 = io.BytesIO()
        plt.savefig(img2, format='png', bbox_inches='tight', dpi=100)
        img2.seek(0)
        plot_url2 = base64.b64encode(img2.getvalue()).decode()
        plt.close(fig2)
        
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        df.groupby('category').size().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
        ax3.spines[['top', 'right']].set_visible(False)
        plt.title('Category Distribution')
        plt.tight_layout()
        
        img3 = io.BytesIO()
        plt.savefig(img3, format='png', bbox_inches='tight', dpi=100)
        img3.seek(0)
        plot_url3 = base64.b64encode(img3.getvalue()).decode()
        plt.close(fig3)
        
        # Basic statistics
        stats = {
            'total_tickets': len(df),
            'sentiment_counts': df['sentiment'].value_counts().to_dict(),
            'product_counts': df['product'].value_counts().to_dict(),
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
        df = pd.read_csv("analyzed_tickets.csv")
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
    app.run(host='0.0.0.0', port=5000, debug=True)
