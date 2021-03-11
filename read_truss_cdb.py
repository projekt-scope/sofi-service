# based on https://www.sofistik.de/documentation/2020/en/cdb_interfaces/python/examples/python_example2.html

from sofistik_daten import *
import os
import platform

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


def check_if_in_list(liste, nr) -> bool:
    for res in liste:
        if res == nr:
            return True
    return False


def get_truss_results(Index, result_dict):
    # 150: truss elements (Fachwerkstäbe)
    # 152: maximum of results of truss elements
    temp = []
    datalen2 = c_int(0)
    ie2 = c_int(0)
    datalen2.value = sizeof(CTRUS_RES)
    RecLen2 = c_int(sizeof(ctrus_res))
    while ie2.value < 2:
        ie2.value = py_sof_cdb_get(Index, 152, 1, byref(ctrus_res), byref(RecLen2), 1)
        if not check_if_in_list(temp, ctrus_res.m_nr) and ctrus_res.m_nr > 0:
            temp.append(ctrus_res.m_nr)
            result_dict["truss_results"].append(
                {"id": ctrus_res.m_nr, "normal-force": ctrus_res.m_n}
            )
    RecLen2 = c_int(sizeof(ctrus_res))
    return result_dict


def get_node_results(Index, result_dict):
    # 24 Node Results
    temp = []
    datalen2 = c_int(0)
    ie2 = c_int(0)
    datalen2.value = sizeof(CN_DISPC)
    RecLen2 = c_int(sizeof(cn_dispc))
    while ie2.value < 2:
        ie2.value = py_sof_cdb_get(Index, 24, 1, byref(cn_dispc), byref(RecLen2), 1)
        if not check_if_in_list(temp, cn_dispc.m_id) and cn_dispc.m_id > 0:
            temp.append(cn_dispc.m_id)
            result_dict["node_results"].append(
                {
                    "id": cn_dispc.m_id,
                    "ux": cn_dispc.m_ux,
                    "uy": cn_dispc.m_uy,
                    "px": cn_dispc.m_px,
                    "py": cn_dispc.m_py,
                }
            )
    RecLen2 = c_int(sizeof(cn_dispc))
    return result_dict
