




$(document).ready(function(){
    try{
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var canvas = document.getElementById("canvas");
    var ctx = canvas.getContext('2d');
    
    function updateCanvas(images){

        ctx.canvas.width  = window.innerWidth;
        ctx.canvas.height = window.innerHeight;

        images = JSON.parse(images)
        for (i = 0; i < images.length ; i += 1){
            image = images[i];
            
            let width = image[-2];
            let height = image[-1];
            let x = image[1];
            let y = image[2];
            let curImage = new Image(width, height)
            curImage.src = image[0];

            ctx.drawImage(curImage, x, y, width,height);


        }
        


    }

    updateCanvas(JSON.stringify([]));


    socket.on('screen', updateCanvas);
}catch(e){
    alert(e);
}
});