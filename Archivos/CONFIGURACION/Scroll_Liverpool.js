function descargarMultiples() {
  const archivos = [
    { nombre: "archivo1.txt", contenido: "Hola Mundo 1" },
    { nombre: "archivo2.txt", contenido: "Hola Mundo 2" }
  ];

  archivos.forEach(archivo => {
    const enlace = document.createElement("a");
    enlace.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(archivo.contenido);
    enlace.download = archivo.nombre;
    document.body.appendChild(enlace);
    enlace.click(); // Aquí se ejecutan las descargas
    document.body.removeChild(enlace);
  });
}

descargarMultiples();