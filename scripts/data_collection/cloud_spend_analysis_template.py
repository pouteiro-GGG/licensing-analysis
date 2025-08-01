#!/usr/bin/env python3
"""
Cloud Spend Analysis Template
Template for collecting detailed cloud spend data to analyze reseller costs
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class CloudSpendAnalysisTemplate:
    def __init__(self):
        self.output_dir = "templates/cloud_spend_analysis"
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Ensure output directory exists."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def create_cloud_invoice_template(self):
        """Create template for cloud provider invoices."""
        
        template = {
            "cloud_invoice_template": {
                "description": "Template for collecting detailed cloud provider invoice data",
                "fields": {
                    "invoice_date": "YYYY-MM-DD",
                    "cloud_provider": "AWS/Azure/GCP/Other",
                    "account_id": "Cloud account identifier",
                    "billing_period": "YYYY-MM",
                    "service_category": "Compute/Storage/Network/Database/Analytics/Security/Other",
                    "service_name": "EC2/S3/RDS/Lambda/etc",
                    "resource_id": "i-1234567890abcdef0",
                    "resource_name": "web-server-01",
                    "region": "us-east-1",
                    "instance_type": "t3.medium",
                    "usage_hours": 720,
                    "unit_price": 0.0416,
                    "total_cost": 29.95,
                    "data_transfer_gb": 100,
                    "data_transfer_cost": 9.00,
                    "reserved_instance": "Yes/No",
                    "spot_instance": "Yes/No",
                    "auto_scaling": "Yes/No",
                    "tags": "Environment=Production,Project=WebApp",
                    "utilization_percentage": 45.2,
                    "rightsizing_opportunity": "Yes/No",
                    "notes": "Additional details"
                },
                "example_records": [
                    {
                        "invoice_date": "2025-01-31",
                        "cloud_provider": "AWS",
                        "account_id": "123456789012",
                        "billing_period": "2025-01",
                        "service_category": "Compute",
                        "service_name": "EC2",
                        "resource_id": "i-1234567890abcdef0",
                        "resource_name": "web-server-01",
                        "region": "us-east-1",
                        "instance_type": "t3.medium",
                        "usage_hours": 720,
                        "unit_price": 0.0416,
                        "total_cost": 29.95,
                        "data_transfer_gb": 100,
                        "data_transfer_cost": 9.00,
                        "reserved_instance": "No",
                        "spot_instance": "No",
                        "auto_scaling": "Yes",
                        "tags": "Environment=Production,Project=WebApp",
                        "utilization_percentage": 45.2,
                        "rightsizing_opportunity": "Yes",
                        "notes": "Underutilized - consider t3.small"
                    }
                ]
            }
        }
        
        return template
    
    def create_synoptek_reseller_template(self):
        """Create template for Synoptek reseller data."""
        
        template = {
            "synoptek_reseller_template": {
                "description": "Template for collecting Synoptek reseller markup and managed services data",
                "fields": {
                    "invoice_date": "YYYY-MM-DD",
                    "synoptek_invoice_number": "SYN-2025-001",
                    "billing_period": "2025-01",
                    "cloud_provider": "AWS/Azure/GCP",
                    "service_category": "Cloud Services/Managed Services/Professional Services",
                    "service_name": "Cloud Management/Azure Consumption/AWS Support",
                    "base_cloud_cost": 1000.00,
                    "synoptek_markup_percentage": 15.0,
                    "synoptek_markup_amount": 150.00,
                    "managed_services_fee": 500.00,
                    "professional_services_fee": 200.00,
                    "support_tier": "Premium/Standard/Basic",
                    "support_hours_included": 40,
                    "support_hours_used": 25,
                    "support_hours_billed": 0,
                    "total_synoptek_charge": 1850.00,
                    "volume_discount_applied": "Yes/No",
                    "discount_percentage": 5.0,
                    "discount_amount": 92.50,
                    "final_amount": 1757.50,
                    "contract_tier": "Enterprise/Standard/Basic",
                    "managed_services_included": "Monitoring, Backup, Security, Patching",
                    "sla_level": "99.9%/99.5%/99.0%",
                    "response_time_guarantee": "2 hours/4 hours/8 hours",
                    "notes": "Additional details"
                },
                "example_records": [
                    {
                        "invoice_date": "2025-01-31",
                        "synoptek_invoice_number": "SYN-2025-001",
                        "billing_period": "2025-01",
                        "cloud_provider": "AWS",
                        "service_category": "Cloud Services",
                        "service_name": "AWS Consumption",
                        "base_cloud_cost": 1000.00,
                        "synoptek_markup_percentage": 15.0,
                        "synoptek_markup_amount": 150.00,
                        "managed_services_fee": 500.00,
                        "professional_services_fee": 200.00,
                        "support_tier": "Premium",
                        "support_hours_included": 40,
                        "support_hours_used": 25,
                        "support_hours_billed": 0,
                        "total_synoptek_charge": 1850.00,
                        "volume_discount_applied": "Yes",
                        "discount_percentage": 5.0,
                        "discount_amount": 92.50,
                        "final_amount": 1757.50,
                        "contract_tier": "Enterprise",
                        "managed_services_included": "Monitoring, Backup, Security, Patching",
                        "sla_level": "99.9%",
                        "response_time_guarantee": "2 hours",
                        "notes": "Includes 24/7 monitoring and backup services"
                    }
                ]
            }
        }
        
        return template
    
    def create_resource_utilization_template(self):
        """Create template for resource utilization data."""
        
        template = {
            "resource_utilization_template": {
                "description": "Template for collecting resource utilization metrics",
                "fields": {
                    "resource_id": "i-1234567890abcdef0",
                    "resource_name": "web-server-01",
                    "cloud_provider": "AWS/Azure/GCP",
                    "service_name": "EC2/VM Instance",
                    "instance_type": "t3.medium",
                    "region": "us-east-1",
                    "measurement_date": "2025-01-15",
                    "cpu_utilization_avg": 25.5,
                    "cpu_utilization_peak": 85.2,
                    "cpu_utilization_min": 5.1,
                    "memory_utilization_avg": 45.8,
                    "memory_utilization_peak": 92.1,
                    "memory_utilization_min": 12.3,
                    "network_in_mbps_avg": 15.2,
                    "network_out_mbps_avg": 8.7,
                    "disk_read_iops_avg": 150,
                    "disk_write_iops_avg": 75,
                    "disk_read_mbps_avg": 25.5,
                    "disk_write_mbps_avg": 12.8,
                    "uptime_percentage": 99.8,
                    "idle_hours_per_day": 8.5,
                    "rightsizing_recommendation": "t3.small",
                    "potential_monthly_savings": 15.50,
                    "notes": "Additional details"
                },
                "example_records": [
                    {
                        "resource_id": "i-1234567890abcdef0",
                        "resource_name": "web-server-01",
                        "cloud_provider": "AWS",
                        "service_name": "EC2",
                        "instance_type": "t3.medium",
                        "region": "us-east-1",
                        "measurement_date": "2025-01-15",
                        "cpu_utilization_avg": 25.5,
                        "cpu_utilization_peak": 85.2,
                        "cpu_utilization_min": 5.1,
                        "memory_utilization_avg": 45.8,
                        "memory_utilization_peak": 92.1,
                        "memory_utilization_min": 12.3,
                        "network_in_mbps_avg": 15.2,
                        "network_out_mbps_avg": 8.7,
                        "disk_read_iops_avg": 150,
                        "disk_write_iops_avg": 75,
                        "disk_read_mbps_avg": 25.5,
                        "disk_write_mbps_avg": 12.8,
                        "uptime_percentage": 99.8,
                        "idle_hours_per_day": 8.5,
                        "rightsizing_recommendation": "t3.small",
                        "potential_monthly_savings": 15.50,
                        "notes": "Low CPU utilization - good candidate for rightsizing"
                    }
                ]
            }
        }
        
        return template
    
    def create_reserved_instance_template(self):
        """Create template for reserved instance analysis."""
        
        template = {
            "reserved_instance_template": {
                "description": "Template for analyzing reserved instance opportunities",
                "fields": {
                    "instance_type": "t3.medium",
                    "region": "us-east-1",
                    "cloud_provider": "AWS/Azure/GCP",
                    "current_pricing_model": "On-Demand/Spot/Reserved",
                    "current_monthly_cost": 29.95,
                    "reserved_instance_term": "1 Year/3 Years",
                    "reserved_instance_payment": "All Upfront/Partial Upfront/No Upfront",
                    "reserved_instance_monthly_cost": 18.50,
                    "upfront_payment": 0.00,
                    "monthly_savings": 11.45,
                    "annual_savings": 137.40,
                    "utilization_requirement": "24/7",
                    "current_utilization_hours": 720,
                    "minimum_utilization_hours": 720,
                    "break_even_months": 0,
                    "roi_percentage": 38.2,
                    "recommendation": "Purchase RI/Not Recommended",
                    "notes": "Additional details"
                },
                "example_records": [
                    {
                        "instance_type": "t3.medium",
                        "region": "us-east-1",
                        "cloud_provider": "AWS",
                        "current_pricing_model": "On-Demand",
                        "current_monthly_cost": 29.95,
                        "reserved_instance_term": "1 Year",
                        "reserved_instance_payment": "No Upfront",
                        "reserved_instance_monthly_cost": 18.50,
                        "upfront_payment": 0.00,
                        "monthly_savings": 11.45,
                        "annual_savings": 137.40,
                        "utilization_requirement": "24/7",
                        "current_utilization_hours": 720,
                        "minimum_utilization_hours": 720,
                        "break_even_months": 0,
                        "roi_percentage": 38.2,
                        "recommendation": "Purchase RI",
                        "notes": "High utilization makes RI cost-effective"
                    }
                ]
            }
        }
        
        return template
    
    def create_managed_services_template(self):
        """Create template for managed services value assessment."""
        
        template = {
            "managed_services_template": {
                "description": "Template for assessing managed services value",
                "fields": {
                    "service_name": "24/7 Monitoring",
                    "service_category": "Monitoring/Backup/Security/Patching/Support",
                    "synoptek_monthly_cost": 500.00,
                    "market_rate_monthly_cost": 400.00,
                    "premium_percentage": 25.0,
                    "premium_amount": 100.00,
                    "service_level": "Premium/Standard/Basic",
                    "sla_uptime": "99.9%/99.5%/99.0%",
                    "response_time": "2 hours/4 hours/8 hours",
                    "support_hours_included": 40,
                    "support_hours_used": 25,
                    "support_hours_billed": 0,
                    "additional_services": "Backup, Security, Patching",
                    "value_added_services": "Proactive monitoring, Automated remediation",
                    "cost_avoidance": "Reduced downtime, Faster issue resolution",
                    "internal_equivalent_cost": "Would require 2 FTE",
                    "internal_equivalent_monthly_cost": 15000.00,
                    "roi_percentage": 96.7,
                    "recommendation": "Keep/Replace/Reconsider",
                    "notes": "Additional details"
                },
                "example_records": [
                    {
                        "service_name": "24/7 Monitoring",
                        "service_category": "Monitoring",
                        "synoptek_monthly_cost": 500.00,
                        "market_rate_monthly_cost": 400.00,
                        "premium_percentage": 25.0,
                        "premium_amount": 100.00,
                        "service_level": "Premium",
                        "sla_uptime": "99.9%",
                        "response_time": "2 hours",
                        "support_hours_included": 40,
                        "support_hours_used": 25,
                        "support_hours_billed": 0,
                        "additional_services": "Backup, Security, Patching",
                        "value_added_services": "Proactive monitoring, Automated remediation",
                        "cost_avoidance": "Reduced downtime, Faster issue resolution",
                        "internal_equivalent_cost": "Would require 2 FTE",
                        "internal_equivalent_monthly_cost": 15000.00,
                        "roi_percentage": 96.7,
                        "recommendation": "Keep",
                        "notes": "High value for the cost - includes multiple services"
                    }
                ]
            }
        }
        
        return template
    
    def create_data_collection_guide(self):
        """Create a comprehensive data collection guide."""
        
        guide = f"""# Cloud Spend Analysis - Data Collection Guide

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Purpose:** Analyze Synoptek reseller costs and identify cloud optimization opportunities

## 📋 Data Collection Requirements

### 1. Cloud Provider Invoices
**Sources:** AWS/Azure/GCP billing portals, Cost Explorer, CloudWatch
**Time Period:** Last 6-12 months
**Frequency:** Monthly

**Key Data Points:**
- Resource-level cost breakdown
- Usage patterns and utilization
- Reserved instance coverage
- Data transfer costs
- Cross-region charges

### 2. Synoptek Reseller Invoices
**Sources:** Synoptek billing portal, contract documents
**Time Period:** Last 6-12 months
**Frequency:** Monthly

**Key Data Points:**
- Base cloud costs vs markup
- Managed services fees
- Support tier costs
- Volume discounts applied
- Professional services charges

### 3. Resource Utilization Metrics
**Sources:** CloudWatch, Azure Monitor, Cloud Monitoring
**Time Period:** Last 3 months
**Frequency:** Daily averages

**Key Data Points:**
- CPU/Memory utilization
- Network I/O patterns
- Storage performance
- Idle resource identification
- Rightsizing opportunities

### 4. Reserved Instance Analysis
**Sources:** Cost Explorer, Reserved Instance recommendations
**Time Period:** Current usage patterns
**Frequency:** Monthly

**Key Data Points:**
- Current vs recommended RI coverage
- Break-even analysis
- ROI calculations
- Utilization requirements

### 5. Managed Services Assessment
**Sources:** Synoptek service catalog, market research
**Time Period:** Current contracts
**Frequency:** Quarterly review

**Key Data Points:**
- Service value vs cost
- Market rate comparison
- Internal equivalent costs
- SLA performance metrics

## 🎯 Analysis Objectives

### Primary Goals:
1. **Cost Optimization:** Identify 20-30% savings opportunities
2. **Reseller Value Assessment:** Evaluate Synoptek's added value
3. **Resource Rightsizing:** Optimize instance types and sizes
4. **Reserved Instance Strategy:** Maximize RI coverage
5. **Managed Services ROI:** Assess service value

### Expected Outcomes:
- Detailed cost comparison (Direct vs Reseller)
- Resource optimization recommendations
- Reserved instance purchase plan
- Managed services value assessment
- Contract negotiation leverage points

## 📊 Data Collection Templates

The following CSV templates have been created:
1. `cloud_invoice_template.csv` - Cloud provider invoice data
2. `synoptek_reseller_template.csv` - Synoptek reseller data
3. `resource_utilization_template.csv` - Resource utilization metrics
4. `reserved_instance_template.csv` - Reserved instance analysis
5. `managed_services_template.csv` - Managed services assessment

## 🚀 Next Steps

1. **Data Collection:** Use templates to gather required data
2. **Data Validation:** Ensure accuracy and completeness
3. **Analysis Execution:** Run comprehensive cloud spend analysis
4. **Recommendations:** Generate actionable optimization plan
5. **Implementation:** Execute cost optimization strategies

---
*Generated by Cloud Spend Analysis Template Tool*
"""
        
        return guide
    
    def generate_templates(self):
        """Generate all templates and guides."""
        print("=" * 70)
        print("    CLOUD SPEND ANALYSIS TEMPLATE GENERATOR")
        print("=" * 70)
        print()
        
        # Create templates
        cloud_invoice = self.create_cloud_invoice_template()
        synoptek_reseller = self.create_synoptek_reseller_template()
        resource_utilization = self.create_resource_utilization_template()
        reserved_instance = self.create_reserved_instance_template()
        managed_services = self.create_managed_services_template()
        
        # Save templates as JSON
        with open(f'{self.output_dir}/cloud_invoice_template.json', 'w') as f:
            json.dump(cloud_invoice, f, indent=2)
        
        with open(f'{self.output_dir}/synoptek_reseller_template.json', 'w') as f:
            json.dump(synoptek_reseller, f, indent=2)
        
        with open(f'{self.output_dir}/resource_utilization_template.json', 'w') as f:
            json.dump(resource_utilization, f, indent=2)
        
        with open(f'{self.output_dir}/reserved_instance_template.json', 'w') as f:
            json.dump(reserved_instance, f, indent=2)
        
        with open(f'{self.output_dir}/managed_services_template.json', 'w') as f:
            json.dump(managed_services, f, indent=2)
        
        # Create CSV templates
        self.create_csv_templates()
        
        # Create data collection guide
        guide = self.create_data_collection_guide()
        with open(f'{self.output_dir}/data_collection_guide.md', 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print("✅ Cloud Spend Analysis Templates generated successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Templates created:")
        print(f"   - cloud_invoice_template.json")
        print(f"   - synoptek_reseller_template.json")
        print(f"   - resource_utilization_template.json")
        print(f"   - reserved_instance_template.json")
        print(f"   - managed_services_template.json")
        print(f"   - data_collection_guide.md")
        print(f"   - CSV templates for data collection")
        
        return True
    
    def create_csv_templates(self):
        """Create CSV templates for data collection."""
        
        # Cloud Invoice Template
        cloud_invoice_df = pd.DataFrame([
            {
                "invoice_date": "2025-01-31",
                "cloud_provider": "AWS",
                "account_id": "123456789012",
                "billing_period": "2025-01",
                "service_category": "Compute",
                "service_name": "EC2",
                "resource_id": "i-1234567890abcdef0",
                "resource_name": "web-server-01",
                "region": "us-east-1",
                "instance_type": "t3.medium",
                "usage_hours": 720,
                "unit_price": 0.0416,
                "total_cost": 29.95,
                "data_transfer_gb": 100,
                "data_transfer_cost": 9.00,
                "reserved_instance": "No",
                "spot_instance": "No",
                "auto_scaling": "Yes",
                "tags": "Environment=Production,Project=WebApp",
                "utilization_percentage": 45.2,
                "rightsizing_opportunity": "Yes",
                "notes": "Underutilized - consider t3.small"
            }
        ])
        cloud_invoice_df.to_csv(f'{self.output_dir}/cloud_invoice_template.csv', index=False)
        
        # Synoptek Reseller Template
        synoptek_df = pd.DataFrame([
            {
                "invoice_date": "2025-01-31",
                "synoptek_invoice_number": "SYN-2025-001",
                "billing_period": "2025-01",
                "cloud_provider": "AWS",
                "service_category": "Cloud Services",
                "service_name": "AWS Consumption",
                "base_cloud_cost": 1000.00,
                "synoptek_markup_percentage": 15.0,
                "synoptek_markup_amount": 150.00,
                "managed_services_fee": 500.00,
                "professional_services_fee": 200.00,
                "support_tier": "Premium",
                "support_hours_included": 40,
                "support_hours_used": 25,
                "support_hours_billed": 0,
                "total_synoptek_charge": 1850.00,
                "volume_discount_applied": "Yes",
                "discount_percentage": 5.0,
                "discount_amount": 92.50,
                "final_amount": 1757.50,
                "contract_tier": "Enterprise",
                "managed_services_included": "Monitoring, Backup, Security, Patching",
                "sla_level": "99.9%",
                "response_time_guarantee": "2 hours",
                "notes": "Includes 24/7 monitoring and backup services"
            }
        ])
        synoptek_df.to_csv(f'{self.output_dir}/synoptek_reseller_template.csv', index=False)
        
        # Resource Utilization Template
        utilization_df = pd.DataFrame([
            {
                "resource_id": "i-1234567890abcdef0",
                "resource_name": "web-server-01",
                "cloud_provider": "AWS",
                "service_name": "EC2",
                "instance_type": "t3.medium",
                "region": "us-east-1",
                "measurement_date": "2025-01-15",
                "cpu_utilization_avg": 25.5,
                "cpu_utilization_peak": 85.2,
                "cpu_utilization_min": 5.1,
                "memory_utilization_avg": 45.8,
                "memory_utilization_peak": 92.1,
                "memory_utilization_min": 12.3,
                "network_in_mbps_avg": 15.2,
                "network_out_mbps_avg": 8.7,
                "disk_read_iops_avg": 150,
                "disk_write_iops_avg": 75,
                "disk_read_mbps_avg": 25.5,
                "disk_write_mbps_avg": 12.8,
                "uptime_percentage": 99.8,
                "idle_hours_per_day": 8.5,
                "rightsizing_recommendation": "t3.small",
                "potential_monthly_savings": 15.50,
                "notes": "Low CPU utilization - good candidate for rightsizing"
            }
        ])
        utilization_df.to_csv(f'{self.output_dir}/resource_utilization_template.csv', index=False)
        
        # Reserved Instance Template
        ri_df = pd.DataFrame([
            {
                "instance_type": "t3.medium",
                "region": "us-east-1",
                "cloud_provider": "AWS",
                "current_pricing_model": "On-Demand",
                "current_monthly_cost": 29.95,
                "reserved_instance_term": "1 Year",
                "reserved_instance_payment": "No Upfront",
                "reserved_instance_monthly_cost": 18.50,
                "upfront_payment": 0.00,
                "monthly_savings": 11.45,
                "annual_savings": 137.40,
                "utilization_requirement": "24/7",
                "current_utilization_hours": 720,
                "minimum_utilization_hours": 720,
                "break_even_months": 0,
                "roi_percentage": 38.2,
                "recommendation": "Purchase RI",
                "notes": "High utilization makes RI cost-effective"
            }
        ])
        ri_df.to_csv(f'{self.output_dir}/reserved_instance_template.csv', index=False)
        
        # Managed Services Template
        ms_df = pd.DataFrame([
            {
                "service_name": "24/7 Monitoring",
                "service_category": "Monitoring",
                "synoptek_monthly_cost": 500.00,
                "market_rate_monthly_cost": 400.00,
                "premium_percentage": 25.0,
                "premium_amount": 100.00,
                "service_level": "Premium",
                "sla_uptime": "99.9%",
                "response_time": "2 hours",
                "support_hours_included": 40,
                "support_hours_used": 25,
                "support_hours_billed": 0,
                "additional_services": "Backup, Security, Patching",
                "value_added_services": "Proactive monitoring, Automated remediation",
                "cost_avoidance": "Reduced downtime, Faster issue resolution",
                "internal_equivalent_cost": "Would require 2 FTE",
                "internal_equivalent_monthly_cost": 15000.00,
                "roi_percentage": 96.7,
                "recommendation": "Keep",
                "notes": "High value for the cost - includes multiple services"
            }
        ])
        ms_df.to_csv(f'{self.output_dir}/managed_services_template.csv', index=False)

def main():
    """Main function to generate cloud spend analysis templates."""
    template_generator = CloudSpendAnalysisTemplate()
    success = template_generator.generate_templates()
    
    if success:
        print()
        print("🎉 Templates generated successfully!")
        print("📋 Ready for data collection")
        print("💼 Use templates to gather detailed cloud spend data")
    else:
        print("❌ Template generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 