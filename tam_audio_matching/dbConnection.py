from datetime import datetime, timezone, timedelta
from config import config
import psycopg2
from settings import settings


def insert_matching_result(rows):
  conn = None
  try:
    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    # create a new cursor
    cur = conn.cursor()

    args = ','.join(cur.mogrify("(%s, %s, %s, %s)", i).decode('utf-8')
                    for i in rows)

    sql = "INSERT INTO matching_results(household_id, member_ids, device_start_datetime, channel_matchings) " \
          "VALUES " + args

    # execute the INSERT statement
    cur.execute(sql)
    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print("DB error => ", error)
  finally:
    if conn is not None:
      conn.close()


def get_row_entry(device_start_date_time, household_id):
  conn = None
  try:
    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    # create a new cursor
    cur = conn.cursor()
    sql = f"SELECT channel_name, channel_matchings FROM matching_results " \
          f"WHERE device_start_datetime = '{device_start_date_time}' " \
          f"AND household_id = {household_id} " \
          f"ORDER BY household_id, device_start_datetime LIMIT 1"
    # execute the INSERT statement

    cur.execute(sql)
    result = cur.fetchone()
    # print(results)
    # close communication with the database
    cur.close()
    return result
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()


def update_row_entry(device_start_date_time, household_id, channel_name = None, channel_datetime= None):
  conn = None
  try:
    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    # create a new cursor
    cur = conn.cursor()

    sql = f"UPDATE matching_results " \
          f"SET is_set = {True} "
    if channel_name and channel_datetime :
          sql = f"{sql}, channel_name = '{channel_name}', " \
                f"channel_datetime = '{channel_datetime}' "

    sql = f"{sql}WHERE device_start_datetime = '{device_start_date_time}' " \
          f"AND household_id = {household_id}"
    # execute the INSERT statement
    cur.execute(sql)
    conn.commit()
    # close communication with the database
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()


def get_matching_rawdata():
  conn = None
  try:
    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    # create a new cursor
    cur = conn.cursor()
    considering_days = settings.get('CONSIDERING_PREV_DAYS')
    matching_date = (datetime.now(timezone.utc) - timedelta(hours=considering_days * 24 - 6)).strftime('%Y-%m-%d %H:%M:%S')
    sql = f"SELECT * FROM matching_results " \
          f"WHERE DATE_TRUNC('day', device_start_datetime) = '{matching_date}'::date AND is_set = {False} " \
          f"ORDER BY household_id, device_start_datetime"

    print(sql)
    # execute the INSERT statement
    cur.execute(sql)
    results = cur.fetchall()
    # close communication with the database
    cur.close()
    return results
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()

def update_send_status(device_start_date_time, household_id):
  conn = None
  try:
    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    # create a new cursor
    cur = conn.cursor()

    sql = f"UPDATE matching_results " \
          f"SET is_sent = {True} " \
          f"WHERE device_start_datetime = '{device_start_date_time}' " \
          f"AND household_id = {household_id}"

    # execute the INSERT statement
    cur.execute(sql)
    conn.commit()
    # close communication with the database
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()

#get_matching_rawdata()