import json
import os

import requests as requests


def cargar_producto():
    host = os.getenv('HOST')
    file_path = "D:\\STL\\Bella - La bella y la bestia - 15cm"
    archivos = [arch.name for arch in os.scandir(file_path) if arch.is_file() and arch.name.endswith(".gcode")]
    path = "/productos"
    data = {
        "descripcion": "Bella - La bella y la bestia - 15cm",
        "idCategoria": "16",
        "dragAndDrop": [],
        "extras": []
    }

    for a in archivos:
        descripcion = a.split(".")[0]
        with open(f"{file_path}\\{a}", "r") as file:
            for line in file:
                if line.startswith(";TIME:"):
                    time = line.split(":")[1].strip()
                if line.startswith(";Filament used: "):
                    filament_used = line.split(": ")[1].strip()[:-1]
                    break

        agregar = {descripcion: {"time": time, "filament_used": filament_used}}
        data["dragAndDrop"].append(agregar)
    login = requests.post(host + "/login",
                          data=json.dumps({"usuario": "lvidela", "password": "Joaquin.2018"}),
                          headers={"Content-Type": "application/json"}).json()

    response = requests.post(host + path, data=json.dumps(data),
                             headers={"x-access-token": login["token"], "Content-Type": "application/json"})
    print(response.status_code)
    print(response.json())
    assert response


if __name__ == '__main__':
    cargar_producto()
