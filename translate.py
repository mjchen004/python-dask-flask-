import psycopg2
import pandas as pd
from psycopg2.extras import execute_values

# 连接到数据库

dbname="python_dash_flask"
user="tvdi_1t1e_user"
password="rBEiLilhmGmOM5yYkkcujQtLHMaLZaQi"
host="dpg-cqhfldt6l47c73fn0ffg-a.singapore-postgres.render.com"
port="5432"

try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
        sslmode='require'  # 启用 SSL/TLS 连接
    )
    print("Connection successful")
except psycopg2.OperationalError as e:
    print(f"Connection failed: {e.pgcode} - {e.pgerror}")
    raise

cur = conn.cursor()

# 读取CSV文件
df = pd.read_csv('C:/Users/user/Desktop/utf8/2018_utf8.csv')

# 插入数据
try:
    # 将DataFrame转换为list of tuples
    data_tuples = [tuple(x) for x in df.to_numpy()]
    columns = list(df.columns)
    
    # 使用execute_values进行批量插入
    insert_query = f"""
        INSERT INTO public.traffic2018 ({', '.join(['"{}"'.format(col) for col in columns])})
        VALUES %s
    """
    execute_values(cur, insert_query, data_tuples)
    conn.commit()
    print("Data inserted successfully")
except Exception as e:
    print(f"Data insertion failed: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()