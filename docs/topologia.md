# Topología y edición

La anatomía heredada proviene de `03_cuerpo_base.blend` y conserva su original.
En el ensamblaje se separaron la cabeza provisional y los extremos de manos;
se añadieron cabeza, manos, dedos y antebrazos independientes.

El rostro se construye con anillos de quads y desplazamientos para nariz,
mejillas y mentón. Tiene subdivisión no aplicada y shape keys iniciales.
No tiene una retopología facial concéntrica de producción alrededor de boca y
ojos ni cavidad oral preparada para habla.

Las prendas usan superficies con quads, grosor y pliegues modelados. Costuras,
cordones, lentes, hebillas y mechones se convierten en mallas para exportación.
Algunas tapas tienen n-gons. La escena favorece edición por piezas, no un
presupuesto de polígonos para videojuegos.

Las UV se generan por Smart Project. Se comprueba su existencia, pero no se
ha certificado estiramiento ni densidad texel uniforme. Antes de animación
exigente o texturizado pintado, revisar loops de articulaciones, UV, pesos y
correctivos con las poses de prueba.
