# Checkpoint CLI per Mamba OS
param([Parameter(ValueFromRemainingArguments=$true)]$args)
python "$PSScriptRoot\scripts\checkpoint.py" @args
