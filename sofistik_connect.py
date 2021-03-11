# based on https://www.sofistik.de/documentation/2020/en/cdb_interfaces/python/examples/python_example1.html


import os
import platform
from ctypes import cdll, c_int
from sofistik_daten import *

try:

    sofi_dir = r".\Sofistik"
    sofi_dir = os.path.abspath(sofi_dir)
    sofi_dir_interface = r".\Sofistik\interfaces\64bit"
    sofi_dir_interface = os.path.abspath(sofi_dir_interface)
    current_path = os.getcwd()

    # Get the DLLs (64bit DLL)
    sof_platform = str(platform.architecture())
    if sof_platform.find("32Bit") < 0:
        # Set DLL dir path
        os.chdir(sofi_dir)
        os.add_dll_directory(sofi_dir_interface)
        os.add_dll_directory(sofi_dir)

        # Get the DLL functions
        myDLL = cdll.LoadLibrary("sof_cdb_w_edu-70.dll")
        py_sof_cdb_get = cdll.LoadLibrary("sof_cdb_w_edu-70.dll").sof_cdb_get
        py_sof_cdb_get.restype = c_int

        py_sof_cdb_kenq = cdll.LoadLibrary("sof_cdb_w_edu-70.dll").sof_cdb_kenq_ex
        os.chdir(current_path)

except Exception as e:
    print("no sofistik files found")


def connect_to_cdb(path):
    Index = c_int()
    cdbIndex = 99
    Index.value = myDLL.sof_cdb_init(path.encode("utf-8"), cdbIndex)
    cdbStat = c_int()  # get the CDB status
    cdbStat.value = myDLL.sof_cdb_status(Index.value)
    print("CDB Status:", cdbStat.value)
    return Index, cdbStat


def close_cdb(Index, cdbStat):
    # Close the CDB, 0 - will close all the files
    myDLL.sof_cdb_close(0)
    cdbStat.value = myDLL.sof_cdb_status(Index.value)
    if cdbStat.value == 0:  # if status = 0 -> CDB Closed successfully
        print("\nCDB closed successfully, status = 0")
