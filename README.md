# lottery-analyser.py

This is a simple program that will download the latest draw results CSV file form the national lottery website.

Once it has downloaded it, the program will remove some columns like draw number, it will also remove spaces fdrom titles,
it wioll add up all the main bnumbers and average them, it will do the same for bonus numbers.

Lastly it will write all data to a mongdoDB collection with the same name as the draw type, using 'lottery' as the DB.

To run the program make sure it has execute permissions and run one of the follwoing:


./lottery-analyser.py -d lotto
./lottery-analyser.py -d lotto
./lottery-analyser.py -d lotto-hotpicks
./lottery-analyser.py -d euromillions-hotpicks
./lottery-analyser.py -d euromillions
./lottery-analyser.py -d thunderball
./lottery-analyser.py -d set-for-life


Program can be easily  mpodifed to run from an array with the abobve draw types in it, or if run on a linux server,
you could run the relevant draw type the day after the draw using a cron job.
