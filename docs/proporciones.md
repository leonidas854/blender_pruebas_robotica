# Proporciones de trabajo

La altura del ensamblaje se normaliza a **1.80 m incluyendo cabello y botas**, sobre Z=0. `validacion_viajero.json` contiene la medida al reabrir la escena.

Las fotos tienen perspectiva y ropa: no son escaneos ni fotografías ortográficas calibradas. Los valores siguientes son **estimaciones de modelado**, no mediciones antropométricas exactas.

| Referencia | Coordenada aproximada antes de normalizar |
|---|---|
| Mentón | Z 1.56 m |
| Ojos | Z 1.685 m |
| Cráneo | Z 1.79 m |
| Hombros del traje | X ±0.205 m; Z 1.465 m |
| Codo | X ±0.352 m; Z 1.27 m |
| Muñeca | X ±0.461 m; Z 1.124 m |
| Cadera | X ±0.105 m; Z 0.90 m |
| Rodilla | Z 0.49 m |
| Tobillo | Z 0.10 m |

La cabeza mide unos 0.23 m antes de normalizar, cerca de un canon de 7.7 cabezas. El factor real está en la propiedad de escena `factor_escala` y el desplazamiento en `suelo_origen`.

Se conserva el original `03_cuerpo_base.blend` preferido por el usuario. El ensamblaje usa una copia de su anatomía, oculta bajo el traje; cabeza, manos y antebrazos visibles se desarrollaron aparte. Estas diferencias no son ajustes exactos de biometría.
