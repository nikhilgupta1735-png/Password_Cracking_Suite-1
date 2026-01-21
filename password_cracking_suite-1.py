#!/usr/bin/env python3
"""
Password Cracking & Credential Attack Suite
Educational cybersecurity toolkit for password security assessment
Author: Educational Project
Version: 1.0
"""

import hashlib
import itertools
import string
import time
import os
import re
import json
import csv
from datetime import datetime, timedelta
import argparse
import sys
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class DictionaryGenerator:
    """Generate custom wordlists for password testing"""
    
    def __init__(self):
        self.common_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master",
            "sunshine", "iloveyou", "princess", "football", "charlie",
            "login", "shadow", "superman", "michael", "jesus"
        ]
        
        self.keyboard_patterns = [
            "qwerty", "asdf", "zxcv", "qwertyuiop", "asdfghjkl",
            "zxcvbnm", "123456789", "qwe123", "asd123", "zxc123",
            "1qaz2wsx", "qazwsx", "123qwe", "qweasd", "zaqwsx"
        ]
        
    def generate_name_date_combinations(self, names, dates):
        """Generate combinations of names with dates"""
        combinations = []
        for name in names:
            for date in dates:
                # Name + full date
                combinations.append(f"{name}{date}")
                combinations.append(f"{name.lower()}{date}")
                combinations.append(f"{name.capitalize()}{date}")
                
                # Name + year only
                year = date[-4:] if len(date) >= 4 else date
                combinations.append(f"{name}{year}")
                combinations.append(f"{name.lower()}{year}")
                
                # Date + name
                combinations.append(f"{date}{name}")
                combinations.append(f"{date}{name.lower()}")
                
        return combinations
    
    def apply_mutations(self, word_list):
        """Apply leet speak and other mutations"""
        mutations = []
        leet_map = {
            'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'],
            's': ['$', '5'], 't': ['7'], 'l': ['1'], 'g': ['9']
        }
        
        for word in word_list:
            # Original word
            mutations.append(word)
            
            # Uppercase variations
            mutations.append(word.upper())
            mutations.append(word.capitalize())
            
            # Leet speak variations
            leet_word = word.lower()
            for char, replacements in leet_map.items():
                for replacement in replacements:
                    leet_word = leet_word.replace(char, replacement)
            mutations.append(leet_word)
            
            # Add numbers at the end
            for i in range(10):
                mutations.append(f"{word}{i}")
                mutations.append(f"{word}0{i}")
                mutations.append(f"{word}{i}{i}")
            
            # Add years
            for year in range(1990, 2025):
                mutations.append(f"{word}{year}")
            
            # Add special characters
            for char in "!@#$":
                mutations.append(f"{word}{char}")
                mutations.append(f"{char}{word}")
        
        return list(set(mutations))  # Remove duplicates
    
    def generate_wordlist(self, names=None, dates=None, custom_words=None, 
                         include_common=True, include_keyboard=True):
        """Generate comprehensive wordlist"""
        wordlist = []
        
        # Add common passwords
        if include_common:
            wordlist.extend(self.common_passwords)
        
        # Add keyboard patterns
        if include_keyboard:
            wordlist.extend(self.keyboard_patterns)
        
        # Add custom words
        if custom_words:
            wordlist.extend(custom_words)
        
        # Add name-date combinations
        if names and dates:
            wordlist.extend(self.generate_name_date_combinations(names, dates))
        
        # Apply mutations to all words
        final_wordlist = self.apply_mutations(wordlist)
        
        return sorted(list(set(final_wordlist)))
    
    def save_wordlist(self, wordlist, filename):
        """Save wordlist to file"""
        with open(filename, 'w') as f:
            for word in wordlist:
                f.write(f"{word}\n")
        print(f"{Colors.GREEN}[+] Wordlist saved to {filename} ({len(wordlist)} entries){Colors.END}")

class HashExtractor:
    """Extract and analyze password hashes"""
    
    def __init__(self):
        self.hash_types = {
            32: "MD5",
            40: "SHA-1",
            56: "SHA-224", 
            64: "SHA-256",
            96: "SHA-384",
            128: "SHA-512",
            16: "LM Hash",
            32: "NTLM"
        }
    
    def identify_hash_type(self, hash_string):
        """Identify hash type based on length and format"""
        hash_string = hash_string.lower().strip()
        # Ensure hex-only hash
        if not re.fullmatch(r"[a-f0-9]+", hash_string):
            return "Not a valid hexadecimal hash"
        hash_lengths = {
        32:  ["MD5"],
        40:  ["SHA1"],
        56:  ["SHA224"],
        64:  ["SHA256", "BLAKE2s"],
        96:  ["SHA384"],
        128: ["SHA512", "BLAKE2b"]
        }
        length = len(hash_string)
        if length in hash_lengths:
            return f"Possible hash type(s): {', '.join(hash_lengths[length])}"
        else:
            return "Unknown hash type"
    
    def extract_linux_shadow_demo(self, shadow_content):
        """Demo function to parse shadow file content"""
        users = []
        lines = shadow_content.strip().split('\n')
        
        for line in lines:
            if line and not line.startswith('#'):
                parts = line.split(':')
                if len(parts) >= 2:
                    username = parts[0]
                    password_hash = parts[1]
                    
                    if password_hash and password_hash not in ['*', '!', '!!']:
                        users.append({
                            'username': username,
                            'hash': password_hash,
                            'hash_type': self.identify_hash_type(password_hash)
                        })
        
        return users
    
    def create_demo_hashes(self):
        """Create demo hashes for testing"""
        demo_passwords = ["password123", "admin", "qwerty", "welcome"]
        hashes = []
        
        for password in demo_passwords:
            # MD5
            md5_hash = hashlib.md5(password.encode()).hexdigest()
            hashes.append({
                'username': f'user_{password}',
                'password': password,  # For demo purposes only
                'hash': md5_hash,
                'hash_type': 'MD5'
            })
            
            # SHA-256
            sha256_hash = hashlib.sha256(password.encode()).hexdigest()
            hashes.append({
                'username': f'user_{password}_sha256',
                'password': password,  # For demo purposes only
                'hash': sha256_hash,
                'hash_type': 'SHA-256'
            })
        
        return hashes

class BruteForceSimulator:
    """Simulate brute-force password cracking"""
    
    def __init__(self):
        self.charset_lower = string.ascii_lowercase
        self.charset_upper = string.ascii_uppercase
        self.charset_digits = string.digits
        self.charset_special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
    def hash_password(self, password, hash_type='MD5'):
        """Hash password with specified algorithm"""
        if hash_type == 'MD5':
            return hashlib.md5(password.encode()).hexdigest()
        elif hash_type == 'SHA-1':
            return hashlib.sha1(password.encode()).hexdigest()
        elif hash_type == 'SHA-256':
            return hashlib.sha256(password.encode()).hexdigest()
        elif hash_type == 'SHA-512':
            return hashlib.sha512(password.encode()).hexdigest()
        return None
    
    def calculate_combinations(self, charset_size, max_length):
        """Calculate total possible combinations"""
        total = 0
        for length in range(1, max_length + 1):
            total += charset_size ** length
        return total
    
    def estimate_crack_time(self, charset_size, password_length, attempts_per_second=1000000):
        """Estimate time to crack password"""
        combinations = charset_size ** password_length
        # Average case: find password at 50% of search space
        avg_attempts = combinations / 2
        seconds = avg_attempts / attempts_per_second
        
        return {
            'combinations': combinations,
            'avg_attempts': avg_attempts,
            'seconds': seconds,
            'readable_time': self.format_time(seconds)
        }
    
    def format_time(self, seconds):
        """Format seconds into readable time"""
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.2f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.2f} hours"
        elif seconds < 31536000:
            return f"{seconds/86400:.2f} days"
        else:
            return f"{seconds/31536000:.2f} years"
    
    def dictionary_attack_simulation(self, target_hash, wordlist, hash_type='MD5'):
        """Simulate dictionary attack"""
        print(f"{Colors.YELLOW}[*] Starting dictionary attack simulation...{Colors.END}")
        start_time = time.time()
        
        for i, password in enumerate(wordlist):
            if i % 1000 == 0:
                print(f"{Colors.CYAN}[*] Tested {i} passwords...{Colors.END}")
            
            hashed = self.hash_password(password, hash_type)
            if hashed == target_hash:
                elapsed = time.time() - start_time
                return {
                    'success': True,
                    'password': password,
                    'attempts': i + 1,
                    'time_elapsed': elapsed
                }
        
        elapsed = time.time() - start_time
        return {
            'success': False,
            'attempts': len(wordlist),
            'time_elapsed': elapsed
        }
    
    def brute_force_simulation(self, target_hash, max_length=4, hash_type='MD5', charset='lower'):
        """Simulate brute force attack (limited for demo)"""
        print(f"{Colors.YELLOW}[*] Starting brute force simulation (max length: {max_length})...{Colors.END}")
        
        if charset == 'lower':
            chars = self.charset_lower
        elif charset == 'upper':
            chars = self.charset_upper
        elif charset == 'digits':
            chars = self.charset_digits
        elif charset == 'all':
            chars = self.charset_lower + self.charset_upper + self.charset_digits
        else:
            chars = self.charset_lower
        
        start_time = time.time()
        attempts = 0
        
        for length in range(1, max_length + 1):
            print(f"{Colors.CYAN}[*] Trying passwords of length {length}...{Colors.END}")
            
            for password_tuple in itertools.product(chars, repeat=length):
                password = ''.join(password_tuple)
                attempts += 1
                
                if attempts % 10000 == 0:
                    print(f"{Colors.CYAN}[*] Attempts: {attempts}...{Colors.END}")
                
                hashed = self.hash_password(password, hash_type)
                if hashed == target_hash:
                    elapsed = time.time() - start_time
                    return {
                        'success': True,
                        'password': password,
                        'attempts': attempts,
                        'time_elapsed': elapsed
                    }
                
                # Safety limit for demo
                if attempts > 100000:
                    print(f"{Colors.RED}[!] Demo limit reached (100,000 attempts){Colors.END}")
                    break
            
            if attempts > 100000:
                break
        
        elapsed = time.time() - start_time
        return {
            'success': False,
            'attempts': attempts,
            'time_elapsed': elapsed
        }

class PasswordStrengthAnalyzer:
    """Analyze password strength and security"""
    
    def __init__(self):
        self.common_passwords = set([
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master"
        ])
    
    def calculate_entropy(self, password):
        """Calculate password entropy"""
        charset_size = 0
        
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            charset_size += 32
        
        if charset_size == 0:
            return 0
        
        import math
        entropy = len(password) * math.log2(charset_size)
        return entropy
    
    def check_complexity_requirements(self, password):
        """Check if password meets complexity requirements"""
        requirements = {
            'length': len(password) >= 8,
            'uppercase': any(c.isupper() for c in password),
            'lowercase': any(c.islower() for c in password),
            'digits': any(c.isdigit() for c in password),
            'special_chars': any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        }
        
        score = sum(requirements.values())
        return requirements, score
    
    def detect_patterns(self, password):
        """Detect common patterns in passwords"""
        patterns = []
        
        # Sequential characters
        for i in range(len(password) - 2):
            if ord(password[i+1]) == ord(password[i]) + 1 and ord(password[i+2]) == ord(password[i]) + 2:
                patterns.append(f"Sequential characters: {password[i:i+3]}")
        
        # Repeated characters
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                patterns.append(f"Repeated characters: {password[i]*3}")
        
        # Common patterns
        common_patterns = ['123', 'abc', 'qwe', 'asd', 'zxc']
        for pattern in common_patterns:
            if pattern in password.lower():
                patterns.append(f"Common pattern: {pattern}")
        
        # Year detection
        import re
        years = re.findall(r'19\d{2}|20\d{2}', password)
        if years:
            patterns.append(f"Year detected: {years[0]}")
        
        return patterns
    
    def analyze_password(self, password):
        """Comprehensive password analysis"""
        entropy = self.calculate_entropy(password)
        requirements, complexity_score = self.check_complexity_requirements(password)
        patterns = self.detect_patterns(password)
        
        # Determine strength level
        if entropy < 30:
            strength = "Very Weak"
            color = Colors.RED
        elif entropy < 40:
            strength = "Weak"
            color = Colors.YELLOW
        elif entropy < 50:
            strength = "Fair"
            color = Colors.YELLOW
        elif entropy < 60:
            strength = "Good"
            color = Colors.GREEN
        else:
            strength = "Strong"
            color = Colors.GREEN
        
        # Check against common passwords
        is_common = password.lower() in self.common_passwords
        
        return {
            'password': password,
            'entropy': entropy,
            'strength': strength,
            'strength_color': color,
            'complexity_score': complexity_score,
            'requirements': requirements,
            'patterns': patterns,
            'is_common': is_common,
            'length': len(password)
        }

class ReportGenerator:
    """Generate security audit reports"""
    
    def __init__(self):
        self.report_data = {}
    
    def add_section(self, section_name, data):
        """Add section to report"""
        self.report_data[section_name] = data
    
    def generate_text_report(self, filename):
        """Generate text-based report"""
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PASSWORD SECURITY AUDIT REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for section, data in self.report_data.items():
                f.write(f"\n{section.upper()}\n")
                f.write("-" * len(section) + "\n")
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        f.write(f"{key}: {value}\n")
                elif isinstance(data, list):
                    for item in data:
                        f.write(f"• {item}\n")
                else:
                    f.write(f"{data}\n")
                
                f.write("\n")
        
        print(f"{Colors.GREEN}[+] Text report saved to {filename}{Colors.END}")
    
    def generate_json_report(self, filename):
        """Generate JSON report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'data': self.report_data
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"{Colors.GREEN}[+] JSON report saved to {filename}{Colors.END}")
    
    def generate_csv_report(self, password_analysis, filename):
        """Generate CSV report for password analysis"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Password', 'Length', 'Entropy', 'Strength', 'Complexity Score', 
                           'Is Common', 'Patterns', 'Uppercase', 'Lowercase', 'Digits', 'Special'])
            
            for analysis in password_analysis:
                writer.writerow([
                    analysis['password'],
                    analysis['length'],
                    f"{analysis['entropy']:.2f}",
                    analysis['strength'],
                    analysis['complexity_score'],
                    analysis['is_common'],
                    '; '.join(analysis['patterns']),
                    analysis['requirements']['uppercase'],
                    analysis['requirements']['lowercase'],
                    analysis['requirements']['digits'],
                    analysis['requirements']['special_chars']
                ])
        
        print(f"{Colors.GREEN}[+] CSV report saved to {filename}{Colors.END}")

class PasswordCrackingSuite:
    """Main suite coordinator"""
    
    def __init__(self):
        self.dict_gen = DictionaryGenerator()
        self.hash_extractor = HashExtractor()
        self.brute_force = BruteForceSimulator()
        self.analyzer = PasswordStrengthAnalyzer()
        self.reporter = ReportGenerator()
        
    def print_banner(self):
        """Print application banner"""
        banner = f"""
{Colors.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                Password Cracking & Credential Attack Suite   ║
║                        Educational Toolkit                   ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
{Colors.YELLOW}[!] FOR EDUCATIONAL AND AUTHORIZED TESTING ONLY{Colors.END}
{Colors.YELLOW}[!] USE RESPONSIBLY IN CONTROLLED ENVIRONMENTS{Colors.END}
        """
        print(banner)
    
    def interactive_menu(self):
        """Interactive menu system"""
        while True:
            print(f"\n{Colors.BOLD}=== MAIN MENU ==={Colors.END}")
            print("1. Generate Dictionary Wordlist")
            print("2. Analyze Password Hashes")
            print("3. Simulate Dictionary Attack")
            print("4. Simulate Brute Force Attack")
            print("5. Analyze Password Strength")
            print("6. Generate Security Report")
            print("7. Run Complete Assessment")
            print("8. Exit")
            
            choice = input(f"\n{Colors.CYAN}Select option (1-8): {Colors.END}")
            
            if choice == '1':
                self.dictionary_generation_menu()
            elif choice == '2':
                self.hash_analysis_menu()
            elif choice == '3':
                self.dictionary_attack_menu()
            elif choice == '4':
                self.brute_force_menu()
            elif choice == '5':
                self.strength_analysis_menu()
            elif choice == '6':
                self.report_generation_menu()
            elif choice == '7':
                self.complete_assessment()
            elif choice == '8':
                print(f"{Colors.GREEN}[+] Exiting... Stay secure!{Colors.END}")
                break
            else:
                print(f"{Colors.RED}[!] Invalid choice. Please try again.{Colors.END}")
    
    def dictionary_generation_menu(self):
        """Dictionary generation submenu"""
        print(f"\n{Colors.BOLD}=== DICTIONARY GENERATOR ==={Colors.END}")
        
        # Get user inputs
        names_input = input("Enter names (comma-separated, or press Enter for demo): ").strip()
        names = [name.strip() for name in names_input.split(',')] if names_input else ['john', 'mary', 'admin']
        
        dates_input = input("Enter dates (DDMMYYYY format, comma-separated, or press Enter for demo): ").strip()
        dates = [date.strip() for date in dates_input.split(',')] if dates_input else ['01011990', '25121995', '2023']
        
        custom_input = input("Enter custom words (comma-separated, or press Enter to skip): ").strip()
        custom_words = [word.strip() for word in custom_input.split(',')] if custom_input else None
        
        filename = input("Enter output filename (default: wordlist.txt): ").strip()
        if not filename:
            filename = "wordlist.txt"
        
        # Generate wordlist
        print(f"{Colors.YELLOW}[*] Generating wordlist...{Colors.END}")
        wordlist = self.dict_gen.generate_wordlist(names, dates, custom_words)
        self.dict_gen.save_wordlist(wordlist, filename)
        
        print(f"{Colors.GREEN}[+] Generated {len(wordlist)} password variations{Colors.END}")
    
    def hash_analysis_menu(self):
        """Hash analysis submenu"""
        print(f"\n{Colors.BOLD}=== HASH ANALYZER ==={Colors.END}")
        
        choice = input("1. Analyze demo hashes\n2. Enter custom hash\nChoice: ").strip()
        
        if choice == '1':
            demo_hashes = self.hash_extractor.create_demo_hashes()
            print(f"\n{Colors.CYAN}Demo Hashes Analysis:{Colors.END}")
            for hash_info in demo_hashes:
                print(f"Username: {hash_info['username']}")
                print(f"Hash Type: {hash_info['hash_type']}")
                print(f"Hash: {hash_info['hash']}")
                print(f"Original Password (demo): {hash_info['password']}")
                print("-" * 50)
        
        elif choice == '2':
            hash_input = input("Enter hash to analyze: ").strip()
            hash_type = self.hash_extractor.identify_hash_type(hash_input)
            print(f"Hash Type: {hash_type}")
            print(f"Hash Length: {len(hash_input)}")
    
    def dictionary_attack_menu(self):
        """Dictionary attack submenu"""
        print(f"\n{Colors.BOLD}=== DICTIONARY ATTACK SIMULATOR ==={Colors.END}")
        
        # Create demo scenario
        demo_password = input("Enter password to test (demo): ").strip()
        if not demo_password:
            demo_password = "password123"
        
        hash_type = input("Hash type (MD5/SHA-256, default: MD5): ").strip().upper()
        if hash_type not in ['MD5', 'SHA-256']:
            hash_type = 'MD5'
        
        target_hash = self.brute_force.hash_password(demo_password, hash_type)
        print(f"Target hash ({hash_type}): {target_hash}")
        
        # Generate quick wordlist
        wordlist = self.dict_gen.generate_wordlist(
            names=['admin', 'user', 'test'],
            dates=['123', '2023'],
            custom_words=[demo_password],  # Ensure it's in the list for demo
            include_common=True
        )
        
        # Run simulation
        result = self.brute_force.dictionary_attack_simulation(target_hash, wordlist[:1000], hash_type)
        
        if result['success']:
            print(f"{Colors.GREEN}[+] Password cracked: {result['password']}{Colors.END}")
            print(f"Attempts: {result['attempts']}")
            print(f"Time elapsed: {result['time_elapsed']:.2f} seconds")
        else:
            print(f"{Colors.RED}[-] Password not found in wordlist{Colors.END}")
            print(f"Attempts: {result['attempts']}")
    
    def brute_force_menu(self):
        """Brute force submenu"""
        print(f"\n{Colors.BOLD}=== BRUTE FORCE SIMULATOR ==={Colors.END}")
        print(f"{Colors.YELLOW}[!] Limited to 4 characters for demo purposes{Colors.END}")
        
        demo_password = input("Enter short password to test (1-4 chars): ").strip()
        if not demo_password or len(demo_password) > 4:
            demo_password = "abc"
        
        hash_type = input("Hash type (MD5/SHA-256, default: MD5): ").strip().upper()
        if hash_type not in ['MD5', 'SHA-256']:
            hash_type = 'MD5'
        
        charset = input("Charset (lower/upper/digits/all, default: lower): ").strip()
        if charset not in ['lower', 'upper', 'digits', 'all']:
            charset = 'lower'
        
        target_hash = self.brute_force.hash_password(demo_password, hash_type)
        print(f"Target hash: {target_hash}")
        
        # Show time estimates
        if charset == 'lower':
            charset_size = 26
        elif charset == 'upper':
            charset_size = 26
        elif charset == 'digits':
            charset_size = 10
        else:
            charset_size = 62
        
        estimate = self.brute_force.estimate_crack_time(charset_size, len(demo_password))
        print(f"Estimated time: {estimate['readable_time']}")
        
        proceed = input("Proceed with simulation? (y/n): ").strip().lower()
        if proceed == 'y':
            result = self.brute_force.brute_force_simulation(target_hash, 4, hash_type, charset)
            
            if result['success']:
                print(f"{Colors.GREEN}[+] Password cracked: {result['password']}{Colors.END}")
                print(f"Attempts: {result['attempts']}")
                print(f"Time elapsed: {result['time_elapsed']:.2f} seconds")
            else:
                print(f"{Colors.RED}[-] Password not found within demo limits{Colors.END}")
    
    def strength_analysis_menu(self):
        """Password strength analysis submenu"""
        print(f"\n{Colors.BOLD}=== PASSWORD STRENGTH ANALYZER ==={Colors.END}")
        
        while True:
            password = input("Enter password to analyze (or 'quit'): ").strip()
            if password.lower() == 'quit':
                break
            
            analysis = self.analyzer.analyze_password(password)
            
            print(f"\n{Colors.CYAN}Analysis Results:{Colors.END}")
            print(f"Password: {'*' * len(password)}")
            print(f"Length: {analysis['length']}")
            print(f"Entropy: {analysis['entropy']:.2f} bits")
            print(f"Strength: {analysis['strength_color']}{analysis['strength']}{Colors.END}")
            print(f"Complexity Score: {analysis['complexity_score']}/5")
            
            print(f"\n{Colors.CYAN}Requirements:{Colors.END}")
            for req, met in analysis['requirements'].items():
                status = f"{Colors.GREEN}✓{Colors.END}" if met else f"{Colors.RED}✗{Colors.END}"
                print(f"  {status} {req.replace('_', ' ').title()}")
            
            if analysis['patterns']:
                print(f"\n{Colors.YELLOW}Detected Patterns:{Colors.END}")
                for pattern in analysis['patterns']:
                    print(f"  • {pattern}")
            
            if analysis['is_common']:
                print(f"\n{Colors.RED}[!] This is a commonly used password!{Colors.END}")
            
            print("-" * 50)
    
    def report_generation_menu(self):
        """Report generation submenu"""
        print(f"\n{Colors.BOLD}=== REPORT GENERATOR ==={Colors.END}")
        print("This feature requires running assessments first.")
        print("Use option 7 (Complete Assessment) to generate comprehensive reports.")
    
    def complete_assessment(self):
        """Run complete security assessment"""
        print(f"\n{Colors.BOLD}=== COMPLETE SECURITY ASSESSMENT ==={Colors.END}")
        
        # Step 1: Generate wordlist
        print(f"{Colors.YELLOW}[1/6] Generating wordlist...{Colors.END}")
        wordlist = self.dict_gen.generate_wordlist(
            names=['admin', 'user', 'john', 'mary'],
            dates=['123', '2023', '01011990'],
            custom_words=['company', 'secure'],
            include_common=True
        )
        
        # Step 2: Create demo hashes
        print(f"{Colors.YELLOW}[2/6] Creating demo password hashes...{Colors.END}")
        demo_hashes = self.hash_extractor.create_demo_hashes()
        
        # Step 3: Analyze password strengths
        print(f"{Colors.YELLOW}[3/6] Analyzing password strengths...{Colors.END}")
        password_analyses = []
        for hash_info in demo_hashes:
            analysis = self.analyzer.analyze_password(hash_info['password'])
            password_analyses.append(analysis)
        
        # Step 4: Run dictionary attacks
        print(f"{Colors.YELLOW}[4/6] Running dictionary attack simulations...{Colors.END}")
        crack_results = []
        for hash_info in demo_hashes[:2]:  # Limit for demo
            result = self.brute_force.dictionary_attack_simulation(
                hash_info['hash'], wordlist[:500], hash_info['hash_type']
            )
            crack_results.append({
                'username': hash_info['username'],
                'result': result
            })
        
        # Step 5: Generate time estimates
        print(f"{Colors.YELLOW}[5/6] Calculating crack time estimates...{Colors.END}")
        time_estimates = []
        for analysis in password_analyses:
            estimates = {}
            for charset_name, size in [('lowercase', 26), ('mixed', 62), ('all', 95)]:
                estimate = self.brute_force.estimate_crack_time(size, analysis['length'])
                estimates[charset_name] = estimate['readable_time']
            time_estimates.append({
                'password_length': analysis['length'],
                'estimates': estimates
            })
        
        # Step 6: Generate reports
        print(f"{Colors.YELLOW}[6/6] Generating reports...{Colors.END}")
        
        # Compile report data
        self.reporter.add_section("Assessment Summary", {
            'Total passwords analyzed': len(password_analyses),
            'Wordlist size': len(wordlist),
            'Weak passwords found': sum(1 for p in password_analyses if p['entropy'] < 40),
            'Strong passwords found': sum(1 for p in password_analyses if p['entropy'] >= 60)
        })
        
        self.reporter.add_section("Crack Results", crack_results)
        
        # Generate different report formats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.reporter.generate_text_report(f"security_report_{timestamp}.txt")
        self.reporter.generate_json_report(f"security_report_{timestamp}.json")
        self.reporter.generate_csv_report(password_analyses, f"password_analysis_{timestamp}.csv")
        
        # Display summary
        print(f"\n{Colors.GREEN}=== ASSESSMENT COMPLETE ==={Colors.END}")
        print(f"Passwords analyzed: {len(password_analyses)}")
        print(f"Weak passwords: {sum(1 for p in password_analyses if p['entropy'] < 40)}")
        print(f"Strong passwords: {sum(1 for p in password_analyses if p['entropy'] >= 60)}")
        
        # Show recommendations
        print(f"\n{Colors.CYAN}=== RECOMMENDATIONS ==={Colors.END}")
        weak_count = sum(1 for p in password_analyses if p['entropy'] < 40)
        if weak_count > 0:
            print(f"{Colors.RED}[!] {weak_count} weak passwords detected{Colors.END}")
            print("• Implement stronger password policies")
            print("• Require minimum 12 characters")
            print("• Enforce complexity requirements")
            print("• Consider multi-factor authentication")
        else:
            print(f"{Colors.GREEN}[+] All passwords meet basic strength requirements{Colors.END}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Password Cracking & Credential Attack Suite')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--demo', action='store_true', help='Run demo assessment')
    
    args = parser.parse_args()
    
    suite = PasswordCrackingSuite()
    suite.print_banner()
    
    if args.demo:
        print(f"{Colors.YELLOW}[*] Running demo assessment...{Colors.END}")
        suite.complete_assessment()
    elif args.interactive or len(sys.argv) == 1:
        suite.interactive_menu()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()