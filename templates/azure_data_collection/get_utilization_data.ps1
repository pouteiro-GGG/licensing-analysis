# PowerShell script to collect Azure resource utilization data
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
