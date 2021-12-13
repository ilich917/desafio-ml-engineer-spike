# Descripción de la solución

La solución cuenta con dos carpetas principales: API y Retrain

* Retrain contiene el código y los datos necesarios para reentrenar el modelo. Además se incluye script para cargar nuevos datos.
* API contiene la aplicación para predecir el precio de la leche el próximo mes y el código necesario para crear y exponer una imagen docker.

## Retrain

Para reentrenar el modelo, modifique o reemplace los csv en la carpeta 'Retrain/data' con la información actualizada del último mes.
A continuación ejecute el archivo 'Retrain/main.py'
Luego copie el nuevo modelo en la carpeta model de 'API/app'.
Ya está listo para crear su imagen docker de la API actualizada

## API

La carpeta 'API' contiene el código para crear la imagen docker correspondiente. 

Necesitará tener instalado Docker[1] en su ordenador.
Abra una consola y diríjase a la carpeta 'API'.
Construya una imagen docker a partir del archivo Dockerfile en la carpeta 'API'
Corra el container con el código 'docker run --publish 5000:5000 name_of_image:latest'
La llamada consiste en enviar con POST, un archivo json idéntico al archivo 'API/app/data/latest_month_copy.json', el que deberá completar manualmente una vez al mes con los datos necesarios para predecir el precio de la leche.
Puede realizar llamadas a la dirección 'localhost:5000/' usando CURL o Postman, por ejemplo.
La respuesta sería similar a "[35.96097446546537]", de tipo text/html.

[1]: <https://www.docker.com> "Link al sitio web de Docker"

### Sobre la solución
Supuestos y limitaciones:

* El modelo asume que en la base de datos se encuentran los valores asociados a los últimos 3 meses.
* Dados los datos, el modelo solo puede predecir Mayo del 2020.
* Se asume que los valores del banco central vienen referenciados respecto a cierto año y que las entradas de nuevos datos que se realicen corresponden en formato con las de la base de datos.

Pendiente: 

* Automatizar con algún gestor de DAGs, pero dada la naturaleza del problema, eso podría pueda esperar una segunda versión, ya que la ingesta de datos es solo una vez al mes.
* Mejorar el servicio de Logging ya que actualmente solo guarda las métricas en un csv.


