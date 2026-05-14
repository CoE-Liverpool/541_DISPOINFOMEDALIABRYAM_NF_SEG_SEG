function(a, b) {
    var alturaTotal = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
    var destino = alturaTotal * 0.75;
    
    window.scrollTo(0, destino);
}