from Libraries import mariaDB


db = mariaDB()
sql = f'select showid, showname, alt_showname, showstatus, premiered from shows ' \
      f'where status = "Followed" and download != "Skip" order by showname'
result = db.execute_sql(sql=sql, sqltype='Fetch')

saved = False
for res in result:
    if not saved:
        prev_show = res[1]
        prev_res = res
        saved = True
    elif prev_show == res[1]:
        print(prev_res)
        print(res)
        prev_show = res[1]
        prev_res = res
        saved = True
    else:
        prev_show = res[1]
        prev_res = res
