function run(method,iteration,depth){
	//iteration = 500;
	print("RUN:"+iteration+"*"+depth);
	for( var i = 0; i < iteration; ++i )
		method(depth);
}