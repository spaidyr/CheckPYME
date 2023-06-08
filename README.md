# CheckPYME

# Restablecimiento de la contraseña del usuario "elastic" en Elasticsearch con HTTPS usando la Interfaz Gráfica de Usuario (GUI)

El siguiente documento describe cómo restablecer la contraseña del usuario "elastic" y "kybana_system" en un clúster de Elasticsearch que está funcionando con HTTPS y X-Pack utilizando nuestra interfaz gráfica de usuario (GUI). La interfaz ha sido diseñada para automatizar este proceso, haciendo que sea más fácil y seguro.

## Motivo

El motivo de este proceso es que el comando `elasticsearch-reset-password` no tiene una opción directa para desactivar la verificación de SSL durante su ejecución. Como resultado, la configuración de HTTPS en Elasticsearch debe ser desactivada temporalmente para permitir el restablecimiento de la contraseña. Nuestra GUI maneja este proceso automáticamente, lo que permite un restablecimiento seguro y sin problemas de la contraseña.

## Procedimiento

Siga los siguientes pasos para restablecer la contraseña del usuario "elastic":

### 1. Abra la interfaz gráfica de usuario (GUI)

Inicie la aplicación y la interfaz gráfica de usuario (GUI) se mostrará.

### 2. Resetear la contraseña del usuario "elastic"

Seleccione la opción 'Configure Elasticsearch password' en el menú de Elasticsearch. Aparecerá una ventana emergente donde podrá introducir la nueva contraseña para el usuario "elastic". Presione 'OK' y la aplicación ejecutará el comando `elasticsearch-reset-password` y restablecerá la contraseña del usuario "elastic". 

### 3. Resetear la contraseña del usuario "kibana_system"

Seleccione la opción 'Configure Elasticsearch password' en el menú de Elasticsearch. Aparecerá una ventana emergente donde podrá introducir la nueva contraseña para el usuario "elastic". Presione 'OK' y la aplicación ejecutará el comando `elasticsearch-reset-password` y restablecerá la contraseña del usuario "kybana_system". A continuación apareceré una ventana emergente que pedirá introducir de nuevo la contraseña, esta accion modificará los archivos de configuración asociados.

## Nota

Esta GUI facilita el proceso de restablecimiento de la contraseña de Elasticsearch al manejar automáticamente la desactivación y reactivación de la configuración de HTTPS y el reinicio de Elasticsearch. Esto minimiza la interrupción de la seguridad SSL y hace que el proceso sea más fácil y seguro. Sin embargo, recuerde que cualquier cambio en la contraseña debe ser registrado y almacenado de manera segura para evitar problemas futuros.
