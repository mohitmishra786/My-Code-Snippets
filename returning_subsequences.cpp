// This is quite memory intensive as it will take around 2^n memory

int subs(string s , string output[]){
	if(s.size() == 0){
		output[0] = "";
		return 1;
	}

	string smallSubstring = s.substr(1);
	int counter = subs(smallSubstring , output);
	for(int i = 0 ; i < counter ; i++){
		output[i + counter] = s[0] + output[i];
	}
	return counter * 2;
}




void solve(){
	string s;
	cin >> s;
	string *output = new string[200000];
	int count = subs(s , output);
	for(int i = 0 ; i < count ; i++){
		cout << output[i] << endl;
	}
}
int main(){
    ios_base::sync_with_stdio(false);
    cin.tie(0);cout.tie(0);
    init_code();

    int t = 1;
   // cin >> t;
    while(t--){
        solve();
    }

}
