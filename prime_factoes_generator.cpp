void prime_factorsint n){
    while(n % 2 == 0){
    	cout << 2 << " ";
    	n/=2;
    }

    for(int i =  3 ; i < sqrt(n) ; i++){
    	while(n % i == 0){
    		cout << i << " ";
    		n /= i;
    	}
    }


    if(n > 2){
    	cout << n << endl;
    }    
}
