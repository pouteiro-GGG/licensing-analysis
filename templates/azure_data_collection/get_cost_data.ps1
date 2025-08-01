# PowerShell script to collect Azure cost data
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
