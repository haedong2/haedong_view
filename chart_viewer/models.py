from django.db import models
from django.db.models.base import ModelBase

from django.db import connection

def get_tick_data(subject_code, time_unit, start_date, end_date):
    if exist_table(subject_code + '_tick_10') and time_unit % 10 == 0:
        time_unit = time_unit / 10
        subject_code = subject_code + '_tick_10'
        query = '''
        select t1.id
                , UNIX_TIMESTAMP(t1.date) * 1000 as date
                , t2.open as open
                , t1.high
                , t1.low
                , t3.close as close
                , cast(t1.volume as int) as volume
                , date_format(t1.working_day, '%%Y%%m%%d') as working_day
         from (
               select Floor((result.row-1) / %s) + 1 as id
                    , date
                    , max(result.id) as max_id
                    , min(result.id) as min_id
                    , max(result.high) as high
                    , min(result.low) as low
                    , sum(result.volume) as volume
                    , working_day
                 from (
                           select @rownum:=if(@working_day = s1.working_day, @rownum+1, if(@rownum=1, 1, ((truncate((@rownum-1) / %s, 0) + 1) * %s + 1))) as row,
                                @working_day:= s1.working_day,
                                  s1.*

                             from %s s1
                            inner join (
                                       select @rownum:=1, @working_day:=Date('2000-01-01')
                                         from dual
                                       ) s2
                            WHERE s1.working_day between '%s' and '%s'
                      ) result
                group by working_day, Floor((result.row-1) / %s)
              ) t1
        inner join %s t2
           on t1.min_id = t2.id
        inner join %s t3
           on t1.max_id = t3.id
        ''' % (time_unit, time_unit, time_unit, subject_code, start_date, end_date, time_unit, subject_code, subject_code)
    else:
        query = '''
        select t1.id
                , UNIX_TIMESTAMP(t1.date) * 1000 as date
                , t2.price as open
                , t1.high
                , t1.low
                , t3.price as close
                , cast(t1.volume as int) as volume
                , date_format(t1.working_day, '%%Y%%m%%d') as working_day
         from (
               select Floor((result.row-1) / %s) + 1 as id
                    , date
                    , max(result.id) as max_id
                    , min(result.id) as min_id
                    , max(result.price) as high
                    , min(result.price) as low
                    , sum(result.volume) as volume
                    , working_day
                 from (
                           select @rownum:=if(@working_day = s1.working_day, @rownum+1, if(@rownum=1, 1, ((truncate((@rownum-1) / %s, 0) + 1) * %s + 1))) as row,
                                @working_day:= s1.working_day,
                                  s1.*

                             from %s s1
                            inner join (
                                       select @rownum:=1, @working_day:=Date('2000-01-01')
                                         from dual
                                       ) s2
                            WHERE s1.working_day between '%s' and '%s'
                      ) result
                group by working_day, Floor((result.row-1) / %s)
              ) t1
        inner join %s t2
           on t1.min_id = t2.id
        inner join %s t3
           on t1.max_id = t3.id
        ;
        ''' % (time_unit, time_unit, time_unit, subject_code, start_date, end_date, time_unit, subject_code, subject_code)

    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    result = dictfetchall(cursor)
    return result


def get_hour_data(subject_code, time_unit, start_date='2017-01-01', end_date='2020-12-31'):
    return get_min_data(subject_code, int(time_unit) * 60, start_date, end_date)


def get_min_data(subject_code, time_unit, start_date='2017-01-01', end_date='2020-12-31'):
    sec = int(time_unit) * 60
    query = '''
    SELECT 
        T1.date * 1000 as date,
        T2.price as open,
        T1.high,
        T1.low,
        T3.price as close,
        T1.volume,
        T1.working_day
    FROM
        (
        SELECT
            FLOOR(UNIX_TIMESTAMP(date) / %s) * %s AS date,
            MIN(id) as open_id,
            MAX(price) AS high,
            MIN(price) AS low,
            MAX(id) as close_id,
            SUM(volume) AS volume,
            working_day
        FROM %s
        WHERE working_day between '%s' and '%s'
        GROUP BY FLOOR(UNIX_TIMESTAMP(date)/%s)
        ORDER BY date
        ) T1
        INNER JOIN
        %s T2
        ON T1.open_id = T2.id
        INNER JOIN
        %s T3
        ON T1.close_id = T3.id            
    ''' % (sec, sec, subject_code, start_date, end_date, sec, subject_code, subject_code)

    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    result = dictfetchall(cursor)
    return result

def exist_table(subject_code):
    query = """
    show tables like '%s'
    """ % subject_code

    cursor = connection.cursor()
    cursor.execute(query)
    result = dictfetchall(cursor)

    if len(result) > 0: return True
    return False


def get_subject_date(subject_code):
    query = """
    select
      min(working_day) as start_date,
      max(working_day) as end_date
    from
      %s
    """ % subject_code
    # query = """
    # select
    #   date_format(min(working_day), '%%m/%%d/%%y') as start_date,
    #   date_format(max(working_day), '%%m/%%d/%%y') as end_date
    # from
    #   %s
    # """ % subject_code

    cursor = connection.cursor()
    cursor.execute(query)
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
