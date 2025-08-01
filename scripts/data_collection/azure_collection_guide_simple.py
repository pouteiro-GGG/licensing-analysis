#!/usr/bin/env python3
"""
Azure Data Collection Guide - Simplified
Step-by-step instructions for collecting cloud spend data from Azure console
"""

from datetime import datetime
from pathlib import Path

class AzureDataCollectionGuide:
    def __init__(self):
        self.output_dir = "templates/azure_data_collection"
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Ensure output directory exists."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def create_azure_guide(self):
        """Create comprehensive Azure data collection guide."""
        
        guide = """# Azure Cloud Spend Data Collection Guide

**Generated:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
**Purpose:** Collect detailed Azure spend data for Synoptek reseller analysis

## 🚀 Quick Start - Azure Data Collection

### 1. Cost Management + Billing (Primary Source)

#### **Step 1: Access Cost Management**
1. Go to Azure Portal → **Cost Management + Billing**
2. Select your **Billing Account** (Enterprise Agreement/Microsoft Customer Agreement)
3. Click on **Cost Management** in the left menu

#### **Step 2: Export Cost Data**
1. Navigate to **Exports** in the left menu
2. Click **+ Add** to create a new export
3. Configure export settings:
   - **Name:** `Azure_Cost_Export_Monthly`
   - **Export type:** `Actual cost (usage and purchases)`
   - **Time period:** `Last 12 months`
   - **Granularity:** `Monthly`
   - **File format:** `CSV`
   - **Storage account:** Select your storage account
   - **Container:** `cost-exports`
   - **Directory:** `azure-costs`

#### **Step 3: Download Cost Data**
1. Go to your **Storage Account** → **Containers** → `cost-exports`
2. Download the CSV files (one per month)
3. Combine into a single file for analysis

### 2. Azure Advisor (Optimization Recommendations)

#### **Step 1: Access Azure Advisor**
1. Go to Azure Portal → **Advisor**
2. Select your **Subscription**
3. Review **Cost** recommendations

#### **Step 2: Export Recommendations**
1. Click on **Cost** tab
2. For each recommendation, note:
   - **Resource ID**
   - **Current cost**
   - **Potential savings**
   - **Recommendation type** (Resize, RI, etc.)

### 3. Azure Monitor (Resource Utilization)

#### **Step 1: Access Resource Metrics**
1. Go to **Virtual Machines** in Azure Portal
2. Select a VM → **Metrics**
3. Add metrics:
   - **CPU Percentage**
   - **Memory Percentage**
   - **Network In/Out**
   - **Disk Read/Write**

#### **Step 2: Export Utilization Data**
1. Set time range to **Last 30 days**
2. Set granularity to **1 hour**
3. Click **Download CSV**
4. Repeat for each VM

### 4. Azure Reserved Instance Analysis

#### **Step 1: Access RI Recommendations**
1. Go to **Cost Management + Billing** → **Reservations**
2. Click **+ Add** to see recommendations
3. Note recommended RIs for your resources

#### **Step 2: Current RI Coverage**
1. Go to **Reservations** → **Reserved instances**
2. Export current RI inventory
3. Note utilization and expiration dates

### 5. Azure Resource Graph (Advanced Querying)

#### **Step 1: Access Resource Graph**
1. Go to Azure Portal → **Resource Graph Explorer**
2. Use the following queries to extract data:

#### **Query 1: All Resources with Costs**
```kusto
Resources
| where type in ('microsoft.compute/virtualmachines', 'microsoft.storage/storageaccounts', 'microsoft.network/virtualnetworks')
| project id, name, type, location, tags
| join kind=leftouter (
    ResourceContainers
    | where type=='microsoft.resources/subscriptions'
    | project subscriptionId, subscriptionName = name
) on subscriptionId
```

#### **Query 2: VM Utilization Data**
```kusto
Resources
| where type == 'microsoft.compute/virtualmachines'
| project id, name, location, properties.hardwareProfile.vmSize
| join kind=leftouter (
    InsightsMetrics
    | where name == 'Percentage CPU'
    | summarize avg(value) by resourceId
) on $left.id == $right.resourceId
```

### 6. Azure CLI (Automated Data Collection)

#### **Step 1: Install Azure CLI**
```bash
# Windows
winget install Microsoft.AzureCLI

# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

#### **Step 2: Login and Set Subscription**
```bash
az login
az account set --subscription "Your-Subscription-Name"
```

#### **Step 3: Export Cost Data**
```bash
# Get cost data for last 12 months
az consumption usage list --start-date 2024-01-01 --end-date 2024-12-31 --output table

# Get VM list with details
az vm list --query "[].{Name:name, ResourceGroup:resourceGroup, Size:hardwareProfile.vmSize, Location:location}" --output table

# Get storage account costs
az storage account list --query "[].{Name:name, ResourceGroup:resourceGroup, Location:location, Sku:sku.name}" --output table
```

### 7. Azure PowerShell (Alternative Method)

#### **Step 1: Install Azure PowerShell**
```powershell
Install-Module -Name Az -AllowClobber
```

#### **Step 2: Connect and Export Data**
```powershell
# Connect to Azure
Connect-AzAccount

# Set subscription
Set-AzContext -Subscription "Your-Subscription-Name"

# Get cost data
$costs = Get-AzConsumptionUsageDetail -StartDate "2024-01-01" -EndDate "2024-12-31"
$costs | Export-Csv -Path "azure-costs.csv" -NoTypeInformation

# Get VM details
$vms = Get-AzVM
$vms | Select-Object Name, ResourceGroupName, Location, @{Name="VMSize";Expression={$_.HardwareProfile.VmSize}} | Export-Csv -Path "azure-vms.csv" -NoTypeInformation
```

## 📊 Data Collection Checklist

### **Required Data Points:**

#### **Cost Data (Monthly for 12 months):**
- [ ] Resource ID and name
- [ ] Service category (Compute, Storage, Network, etc.)
- [ ] Resource type (VM, Storage Account, etc.)
- [ ] Region
- [ ] Instance size/type
- [ ] Usage hours
- [ ] Unit price
- [ ] Total cost
- [ ] Tags (Environment, Project, etc.)

#### **Utilization Data (Daily averages for 30 days):**
- [ ] CPU utilization (avg, peak, min)
- [ ] Memory utilization (avg, peak, min)
- [ ] Network I/O (in/out MB/s)
- [ ] Disk I/O (read/write IOPS)
- [ ] Uptime percentage
- [ ] Idle hours per day

#### **Reserved Instance Data:**
- [ ] Current RI coverage
- [ ] Recommended RIs
- [ ] Break-even analysis
- [ ] ROI calculations
- [ ] Utilization requirements

#### **Synoptek Reseller Data:**
- [ ] Base Azure costs
- [ ] Synoptek markup percentage
- [ ] Managed services fees
- [ ] Support tier costs
- [ ] Volume discounts
- [ ] Professional services

## 🎯 Pro Tips for Azure Data Collection

### **1. Use Azure Cost Management Exports**
- Set up **automated exports** to avoid manual collection
- Export **daily** for detailed analysis
- Use **resource-level** granularity for rightsizing

### **2. Leverage Azure Advisor**
- Check **Cost** recommendations weekly
- Implement **quick wins** immediately
- Track **savings potential** over time

### **3. Monitor Resource Utilization**
- Set up **Azure Monitor** alerts for underutilized resources
- Use **Log Analytics** for detailed performance data
- Create **custom dashboards** for cost visibility

### **4. Reserved Instance Strategy**
- Use **Azure Advisor** for RI recommendations
- Consider **hybrid benefit** for Windows VMs
- Plan **RI purchases** based on usage patterns

### **5. Tagging Strategy**
- Implement **consistent tagging** for cost allocation
- Use tags for **Environment**, **Project**, **Owner**
- Enable **cost allocation** rules

## 📈 Expected Data Volume

### **Typical Data Points per Month:**
- **100-500 resources** (VMs, storage, networking)
- **30 days** of utilization metrics per resource
- **12 months** of cost data
- **RI recommendations** for eligible resources

### **File Sizes:**
- **Cost data:** 1-5 MB per month
- **Utilization data:** 10-50 MB per month
- **Total collection:** 100-500 MB

## 🚀 Next Steps

1. **Start with Cost Management exports** (easiest)
2. **Add Azure Advisor recommendations** (quick wins)
3. **Collect utilization data** (rightsizing opportunities)
4. **Analyze RI opportunities** (long-term savings)
5. **Compare with Synoptek data** (reseller analysis)

---
*Generated by Azure Data Collection Guide Tool*
"""
        
        return guide
    
    def create_powershell_scripts(self):
        """Create PowerShell scripts for automated data collection."""
        
        cost_script = """# PowerShell script to collect Azure cost data
# Run this script to collect cost data for the last 12 months

# Connect to Azure
Connect-AzAccount

# Set your subscription
$subscriptionName = "Your-Subscription-Name"
Set-AzContext -Subscription $subscriptionName

# Create output directory
$outputDir = "azure-cost-data"
New-Item -ItemType Directory -Force -Path $outputDir

# Get cost data for last 12 months
$startDate = (Get-Date).AddMonths(-12).ToString("yyyy-MM-dd")
$endDate = (Get-Date).ToString("yyyy-MM-dd")

Write-Host "Collecting cost data from $startDate to $endDate..."

$costs = Get-AzConsumptionUsageDetail -StartDate $startDate -EndDate $endDate
$costs | Export-Csv -Path "$outputDir/azure-costs.csv" -NoTypeInformation

Write-Host "Cost data exported to $outputDir/azure-costs.csv"

# Get VM details
Write-Host "Collecting VM details..."
$vms = Get-AzVM
$vmDetails = $vms | Select-Object Name, ResourceGroupName, Location, 
    @{Name="VMSize";Expression={$_.HardwareProfile.VmSize}},
    @{Name="OSType";Expression={$_.StorageProfile.OsDisk.OsType}},
    @{Name="Tags";Expression={$_.Tags | ConvertTo-Json -Compress}}

$vmDetails | Export-Csv -Path "$outputDir/azure-vms.csv" -NoTypeInformation

Write-Host "VM details exported to $outputDir/azure-vms.csv"

Write-Host "Data collection complete! Check the $outputDir folder for CSV files."
"""
        
        utilization_script = """# PowerShell script to collect Azure resource utilization data
# Run this script to collect utilization metrics for VMs

# Connect to Azure
Connect-AzAccount

# Set your subscription
$subscriptionName = "Your-Subscription-Name"
Set-AzContext -Subscription $subscriptionName

# Create output directory
$outputDir = "azure-utilization-data"
New-Item -ItemType Directory -Force -Path $outputDir

# Get all VMs
$vms = Get-AzVM

Write-Host "Collecting utilization data for $($vms.Count) VMs..."

$utilizationData = @()

foreach ($vm in $vms) {
    Write-Host "Processing VM: $($vm.Name)"
    
    # Get CPU utilization (last 30 days)
    $cpuMetrics = Get-AzMetric -ResourceId $vm.Id -MetricName "Percentage CPU" -StartTime (Get-Date).AddDays(-30) -EndTime (Get-Date) -TimeGrain 01:00:00
    
    if ($cpuMetrics.Data) {
        $cpuAvg = ($cpuMetrics.Data | Measure-Object -Property Total -Average).Average
        $cpuMax = ($cpuMetrics.Data | Measure-Object -Property Total -Maximum).Maximum
        $cpuMin = ($cpuMetrics.Data | Measure-Object -Property Total -Minimum).Minimum
    } else {
        $cpuAvg = $cpuMax = $cpuMin = 0
    }
    
    $utilizationData += [PSCustomObject]@{
        ResourceId = $vm.Id
        ResourceName = $vm.Name
        ResourceGroup = $vm.ResourceGroupName
        Location = $vm.Location
        VMSize = $vm.HardwareProfile.VmSize
        CPUUtilizationAvg = [math]::Round($cpuAvg, 2)
        CPUUtilizationMax = [math]::Round($cpuMax, 2)
        CPUUtilizationMin = [math]::Round($cpuMin, 2)
        CollectionDate = (Get-Date).ToString("yyyy-MM-dd")
    }
}

# Export utilization data
$utilizationData | Export-Csv -Path "$outputDir/azure-utilization.csv" -NoTypeInformation

Write-Host "Utilization data exported to $outputDir/azure-utilization.csv"
Write-Host "Processed $($utilizationData.Count) VMs"
"""
        
        return {
            "get_cost_data.ps1": cost_script,
            "get_utilization_data.ps1": utilization_script
        }
    
    def generate_azure_guide(self):
        """Generate the complete Azure data collection guide."""
        print("=" * 70)
        print("    AZURE DATA COLLECTION GUIDE GENERATOR")
        print("=" * 70)
        print()
        
        # Create guide
        guide = self.create_azure_guide()
        with open(f'{self.output_dir}/azure_data_collection_guide.md', 'w', encoding='utf-8') as f:
            f.write(guide)
        
        # Create PowerShell scripts
        scripts = self.create_powershell_scripts()
        for filename, content in scripts.items():
            with open(f'{self.output_dir}/{filename}', 'w', encoding='utf-8') as f:
                f.write(content)
        
        print("✅ Azure Data Collection Guide generated successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Files created:")
        print(f"   - azure_data_collection_guide.md")
        print(f"   - get_cost_data.ps1")
        print(f"   - get_utilization_data.ps1")
        
        return True

def main():
    """Main function to generate Azure data collection guide."""
    guide_generator = AzureDataCollectionGuide()
    success = guide_generator.generate_azure_guide()
    
    if success:
        print()
        print("🎉 Azure guide generated successfully!")
        print("📋 Ready for Azure data collection")
        print("💼 Use PowerShell scripts for automated collection")
    else:
        print("❌ Guide generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 