import sqlite3
import constants

# creates a sqlite file if there isn;t one
sql_session = sqlite3.connect(constants.sqlite_file)
c = sql_session.cursor()

# create table
c.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf} {ft} PRIMARY KEY)'\
        .format(tn=constants.table_replies, nf=constants.field_mention_id, ft=constants.field_mention_id_type))

# commit and close
sql_session.commit()
sql_session.close()
