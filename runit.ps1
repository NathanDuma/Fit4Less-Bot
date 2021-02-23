$date = ("{0:yyyyMMddHHmm}" -f (Get-Date))
echo "Starting up!" >> ./logs/logs$($date).txt
while ($true) {
	echo "Running python script!" >> ./logs/logs$($date).txt
	python3 main.py >> ./logs/logs$($date).txt
	if (!($?)){
		echo "Error" >> ./logs/logs$($date).txt
	}
	else
	{
		echo "We are done all this!" >> ./logs/logs$($date).txt
		break
	}
}