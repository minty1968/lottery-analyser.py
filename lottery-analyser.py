#!/usr/bin/env python3

#  Import required extensiuons
import random, sys, os.path, shutil, csv, io, requests, collections, json, pymongo, textwrap, argparse
import pandas as pd
from prettytable import PrettyTable

drawTypeFullName = ""
draw_data = {}
baseDirName = os.getcwd() + '/'  #  Get current working directory, so this can be used on any system without modification
working_dir = os.path.join(os.getcwd(), 'working')  #  Create a global variable for working directory to be used later


def get_arguments():
  """
       Here we are looking for lottery draw names as arguments:
       lotto, euromillions, thunderball, set-for-life,
       lotto-hotpicks, euromillions-hotpicks
  """

  parser = argparse.ArgumentParser(
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=textwrap.dedent('''\
         Type in the draw name required from the below list
         --------------------------------------------------
          use -d followed by one of the below draw names
          example:  lottery-analyser.py -d lotto
                             lotto
                        lotto-hotpicks
                         euromillions
                     euromillions-hotpicks
                          set-for-life
                          thunderball
         '''))
  parser.add_argument('-d', dest='DRAW', help='Draw Analyser')
  args = parser.parse_args()

  if not args.DRAW:
    parser.print_help()
    print('')
    print('I\'m going to use lotto as default on this occassion, use one of the above draw names in the future')
    args.DRAW = 'lotto'

  return args



def downloadLotteryNumbers(drawType, working_dir):
  """
       Here we are downloading the relevant draw files from the national lottery Website
       and saving them to readable csv files
  """
  # Create target Directory structure, if don't exist
  if not os.path.exists(working_dir):
    os.makedirs(working_dir)
  try:
    url = 'https://www.national-lottery.co.uk/results/{}/draw-history/csv'.format(drawType)  # Setup URL for results file, this will differ between draws
    df = pd.read_csv(url)
  except Exception as e :
    print ("Exception: ",e," at ",url)
  writeJson = os.path.join(working_dir,'{}.json'.format(drawType))
  if drawType == "lotto" or drawType == "lotto-hotpicks":
      main_total = df["Ball 1"] + df["Ball 2"] + df["Ball 3"] + df["Ball 4"] + df["Ball 5"] + df["Ball 6"]
      main_average = main_total / 6
      rounded_average = round(main_average, 0)
      df.insert(7, "Total", main_total)
      df.insert(8, "Average", rounded_average)
      df = df.rename(columns = {"DrawDate":"_id", "Ball 1":"Ball1", "Ball 2":"Ball2", "Ball 3":"Ball3", "Ball 4":"Ball4", "Ball 5":"Ball5", "Ball 6":"Ball6", "Bonus Ball":"Bonus_Ball", "Ball Set":"Ball_Set"})  # Here we are changiong the draw date to _id so we can use it with mongodb later.
  else:
      main_total = df["Ball 1"] + df["Ball 2"] + df["Ball 3"] + df["Ball 4"] + df["Ball 5"]
      main_average = main_total / 5
      rounded_average = round(main_average, 0)
      df.insert(6, "Main_Total", main_total)
      df.insert(7, "Main_Average", rounded_average)
      df = df.rename(columns = {"DrawDate":"_id", "Ball 1":"Ball1", "Ball 2":"Ball2", "Ball 3":"Ball3", "Ball 4":"Ball4", "Ball 5":"Ball5"})  # Here we are changiong the draw date to _id so we can use it with mongodb later.
  if drawType == "euromillions":
      bonus_total = df["Lucky Star 1"] + df["Lucky Star 2"]
      bonus_average = bonus_total / 2
      rounded_average = round(bonus_average, 0)
      df.insert(10, "Bonus_Total", bonus_total)
      df.insert(11, "Bonus_Average", rounded_average)
      df = df.rename(columns = {"Lucky Star 1":"LuckyStar1", "Lucky Star 2":"LuckyStar2"})
      df = df.drop(columns = "UK Millionaire Maker")
  elif drawType == "set-for-life":
      df = df.rename(columns = {"Life Ball":"LifeBall", "Ball Set":"BallSet"})
  else:
      df = df.rename(columns = {"Ball Set":"BallSet"})     
  df = df.drop(columns = "DrawNumber")
  draw_data = df.to_dict('records')  #  Here we are creating a python dictionarty of records, as this is the best format for this data
  try:
    with open(writeJson, 'w') as fp:  #  Open json file for writing
      json.dump(draw_data, fp)
  except EOFError as ex:
    print("Caught the EOF error.")
    raise ex
  except IOError as e:
    print("Caught the I/O error.")
    raise ex



def write_to_db(drawType, working_dir):
  """
       Here we will write all json files to mongodb collections.
  """
  json_file = os.path.join(working_dir, '{}.json'.format(drawType))
  db_conn = "mongodb://localhost:27017/"
  db_name = "lottery"

  myconn = pymongo.MongoClient(db_conn)
  mydb = myconn[db_name]
  mycol = mydb[drawType]

  mycol.drop()  #  Firstly, we will drop the current data in the collection, then re-insert new data

  try:
    a = json.load(open(json_file, 'r'))
    mycol.insert_many(a)
  except EOFError as ex:
    print("Caught the EOF error.")
    raise ex
  except IOError as e:
    print("Caught the I/O error.")
    raise ex


def clean_up(drawType, working_dir):
  """
       Here we are cleaning up, removing current directory, also copying all .json files from final direcotry to json directory.
  """
  os.remove(os.path.join(working_dir,'{}.json'.format(drawType)))
  shutil.rmtree(working_dir)



####################################################################
###   Program starts here, we'll call each directoy one by one   ###
####################################################################

args = get_arguments()   # Here we are getting the arguments before running the app.
drawType = args.DRAW   # Here we are assigning the entered argument to drawType
downloadLotteryNumbers(drawType, working_dir)   # Here we are now download ing the draw files for the argument draw name
#compare_json_files(drawType, working_dir)   # Here we willbe comparing two json compare_json_files
write_to_db(drawType, working_dir)   # Here will will write our JSON file to our MongoDB Collection
#clean_up(drawType, working_dir)  # Here we are cleaning up the mess we made of the file system  :-)
