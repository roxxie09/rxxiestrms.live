# Shows a /raw page selected in File Explorer. Started by the folder buttons in the EPG logo dashboard.
# The links look like  roxie-raw:raw/tsn5.html  - only a plain page name is accepted, nothing else is opened.
param([string]$Link = '')

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)   # this file lives in <project>\tools\folder-button
$raw = Join-Path $root 'raw'
$explorer = Join-Path $env:SystemRoot 'explorer.exe'

try { $Link = [System.Uri]::UnescapeDataString($Link) } catch { }
$m = [regex]::Match($Link, '^(?i:roxie-raw):(?://)?/?raw/([A-Za-z0-9-][A-Za-z0-9_-]*\.html)/?$')
$file = $null
if ($m.Success) { $file = Join-Path $raw $m.Groups[1].Value }

if ($file -and (Test-Path -LiteralPath $file -PathType Leaf)) {
    Start-Process -FilePath $explorer -ArgumentList ('/select,"' + $file + '"')
} elseif (Test-Path -LiteralPath $raw -PathType Container) {
    Start-Process -FilePath $explorer -ArgumentList ('"' + $raw + '"')   # page not in your copy yet: just the folder
}
