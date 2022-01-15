# Author: Greg Glezman
#
# Copyright (c) 2018-2022 G.Glezman.  All Rights Reserved.
#
# Upgrade a database for a new version of the cf code.
# A copy of the original is created as a backup.  Its name is
#         filename_old_version.db
# The upgraded file has the original name
# 
# Here is the general flow of using the upgrader
# 
#  caller opens the DB and passes in the connection
#  This code
#     returns immediately if the DB is up to date
#     Otherwise,
#        closes the db
#        copies it to filename.old_version.db
#        open the db
#        upgrades it
#        returns a connection to the upgraded BD

import sqlite3
# import csv
# import logging
from shutil import copyfile
# import utilities as util
import data_file_constants as dfc


def get_extended_version(major, minor):
    """Minor version number maxes out at 99"""
    return major * 100 + minor


def database_upgrade(filename, db_conn, cfa):
    """Upgrade until we are at the current release level"""

    version_info = cfa.get_from_db('version_info')
    db_version = version_info[0]['base_version']

    if db_version == dfc.SW_VERSION:
        # db is at correct level
        return db_conn

    # backup the db, adding the version number to the old version filename
    old_db_conn, db_conn = backup_db(filename, db_conn, db_version)

    db_extended_version = get_extended_version(int(db_version.split(".")[0]),
                                               int(db_version.split(".")[1]))
    if db_extended_version < get_extended_version(2, 1):
        upgrade_to_2_1(cfa, db_conn)

    old_db_conn.close()

    return db_conn


def upgrade_to_2_1(cfa, db_conn):
    cfa.set_version(db_conn, 'base_version', dfc.SW_VERSION)


def backup_db(filename, db_conn, old_version):
    # close the original db
    db_conn.close()

    # make a copy - add in the version number
    name = filename.split(".")[0]
    ext = filename.split(".")[1]
    old_filename = name + "_" + old_version + "." + ext

    copyfile(filename, old_filename)

    # reopen the db
    new_db_conn = sqlite3.connect(filename)
    old_db_conn = sqlite3.connect(old_filename)

    return old_db_conn, new_db_conn

