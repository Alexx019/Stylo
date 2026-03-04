# Stylo: Digitalizando la escritura analógica con TinyML

**Stylo** es un proyecto experimental de hardware y Machine Learning diseñado para traducir los movimientos físicos de la escritura a mano alzada en texto digital. 

A diferencia de los enfoques tradicionales basados en pantallas táctiles o sensores externos, Stylo se basa puramente en la captura de la biometría del trazo. Mediante el uso de sensores inerciales (giroscopio) y de presión integrados en un bolígrafo físico, el sistema captura los patrones cinemáticos de la escritura y utiliza redes neuronales para predecir y clasificar los caracteres trazados. Un acercamiento práctico al mundo del *TinyML* combinando electrónica casera e Inteligencia Artificial.

Stylo se diferencia del resto de sistemas de reconocimiento de escritura que ya existen, en que todo lo necesario está dentro del boli. No se necesitan sensores externos o libretas específicas para que el reconocimiento de la escritura funcione.

## Sobre el Proyecto

El objetivo final de **Stylo** es permitir al usuario escribir en cualquier lugar y que el bolígrafo se encargue de interpretar la escritura para guardar el texto en la nube.

Para lograr esto, el sistema se basa puramente en **datos espaciales (rotación y aceleración) y de presión**. El reto principal radica en interpretar estas series temporales de datos en bruto para encontrar los patrones únicos que definen la biometría de cada letra escrita por el usuario.

**El flujo de trabajo conceptual del sistema es el siguiente:**
1. **Contacto y Captura:** El sensor de presión detecta el momento exacto en el que el bolígrafo toca la superficie (inicio y fin del trazo y fuerza), mientras que el giroscopio registra la cinemática del movimiento en el espacio.
2. **Adquisición:** El microcontrolador recoge y empaqueta estos datos brutos.
3. **Inferencia (ML):** Una red neuronal procesa la secuencia temporal de movimientos y calcula la probabilidad estadística de qué carácter o forma se acaba de trazar.
4. **Traducción:** Las predicciones exitosas se concatenan para digitalizar el texto.

Más allá del resultado final, Stylo tiene un fuerte propósito **educativo y experimental**. Es un campo de pruebas personal para explorar hasta dónde se puede llegar combinando hardware asequible con Inteligencia Artificial, y cómo el Machine Learning puede superar problemas clásicos de los sensores inerciales (como el ruido y el *drift* o deriva) para extraer información útil de datos caóticos.
