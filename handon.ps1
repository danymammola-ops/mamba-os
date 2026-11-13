param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)
python "$PSScriptRoot\scripts\show_handoff.py" @Arguments
