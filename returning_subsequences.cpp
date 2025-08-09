// This is quite memory intensive as it will take around 2^n memory

/**
 * \brief Computes the lexicographically smallest substring of a given string.
 * \param s The input string.
 * \param output The array to store the result.
 */
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




/**
 * \brief Solves a problem by reading a string from input, processing it using the subs function, and outputting the results.
 */
void solve(){
	string s;
	cin >> s;
	string *output = new string[200000];
	int count = subs(s , output);
	for(int i = 0 ; i < count ; i++){
		cout << output[i] << endl;
	}
}
/**
 * \brief Runs the main program, initializes the code, and solves the problem for a specified number of test cases.
 * \return None.
 */
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
