$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$projectRoot = Split-Path -Parent $PSScriptRoot
$sourceDir = Join-Path $projectRoot 'Quellen/dekompiliert'
$outputDir = Join-Path $projectRoot 'build/medien'
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
$inventory = @()
foreach ($file in (Get-ChildItem -LiteralPath $sourceDir | Where-Object { $_.Extension -in '.BMP','.WMF' })) {
    $im = [Drawing.Image]::FromFile($file.FullName)
    try {
        $pngPath = Join-Path $outputDir ($file.BaseName + '.png')
        if ($file.Extension -eq '.WMF') {
            $width = [int][Math]::Ceiling($im.Width / $im.HorizontalResolution * 300)
            $height = [int][Math]::Ceiling($im.Height / $im.VerticalResolution * 300)
            $bmp = New-Object Drawing.Bitmap($width,$height)
            $bmp.SetResolution(300,300)
            $g = [Drawing.Graphics]::FromImage($bmp)
            try {
                $g.Clear([Drawing.Color]::White)
                $g.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::HighQuality
                $g.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
                $g.DrawImage($im, [Drawing.Rectangle]::new(0,0,$width,$height))
                $bmp.Save($pngPath,[Drawing.Imaging.ImageFormat]::Png)
            } finally { $g.Dispose(); $bmp.Dispose() }
        } else {
            $width = $im.Width; $height = $im.Height
            $im.Save($pngPath,[Drawing.Imaging.ImageFormat]::Png)
        }
        $inventory += [PSCustomObject]@{file=$file.Name; png=$file.BaseName+'.png'; width=$width; height=$height; sourceWidth=$im.Width; sourceHeight=$im.Height; dpi=$im.HorizontalResolution}
    } finally { $im.Dispose() }
}
$inventory | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputDir 'inventar.json') -Encoding UTF8
Write-Output ('Converted images: ' + $inventory.Count)
