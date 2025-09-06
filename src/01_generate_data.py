import requests
import pandas as pd
import random
import json
import time
import os
from datetime import datetime

class DataGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "deepseek-r1:8b"
        self.products = [
            "CloudSync Pro", 
            "FinanceManager SaaS", 
            "StreamFlix Subscription", 
            "HomeSecurity Hub", 
            "GymFlow App",
            "OfficeSuite 365",
            "DataBackup Pro",
            "EmailShield Security",
            "ProjectFlow Manager",
            "CustomerCRM Platform"
        ]
        self.issues = [
            "login problems", "billing dispute", "feature request", 
            "bug report", "account deletion", "performance issues",
            "subscription renewal", "data sync error", "mobile app crash",
            "payment failure", "account setup", "password reset",
            "invoice discrepancy", "feature not working", "slow performance"
        ]
        self.sentiments = ["frustrated", "neutral", "happy", "confused", "angry", "urgent", "satisfied", "disappointed"]
        
    def check_ollama_connection(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def generate_single_ticket(self, attempt=0):
        """Generate one customer support ticket"""
        if attempt > 3:
            return None, None
            
        product = random.choice(self.products)
        issue = random.choice(self.issues)
        sentiment = random.choice(self.sentiments)
        
        prompt = f"""
        Generate a realistic customer support ticket for '{product}' about '{issue}'.
        The customer should sound {sentiment}.
        Include specific details like error messages, account IDs, timestamps, or feature names.
        Make it 2-3 sentences maximum.
        Return ONLY the ticket text without any explanations or formatting.
        """
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.85,
                "seed": random.randint(1, 100000)
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=180)
            response.raise_for_status()
            
            response_data = response.json()
            generated_text = response_data.get('response', '').strip()
            
            # Clean up the response
            lines = generated_text.split('\n')
            clean_lines = []
            for line in lines:
                clean_line = line.strip()
                if (clean_line and 
                    not clean_line.startswith(('Sure', 'Here', '```', '**', '===')) and
                    len(clean_line) > 15 and
                    not clean_line.lower().startswith('customer') and
                    not clean_line.lower().startswith('subject')):
                    clean_lines.append(clean_line)
            
            if clean_lines:
                return ' '.join(clean_lines[:2]), product
            else:
                return generated_text[:150], product
            
        except requests.exceptions.Timeout:
            print("Request timeout, retrying...")
            time.sleep(3)
            return self.generate_single_ticket(attempt + 1)
        except requests.exceptions.ConnectionError:
            print("Connection error, waiting 10 seconds...")
            time.sleep(10)
            return self.generate_single_ticket(attempt + 1)
        except Exception as e:
            print(f"Error generating ticket: {e}")
            time.sleep(2)
            return None, None
    
    def generate_dataset(self, num_tickets=1200):
        """Generate multiple tickets and save to CSV with checkpointing"""
        print("🔍 Checking Ollama connection...")
        if not self.check_ollama_connection():
            print("❌ Ollama is not running. Please start Ollama first!")
            print("💡 Run: ollama serve")
            return False
        
        print("✅ Ollama is running!")
        print(f"🚀 Generating {num_tickets} synthetic tickets...")
        print("💡 This will take approximately 60-90 minutes")
        print("💡 Press Ctrl+C to pause and save progress\n")
        
        tickets = []
        products_used = []
        successful_tickets = 0
        start_time = time.time()
        
        # Try to load existing progress if any
        checkpoint_file = 'generated_tickets_checkpoint.csv'
        if os.path.exists(checkpoint_file):
            try:
                existing_df = pd.read_csv(checkpoint_file)
                tickets = existing_df['ticket_text'].tolist()
                products_used = existing_df['product'].tolist()
                successful_tickets = len(tickets)
                print(f"📂 Loaded {successful_tickets} existing tickets from checkpoint")
            except:
                pass
        
        try:
            for i in range(successful_tickets, num_tickets):
                print(f"📝 Generating ticket {i+1}/{num_tickets}...")
                ticket, product = self.generate_single_ticket()
                
                if ticket:
                    tickets.append(ticket)
                    products_used.append(product)
                    successful_tickets += 1
                    
                    if successful_tickets % 10 == 0:
                        elapsed = time.time() - start_time
                        avg_time = elapsed / successful_tickets
                        remaining = (num_tickets - successful_tickets) * avg_time
                        print(f"   ✅ {successful_tickets}/{num_tickets} - "
                              f"Avg: {avg_time:.1f}s/ticket - "
                              f"ETA: {remaining/60:.1f}min")
                        
                        # Save checkpoint every 50 tickets
                        if successful_tickets % 50 == 0:
                            self._save_checkpoint(tickets, products_used, checkpoint_file)
                            print(f"💾 Checkpoint saved at {successful_tickets} tickets")
                
                else:
                    print("   ❌ Failed to generate ticket, skipping...")
                
                # Dynamic sleep based on performance
                sleep_time = random.uniform(1.5, 3.0)
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n⏸️  Generation paused by user. Saving progress...")
        
        # Final save
        self._save_final_dataset(tickets, products_used)
        
        total_time = time.time() - start_time
        print(f"\n🎉 Successfully generated {successful_tickets} tickets!")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"📊 Average: {total_time/successful_tickets:.1f} seconds per ticket")
        print("💾 Saved to 'generated_tickets.csv'")
        
        return True
    
    def _save_checkpoint(self, tickets, products_used, filename):
        """Save progress to checkpoint file"""
        df = pd.DataFrame({
            'ticket_id': range(1, len(tickets) + 1),
            'product': products_used,
            'ticket_text': tickets
        })
        df.to_csv(filename, index=False)
    
    def _save_final_dataset(self, tickets, products_used):
        """Save final dataset with timestamp"""
        df = pd.DataFrame({
            'ticket_id': range(1, len(tickets) + 1),
            'product': products_used,
            'ticket_text': tickets,
            'generated_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        df.to_csv('generated_tickets.csv', index=False)
        
        # Save a backup with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backups/generated_tickets_{timestamp}.csv'
        os.makedirs('backups', exist_ok=True)
        df.to_csv(backup_file, index=False)

def main():
    """Main function to generate data"""
    print("=" * 60)
    print("🤖 AI-Powered Customer Support Data Generator")
    print("🔄 Optimized for 1200 tickets")
    print("💻 Hardware: RTX 3060 8GB + 16GB RAM")
    print("=" * 60)
    
    generator = DataGenerator()
    success = generator.generate_dataset(num_tickets=1200)
    
    if success:
        print("\n✅ Data generation completed successfully!")
        print("\nNext step: Run '02_analyze_data.py' to analyze the tickets")
    else:
        print("\n❌ Data generation failed!")

if __name__ == "__main__":
    main()