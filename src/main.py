# src/main.py

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import argparse
from datetime import datetime
import sys

from .conversions import CryptoConverter
from .utils import ValidationError

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('crypto_processor.log')
    ]
)
logger = logging.getLogger(__name__)

class CryptoProcessor:
    """
    Process cryptographic data files and perform conversions between unknown, hex, and ASCII formats.
    Includes validation and detailed error reporting.
    """
    
    def __init__(self, input_file: str, output_dir: str, debug: bool = False):
        """
        Initialize the processor with input and output paths.
        
        Args:
            input_file (str): Path to input JSON file
            output_dir (str): Directory for output files
            debug (bool): Enable debug mode for additional logging
        """
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.converter = CryptoConverter(debug=debug)
        self._setup_output_directory()
        
    def _setup_output_directory(self) -> None:
        """Create output directory structure if it doesn't exist."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Output directory setup complete: {self.output_dir}")
        except Exception as e:
            logger.error(f"Failed to create output directory: {str(e)}")
            raise

    def validate_dataset(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate the structure and content of input dataset.
        
        Args:
            data (Dict[str, Any]): Input data dictionary
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        required_fields = {'unknown', 'hex', 'ascii_text'}
        
        if not isinstance(data, dict):
            return False, "Input data must be a dictionary"
            
        for key, entry in data.items():
            if not isinstance(entry, dict):
                return False, f"Dataset {key} must be a dictionary"
                
            if not all(field in entry for field in required_fields):
                return False, f"Dataset {key} missing required fields: {required_fields}"
                
            if not isinstance(entry['ascii_text'], dict):
                return False, f"Dataset {key}: ascii_text must be a JSON object"
                
        return True, ""

    def load_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load and validate the JSON data file.
        
        Returns:
            Dict[str, Dict[str, Any]]: Loaded and validated data
            
        Raises:
            ValidationError: If data validation fails
            FileNotFoundError: If input file doesn't exist
            json.JSONDecodeError: If JSON parsing fails
        """
        try:
            if not self.input_file.exists():
                raise FileNotFoundError(f"Input file not found: {self.input_file}")
                
            with open(self.input_file, 'r') as f:
                data = json.load(f)
                
            is_valid, error_msg = self.validate_dataset(data)
            if not is_valid:
                raise ValidationError(error_msg)
                
            logger.info(f"Successfully loaded {len(data)} datasets from {self.input_file}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in input file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading input file: {str(e)}")
            raise

    def process_single_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate a single dataset entry.
        
        Args:
            entry (Dict[str, Any]): Single dataset entry
            
        Returns:
            Dict[str, Any]: Processing results with validation details
        """
        results = {
            'original': entry.copy(),
            'validations': {},
            'conversions': {},
            'errors': []
        }
        
        try:
            # Validate hex to ASCII conversion
            try:
                ascii_result = self.converter.hex_to_ascii(entry['hex'])
                results['validations']['hex_to_ascii_valid'] = True
                results['conversions']['hex_to_ascii'] = ascii_result
            except Exception as e:
                results['validations']['hex_to_ascii_valid'] = False
                results['errors'].append(f"Hex to ASCII conversion failed: {str(e)}")

            # Validate hex to unknown conversion
            try:
                unknown_result = self.converter.hex_to_unknown(entry['hex'])
                results['validations']['hex_to_unknown_valid'] = True
                results['conversions']['hex_to_unknown'] = unknown_result
            except Exception as e:
                results['validations']['hex_to_unknown_valid'] = False
                results['errors'].append(f"Hex to unknown conversion failed: {str(e)}")

            # Validate unknown to hex conversion
            if results['validations'].get('hex_to_unknown_valid', False):
                try:
                    hex_result = self.converter.unknown_to_hex(entry['unknown'])
                    results['validations']['unknown_to_hex_valid'] = True
                    results['conversions']['unknown_to_hex'] = hex_result
                except Exception as e:
                    results['validations']['unknown_to_hex_valid'] = False
                    results['errors'].append(f"Unknown to hex conversion failed: {str(e)}")

            # Validate conversion pair
            results['validations']['conversion_pair_valid'] = (
                self.converter.validate_conversion_pair(entry['unknown'], entry['hex'])
            )

            return results
            
        except Exception as e:
            logger.error(f"Error processing entry: {str(e)}")
            results['errors'].append(f"General processing error: {str(e)}")
            return results

    def process_all_data(self) -> None:
        """
        Process all datasets and generate detailed results with validation.
        """
        try:
            data = self.load_data()
            results = {}
            summary_stats = {
                'total_entries': len(data),
                'successful_conversions': 0,
                'failed_conversions': 0,
                'validation_stats': {
                    'hex_to_ascii_valid': 0,
                    'hex_to_unknown_valid': 0,
                    'unknown_to_hex_valid': 0,
                    'conversion_pair_valid': 0
                }
            }
            
            for idx, (key, entry) in enumerate(data.items(), 1):
                logger.info(f"Processing dataset {idx}/{len(data)}: {key}")
                
                result = self.process_single_entry(entry)
                results[key] = result
                
                # Update summary statistics
                if not result.get('errors'):
                    summary_stats['successful_conversions'] += 1
                else:
                    summary_stats['failed_conversions'] += 1
                    
                for validation_key in summary_stats['validation_stats'].keys():
                    if result['validations'].get(validation_key, False):
                        summary_stats['validation_stats'][validation_key] += 1
            
            self.save_results(results, summary_stats)
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise

    def save_results(self, results: Dict[str, Any], summary_stats: Dict[str, Any]) -> None:
        """
        Save processing results and summary statistics to output files.
        
        Args:
            results (Dict[str, Any]): Processing results
            summary_stats (Dict[str, Any]): Summary statistics
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Save detailed results
            detailed_output = self.output_dir / f"detailed_results_{timestamp}.json"
            with open(detailed_output, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Save summary with statistics
            summary = {
                **summary_stats,
                'timestamp': timestamp,
                'input_file': str(self.input_file),
                'success_rate': f"{(summary_stats['successful_conversions'] / summary_stats['total_entries']) * 100:.2f}%"
            }
            
            summary_output = self.output_dir / f"summary_{timestamp}.json"
            with open(summary_output, 'w') as f:
                json.dump(summary, f, indent=2)
                
            logger.info(f"Results saved to {self.output_dir}")
            logger.info(f"Success rate: {summary['success_rate']}")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise

def main():
    """Main entry point with enhanced argument parsing and error handling."""
    parser = argparse.ArgumentParser(
        description='Cryptographic Conversion Tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input_file', help='Path to input JSON file')
    parser.add_argument(
        '--output-dir', 
        default='output',
        help='Directory for output files'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug mode with verbose logging'
    )
    parser.add_argument(
        '--log-file',
        help='Path to log file (optional)'
    )

    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
        
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

    try:
        processor = CryptoProcessor(args.input_file, args.output_dir, debug=args.debug)
        processor.process_all_data()
        logger.info("Processing completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())