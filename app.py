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
        # Debug: Check if file exists and show directory contents
        if not os.path.exists(DATA_FILE):
            files = os.listdir('.')
            return f"""
            <h1>Data File Not Found</h1>
            <p>File '{DATA_FILE}' not found in current directory.</p>
            <p>Current directory: {os.getcwd()}</p>
            <p>Files present: {', '.join(files)}</p>
            <p>Please ensure analyzed_tickets.csv is in your GitHub repository.</p>
            """
        
        # Load dataset with error handling
        try:
            df = pd.read_csv(DATA_FILE)
        except Exception as e:
            return f"Error reading CSV file: {str(e)}"
        
        # Check if dataframe is empty
        if df.empty:
            return "Error: The dataset is empty. Please check your CSV file."
        
        # Check for required columns
        required_columns = ['sentiment', 'urgency', 'category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return f"Error: Missing required columns in CSV: {', '.join(missing_columns)}. Available columns: {', '.join(df.columns)}"
        
        # Generate plots with smaller size to save memory
        plt.style.use('default')  # Use default style to avoid memory issues
        
        # Plot 1: Sentiment Distribution
        fig1, ax1 = plt.subplots(figsize=(8, 4))  # Smaller size
        sentiment_counts = df["sentiment"].value_counts()
        sentiment_counts.plot(kind='barh', ax=ax1, color=sns.color_palette("Dark2"))
        ax1.spines[['top', 'right']].set_visible(False)
        ax1.set_title('Sentiment Distribution')
        plot_url1 = plot_to_base64(fig1)

        # Plot 2: Urgency Distribution
        fig2, ax2 = plt.subplots(figsize=(8, 4))  # Smaller size
        urgency_counts = df["urgency"].value_counts()
        urgency_counts.plot(kind='barh', ax=ax2, color=sns.color_palette("Dark2"))
        ax2.spines[['top', 'right']].set_visible(False)
        ax2.set_title('Urgency Distribution')
        plot_url2 = plot_to_base64(fig2)

        # Plot 3: Category Distribution (only top 10 to save memory)
        fig3, ax3 = plt.subplots(figsize=(8, 4))  # Smaller size
        category_counts = df["category"].value_counts().head(10)  # Only top 10
        category_counts.plot(kind='barh', ax=ax3, color=sns.color_palette("Dark2"))
        ax3.spines[['top', 'right']].set_visible(False)
        ax3.set_title('Top 10 Categories Distribution')
        plot_url3 = plot_to_base64(fig3)

        # Statistics
        stats = {
            'total_tickets': len(df),
            'sentiment_counts': df['sentiment'].value_counts().to_dict(),
            'urgency_counts': df['urgency'].value_counts().to_dict(),
            'category_counts': df['category'].value_counts().head(10).to_dict(),  # Only top 10
            'data_preview': df.head(3).to_dict(orient='records')  # Sample data for debugging
        }

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return render_template('index.html',
                               plot1=plot_url1,
                               plot2=plot_url2,
                               plot3=plot_url3,
                               stats=stats,
                               current_time=current_time)

    except MemoryError:
        return """
        <h1>Memory Error</h1>
        <p>The application exceeded memory limits on Render's free tier.</p>
        <p>This is likely due to the CSV file being too large or too many plots.</p>
        <p>Try reducing the CSV file size or upgrading to a paid plan.</p>
        """
    except Exception as e:
        return f"""
        <h1>Application Error</h1>
        <p><strong>Error Type:</strong> {type(e).__name__}</p>
        <p><strong>Error Message:</strong> {str(e)}</p>
        <p><strong>Current Directory:</strong> {os.getcwd()}</p>
        <p><strong>Files Present:</strong> {', '.join(os.listdir('.'))}</p>
        """

@app.route('/debug')
def debug():
    """Debug endpoint to check file status"""
    try:
        files = os.listdir('.')
        csv_exists = os.path.exists(DATA_FILE)
        csv_size = os.path.getsize(DATA_FILE) if csv_exists else 0
        
        return jsonify({
            'status': 'debug',
            'current_directory': os.getcwd(),
            'files': files,
            'csv_exists': csv_exists,
            'csv_size': csv_size,
            'csv_columns': list(pd.read_csv(DATA_FILE).columns) if csv_exists and csv_size > 0 else []
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/data')
def get_data():
    try:
        if not os.path.exists(DATA_FILE):
            return jsonify({'success': False, 'error': f'File {DATA_FILE} not found'})
        
        df = pd.read_csv(DATA_FILE)
        return jsonify({
            'success': True,
            'data': df.head(50).to_dict(orient='records'),  # Limit to 50 records
            'total_records': len(df)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
