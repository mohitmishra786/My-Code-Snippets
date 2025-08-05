/**
 * \brief Recursively prints all permutations of a given string
 * 
 * \param s The input string
 * \param o The output string
 * \return None
 */
void subs(string s , string o){
    if(s.length() == 0){
        cout << o << endl;
        return;
    }

    subs(s.substr(1) , o);
    subs(s.substr(1) , o + s[0]);

}

/**
 * \brief Reads a string input and calls the subs function
 * 
 * \param input A string input
 * \return No return value
 */
void solve(){
    string input;
    cin >> input;
    string output = "";
    subs(input , output);
}
