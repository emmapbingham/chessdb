# chessdb

This is a repo for the chess database project. 

To create a database, you need to download a zipped PGN file from database.lichess.org and unzip it using `pzstd -d filename.pgn.zst`. Then you can use the db.py file to create a SQLite3 DB and insert all the games from the file. This may take a few minutes. There are no dependencies for this script, just the Python standard library. I am currently using Python 3.10 but it probably works for other versions of Python too.

There is also a notebook (query.ipynb) with example queries you can try once you've created the database. This has numpy and pandas as dependencies. 