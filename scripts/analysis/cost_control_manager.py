"""
Cost Control Manager for Licensing Analysis
Advanced caching and cost tracking to minimize API calls and control expenses
"""

import os
import json
import hashlib
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging
from dataclasses import dataclass, asdict
from config import CACHE_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class AnalysisRecord:
    """Record of a completed analysis."""
    id: str
    vendor: str
    invoice_date: str
    total_amount: float
    analysis_hash: str
    api_cost_usd: float
    tokens_used: int
    created_at: datetime
    last_accessed: datetime
    analysis_data: Dict[str, Any]

@dataclass
class CostMetrics:
    """Cost tracking metrics."""
    total_api_calls: int
    total_tokens_used: int
    total_cost_usd: float
    cache_hits: int
    cache_misses: int
    cost_savings_usd: float
    last_updated: datetime

class CostControlManager:
    """
    Advanced cost control manager that tracks API usage, caches results,
    and provides cost optimization recommendations.
    """
    
    def __init__(self, db_path: str = "cost_control.db"):
        self.db_path = db_path
        self.analysis_db_path = "analysis_persistence.db"
        self.cost_tracking_db_path = "cost_tracking.db"
        
        # Initialize databases
        self._init_databases()
        
        # Load cost metrics
        self.cost_metrics = self._load_cost_metrics()
        
        logger.info("Cost Control Manager initialized")
    
    def _init_databases(self):
        """Initialize SQLite databases for persistent storage."""
        # Analysis persistence database
        with sqlite3.connect(self.analysis_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_records (
                    id TEXT PRIMARY KEY,
                    vendor TEXT NOT NULL,
                    invoice_date TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    analysis_hash TEXT NOT NULL,
                    api_cost_usd REAL NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    analysis_data TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vendor ON analysis_records(vendor)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analysis_hash ON analysis_records(analysis_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON analysis_records(created_at)")
        
        # Cost tracking database
        with sqlite3.connect(self.cost_tracking_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cost_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_api_calls INTEGER NOT NULL,
                    total_tokens_used INTEGER NOT NULL,
                    total_cost_usd REAL NOT NULL,
                    cache_hits INTEGER NOT NULL,
                    cache_misses INTEGER NOT NULL,
                    cost_savings_usd REAL NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    vendor TEXT NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    cost_usd REAL NOT NULL,
                    cache_hit BOOLEAN NOT NULL,
                    analysis_hash TEXT NOT NULL
                )
            """)
    
    def _load_cost_metrics(self) -> CostMetrics:
        """Load current cost metrics from database."""
        with sqlite3.connect(self.cost_tracking_db_path) as conn:
            cursor = conn.execute("SELECT * FROM cost_metrics ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                return CostMetrics(
                    total_api_calls=row[1],
                    total_tokens_used=row[2],
                    total_cost_usd=row[3],
                    cache_hits=row[4],
                    cache_misses=row[5],
                    cost_savings_usd=row[6],
                    last_updated=datetime.fromisoformat(row[7])
                )
            else:
                # Initialize with default values
                return CostMetrics(
                    total_api_calls=0,
                    total_tokens_used=0,
                    total_cost_usd=0.0,
                    cache_hits=0,
                    cache_misses=0,
                    cost_savings_usd=0.0,
                    last_updated=datetime.now()
                )
    
    def _save_cost_metrics(self):
        """Save current cost metrics to database."""
        with sqlite3.connect(self.cost_tracking_db_path) as conn:
            conn.execute("""
                INSERT INTO cost_metrics 
                (total_api_calls, total_tokens_used, total_cost_usd, cache_hits, cache_misses, cost_savings_usd, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.cost_metrics.total_api_calls,
                self.cost_metrics.total_tokens_used,
                self.cost_metrics.total_cost_usd,
                self.cost_metrics.cache_hits,
                self.cost_metrics.cache_misses,
                self.cost_metrics.cost_savings_usd,
                self.cost_metrics.last_updated.isoformat()
            ))
    
    def _record_api_call(self, vendor: str, tokens_used: int, cost_usd: float, cache_hit: bool, analysis_hash: str):
        """Record an API call for tracking."""
        with sqlite3.connect(self.cost_tracking_db_path) as conn:
            conn.execute("""
                INSERT INTO api_calls (timestamp, vendor, tokens_used, cost_usd, cache_hit, analysis_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                vendor,
                tokens_used,
                cost_usd,
                cache_hit,
                analysis_hash
            ))
    
    def get_cached_analysis(self, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result if available.
        Returns the analysis data if found, None otherwise.
        """
        analysis_hash = self._generate_analysis_hash(invoice_data)
        
        with sqlite3.connect(self.analysis_db_path) as conn:
            cursor = conn.execute("""
                SELECT analysis_data, last_accessed FROM analysis_records 
                WHERE analysis_hash = ?
            """, (analysis_hash,))
            
            row = cursor.fetchone()
            if row:
                # Update last accessed time
                conn.execute("""
                    UPDATE analysis_records SET last_accessed = ? WHERE analysis_hash = ?
                """, (datetime.now().isoformat(), analysis_hash))
                
                # Update cost metrics
                self.cost_metrics.cache_hits += 1
                self.cost_metrics.last_updated = datetime.now()
                self._save_cost_metrics()
                
                logger.info(f"Cache hit for analysis hash: {analysis_hash[:16]}...")
                return json.loads(row[0])
            
            # Cache miss
            self.cost_metrics.cache_misses += 1
            self.cost_metrics.last_updated = datetime.now()
            self._save_cost_metrics()
            
            logger.info(f"Cache miss for analysis hash: {analysis_hash[:16]}...")
            return None
    
    def store_analysis_result(self, invoice_data: Dict[str, Any], analysis_result: Dict[str, Any], 
                            tokens_used: int, cost_usd: float):
        """
        Store analysis result in persistent cache.
        """
        analysis_hash = self._generate_analysis_hash(invoice_data)
        
        # Create analysis record
        record = AnalysisRecord(
            id=f"analysis_{int(time.time())}_{hash(analysis_hash) % 1000000}",
            vendor=invoice_data.get("vendor", "Unknown"),
            invoice_date=invoice_data.get("invoice_date", ""),
            total_amount=invoice_data.get("total_amount", 0),
            analysis_hash=analysis_hash,
            api_cost_usd=cost_usd,
            tokens_used=tokens_used,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            analysis_data=analysis_result
        )
        
        # Store in database
        with sqlite3.connect(self.analysis_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO analysis_records 
                (id, vendor, invoice_date, total_amount, analysis_hash, api_cost_usd, tokens_used, 
                 created_at, last_accessed, analysis_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.vendor,
                record.invoice_date,
                record.total_amount,
                record.analysis_hash,
                record.api_cost_usd,
                record.tokens_used,
                record.created_at.isoformat(),
                record.last_accessed.isoformat(),
                json.dumps(record.analysis_data)
            ))
        
        # Update cost metrics
        self.cost_metrics.total_api_calls += 1
        self.cost_metrics.total_tokens_used += tokens_used
        self.cost_metrics.total_cost_usd += cost_usd
        self.cost_metrics.last_updated = datetime.now()
        self._save_cost_metrics()
        
        # Record API call
        self._record_api_call(
            vendor=record.vendor,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            cache_hit=False,
            analysis_hash=analysis_hash
        )
        
        logger.info(f"Stored analysis result for {record.vendor} (${cost_usd:.4f})")
    
    def _generate_analysis_hash(self, invoice_data: Dict[str, Any]) -> str:
        """Generate a unique hash for invoice data."""
        # Create a normalized version of the data for consistent hashing
        normalized_data = {
            "vendor": invoice_data.get("vendor", "").lower().strip(),
            "line_items": sorted([
                {
                    "description": item.get("description", "").lower().strip(),
                    "quantity": item.get("quantity", 0),
                    "unit_price": round(item.get("unit_price", 0), 2),
                    "total_amount": round(item.get("total_amount", 0), 2)
                }
                for item in invoice_data.get("line_items", [])
            ], key=lambda x: x["description"])
        }
        
        data_str = json.dumps(normalized_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get comprehensive cost summary."""
        # Calculate cost savings from cache hits
        estimated_cost_per_call = 0.15  # Estimated cost per API call
        potential_savings = self.cost_metrics.cache_hits * estimated_cost_per_call
        self.cost_metrics.cost_savings_usd = potential_savings
        self._save_cost_metrics()
        
        return {
            "total_api_calls": self.cost_metrics.total_api_calls,
            "total_tokens_used": self.cost_metrics.total_tokens_used,
            "total_cost_usd": self.cost_metrics.total_cost_usd,
            "cache_hits": self.cost_metrics.cache_hits,
            "cache_misses": self.cost_metrics.cache_misses,
            "cache_hit_rate": self.cost_metrics.cache_hits / max(1, self.cost_metrics.cache_hits + self.cost_metrics.cache_misses),
            "cost_savings_usd": self.cost_metrics.cost_savings_usd,
            "net_cost_usd": self.cost_metrics.total_cost_usd - self.cost_metrics.cost_savings_usd,
            "last_updated": self.cost_metrics.last_updated.isoformat()
        }
    
    def get_vendor_cost_breakdown(self) -> Dict[str, Any]:
        """Get cost breakdown by vendor."""
        with sqlite3.connect(self.cost_tracking_db_path) as conn:
            cursor = conn.execute("""
                SELECT vendor, 
                       COUNT(*) as api_calls,
                       SUM(tokens_used) as total_tokens,
                       SUM(cost_usd) as total_cost,
                       SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits
                FROM api_calls 
                GROUP BY vendor 
                ORDER BY total_cost DESC
            """)
            
            vendors = []
            for row in cursor.fetchall():
                vendors.append({
                    "vendor": row[0],
                    "api_calls": row[1],
                    "total_tokens": row[2],
                    "total_cost_usd": row[3],
                    "cache_hits": row[4],
                    "cache_hit_rate": row[4] / max(1, row[1])
                })
            
            return {"vendors": vendors}
    
    def get_cost_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get cost trends over time."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.cost_tracking_db_path) as conn:
            cursor = conn.execute("""
                SELECT DATE(timestamp) as date,
                       COUNT(*) as api_calls,
                       SUM(tokens_used) as total_tokens,
                       SUM(cost_usd) as total_cost,
                       SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits
                FROM api_calls 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (cutoff_date.isoformat(),))
            
            trends = []
            for row in cursor.fetchall():
                trends.append({
                    "date": row[0],
                    "api_calls": row[1],
                    "total_tokens": row[2],
                    "total_cost_usd": row[3],
                    "cache_hits": row[4],
                    "cache_hit_rate": row[4] / max(1, row[1])
                })
            
            return {"trends": trends, "period_days": days}
    
    def export_analysis_data(self, output_file: str = "exported_analysis_data.json"):
        """Export all analysis data for backup or migration."""
        with sqlite3.connect(self.analysis_db_path) as conn:
            cursor = conn.execute("SELECT * FROM analysis_records")
            
            exported_data = []
            for row in cursor.fetchall():
                exported_data.append({
                    "id": row[0],
                    "vendor": row[1],
                    "invoice_date": row[2],
                    "total_amount": row[3],
                    "analysis_hash": row[4],
                    "api_cost_usd": row[5],
                    "tokens_used": row[6],
                    "created_at": row[7],
                    "last_accessed": row[8],
                    "analysis_data": json.loads(row[9])
                })
            
            with open(output_file, 'w') as f:
                json.dump(exported_data, f, indent=2)
            
            logger.info(f"Exported {len(exported_data)} analysis records to {output_file}")
            return output_file
    
    def cleanup_old_analyses(self, days_old: int = 365):
        """Clean up old analysis records to save space."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with sqlite3.connect(self.analysis_db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM analysis_records 
                WHERE created_at < ?
            """, (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            logger.info(f"Cleaned up {deleted_count} analysis records older than {days_old} days")
            return deleted_count
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get cost optimization recommendations."""
        recommendations = []
        
        # Check cache hit rate
        hit_rate = self.cost_metrics.cache_hits / max(1, self.cost_metrics.cache_hits + self.cost_metrics.cache_misses)
        if hit_rate < 0.5:
            recommendations.append("Low cache hit rate detected. Consider running analysis on similar invoices to improve caching.")
        
        # Check for duplicate analyses
        with sqlite3.connect(self.analysis_db_path) as conn:
            cursor = conn.execute("""
                SELECT vendor, COUNT(*) as count 
                FROM analysis_records 
                GROUP BY vendor 
                HAVING count > 10
            """)
            
            for row in cursor.fetchall():
                recommendations.append(f"High analysis count for {row[0]} ({row[1]} analyses). Consider batch processing.")
        
        # Check cost trends
        if self.cost_metrics.total_cost_usd > 100:
            recommendations.append("Total API costs exceed $100. Consider implementing stricter caching policies.")
        
        return recommendations

def get_cost_control_manager() -> CostControlManager:
    """Get a configured cost control manager instance."""
    return CostControlManager() 