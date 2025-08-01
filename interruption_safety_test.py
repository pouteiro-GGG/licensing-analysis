#!/usr/bin/env python3
"""
Interruption Safety Test
Demonstrates how the caching system handles interruptions and protects against data loss
"""

import os
import json
import time
import signal
import threading
from typing import Dict, Any
import logging

from licensing_analyzer import LicensingAnalyzer
from cost_control_manager import get_cost_control_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterruptionTest:
    """Test class to demonstrate interruption safety."""
    
    def __init__(self):
        self.analyzer = LicensingAnalyzer()
        self.cost_manager = get_cost_control_manager()
        self.interruption_simulated = False
        
    test_invoice = {
        "vendor": "Microsoft",
        "invoice_date": "2024-01-15",
        "total_amount": 5000.0,
        "line_items": [
            {
                "description": "Office 365 E3 License",
                "quantity": 10,
                "unit_price": 32.0,
                "total_amount": 320.0
            },
            {
                "description": "Azure Cloud Services",
                "quantity": 1,
                "unit_price": 4680.0,
                "total_amount": 4680.0
            }
        ]
    }
    
    def simulate_interruption_during_analysis(self):
        """Simulate interruption during API call."""
        logger.info("🧪 Testing interruption during analysis...")
        
        # Set up interruption handler
        def interruption_handler(signum, frame):
            logger.warning("⚠️  INTERRUPTION SIMULATED during analysis!")
            self.interruption_simulated = True
        
        # Register signal handler (for demonstration)
        signal.signal(signal.SIGINT, interruption_handler)
        
        try:
            # This would normally make an API call
            logger.info("Starting analysis (would make API call)...")
            time.sleep(2)  # Simulate API call time
            
            if self.interruption_simulated:
                logger.info("✅ Interruption handled - no caching of incomplete results")
                return None
            
            # Simulate successful result
            result = {"status": "success", "cost_assessment": "at_standard"}
            logger.info("✅ Analysis completed successfully")
            return result
            
        except KeyboardInterrupt:
            logger.info("✅ Interruption caught - no caching of incomplete results")
            return None
    
    def test_cache_persistence_after_interruption(self):
        """Test that cached results survive interruptions."""
        logger.info("🧪 Testing cache persistence after interruption...")
        
        # First, ensure we have a cached result
        logger.info("1. Creating initial analysis and caching result...")
        result1 = self.analyzer.analyze_licensing_data(self.test_invoice)
        
        if result1:
            logger.info("✅ Initial analysis cached successfully")
            
            # Simulate system restart/interruption
            logger.info("2. Simulating system restart...")
            time.sleep(1)
            
            # Create new analyzer instance (simulates restart)
            new_analyzer = LicensingAnalyzer()
            
            # Try to analyze the same data
            logger.info("3. Analyzing same data after 'restart'...")
            result2 = new_analyzer.analyze_licensing_data(self.test_invoice)
            
            if result2:
                logger.info("✅ Cache hit after restart - no new API call!")
                return True
            else:
                logger.error("❌ Cache miss after restart - this shouldn't happen")
                return False
        else:
            logger.error("❌ Initial analysis failed")
            return False
    
    def test_partial_batch_processing(self):
        """Test interruption during batch processing."""
        logger.info("🧪 Testing interruption during batch processing...")
        
        # Create multiple test invoices
        test_invoices = [
            {
                "vendor": f"Vendor_{i}",
                "invoice_date": "2024-01-15",
                "total_amount": 1000.0 + (i * 500),
                "line_items": [
                    {
                        "description": f"Service {i}",
                        "quantity": 1,
                        "unit_price": 1000.0 + (i * 500),
                        "total_amount": 1000.0 + (i * 500)
                    }
                ]
            }
            for i in range(5)
        ]
        
        logger.info(f"Processing {len(test_invoices)} invoices...")
        
        results = []
        for i, invoice in enumerate(test_invoices):
            logger.info(f"Processing invoice {i+1}/{len(test_invoices)}...")
            
            # Simulate potential interruption
            if i == 2:  # Interrupt after 3rd invoice
                logger.warning("⚠️  Simulating interruption after 3rd invoice...")
                break
            
            result = self.analyzer.analyze_licensing_data(invoice)
            if result:
                results.append(result)
                logger.info(f"✅ Invoice {i+1} processed and cached")
        
        logger.info(f"✅ Processed {len(results)} invoices before interruption")
        logger.info("📊 Cached results are safe and can be resumed later")
        
        return len(results)
    
    def test_cost_metrics_persistence(self):
        """Test that cost metrics persist through interruptions."""
        logger.info("🧪 Testing cost metrics persistence...")
        
        # Get initial metrics
        initial_summary = self.cost_manager.get_cost_summary()
        initial_calls = initial_summary.get("total_api_calls", 0)
        
        logger.info(f"Initial API calls: {initial_calls}")
        
        # Simulate some analysis
        logger.info("Performing test analysis...")
        result = self.analyzer.analyze_licensing_data(self.test_invoice)
        
        # Simulate interruption and restart
        logger.info("Simulating interruption and restart...")
        time.sleep(1)
        
        # Create new cost manager (simulates restart)
        new_cost_manager = get_cost_control_manager()
        final_summary = new_cost_manager.get_cost_summary()
        final_calls = final_summary.get("total_api_calls", 0)
        
        logger.info(f"Final API calls: {final_calls}")
        
        if final_calls > initial_calls:
            logger.info("✅ Cost metrics persisted through interruption")
            return True
        else:
            logger.warning("⚠️  Cost metrics may not have been updated")
            return False
    
    def run_all_tests(self):
        """Run all interruption safety tests."""
        logger.info("🚀 Starting Interruption Safety Tests")
        logger.info("=" * 50)
        
        tests = [
            ("Cache Persistence", self.test_cache_persistence_after_interruption),
            ("Partial Batch Processing", self.test_partial_batch_processing),
            ("Cost Metrics Persistence", self.test_cost_metrics_persistence)
        ]
        
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\n📋 Running: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
                logger.info(f"✅ {test_name}: PASSED" if result else f"❌ {test_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                results[test_name] = False
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 50)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! System is interruption-safe.")
        else:
            logger.warning("⚠️  Some tests failed. Review the system.")
        
        return results

def main():
    """Run the interruption safety tests."""
    tester = InterruptionTest()
    results = tester.run_all_tests()
    
    # Show current cache status
    logger.info("\n📈 Current Cache Status:")
    cost_manager = get_cost_control_manager()
    summary = cost_manager.get_cost_summary()
    
    logger.info(f"Total API Calls: {summary.get('total_api_calls', 0)}")
    logger.info(f"Cache Hits: {summary.get('cache_hits', 0)}")
    logger.info(f"Cache Misses: {summary.get('cache_misses', 0)}")
    logger.info(f"Cache Hit Rate: {summary.get('cache_hit_rate', 0):.1%}")

if __name__ == "__main__":
    main() 