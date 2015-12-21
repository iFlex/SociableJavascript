function makeid(len)
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < len; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

try {
 //heapSize = 50;
 size = 1024*20;
 var items = [];

 for( var i = 0; i < 1000; ++i ){
 	//print((i+1)*size+"B"+" av:"+_getHeapAvailable()+" hs:"+_getHeapSize());
 	
 	if( i == 625 )
 		_setMaxHeapSize("800");
 	
	//generate 1 MB
 	items.push(makeid(size));
	print(_getHeapSize()); 
}

} catch(e){
  print(e);
}
