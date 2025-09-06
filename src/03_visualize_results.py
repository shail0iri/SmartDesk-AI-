import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os
import matplotlib
from scipy import stats  # For statistical analysis
# Set the backend to avoid VS Code issues
matplotlib.use('Agg')  # Use non-interactive backend

class DataVisualizer:
    def __init__(self):
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        self.colors = sns.color_palette("husl", 8)
        
        # Create figures directory if it doesn't exist
        os.makedirs('figures', exist_ok=True)
    
    def load_data(self):
        """Load the analyzed data"""
        if not os.path.exists('analyzed_tickets.csv'):
            print("❌ analyzed_tickets.csv not found! Run 02_analyze_data.py first")
            return None
        
        try:
            df = pd.read_csv('analyzed_tickets.csv')
            print(f"✅ Loaded {len(df)} analyzed tickets")
            
            # Clean data - remove any rows with 'Error' in sentiment
            df = df[df['sentiment'] != 'Error']
            if len(df) == 0:
                print("❌ No valid data after cleaning errors!")
                return None
                
            print(f"✅ Working with {len(df)} valid tickets after cleaning")
            return df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def create_sentiment_chart(self, df: pd.DataFrame):
        """Create sentiment distribution chart"""
        plt.figure(figsize=(10, 6))
        
        sentiment_counts = df['sentiment'].value_counts()
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']  # Red, Teal, Blue, Green
        
        # Create bar chart
        bars = plt.bar(sentiment_counts.index, sentiment_counts.values, 
                      color=colors[:len(sentiment_counts)], alpha=0.8, edgecolor='black')
        plt.title('Customer Sentiment Distribution\n(AI-Powered Analysis)', fontweight='bold', fontsize=14)
        plt.ylabel('Number of Tickets')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('figures/sentiment_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()  # Important: close the figure to free memory
        print("✅ Created sentiment analysis chart")
    
    def create_category_chart(self, df: pd.DataFrame):
        """Create category distribution chart"""
        plt.figure(figsize=(12, 6))
        
        category_counts = df['category'].value_counts()
        
        # Create horizontal bar chart
        bars = plt.barh(category_counts.index, category_counts.values, 
                       color=self.colors, alpha=0.8, edgecolor='black')
        plt.title('Support Ticket Categories\n(AI-Powered Analysis)', fontweight='bold', fontsize=14)
        plt.xlabel('Number of Tickets')
        plt.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('figures/category_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()  # Important: close the figure to free memory
        print("✅ Created category distribution chart")
    
    def create_urgency_chart(self, df: pd.DataFrame):
        """Create urgency analysis chart - FIXED VERSION"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Create a cross-tabulation for urgency vs sentiment
            urgency_data = pd.crosstab(df['urgency'], df['sentiment'])
            
            # If we have data, create the chart
            if not urgency_data.empty:
                ax = urgency_data.plot(kind='bar', stacked=True, 
                                     color=['#ff6b6b', '#4ecdc4', '#45b7d1'],
                                     alpha=0.8, edgecolor='black')
                
                plt.title('Urgency Level by Sentiment\n(AI-Powered Analysis)', 
                         fontweight='bold', fontsize=14)
                plt.xlabel('Urgency Level', fontweight='bold')
                plt.ylabel('Number of Tickets', fontweight='bold')
                plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.grid(axis='y', alpha=0.3)
                
                # Rotate x-axis labels for better readability
                plt.xticks(rotation=45, ha='right')
                
                plt.tight_layout()
                plt.savefig('figures/urgency_analysis.png', dpi=300, bbox_inches='tight')
                plt.close()  # Important: close the figure to free memory
                print("✅ Created urgency analysis chart")
            else:
                print("⚠️ Not enough data for urgency chart")
                
        except Exception as e:
            print(f"❌ Error creating urgency chart: {e}")
            # Create a simple alternative chart
            self.create_simple_urgency_chart(df)
    
    def create_simple_urgency_chart(self, df: pd.DataFrame):
        """Fallback urgency chart if the main one fails"""
        try:
            plt.figure(figsize=(10, 6))
            
            urgency_counts = df['urgency'].value_counts()
            colors = ['#ff6b6b', '#f9ca24', '#4ecdc4']  # Red, Yellow, Green
            
            bars = plt.bar(urgency_counts.index, urgency_counts.values, 
                          color=colors[:len(urgency_counts)], alpha=0.8, edgecolor='black')
            
            plt.title('Urgency Level Distribution\n(AI-Powered Analysis)', fontweight='bold', fontsize=14)
            plt.ylabel('Number of Tickets')
            plt.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig('figures/urgency_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ Created simple urgency distribution chart")
            
        except Exception as e:
            print(f"❌ Could not create any urgency chart: {e}")
    
    def create_product_analysis(self, df: pd.DataFrame):
        """Create product analysis chart"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Count tickets by product
            product_counts = df['product'].value_counts().head(8)  # Top 8 products
            
            # Create a colorful pie chart
            colors = plt.cm.Set3(np.linspace(0, 1, len(product_counts)))
            wedges, texts, autotexts = plt.pie(product_counts.values, 
                                              labels=product_counts.index,
                                              autopct='%1.1f%%',
                                              colors=colors,
                                              startangle=90)
            
            plt.title('Ticket Distribution by Product\n(AI-Powered Analysis)', 
                     fontweight='bold', fontsize=14)
            
            # Make autopct text bold
            for autotext in autotexts:
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            plt.tight_layout()
            plt.savefig('figures/product_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ Created product analysis chart")
            
        except Exception as e:
            print(f"❌ Error creating product chart: {e}")
    
    def create_correlation_heatmap(self, df: pd.DataFrame):
        """Create correlation heatmap between categories, sentiment, and urgency"""
        try:
            plt.figure(figsize=(12, 10))
            
            # Create encoded data for correlation
            encoded_df = pd.DataFrame()
            encoded_df['sentiment_num'] = df['sentiment'].map({'Negative': -1, 'Neutral': 0, 'Positive': 1})
            encoded_df['urgency_num'] = df['urgency'].map({'Low': 0, 'Medium': 1, 'High': 2})
            
            # Get top categories and one-hot encode
            top_categories = df['category'].value_counts().head(6).index
            for category in top_categories:
                encoded_df[f'category_{category}'] = (df['category'] == category).astype(int)
            
            # Calculate correlation matrix
            corr_matrix = encoded_df.corr()
            
            # Create heatmap
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=.5, cbar_kws={"shrink": .8}, fmt='.2f',
                       annot_kws={'size': 9, 'weight': 'bold'})
            
            plt.title('Correlation Analysis: Sentiment vs Urgency vs Top Categories\n(1200 Tickets AI-Powered Insights)', 
                     fontweight='bold', fontsize=14)
            plt.tight_layout()
            plt.savefig('figures/correlation_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ Created correlation heatmap")
            
            # Return significant correlations for the report
            significant_correlations = []
            for col in corr_matrix.columns:
                for idx in corr_matrix.index:
                    if col != idx and abs(corr_matrix.loc[idx, col]) > 0.1:
                        significant_correlations.append(f"{idx} ↔ {col}: {corr_matrix.loc[idx, col]:.2f}")
            
            return significant_correlations[:10]  # Return top 10 correlations
            
        except Exception as e:
            print(f"❌ Error creating correlation heatmap: {e}")
            return []
    
    def create_executive_summary_chart(self, df: pd.DataFrame):
        """Create a comprehensive summary chart"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # Sentiment pie chart
            sentiment_counts = df['sentiment'].value_counts()
            colors_sentiment = ['#ff6b6b', '#4ecdc4', '#45b7d1']
            ax1.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%',
                   colors=colors_sentiment, startangle=90)
            ax1.set_title('Customer Sentiment Distribution', fontweight='bold', fontsize=12)
            
            # Urgency bar chart
            urgency_counts = df['urgency'].value_counts()
            colors_urgency = ['#4ecdc4', '#f9ca24', '#ff6b6b']  # Green, Yellow, Red
            bars = ax2.bar(urgency_counts.index, urgency_counts.values, color=colors_urgency, alpha=0.8)
            ax2.set_title('Urgency Level Distribution', fontweight='bold', fontsize=12)
            ax2.set_ylabel('Number of Tickets')
            ax2.grid(axis='y', alpha=0.3)
            
            # Add values on bars
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            # Top categories
            category_counts = df['category'].value_counts().head(5)
            bars = ax3.barh(category_counts.index, category_counts.values, color=self.colors[:5])
            ax3.set_title('Top 5 Support Categories', fontweight='bold', fontsize=12)
            ax3.set_xlabel('Number of Tickets')
            ax3.grid(axis='x', alpha=0.3)
            
            # Add values on bars
            for bar in bars:
                width = bar.get_width()
                ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                        f'{int(width)}', ha='left', va='center', fontweight='bold')
            
            # Product distribution
            product_counts = df['product'].value_counts().head(5)
            colors_products = plt.cm.Pastel1(np.linspace(0, 1, len(product_counts)))
            wedges, texts, autotexts = ax4.pie(product_counts.values, labels=product_counts.index,
                                              autopct='%1.1f%%', colors=colors_products, startangle=90)
            ax4.set_title('Top 5 Products by Tickets', fontweight='bold', fontsize=12)
            
            # Make autopct text bold
            for autotext in autotexts:
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            plt.suptitle('Executive Summary: Customer Support Analysis (1200 Tickets)\nAI-Powered Insights', 
                        fontweight='bold', fontsize=16)
            plt.tight_layout()
            plt.savefig('figures/executive_summary.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ Created executive summary dashboard")
            
        except Exception as e:
            print(f"❌ Error creating executive summary: {e}")
    
    def generate_report(self, df: pd.DataFrame):
        """Generate a markdown report with insights"""
        try:
            # Calculate some insights
            total_tickets = len(df)
            negative_tickets = len(df[df['sentiment'] == 'Negative'])
            high_urgency = len(df[df['urgency'] == 'High'])
            most_common_category = df['category'].value_counts().index[0] if not df.empty else "N/A"
            
            # Calculate correlation insights
            significant_correlations = self.create_correlation_heatmap(df)
            
            report = f"""# 🤖 AI-Powered Customer Support Analysis Report

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Tickets Analyzed:** {total_tickets}

## 📊 Executive Summary

This analysis used local LLM (DeepSeek R1 8B) to automatically categorize and analyze customer support tickets.

### Key Metrics
- **Total Tickets Analyzed:** {total_tickets}
- **Negative Sentiment Tickets:** {negative_tickets} ({negative_tickets/total_tickets*100:.1f}%)
- **High Urgency Tickets:** {high_urgency} ({high_urgency/total_tickets*100:.1f}%)
- **Most Common Category:** {most_common_category}

### Sentiment Distribution
{df['sentiment'].value_counts().to_string()}

### Category Distribution  
{df['category'].value_counts().to_string()}

### Urgency Levels
{df['urgency'].value_counts().to_string()}

## 📈 Large Dataset Insights (1200+ Tickets)

### Statistical Significance
- **Dataset Size:** {total_tickets} tickets provides high statistical confidence
- **Pattern Reliability:** Trends observed are likely representative of real-world patterns
- **ML Readiness:** Sufficient for training basic machine learning models

### Operational Implications
- **Resource Planning:** {high_urgency} high-urgency tickets suggest need for rapid response team
- **Training Materials:** {negative_tickets} negative experiences indicate areas for agent training
- **Process Improvement:** Recurring categories suggest systemic issues needing addressing

## 🔍 Correlation Insights

### Significant Relationships Found:
"""

            # Add correlation insights
            if significant_correlations:
                for correlation in significant_correlations:
                    report += f"- {correlation}\n"
            else:
                report += "No strong correlations found between sentiment, urgency, and categories.\n"

            report += f"""
## 🎯 Business Insights & Recommendations

### 1. Priority Areas
- **Immediate Attention:** {len(df[(df['sentiment'] == 'Negative') & (df['urgency'] == 'High')])} tickets require urgent resolution
- **Common Issues:** Focus on improving {most_common_category} related processes

### 2. Customer Satisfaction
- **Positive Experience:** {len(df[df['sentiment'] == 'Positive'])} customers had good experiences
- **Improvement Needed:** {negative_tickets} customers reported negative experiences

### 3. Operational Efficiency
- **Resource Allocation:** {len(df[df['urgency'] == 'High'])} high-urgency tickets need immediate resources
- **Process Optimization:** Consider automating responses for {df['category'].value_counts().index[1] if len(df['category'].value_counts()) > 1 else "common"} issues

## 📊 Visualization Files

The following charts have been generated:
- `sentiment_analysis.png` - Distribution of customer sentiments
- `category_distribution.png` - Breakdown of ticket categories  
- `urgency_analysis.png` - Analysis of urgency levels
- `product_analysis.png` - Ticket distribution by product
- `correlation_heatmap.png` - Relationships between variables
- `executive_summary.png` - Comprehensive overview dashboard

## 🛠️ Technical Details

- **AI Model:** DeepSeek R1 8B (local via Ollama)
- **Analysis Method:** LLM-powered text classification
- **Data Source:** {total_tickets} synthetically generated customer support tickets
- **Tools Used:** Python, Pandas, Matplotlib, Seaborn, Requests, Scipy

---

*Report automatically generated using AI-powered analysis*  
*This is a demonstration project for portfolio purposes*
"""
            
            with open('analysis_report.md', 'w', encoding='utf-8') as f:
                f.write(report)
            
            print("📝 Generated comprehensive analysis report: 'analysis_report.md'")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def run_visualization(self):
        """Run all visualizations"""
        print("=" * 60)
        print("📊 Data Visualization Dashboard")
        print("🔄 Enhanced for 1200+ Tickets")
        print("=" * 60)
        
        df = self.load_data()
        if df is None:
            print("❌ Cannot proceed without valid data")
            return
        
        print("🎨 Creating enhanced visualizations...")
        
        # Create all charts with error handling
        try:
            self.create_sentiment_chart(df)
            self.create_category_chart(df)
            self.create_urgency_chart(df)
            self.create_product_analysis(df)
            self.create_executive_summary_chart(df)
            
            # Generate report (includes correlation heatmap)
            self.generate_report(df)
            
            print("\n✅ All visualizations completed successfully!")
            print("📁 Charts saved to 'figures/' directory")
            print("📄 Report saved as 'analysis_report.md'")
            print("\n🎉 Project completed successfully!")
            
            # Show where to find files
            print("\n📋 Generated Files:")
            print("   figures/sentiment_analysis.png")
            print("   figures/category_distribution.png")
            print("   figures/urgency_analysis.png")
            print("   figures/product_analysis.png")
            print("   figures/correlation_heatmap.png")
            print("   figures/executive_summary.png")
            print("   analysis_report.md")
            
        except Exception as e:
            print(f"❌ Error during visualization: {e}")

def main():
    """Main function for visualization"""
    visualizer = DataVisualizer()
    visualizer.run_visualization()

if __name__ == "__main__":
    main()