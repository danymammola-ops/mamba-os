param(
    [string]$Focus = ""
)

$script = "scripts/handoff_generator.py"
Push-Location $PSScriptRoot\..

if ($Focus) {
    & python $script $Focus
} else {
    & python $script
}

Pop-Location