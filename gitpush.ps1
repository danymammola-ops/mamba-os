param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)
python "$PSScriptRoot\scripts\gitpush.py" @Arguments
