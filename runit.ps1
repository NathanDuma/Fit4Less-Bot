$date = ("{0:yyyyMMddHHmm}" -f (Get-Date))
$file = "./logs/logs$($date).txt"
echo "Starting up!" >> $file
while ($true) {
	echo "Running python script!" >> $file
	python3 main.py >> $file
	if (!($?)){
		echo "Error" >> $file
	}
	else
	{
		echo "We are done all this!" >> $file
		break
	}
}