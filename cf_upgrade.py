# Author: Greg Glezman
#
# Copyright (c) 2018-2022 G.Glezman.  All Rights Reserved.
#
# Upgrade a data file for a new version of the cf code.
# A copy of the original is created as a backup.  Its name is
#         filename.old_version
# The upgraded file has the original name
# 
# Here is the general flow of using the upgrader
# 
#  caller
#     opens data file and verifies magic tag
#  upgrader gets a filename, fileHandle
#     reads version
#     if upgrade required
#         close the file handle
#         reopen and write to a new file fileName.old_version (ie copy it)
#         reopen and
#         write the new version of the data file
#         create a dictionary for each entry, adjusting each entry
#         write the entry back out
#         close the upgraded file
#         reopen and advance beyond the magic number
#      return the fileHandle

# import csv
# import logging
# from shutil import copyfile
# import utilities as util
# import data_file_constants as dfc


def get_raw_version(major, minor):
    """Minor version number maxes out at 99"""
    return major * 100 + minor


def data_file_upgrade(filename, file_handle, parent):
    """Upgrade until we are at the current release level"""
    pass
