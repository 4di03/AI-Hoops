

var imageMap = new Map();




$(document).ready(function(){
    try{
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var canvas = document.getElementById("canvas");
    var ctx = canvas.getContext('2d');

    var gameWidth = null;
    var gameHeight = null;
    socket.on('dimensions', function(msg){
        console.log('dimenesions recieved');
        dims = JSON.parse(msg);
        gameWidth = dims[0];
        gameHeight = dims[1];

        // ctx.fillStyle = "black";
        // ctx.fillRect(10,10,200,100);
    });


    // alert(gameWidth, gameHeight);
    
    function updateCanvas(images){

        ctx.canvas.width  = window.innerWidth;
        ctx.canvas.height = window.innerHeight;
        images = JSON.parse(images);
        for (i = 0; i < images.length ; i += 1){
            image = images[i];
            
            let width = image[-2];
            let height = image[-1];
            let x = image[1];
            let y = image[2];
            let src = "../" + image[0];
            

            if (!imageMap.has(src)){
                let img = new Image(width, height);
                img.src = src;
                
                img.onload = function(){

                imageMap.set(src, img);
                };
                
            }

            console.log(imageMap.get(src))
        
            ctx.drawImage(imageMap.get(src), x, y, 50,50);



        }
        


    }

    updateCanvas(JSON.stringify([]));


    socket.on('screen', updateCanvas);
}catch(e){
    alert(e);
}
});