import sqlite3

# configure SQLite3 DB for storing tweet replies
sqlite_file = 'lpbcbot_replies.sqlite'
table_replies = 'lpbcbot_replies'
field_mention_id = 'mention_id'
field_mention_id_type = 'INTEGER'

# creates a sqlite file if there isn;t one
sql_session = sqlite3.connect(sqlite_file)
c = sql_session.cursor()

# create table
c.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf} {ft} PRIMARY KEY)'\
        .format(tn=table_replies, nf=field_mention_id, ft=field_mention_id_type))

# commit and close
sql_session.commit()
sql_session.close()
