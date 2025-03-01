param(
    [string]$script_path,
    [string]$output_path
)

$array = Invoke-ScriptAnalyzer $script_path -Settings PSGallery -Recurse
$array | Export-Csv -Path $output_path -NoTypeInformation