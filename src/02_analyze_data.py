import requests
import pandas as pd
import json
import time
import re
from typing import Dict, Any
from datetime import datetime
import os
import random  # Moved to top level

class TicketAnalyzer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "deepseek-r1:8b"
        
    def check_ollama_connection(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            return response.status_code == 200
        except:
            return False
        
    def clean_json_response(self, raw_response: str) -> Dict[str, Any]:
        """Clean and extract JSON from the model's response - FIXED VERSION"""
        try:
            # Remove markdown code blocks if present
            cleaned_response = re.sub(r'```json|```', '', raw_response).strip()
            
            # Remove any text before the first {
            json_start = cleaned_response.find('{')
            if json_start != -1:
                cleaned_response = cleaned_response[json_start:]
            
            # Remove any text after the last }
            json_end = cleaned_response.rfind('}')
            if json_end != -1:
                cleaned_response = cleaned_response[:json_end + 1]
            
            # 🔥 CRITICAL FIX 1: Remove extra closing braces (}} issue)
            cleaned_response = re.sub(r'}\s*}$', '}', cleaned_response)
            
            # Fix common JSON issues
            cleaned_response = cleaned_response.replace("'", '"')  # Replace single quotes with double quotes
            cleaned_response = re.sub(r',\s*}', '}', cleaned_response)  # Remove trailing commas
            cleaned_response = re.sub(r',\s*]', ']', cleaned_response)  # Remove trailing commas in arrays
            
            # Parse the JSON
            analysis_data = json.loads(cleaned_response)
            return analysis_data
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON decode error: {e}")
            print(f"   ❌ Problematic response: {raw_response[:200]}...")
            return None
        except Exception as e:
            print(f"   ❌ Other error cleaning JSON: {e}")
            return None
    
    def analyze_ticket(self, ticket_text: str, attempt: int = 0) -> Dict[str, Any]:
        """Analyze a single ticket and extract structured data - FIXED VERSION"""
        if attempt > 2:
            return self.get_error_response()
            
        prompt = f"""
        Analyze this customer support ticket and return ONLY valid JSON without any other text.
        
        REQUIRED JSON FORMAT:
        {{
          "sentiment": "Negative", "Neutral", or "Positive",
          "urgency": "High", "Medium", or "Low",
          "category": "Billing", "Login Issue", "Feature Request", "Bug Report", "Technical Issue", "Account Management", "Payment Issue", "Other",
          "summary": "One-sentence summary of the issue"
        }}
        
        TICKET TEXT: "{ticket_text[:500]}"  # Limit text length for efficiency
        """
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.3,
                "seed": random.randint(1, 100000)
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=180)
            response.raise_for_status()
            
            response_data = response.json()
            raw_response = response_data.get('response', '').strip()
            
            if not raw_response:
                print("   ⚠️ Empty response from model")
                return self.get_error_response()
            
            # Use the improved JSON cleaning function
            analysis_data = self.clean_json_response(raw_response)
            
            if analysis_data is None:
                print("   ⚠️ JSON parsing failed, retrying...")
                time.sleep(2)
                return self.analyze_ticket(ticket_text, attempt + 1)
            
            # 🔥 CRITICAL FIX 2: Handle missing keys gracefully
            required_keys = {"sentiment", "urgency", "category", "summary"}
            missing_keys = required_keys - set(analysis_data.keys())
            
            if missing_keys:
                print(f"   ⚠️ Missing keys: {missing_keys}. Got: {list(analysis_data.keys())}")
                
                # Try to fill in missing keys with defaults
                for key in missing_keys:
                    if key == "sentiment":
                        analysis_data["sentiment"] = "Neutral"
                    elif key == "urgency":
                        analysis_data["urgency"] = "Medium"
                    elif key == "category":
                        analysis_data["category"] = "Other"
                    elif key == "summary":
                        analysis_data["summary"] = "No summary generated"
                
                print(f"   ⚠️ Fixed missing keys: {analysis_data}")
            
            # Validate values are acceptable
            valid_sentiments = {"Negative", "Neutral", "Positive"}
            valid_urgency = {"High", "Medium", "Low"}
            valid_categories = {"Billing", "Login Issue", "Feature Request", "Bug Report", 
                               "Technical Issue", "Account Management", "Payment Issue", "Other"}
            
            if (analysis_data.get("sentiment") in valid_sentiments and
                analysis_data.get("urgency") in valid_urgency and
                analysis_data.get("category") in valid_categories):
                
                return analysis_data
            else:
                print(f"   ⚠️ Invalid values in response: {analysis_data}")
                return self.get_error_response()
                
        except requests.exceptions.Timeout:
            print("   ⏰ Request timeout, retrying...")
            time.sleep(5)
            return self.analyze_ticket(ticket_text, attempt + 1)
        except requests.exceptions.ConnectionError:
            print("   🔌 Connection error, waiting 15 seconds...")
            time.sleep(15)
            return self.analyze_ticket(ticket_text, attempt + 1)
        except Exception as e:
            print(f"❌ Error analyzing ticket: {e}")
            time.sleep(3)
            return self.get_error_response()
    
    def get_error_response(self) -> Dict[str, Any]:
        """Return default error response"""
        return {
            "sentiment": "Error",
            "urgency": "Error", 
            "category": "Error",
            "summary": "Analysis failed"
        }
    
    def analyze_dataset(self, input_file: str = 'generated_tickets.csv', 
                       output_file: str = 'analyzed_tickets.csv'):
        """Analyze all tickets in the dataset"""
        print("🔍 Checking Ollama connection...")
        if not self.check_ollama_connection():
            print("❌ Ollama is not running. Please start Ollama first!")
            print("💡 Run: ollama serve")
            return False
            
        print("📖 Loading generated tickets...")
        try:
            df = pd.read_csv(input_file)
        except FileNotFoundError:
            print(f"❌ File {input_file} not found. Run 01_generate_data.py first!")
            return False
        
        print(f"✅ Loaded {len(df)} tickets")
        print(f"🔍 Analyzing {len(df)} tickets with local LLM...")
        print("⏰ This will take 60-90 minutes for 1200 tickets...")
        print("💡 Press Ctrl+C to pause and save progress\n")
        
        # Try to load existing progress
        analyses = []
        start_index = 0
        checkpoint_file = 'analyzed_tickets_checkpoint.csv'
        
        if os.path.exists(checkpoint_file):
            try:
                existing_df = pd.read_csv(checkpoint_file)
                analyses = existing_df[['sentiment', 'urgency', 'category', 'summary']].to_dict('records')
                start_index = len(analyses)
                print(f"📂 Resuming from checkpoint: {start_index}/{len(df)} tickets already analyzed")
            except:
                print("⚠️ Could not load checkpoint, starting from beginning")
        
        start_time = time.time()
        
        try:
            for index in range(start_index, len(df)):
                if index >= len(df):
                    break
                    
                row = df.iloc[index]
                print(f"   Analyzing ticket {index + 1}/{len(df)}...")
                
                analysis = self.analyze_ticket(row['ticket_text'])
                analyses.append(analysis)
                
                print(f"      ✅ {analysis['sentiment']} | {analysis['urgency']} | {analysis['category']}")
                
                # Progress tracking every 10 tickets
                if (index + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (index + 1 - start_index)
                    remaining = (len(df) - (index + 1)) * avg_time
                    print(f"   📊 {index + 1}/{len(df)} - "
                          f"Avg: {avg_time:.1f}s/ticket - "
                          f"ETA: {remaining/60:.1f}min")
                
                # Save checkpoint every 50 tickets
                if (index + 1) % 50 == 0:
                    self._save_checkpoint(df, analyses, checkpoint_file, index + 1)
                    print(f"💾 Checkpoint saved at {index + 1} tickets")
                
                # Dynamic sleep to prevent overheating
                sleep_time = random.uniform(1.5, 2.5)
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n⏸️  Analysis paused by user. Saving progress...")
            self._save_checkpoint(df, analyses, checkpoint_file, len(analyses))
            return False
        
        # Final save
        result_df = self._save_final_results(df, analyses, output_file)
        
        total_time = time.time() - start_time
        print(f"\n🎉 Analysis completed!")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"📊 Average: {total_time/len(analyses):.1f} seconds per ticket")
        print(f"💾 Saved to '{output_file}'")
        
        # Show summary
        self.print_summary(result_df)
        
        return result_df
    
    def _save_checkpoint(self, df, analyses, filename, current_count):
        """Save progress to checkpoint file"""
        if len(analyses) > 0:
            result_df = pd.concat([df.iloc[:len(analyses)], pd.DataFrame(analyses)], axis=1)
            result_df.to_csv(filename, index=False)
    
    def _save_final_results(self, df, analyses, output_file):
        """Save final results with timestamp"""
        result_df = pd.concat([df, pd.DataFrame(analyses)], axis=1)
        result_df.to_csv(output_file, index=False)
        
        # Save backup with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'analysis_backups'
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = f'{backup_dir}/analyzed_tickets_{timestamp}.csv'
        result_df.to_csv(backup_file, index=False)
        
        return result_df
    
    def print_summary(self, df: pd.DataFrame):
        """Print analysis summary"""
        print("\n" + "="*60)
        print("📊 AI-POWERED ANALYSIS SUMMARY")
        print("="*60)
        
        # Filter out errors
        valid_df = df[df['sentiment'] != 'Error']
        
        if len(valid_df) > 0:
            # Sentiment distribution
            sentiment_counts = valid_df['sentiment'].value_counts()
            print(f"\n😊 Sentiment Distribution ({len(valid_df)} valid tickets):")
            for sentiment, count in sentiment_counts.items():
                percentage = count/len(valid_df)*100
                print(f"   {sentiment}: {count} tickets ({percentage:.1f}%)")
            
            # Category distribution
            category_counts = valid_df['category'].value_counts()
            print(f"\n📋 Top Categories:")
            for category, count in category_counts.head(10).items():
                print(f"   {category}: {count} tickets")
            
            # Urgency distribution
            urgency_counts = valid_df['urgency'].value_counts()
            print(f"\n🚨 Urgency Levels:")
            for urgency, count in urgency_counts.items():
                percentage = count/len(valid_df)*100
                print(f"   {urgency}: {count} tickets ({percentage:.1f}%)")
        
        # Error rate
        error_count = len(df[df['sentiment'] == 'Error'])
        print(f"\n❌ Analysis Errors: {error_count}/{len(df)} ({error_count/len(df)*100:.1f}%)")
        
        # Data quality metrics
        print(f"\n📈 Data Quality:")
        print(f"   Total Tickets: {len(df)}")
        print(f"   Successfully Analyzed: {len(valid_df)} ({len(valid_df)/len(df)*100:.1f}%)")
        
        if len(valid_df) > 0:
            avg_summary_length = valid_df['summary'].str.len().mean()
            print(f"   Avg Summary Length: {avg_summary_length:.1f} characters")

def main():
    """Main function to analyze data"""
    print("=" * 60)
    print("🔍 AI-Powered Customer Support Analyzer")
    print("🔄 Optimized for 1200 tickets")
    print("💻 Hardware: RTX 3060 8GB + 16GB RAM")
    print("=" * 60)
    
    analyzer = TicketAnalyzer()
    result_df = analyzer.analyze_dataset()
    
    if result_df is not False:
        print("\n✅ Analysis completed successfully!")
        print("\nNext step: Run '03_visualize_results.py' to create visualizations")
    else:
        print("\n❌ Analysis failed or paused!")

if __name__ == "__main__":
    main()