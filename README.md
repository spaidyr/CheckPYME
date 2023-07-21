# CheckPYME

CheckPYME es una aplicación de comprobación de seguridad con la cual, las pequeñas y medianas empresas (PYMEs) podrán tener una visión global del estado de sus defensas frente a ciber amenazas. Esta aplicación consta de una interfaz amigable que permite evaluar en diferentes umbrales de seguridad cual es el estado de seguridad de los equipos de la organización. Esta capacidad se ve potenciada con la posibilidad de monitorizar en tiempo real las políticas de seguridad implementadas en los dispositivos de los usuarios, así como de personalizar cada uno de los umbrales de seguridad a analizar. 

Actualmente, esta aherramienta goza de módulos que comprueban los nievles de seguridad en base a las guías de configuración segura de Windows 10. No obstante, dado que las arquitecturas tecnológicas de las PYMEs son complejas y adaptativas, se ha propuesto una aplicación totalmente escalable, por lo que el administrador de CheckPYME podrá generar sus propios módulos de comprobación de seguridad, no solo para Windows 10, si no que podrá integrar cualquier tipo de plataforma o servicio. Por otro lado, gracias a Elasticsearch, esta herramienta es fácilmente integrable con otras herramientas de monitorización de seguridad, tales como los Sistemas de Detección de Intrusión (IDS), Sistemas de prevención de Intrusión (IPS), Endpoint Detection Response (EDR), etc., lo que permite ampliar el espectro de trazabilidad en la respuesta ante incidentes.

Por último, dado que para el desarrollo de la herramienta se ha tomado como referencia la estandarización del sistema operativo en Windows. Será necesario un sistema Windows para alojar la aplicación, debido a que algunos archivos se ejecutan bajo esta premisa. No obstante, dado que la herramienta está generada en python, será facilmente adaptable llegado el caso.

En conclusión, la solución propuesta no solo permitirá a las pequeñas y medianas empresas obtener una visión del estado de la seguridad de sus equipos remotos con Windows 10, si no que gracias a la escalabilidad que se propone, se podrá extender a la totalidad de las plataformas operativas dentro de la organización.

# Primeros pasos en la Herramienta.

## Descarga e instalación
Para la descaraga de la aplicación se podrá descargar el fichero ZIP con el proyecto `https://github.com/spaidyr/CheckPYME/archive/refs/heads/main.zip`, o bien descargarlo haciendo uso de la herramienta git `git clone https://github.com/spaidyr/CheckPYME.git`
Será necesario tener Python versión 3.9.13, instalado en el equipo para instalar las librerías necesarias para el correcto funcionamiento del equipo. Para ello, desde la carpeta del proyecto se deberá ejecutar el siguiente comando: `pip install -r Requirements.txt`

## Inicialización por primera vez
Para ejecutar la herramienta, se ejecutará, desde el terminal el archivo `main.py`. El sistema avisará de que se debe configurar la IP del servidor, lo cual se podrá hacer desde el menú `Option Menu > Configuration`.
Tras reiniciar la herramienta, se prodecerá a la instalación de los paquetes necesarios, lo cual se realizará de forma desatendida. Tras este paso, se deberán generar los certificados que validarán las comunicaciones entre los diferentes servicios de la aplicación. La generación de certificados deberá hacerse desde `Options Menu > Configure Certificates`. aui se deberán rellenar cada uno de los campos con los datos correspondientes y el campo `sans_ip` con la IP del Servidor que aloje la aplicación CheckPYME.

## Inicio de Servicios
La aplicación deberá inicializar el servicio de Elasticsearch y de Kibana tras su puesta en marcha. No obstante, si el la primera vez que se inicia la aplicación, se deberán realizar algunos pasos adicionales.
- Inicializar el servicio de ElasticSearch: Este paso se podrá completar desde la opción 'Start Elasticsearch' del menú Elasticsearch, esto abrirá un terminal en el que se podrá ver el estado del Elastic STACK. Además, desde la URL https://127.0.0.1:9200/ se podrá acceder a Elasticsearch, aunque pedirá usuario y contraseña.
- Para poder acceder a Elasticsearch será necesario restablecer la contraseña del usuario `elastic`. Seleccione la opción 'Configure Elasticsearch password' en el menú de Elasticsearch. Aparecerá una ventana emergente donde podrá introducir la nueva contraseña para el usuario "elastic". Presione 'OK' y la aplicación ejecutará el comando `elasticsearch-reset-password` y restablecerá la contraseña del usuario "elastic". 
- El siguiente paso es configurar Kibana, para lo cual, seleccione la opción 'Configure Elasticsearch password' en el menú de Elasticsearch. Aparecerá una ventana emergente donde podrá introducir la nueva contraseña para el usuario "elastic". Presione 'OK' y la aplicación ejecutará el comando `elasticsearch-reset-password` y restablecerá la contraseña del usuario "kybana_system". A continuación apareceré una ventana emergente que pedirá introducir de nuevo la contraseña, esta accion modificará los archivos de configuración asociados.
- Por último, se inicializará el servicio de Kibana desde el menú `Elasticsearch > Start Kibana`. Estas acciones permitirán abrir una interfaz web en https://127.0.0.1:5601, a la que se podrá acceder utilizando las credenciales del usuario `elastic` que se configuró previamente.

Esta GUI facilita el proceso de restablecimiento de la contraseña de Elasticsearch al manejar automáticamente la desactivación y reactivación de la configuración de HTTPS y el reinicio de Elasticsearch. Esto minimiza la interrupción de la seguridad SSL y hace que el proceso sea más fácil y seguro. Sin embargo, recuerde que cualquier cambio en la contraseña debe ser registrado y almacenado de manera segura para evitar problemas futuros.

## Configuración previa al despliegue
La herramienta trabaja sobre diferentes index en Elasticsearch. Será importante, por tanto, inicializar estos índex para evitar problemas futuros durante la indexación de información relativa a la seguridad de los endpoints. Esta comprobación se podrá realizar desde la opción 'Check Index' en el emnú Elasticsearch, la cual generarará los índices en caso de que no existean.
Por último, sedeberá crear el usuario que servirá dpara que los diferentes agentes se autentiquen e inserten información en Elasticsearch. Este usuario está limitado por permisos y roles, por lo que se deberá crear desde la opción 'Create User for client' del menú Elasticsearch.

# Paquete instalador del Agente
CheckPYME utiliza el software 'Inno Setup' para la generación del paquete instalador del cliente. Este paquete se podrá instalar desde la opción 'Generate Packet_Client' del menú 'Option Menu' de la interfaz gráfica de la aplicación. Durante este proceso, CheckPYME comprobará la existencia del software 'Inno Setup', y en caso de no encontrarse se procederá a su instalación. a continuación, se inicializará la compilación del agente, el cual se guardará en la carpeta 'Agent_Installer' del proyecto (NOTA: En el supuesto caso de que el instalador no compile el paquete, se podrá realizar el proceso desde la propia aplicación 'Inno Setup'). 
Una vez Generado el ejecutable, este se deberá instalar en todos los endpoints que se desee con permisos de administrador. La persistencia del agente como servicio aún no está implementada, por lo que se recomienda que cada administrador implemente la que sea necesaria.

