#!/usr/bin/env python3
"""
PHI (Personal Health Information) Removal Script

This script identifies and removes various types of Personal Health Information
from text files to ensure HIPAA compliance and protect patient privacy.

Supported PHI types:
- Social Security Numbers (SSN)
- Phone numbers
- Email addresses
- Dates (various formats)
- Medical Record Numbers (MRN)
- Names (basic pattern matching)
- Addresses
- Credit card numbers
- IP addresses
- URLs containing potential PHI

Usage:
    python phi_removal.py input.txt [options]
"""

import re
import argparse
import os
import sys
from typing import List, Tuple, Dict
from pathlib import Path
import logging

class PHIRemover:
    """Class to handle PHI removal from text content."""
    
    def __init__(self, replacement_text: str = "[REDACTED]"):
        """Initialize PHI remover with replacement text."""
        self.replacement_text = replacement_text
        self.phi_patterns = self._define_phi_patterns()
        self.removal_stats = {}
        
    def _define_phi_patterns(self) -> Dict[str, re.Pattern]:
        """Define regex patterns for various PHI types."""
        return {
            # Social Security Numbers (XXX-XX-XXXX, XXXXXXXXX, XXX XX XXXX)
            'ssn': re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'),
            
            # Phone numbers (various formats)
            'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
            
            # Email addresses
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            
            # Dates (MM/DD/YYYY, MM-DD-YYYY, DD/MM/YYYY, YYYY-MM-DD, etc.)
            'date': re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'),
            
            # Medical Record Numbers (MRN) - common patterns
            'mrn': re.compile(r'\b(?:MRN|mrn|Medical Record|medical record)[\s:]*#?[\s]*[A-Z0-9]{6,12}\b', re.IGNORECASE),
            
            # Credit card numbers (basic pattern)
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            
            # IP addresses
            'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            
            # URLs that might contain PHI
            'url': re.compile(r'https?://[^\s]+'),
            
            # US ZIP codes
            'zip_code': re.compile(r'\b\d{5}(?:-\d{4})?\b'),
            
            # Driver's License patterns (state-specific would be better)
            'drivers_license': re.compile(r'\b(?:DL|dl|license|License)[\s:]*#?[\s]*[A-Z0-9]{8,15}\b', re.IGNORECASE),
            
            # Doctor's License Numbers (various medical license patterns)
            'doctor_license': re.compile(r'\b(?:MD|Dr|Doctor|Physician|NPI|DEA|Medical)[\s]*(?:License|Lic|#|Number|No|ID)[\s:]*#?[\s]*[A-Z0-9]{6,15}\b', re.IGNORECASE),
            
            # Account numbers (generic pattern)
            'account_number': re.compile(r'\b(?:account|Account|ACCOUNT)[\s:]*#?[\s]*[A-Z0-9]{6,20}\b'),
            
            # Patient ID patterns
            'patient_id': re.compile(r'\b(?:patient|Patient|PATIENT)[\s:]*(?:id|ID|Id)[\s:]*#?[\s]*[A-Z0-9]{4,15}\b'),
        }
    
    def _remove_names(self, text: str) -> str:
        """
        Remove potential names using basic heuristics.
        This is a simplified approach - more sophisticated NER would be better.
        """
        # Pattern for potential names (Title Case words that could be names)
        # This is conservative to avoid false positives
        name_patterns = [
            # Dr. FirstName LastName, Mr. FirstName LastName, etc.
            re.compile(r'\b(?:Dr|Mr|Ms|Mrs|Miss)\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b'),
            # Patient: FirstName LastName
            re.compile(r'\b(?:Patient|patient|PATIENT)[\s:]+[A-Z][a-z]+\s+[A-Z][a-z]+\b'),
        ]
        
        for pattern in name_patterns:
            if matches := pattern.findall(text):
                self.removal_stats['names'] = self.removal_stats.get('names', 0) + len(matches)
                text = pattern.sub(self.replacement_text, text)
        
        return text
    
    def remove_phi(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Remove PHI from the given text and return cleaned text with statistics.
        
        Args:
            text: Input text containing potential PHI
            
        Returns:
            Tuple of (cleaned_text, removal_statistics)
        """
        self.removal_stats = {}
        cleaned_text = text
        
        # Apply each PHI pattern
        for phi_type, pattern in self.phi_patterns.items():
            if matches := pattern.findall(cleaned_text):
                self.removal_stats[phi_type] = len(matches)
                cleaned_text = pattern.sub(self.replacement_text, cleaned_text)
        
        # Handle names separately (more complex logic)
        cleaned_text = self._remove_names(cleaned_text)
        
        return cleaned_text, self.removal_stats
    
    def process_file(self, input_path: str, output_path: str = None, 
                    encoding: str = 'utf-8') -> Dict[str, int]:
        """
        Process a single file to remove PHI.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file (if None, overwrites input)
            encoding: File encoding
            
        Returns:
            Dictionary with removal statistics
        """
        try:
            # Read input file
            with open(input_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Remove PHI
            cleaned_content, stats = self.remove_phi(content)
            
            # Write output
            output_file = output_path or input_path
            with open(output_file, 'w', encoding=encoding) as f:
                f.write(cleaned_content)
            
            return stats
            
        except Exception as e:
            logging.error(f"Error processing file {input_path}: {e}")
            raise
    
    def process_directory(self, input_dir: str, output_dir: str = None,
                         file_extensions: List[str] = None) -> Dict[str, Dict[str, int]]:
        """
        Process all text files in a directory.
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path (if None, overwrites input files)
            file_extensions: List of file extensions to process
            
        Returns:
            Dictionary mapping filenames to their removal statistics
        """
        if file_extensions is None:
            file_extensions = ['.txt', '.md', '.csv', '.log']
        
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for file_path in input_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                try:
                    if output_dir:
                        # Maintain directory structure in output
                        rel_path = file_path.relative_to(input_path)
                        output_file = output_path / rel_path
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        output_file_str = str(output_file)
                    else:
                        output_file_str = None
                    
                    stats = self.process_file(str(file_path), output_file_str)
                    results[str(file_path)] = stats
                    
                except Exception as e:
                    logging.error(f"Failed to process {file_path}: {e}")
                    results[str(file_path)] = {'error': str(e)}
        
        return results


def print_statistics(stats: Dict[str, int], filename: str = None):
    """Print removal statistics in a formatted way."""
    if filename:
        print(f"\nPHI Removal Statistics for {filename}:")
    else:
        print("\nPHI Removal Statistics:")
    
    print("-" * 40)
    
    total_removals = sum(stats.values())
    if total_removals == 0:
        print("No PHI detected in the file.")
        return
    
    for phi_type, count in sorted(stats.items()):
        if count > 0:
            print(f"{phi_type.replace('_', ' ').title()}: {count}")
    
    print(f"Total PHI items removed: {total_removals}")


def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(
        description="Remove PHI (Personal Health Information) from text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process single file (overwrite)
    python phi_removal.py patient_notes.txt
    
    # Process single file with output
    python phi_removal.py input.txt -o cleaned_output.txt
    
    # Process directory
    python phi_removal.py /path/to/files/ -d -o /path/to/cleaned/
    
    # Custom replacement text
    python phi_removal.py input.txt -r "[REMOVED]"
    
    # Process specific file types
    python phi_removal.py /path/to/files/ -d --extensions .txt .md .csv
        """
    )
    
    parser.add_argument('input', help='Input file or directory path')
    parser.add_argument('-o', '--output', help='Output file or directory path')
    parser.add_argument('-d', '--directory', action='store_true',
                       help='Process directory instead of single file')
    parser.add_argument('-r', '--replacement', default='[REDACTED]',
                       help='Replacement text for PHI (default: [REDACTED])')
    parser.add_argument('--extensions', nargs='+', default=['.txt', '.md', '.csv', '.log'],
                       help='File extensions to process (default: .txt .md .csv .log)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--encoding', default='utf-8',
                       help='File encoding (default: utf-8)')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Validate input
    if not os.path.exists(args.input):
        print(f"Error: Input path '{args.input}' does not exist.")
        sys.exit(1)
    
    # Create PHI remover
    phi_remover = PHIRemover(replacement_text=args.replacement)
    
    try:
        if args.directory:
            # Process directory
            results = phi_remover.process_directory(
                args.input, 
                args.output,
                args.extensions
            )
            
            print(f"Processed {len(results)} files.")
            
            # Print summary statistics
            total_stats = {}
            for filename, stats in results.items():
                if 'error' in stats:
                    print(f"Error processing {filename}: {stats['error']}")
                else:
                    for phi_type, count in stats.items():
                        total_stats[phi_type] = total_stats.get(phi_type, 0) + count
            
            if total_stats:
                print_statistics(total_stats, "All Files")
        
        else:
            # Process single file
            stats = phi_remover.process_file(args.input, args.output, args.encoding)
            print(f"Successfully processed: {args.input}")
            if args.output:
                print(f"Output written to: {args.output}")
            print_statistics(stats, args.input)
    
    except Exception as e:
        logging.error(f"Processing failed: {e}")
        sys.exit(1)


# remove phi from all the files within the directory:
# /home/tan/Downloads/speaker_1207224/phi-removed
# and save the output in the same directory with the suffix _phi_removed
def remove_phi_from_directory(input_dir: str, output_dir: str = None):
    """
    Remove PHI from all the files within the directory and save the output in the same directory with the suffix _phi_removed
    """
    phi_remover = PHIRemover(replacement_text="[REDACTED]")
    return phi_remover.process_directory(input_dir, output_dir)

if __name__ == '__main__':
    remove_phi_from_directory("/home/tan/Downloads/speaker_1207224/phi-removed", "/home/tan/Downloads/speaker_1207224/phi-removed")
