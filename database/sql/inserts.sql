DELETE FROM extras;
INSERT INTO extras(descripcion,precio) VALUES('POLIMERO NOST3RD', 59);
INSERT INTO extras(descripcion,precio) VALUES('BOMBILLA ALUMINIO CON LIMPIADOR', 50);
INSERT INTO extras(descripcion,precio) VALUES('PEGAMENTO SUPER GLUE', 84);

DELETE FROM categorias;
INSERT INTO categorias(categoria) VALUES('MATES');
INSERT INTO categorias(categoria) VALUES('LLAVEROS');
INSERT INTO categorias(categoria) VALUES('IDENTIFICADORES');
INSERT INTO categorias(categoria) VALUES('OTROS');
INSERT INTO categorias(categoria) VALUES('COMPUTACION');

DELETE FROM cotizacion;
INSERT INTO cotizacion VALUES('costePlastico',1500);
INSERT INTO cotizacion VALUES('costeEnergetico',3.04);
INSERT INTO cotizacion VALUES('consumoMedio',0.9);
INSERT INTO cotizacion VALUES('valorImpresora',33534+53000);
INSERT INTO cotizacion VALUES('tiempoDepresiacion',24);
INSERT INTO cotizacion VALUES('diasActiva',260);
INSERT INTO cotizacion VALUES('horasDia',8);
INSERT INTO cotizacion VALUES('tasaFallos',10);

INSERT INTO usuarios (usuario, password) VALUES('fmartinez','pbkdf2:sha256:260000$b5ILhWjDCVRrpIIm$90afca4c99f2c17f34feb7ab48bca800a95ecad6ffc0c16c52b26abd32f04190');
INSERT INTO usuarios (usuario, password) VALUES('lvidela','pbkdf2:sha256:260000$b5ILhWjDCVRrpIIm$90afca4c99f2c17f34feb7ab48bca800a95ecad6ffc0c16c52b26abd32f04190');

DELETE FROM estados;
INSERT INTO estados (estado, ventas, productos,piezas,saltear,icono) VALUES('PENDIENTE'  ,'1','0','0','0', 'bx-time-five');
INSERT INTO estados (estado, ventas, productos,piezas,saltear,icono) VALUES('EN PROCESO' ,'1','0','0','0', 'bx-time-five' );
INSERT INTO estados (estado, ventas, productos,piezas,saltear,icono) VALUES('IMPRIMIR'   ,'0','1','1','0', 'bxs-printer');
INSERT INTO estados (estado, ventas, productos,piezas,saltear,icono) VALUES('IMPRIMIENDO','0','1','1','0', 'bx-printer');
INSERT INTO estados (estado, ventas, productos,piezas,saltear,icono) VALUES('PINTAR'     ,'0','1','1','1', 'bx-time-five' );
INSERT INTO estados (estado, ventas, productos,piezas,saltear,icono) VALUES('PINTANDO'   ,'0','1','1','0', 'bx-time-five' );
INSERT INTO estados (estado, ventas, productos,piezas,saltear,icono) VALUES('LISTO'      ,'1','1','1','0', 'bx-time-five' );
INSERT INTO estados (estado, ventas, productos,piezas,saltear,icono) VALUES('ENTREGADO'  ,'1','0','0','0', 'bx-time-five' );
INSERT INTO estados (estado, ventas, productos,piezas,saltear,icono) VALUES('CANCELADO'  ,'1','1','0','0', 'bx-time-five' );

DELETE FROM medios_pago;
INSERT INTO medios_pago (descripcion) VALUES('MERCADO PAGO');
INSERT INTO medios_pago (descripcion) VALUES('EFECTIVO');
INSERT INTO medios_pago (descripcion) VALUES('BANCO SANTANDER');