param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)
python "$PSScriptRoot\scripts\handoff_generator.py" @Arguments
