import os
import logging
import platform
import shutil
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# ----------- for Upload files---------------------------#
from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp

# ----------- for SOFiSTiK-------------------------------#
import subprocess
from sofistik_connect import connect_to_cdb, close_cdb
from read_truss_cdb import get_truss_results, get_node_results
from read_plate_cdb import get_quad_forces_results


load_dotenv()

log = logging.getLogger("sofi-service")
FORMAT_CONS = "%(asctime)s %(name)-12s %(levelname)8s\t%(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)

log.debug(
    """

░██████╗░█████╗░░█████╗░██████╗░███████╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝
╚█████╗░██║░░╚═╝██║░░██║██████╔╝█████╗░░
░╚═══██╗██║░░██╗██║░░██║██╔═══╝░██╔══╝░░
██████╔╝╚█████╔╝╚█████╔╝██║░░░░░███████╗
╚═════╝░░╚════╝░░╚════╝░╚═╝░░░░░╚══════╝
█                                       █
█  https://www.projekt-scope.de/        █
█        - sofi-service -               █

    """
)


app = FastAPI(
    title="Sofi Service",
    description="This API starts the calculation with SOFiSTiK.",
    version="0.1",
)


class Input(BaseModel):
    dat: str


class Result(BaseModel):
    id: str


def save_upload_file_tmp(upload_file: UploadFile):
    """Saves recieved dat and returns directory"""
    try:
        suffix = Path(upload_file.filename).suffix
        direc = mkdtemp(dir="dat")
        with NamedTemporaryFile(
            delete=False, suffix=suffix, dir=os.path.abspath(direc)
        ) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path, direc


@app.post("/dat2calculationfile/")
async def building_2_dat_file(dat_file: Optional[UploadFile] = File(None)):
    """
        Start calculation from DAT and return directory of the result cdb
        @input: Dat-File
        @return: Name of CDB / directory where CDB is located
    """
    if dat_file is None:
        raise HTTPException(status_code=400, detail="*.dat file is required")
    tmp_path, direc = save_upload_file_tmp(dat_file)
    try:
        program = "C:/Program Files/SOFiSTiK/2018/SOFiSTiK 2018/wps.exe"
        subprocess.call([program, tmp_path, "-b"], timeout=60)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="timeout in calculation")
    except FileNotFoundError:
        log.error("SOFiSTiK is not installed")
        raise HTTPException(status_code=503, detail="SOFiSTiK is not installed")
    finally:
        tmp_path.unlink()  # Delete the temp file
    if platform.system() == "Linux":
        return direc.split("/")[1]
    else:
        return direc.split("\\")[1]


@app.post("/dat2result/frame")
async def dat_2_result(dat_file: Optional[UploadFile] = File(None)):
    """
        Calculate dat and return result-json (truss and node results)
        @input: dat
        @return: result-json
    """
    if dat_file is None:
        raise HTTPException(status_code=400, detail="*.dat file is required")
    res = calculate(dat_file)
    if type(res) == HTTPException:
        raise res
    return return_results_frame(res)


@app.post("/dat2result/building")
async def dat_2_result_building(dat_file: Optional[UploadFile] = File(None)):
    """
        Calculate 3D building dat and return result-json (for quad elements)
        @inupt: dat
        @return: result-json
    """
    if dat_file is None:
        raise HTTPException(status_code=400, detail="*.dat file is required")
    res = calculate(dat_file)
    if type(res) == HTTPException:
        raise res
    return return_results_building(res)


@app.post("/returnResults/")
async def return_result(result: Result):
    """
        Returns result to corresponding calculation id (without starting the calculation again)
        @input: id (json)
        @return: result-json (truss & node results)
    """
    return await return_results_frame(result.id)


def calculate(dat_file):
    tmp_path, direc = save_upload_file_tmp(dat_file)
    try:
        program = os.getenv("SOFISTIK_PATH") + "wps.exe"
        subprocess.call([program, tmp_path, "-b"], timeout=60)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="timeout in calculation")
    except FileNotFoundError:
        log.error("SOFiSTiK is not installed")
        raise HTTPException(status_code=503, detail="SOFiSTiK is not installed")
    finally:
        tmp_path.unlink()  # Delete the temp file
        if platform.system() == "Linux":
            id_ = direc.split("/")[1]
        else:
            id_ = direc.split("\\")[1]
    return id_


def return_results_frame(id_):
    """
        FRAME: Return results to corresponding id
    """
    result_dict = {
        "calculation_id": "",
        "truss_results": [],
        "node_results": [],
    }
    filepath = search_cdb_in_folder(id_)
    index, cdb_stat = connect_to_cdb(filepath)
    result_dict = get_truss_results(index, result_dict)
    result_dict = get_node_results(index, result_dict)
    close_cdb(index, cdb_stat)
    path = Path(os.path.abspath("dat/" + id_))
    # BE CAREFUL WITH `rmtree` !
    shutil.rmtree(path)

    return result_dict


def return_results_building(id_):
    """
        BUILDING: Return results to corresponding id
    """
    result_dict = {"calculation_id": "", "quad_results": []}
    filepath = search_cdb_in_folder(id_)
    index, cdb_stat = connect_to_cdb(filepath)
    result_dict = get_quad_forces_results(index, result_dict)
    close_cdb(index, cdb_stat)
    path = Path(os.path.abspath("dat/" + id_))
    # BE CAREFUL WITH `rmtree` !
    shutil.rmtree(path)

    return result_dict


def search_cdb_in_folder(folder):
    for file in os.listdir("dat/" + folder):
        if file.endswith(".cdb"):
            return os.path.abspath(os.path.join("dat/" + folder, file))
