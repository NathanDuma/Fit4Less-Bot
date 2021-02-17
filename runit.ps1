$date = ("{0:yyyyMMddHHmm}" -f (Get-Date))
python3 main.py > logs$($date).txt