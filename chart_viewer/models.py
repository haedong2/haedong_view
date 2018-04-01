from django.db import models
from django.db.models.base import ModelBase

def get_chart_data():
    query_string = """
    select Floor((result.row-1) / 60) + 1 as id
        , max(case when mod((result.row-1), 60) = 0 then date end) as date
        , max(price) as high
        , min(price) as low 
        , max(case when mod((result.row-1), 60) = 0 then price end) as open
        , max(case when mod((result.row-1), 60) = 59 then price end) as close
          from (select @rownum:=@rownum+1 as row
                      , price , cast(date as unsigned) as date
                 from GCJ17
                  , (select @rownum:=0) R
               )result
                 group by Floor((result.row-1) / 60)
    """

    from django.db import connection

    cursor = connection.cursor()
    res = cursor.execute(query_string)
    result = dictfetchall(cursor)
    return result

def get_deposit_history():
    query_string = "select * from deposit_history"

    from django.db import connection

    cursor = connection.cursor()
    res = cursor.execute(query_string)
    result = dictfetchall(cursor)
    return result

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def create_model(db_table):
    print("db_table: " + db_table)

    class CustomMetaClass(ModelBase):
        def __new__(cls, name, bases, attrs):
            model = super(CustomMetaClass, cls).__new__(cls, name, bases, attrs)
            model._meta.db_table = db_table
            return model

    class CustomModel(models.Model, metaclass=CustomMetaClass):

        # define your fileds here
        date = models.CharField(max_length=14)
        open = models.CharField(max_length=9)
        high = models.CharField(max_length=9)
        low = models.CharField(max_length=9)
        close = models.CharField(max_length=9)
    return CustomModel
