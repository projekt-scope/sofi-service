# based on https://www.sofistik.de/documentation/2020/en/cdb_interfaces/python/examples/python_example2.html

from ctypes import sizeof, c_int
from sofistik_daten import *


def get_quad_forces_results(Index, result_dict):
    # 210: maximum forces of Quad elements
    temp = []
    datalen2 = c_int(0)
    ie2 = c_int(0)
    datalen2.value = sizeof(CQUAD_FOC)
    RecLen2 = c_int(sizeof(cquad_foc))
    while ie2.value < 2:
        ie2.value = py_sof_cdb_get(Index, 210, 1, byref(cquad_foc), byref(RecLen2), 1)

        temp.append(cquad_foc.m_nr)
        result_dict["quad_results"].append({"id": cquad_foc.m_nr})

    RecLen2 = c_int(sizeof(cquad_foc))
    print(temp)
    return result_dict
