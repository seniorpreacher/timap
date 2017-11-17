import os

from playhouse.postgres_ext import PostgresqlExtDatabase

db = PostgresqlExtDatabase(
    os.environ.get('MY_PSQL_DBNAME'),
    user=os.environ.get('MY_PSQL_USER'),
    password=os.environ.get('MY_PSQL_PASSWORD'),
    register_hstore=False,
)


def init_db():
    db.connect()

    from backend.models.feed import Feed
    from backend.models.stop import Stop
    from backend.models.agency import Agency
    from backend.models.route import Route
    from backend.models.shape import Shape
    from backend.models.trip import Trip
    from backend.models.stop_time import StopTime
    db.create_tables([
        Feed,
        Stop,
        Route,
        Agency,
        Shape,
        Trip,
        StopTime,
    ], safe=True)
    db.close()

#
# def establish_connection(connection_data=None):
#     """
#     Create a database connection based on the :connection_data: parameter
#
#     :connection_data: Connection string attributes
#
#     :returns: psycopg2.connection
#     """
#     if connection_data is None:
#         connection_data = get_connection_data()
#     try:
#         conn = psycopg2.connect(
#             dbname=connection_data['dbname'],
#             user=connection_data['user'],
#             host=connection_data['host'],
#             password=connection_data['password'])
#         conn.autocommit = True
#     except psycopg2.DatabaseError as e:
#         print("Cannot connect to database.")
#         print(e)
#     else:
#         return conn
#
#
# def get_connection_data(db_name=None):
#     """
#     Give back a properly formatted dictionary based on the environment variables values which are started
#     with :MY__PSQL_: prefix
#
#     :db_name: optional parameter. By default it uses the environment variable value.
#     """
#     if db_name is None:
#         db_name = os.environ.get('MY_PSQL_DBNAME')
#
#     return {
#         'dbname': db_name,
#         'user': os.environ.get('MY_PSQL_USER'),
#         'host': os.environ.get('MY_PSQL_HOST'),
#         'password': os.environ.get('MY_PSQL_PASSWORD')
#     }
#
#
# def execute_script_file(file_path):
#     """
#     Execute script file based on the given file path.
#     Print the result of the execution to console.
#
#     Example:
#     > execute_script_file('db_schema/01_create_schema.sql')
#
#     :file_path: Relative path of the file to be executed.
#     """
#     package_directory = os.path.dirname(os.path.abspath(__file__))
#     full_path = os.path.join(package_directory, file_path)
#     with open(full_path) as script_file:
#         with establish_connection() as conn, \
#                 conn.cursor() as cursor:
#             try:
#                 sql_to_run = script_file.read()
#                 cursor.execute(sql_to_run)
#                 print("{} script executed successsfully.".format(file_path))
#             except Exception as ex:
#                 print("Execution of {} failed".format(file_path))
#                 print(ex.args)
#
#
# def execute_select(statement, variables=None):
#     """
#     Execute SELECT statement optionally parameterized
#
#     Example:
#     > execute_select('SELECT %(title)s;', variables={'title': 'Codecool'})
#
#     :statment: SELECT statement
#
#     :variables:  optional parameter dict"""
#     result_set = []
#     with establish_connection() as conn:
#         with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
#             cursor.execute(statement, variables)
#             result_set = cursor.fetchall()
#     return result_set
#
#
# def execute_dml_statement(statement, variables=None):
#     """
#     Execute data manipulation query statement (optionally parameterized)
#
#     :statment: SQL statement
#
#     :variables:  optional parameter dict"""
#     result = None
#     with establish_connection() as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(statement, variables)
#             try:
#                 result = cursor.fetchone()
#             except psycopg2.ProgrammingError as pe:
#                 pass
#     return result
#
#
# def connection_handler(function):
#     def wrapper(*args, **kwargs):
#         connection = establish_connection()
#         # we set the cursor_factory parameter to return with a RealDictCursor cursor (cursor which provide dictionaries)
#         dict_cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#         ret_value = function(dict_cur, *args, **kwargs)
#         dict_cur.close()
#         connection.close()
#         return ret_value
#     return wrapper
