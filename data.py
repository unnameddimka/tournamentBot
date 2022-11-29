import sys
import configparser
import mysql.connector


config = configparser.ConfigParser()
config.read('config/config.ini')

db_config = {
  'user': config['MYSQL']['user'],
  'password': config['MYSQL']['password'],
  'host': config['MYSQL']['host'],
  'database': config['MYSQL']['database'],
  'raise_on_warnings': True
}


mydb = mysql.connector.connect(**db_config)


def exec_request(req: str, params: tuple = tuple()):
    mycursor = mydb.cursor()
    t_params = tuple(params)
    mycursor.execute(req, t_params)
    result = mycursor.fetchall()
    mydb.commit()
    return result


def test_1():
    result = exec_request("SELECT %s", ('hello world',))
    print(result)
    if result[0][0] == 'hello world':
        return 1
    return 'ERROR'


if __name__ == '__main__':
    if test_1() == 1:
        sys.exit(0)
    sys.exit(1)
